#!/usr/bin/env python3
"""
AquaPulse TUI ダッシュボード - Pip-Boy 風（総合依頼書準拠）
Dolphie/Grafana のような滑らかな点字折れ線 + Pip-boy グリーンモノクローム。
plotext でグラフ描画、800x480 最適化。
"""
import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# デバッグログ設定
logging.basicConfig(
    filename='/tmp/aquapulse-debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Grid, Vertical
from textual.events import Resize
from textual.widgets import Static
from textual import work

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db import (
    get_conn,
    get_water_temp_series,
    get_room_temp_series,
    get_humidity_series,
    get_light_state,
)
from plotext_wrapper import build_pipboy_line_plot, PIPBOY_DIM, PIPBOY_GREEN

# Pip-boy カラー（plotext_wrapper と共通）
PIPBOY_BG = "#0a0e0a"
PIPBOY_ACCENT = "#00ff88"

JST = ZoneInfo("Asia/Tokyo")

# グラフのリサンプル数（24h）
GRAPH_BUCKETS = 80


def _resample(
    series: list[tuple[datetime, float]], hours: int, buckets: int
) -> tuple[list[datetime], list[float]]:
    """時系列を等間隔にリサンプル（前方補完）。(timestamps, values) を返す。"""
    if not series:
        return [], []
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)
    step_sec = hours * 3600 / buckets
    timestamps = []
    result = []
    idx = 0
    last_val = series[0][1] if series else 0.0
    for i in range(buckets):
        t = start.timestamp() + i * step_sec
        timestamps.append(datetime.fromtimestamp(t, tz=timezone.utc))
        while idx < len(series) and series[idx][0].timestamp() <= t:
            last_val = series[idx][1]
            idx += 1
        result.append(last_val)
    return timestamps, result


class GraphWidget(Static):
    """Static を直接継承し、update() で描画。Vertical のネスト問題を回避。"""

    def __init__(self, unit: str = "", **kwargs):
        super().__init__("", **kwargs)
        self.unit = unit
        self.series: list[float] = []
        self.timestamps: list[datetime] = []
        self._valid_width = 0
        self._valid_height = 0

    # これより小さいサイズは「レイアウト計算中の一時値」とみなし、キャッシュを更新しない
    _MIN_VALID_WIDTH = 20
    _MIN_VALID_HEIGHT = 5

    def on_resize(self, event: Resize) -> None:
        """レイアウト確定時に正しい物理サイズをキャッシュし、再描画する。"""
        w = max(0, event.size.width - 2)
        h = max(0, event.size.height - 1)
        logging.debug(f"on_resize: event.size={event.size.width}x{event.size.height}, w={w}, h={h}, cache={self._valid_width}x{self._valid_height}")
        if w >= self._MIN_VALID_WIDTH and h >= self._MIN_VALID_HEIGHT:
            self._valid_width = w
            self._valid_height = h
        self._redraw()

    def _redraw(self) -> None:
        """キャッシュされたサイズで build_pipboy_line_plot を呼び、自身を update する。"""
        try:
            if self._valid_width <= 0 or self._valid_height <= 0:
                return
            if not self.series or len(self.series) < 2:
                return
            logging.debug(f"_redraw: DRAWING {self._valid_width}x{self._valid_height}")
            plot_text = build_pipboy_line_plot(
                self.series, self.unit,
                width=self._valid_width, height=self._valid_height,
                timestamps=self.timestamps,
            )
            # 自身を直接 update し、即座に再描画を強制
            self.update(plot_text, layout=False)
            self.refresh(layout=True)  # 即座にレイアウト再計算と再描画を強制
        except Exception as e:
            logging.error(f"_redraw: EXCEPTION {e}")


