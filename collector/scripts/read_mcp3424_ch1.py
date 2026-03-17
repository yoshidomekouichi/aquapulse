#!/usr/bin/env python3
"""
MCP3424 CH1（TDS センサー）の生電圧を読むテストスクリプト。

ホスト上で実行すること（/dev/i2c-1 にアクセスするため）。
事前に `sudo modprobe i2c-dev` を実行しておく。

Usage:
    python3 collector/scripts/read_mcp3424_ch1.py
"""
import smbus
import time

# === I2C の設定 ===
# ラズパイのピン3(SDA), 5(SCL) が接続されているバス番号
I2C_BUS = 1
# MCP3424 の I2C アドレス（Adr0, Adr1 を GND に接続した場合 0x68）
MCP3424_ADDR = 0x68


def read_ch1_voltage():
    """
    MCP3424 CH1 の電圧（V）を返す。
    18bit 分解能、1x ゲイン、ワンショット変換。
    """
    # --- I2C 通信の開始 ---
    # smbus は I2C プロトコルを抽象化したライブラリ
    # /dev/i2c-1 を開き、デバイスとやり取りする準備
    bus = smbus.SMBus(I2C_BUS)
    try:
        # --- ADC（MCP3424）への設定送信 ---
        # MCP3424 は「設定バイト」を書き込むと、その設定で変換を開始する
        # 0x80 = 0b10000000 の意味:
        #   bit7(RDY)=1: 新規変換開始
        #   bit6-5(C1,C0)=00: チャンネル1（CH1）を選択
        #   bit4-3(O1,O0)=00: ワンショット変換（1回だけ変換して停止）
        #   bit2-1(S1,S0)=00: 240 SPS（1秒あたり240サンプル）
        #   bit0(G0)=0: ゲイン1x（入力電圧をそのまま測定）
        bus.write_byte(MCP3424_ADDR, 0x80)

        # --- 変換完了待ち ---
        # ADC がアナログ電圧をデジタル値に変換するのに時間がかかる
        # 240 SPS なら約 4ms で完了するが、余裕を持って 100ms 待つ
        time.sleep(0.1)

        # --- ADC からのデータ読み取り ---
        # MCP3424 は 4 バイトを返す: [データ上位][データ中位][データ下位][設定バイト]
        # read_i2c_block_data(addr, cmd, length): cmd はレジスタ指定（MCP3424 では 0 でよい）
        raw = bus.read_i2c_block_data(MCP3424_ADDR, 0, 4)

        # --- 18bit デジタル値への復元 ---
        # MCP3424 の 18bit モードでは、先頭バイトの下位 2bit だけが有効
        # （上位 6bit は符号拡張のため 0 または 1 で埋まる）
        # マスクしないと 0xff が 24bit として解釈され、128V などの異常値になる
        val = ((raw[0] & 0x03) << 16) | (raw[1] << 8) | raw[2]

        # --- 符号付き整数への変換 ---
        # 18bit 符号付き: -131072 〜 131071
        # bit17 が 1 なら負の値。32bit に符号拡張する
        if val & 0x20000:
            val -= 0x40000

        # --- 電圧（V）への変換 ---
        # MCP3424 の内部基準電圧は 2.048V
        # 18bit の最大値 262144 (= 2^18) が 2.048V に相当
        # 例: val=-6400 → -6400 * 2.048 / 262144 ≈ -0.05V
        voltage = val * 2.048 / 262144

        return voltage
    finally:
        bus.close()


if __name__ == "__main__":
    # --- TDS センサーについて ---
    # TDS センサーは水の導電率に応じた電圧（0〜3.3V 付近）を出力する
    # この電圧を MCP3424 がデジタル化している
    # 本スクリプトは「生の電圧」のみ表示。TDS 値(ppm)への換算は別処理
    v = read_ch1_voltage()
    print(f"CH1 voltage: {v:.4f} V")
