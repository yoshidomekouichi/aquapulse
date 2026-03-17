"""
plotext を Textual 上で Pip-boy 風にレンダリングするラッパー。
Dolphie/Grafana のような滑らかな点字折れ線 + Pip-boy グリーンモノクローム。
複数パネル同時描画時の plotext グローバル状態衝突を防ぐため Lock で直列化。
"""
from datetime import datetime
from zoneinfo import ZoneInfo
import re
import threading
import logging

from rich.text import Text
from rich.style import Style

_PLOT_LOCK = threading.Lock()

# Pip-boy カラー（階調で奥行き）
PIPBOY_GREEN = "#00ff41"
PIPBOY_DIM = "#00aa2a"
PIPBOY_GRID = "#005500"  # グリッド・目盛り：暗いグリーンで目立たせない

JST = ZoneInfo("Asia/Tokyo")

PLOT_WIDTH_FALLBACK = 50
PLOT_HEIGHT_FALLBACK = 18
PLOT_SIZE_MAX = 200


def _safe_int(val, fallback: int, min_val: int = 2, max_val: int = PLOT_SIZE_MAX) -> int:
    """安全に整数に変換し、範囲内にクランプする。"""
    try:
        n = int(val) if val is not None else fallback
        return max(min_val, min(max_val, n)) if n > 0 else fallback
    except (TypeError, ValueError):
        return fallback


def build_pipboy_line_plot(
    values: list[float],
    unit: str,
    width: int | None = None,
    height: int | None = None,
    timestamps: list[datetime] | None = None,
) -> Text:
    """plotext で点字折れ線グラフを生成し、Pip-boy グリーンで Rich Text に変換。
    呼び出しはメインスレッドの update_data/_redraw から。Lock で直列化し Race Condition を防止。"""
    try:
        import plotext as plt
    except ImportError:
        return Text.from_markup(f"[dim]plotext not installed[/]")

    if not values or len(values) < 2:
        return Text.from_markup(f"[{PIPBOY_DIM}]-- no data --[/]")

    w = _safe_int(width, PLOT_WIDTH_FALLBACK)
    h = _safe_int(height, PLOT_HEIGHT_FALLBACK)
    logging.debug(f"build_pipboy_line_plot: input width={width}, height={height} -> w={w}, h={h}")

    with _PLOT_LOCK:
        canvas = ""
        try:
            # 前回の描画状態を完全にリセット（必須）
            plt.clf()
            plt.limit_size(False, False)
            plt.plot_size(w, h)
            plt.theme("clear")
            plt.title("")
            plt.xlabel("")
            plt.ylabel("")
            plt.xaxes(True, False)

            x = list(range(len(values)))
            plt.plot(x, values, marker="braille", fillx=False)
            plt.grid(True)
            plt.ticks_color("green")

            if timestamps and len(timestamps) == len(values):
                n = len(values)
                tick_indices = [0, n // 4, n // 2, 3 * n // 4, n - 1]
                tick_indices = list(dict.fromkeys(tick_indices))
                labels = [
                    timestamps[i].astimezone(JST).strftime("%H:%M")
                    for i in tick_indices
                ]
                plt.xticks(tick_indices, labels)

            canvas = plt.build()
        except Exception:
            return Text.from_markup(f"[{PIPBOY_DIM}]plot error[/]")
        finally:
            try:
                plt.clf()
            except Exception:
                pass

    try:
        plain = re.sub(r"\033\[[0-9;]*m", "", canvas) if isinstance(canvas, str) else str(canvas)
    except Exception:
        return Text.from_markup(f"[{PIPBOY_DIM}]render error[/]")

    style = Style(color=PIPBOY_GREEN)
    grid_style = Style(color=PIPBOY_GRID)
    t = Text()
    for i, line in enumerate(plain.splitlines()):
        if i > 0:
            t.append("\n")
        s = grid_style if ("│" in line or "─" in line or "┌" in line or "┐" in line or "└" in line or "┘" in line) else style
        t.append(line, style=s)
    return t