class GraphPanel(Vertical):
    """線グラフパネル（plotext 点字折れ線 + タイトル + 最新値）"""

    def __init__(self, title: str, unit: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.unit = unit
        self.series: list[float] = []
        self.timestamps: list[datetime] = []
        self.latest: float | None = None

    def compose(self) -> ComposeResult:
        yield Static(f"{self.title} 24h", classes="panel-title")
        yield GraphWidget(unit=self.unit, id="graph")
        yield Static("", id="latest", classes="panel-latest")

    def update_data(
        self,
        series: list[float] | None = None,
        timestamps: list[datetime] | None = None,
        latest: float | None = None,
    ) -> None:
        """データのみ更新。call_from_thread 経由でメインスレッドから呼ばれ、描画は安全に実行される。"""
        if series is not None:
            self.series = series
        if timestamps is not None:
            self.timestamps = timestamps
        if latest is not None:
            self.latest = latest
        logging.debug(f"GraphPanel.update_data: title={self.title}, series_len={len(self.series)}, latest={self.latest}")
        try:
            g = self.query_one("#graph", GraphWidget)
            g.series = self.series
            g.timestamps = self.timestamps
            g.unit = self.unit
            logging.debug(f"GraphPanel.update_data: calling g._redraw(), g.cache={g._valid_width}x{g._valid_height}")
            g._redraw()  # キャッシュされたサイズで update() による描画（refresh 依存なし）

            lw = self.query_one("#latest", Static)
            if self.latest is not None:
                lw.update(f"{self.latest:.1f} {self.unit}", layout=False)
            else:
                lw.update("--", layout=False)
        except Exception as e:
            logging.error(f"GraphPanel.update_data: EXCEPTION {e}")


class TankStatusPanel(Static):
    """Tapo_Tank_Light: 現在のステータスを大きく ON/OFF で中央表示"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_on = False

    def compose(self) -> ComposeResult:
        yield Static("Tapo_Tank_Light", classes="panel-title")
        yield Static("", id="tank-status")

    def update_data(self, is_on: bool | None = None) -> None:
        if is_on is not None:
            self.is_on = is_on
        try:
            w = self.query_one("#tank-status", Static)
            status = "ON" if self.is_on else "OFF"
            from rich.style import Style
            style = Style(bold=True, color=PIPBOY_ACCENT) if self.is_on else Style(dim=True, color=PIPBOY_DIM)
            # layout=False: レイアウト再計算を防ぎ、Resize イベントの発火を抑制
            w.update(Text(status, style=style), layout=False)
        except Exception:
            pass


class AquaPulseDashboard(App[None]):
    """Pip-Boy 風 AquaPulse ダッシュボード（総合依頼書準拠）"""

    CSS = f"""
    Screen {{
        background: {PIPBOY_BG};
        overflow: hidden;
        scrollbar-size: 0 0;
    }}

    #header {{
        dock: top;
        color: {PIPBOY_GREEN};
        height: 1;
        padding: 0 2;
        width: 100%;
    }}

    #main {{
        layout: grid;
        grid-size: 2 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr;
        height: 1fr;
        padding: 1 2;
        overflow: hidden;
        scrollbar-size: 0 0;
    }}

    .panel {{
        height: 1fr;
        border: solid {PIPBOY_DIM};
        padding: 1 2;
        margin: 1;
        overflow: hidden;
    }}

    .panel-title {{
        color: {PIPBOY_DIM};
        text-style: bold;
        height: auto;
    }}

    #graph {{
        height: 1fr;
        color: {PIPBOY_GREEN};
    }}


    .panel-latest {{
        color: {PIPBOY_ACCENT};
        height: auto;
    }}

    #tank-status {{
        color: {PIPBOY_ACCENT};
        text-align: center;
        padding: 2 0;
        height: 1fr;
        content-align: center middle;
    }}

    #status {{
        background: {PIPBOY_BG};
        color: {PIPBOY_DIM};
    }}
    """

    def compose(self) -> ComposeResult:
        yield Static("Loading...", id="header")
        with Grid(id="main"):
            yield GraphPanel("Water Temp", "°C", id="water", classes="panel")
            yield GraphPanel("Tapo_Temp", "°C", id="room", classes="panel")
            yield GraphPanel("Tapo_Humidity", "%", id="humidity", classes="panel")
            yield TankStatusPanel(id="light", classes="panel")
        yield Static("", id="status")

    def on_mount(self) -> None:
        # マウント直後にヘッダーに初期表示（DB取得前に見えるように）
        now_str = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
        self.query_one("#header", Static).update(
            f"{now_str}  |  Water: --  |  Room: --  |  Hum: --  |  Light: --",
            layout=False
        )
        self.set_interval(30, self.refresh_data)
        self.refresh_data()
        # ゴースト対策：常に1秒ごとに強制再描画
        self.set_interval(1, self._force_redraw_all)

    def _force_redraw_all(self) -> None:
        """全グラフを強制再描画"""
        logging.debug("_force_redraw_all: START")
        for panel_id in ["water", "room", "humidity"]:
            try:
                p = self.query_one(f"#{panel_id}", GraphPanel)
                g = p.query_one("#graph", GraphWidget)
                g._redraw()
            except Exception as e:
                logging.error(f"_force_redraw_all: {panel_id} error: {e}")
        logging.debug("_force_redraw_all: END")

    @work(exclusive=True, thread=True)
    def refresh_data(self) -> None:
        """データ更新"""
        logging.debug("refresh_data: START")
        try:
            conn = get_conn()
            try:
                w_raw = get_water_temp_series(conn, 24)
                h_raw = get_humidity_series(conn, 24)
                r_raw = get_room_temp_series(conn, 24)
                light_val, _ = get_light_state(conn)

                w_series = [v for _, v in w_raw]
                h_series = [v for _, v in h_raw]
                r_series = [v for _, v in r_raw]

                w_ts, w_resampled = _resample(w_raw, 24, GRAPH_BUCKETS)
                h_ts, h_resampled = _resample(h_raw, 24, GRAPH_BUCKETS)
                r_ts, r_resampled = _resample(r_raw, 24, GRAPH_BUCKETS)

                w_latest = w_series[-1] if w_series else None
                h_latest = h_series[-1] if h_series else None
                r_latest = r_series[-1] if r_series else None
                is_on = light_val is not None and light_val > 0.5

                def safe_update(panel_id: str, **kwargs) -> None:
                    try:
                        p = self.query_one(f"#{panel_id}")
                        if hasattr(p, "update_data"):
                            p.update_data(**kwargs)
                    except Exception:
                        pass

                def update_header() -> None:
                    try:
                        now_str = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
                        w = f"{w_latest:.1f}°C" if w_latest is not None else "--"
                        r = f"{r_latest:.1f}°C" if r_latest is not None else "--"
                        h = f"{h_latest:.1f}%" if h_latest is not None else "--"
                        l = "ON" if is_on else "OFF"
                        # layout=False: レイアウト再計算を防ぎ、Resize イベントの発火を抑制
                        self.query_one("#header", Static).update(
                            f"{now_str}  |  Water: {w}  |  Room: {r}  |  Hum: {h}  |  Light: {l}",
                            layout=False
                        )
                    except Exception:
                        pass

                def safe_status_update(msg: str) -> None:
                    try:
                        # layout=False: レイアウト再計算を防ぎ、Resize イベントの発火を抑制
                        self.query_one("#status", Static).update(msg, layout=False)
                    except Exception:
                        pass

                # call_from_thread でメインスレッドにディスパッチ
                self.call_from_thread(lambda: safe_update("water", series=w_resampled, timestamps=w_ts, latest=w_latest))
                self.call_from_thread(lambda: safe_update("room", series=r_resampled, timestamps=r_ts, latest=r_latest))
                self.call_from_thread(lambda: safe_update("humidity", series=h_resampled, timestamps=h_ts, latest=h_latest))
                self.call_from_thread(lambda: safe_update("light", is_on=is_on))
                self.call_from_thread(update_header)

                now = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")
                self.call_from_thread(lambda: safe_status_update(now))
                logging.debug("refresh_data: END")
            finally:
                conn.close()
        except Exception as e:
            logging.error(f"refresh_data: EXCEPTION {e}")
            def show_db_error() -> None:
                try:
                    self.query_one("#status", Static).update(f"DB Error: {str(e)[:50]}", layout=False)
                except Exception:
                    pass
            try:
                self.call_from_thread(show_db_error)
            except Exception:
                pass


def main() -> None:
    app = AquaPulseDashboard()
    app.run()


if __name__ == "__main__":
    main()
