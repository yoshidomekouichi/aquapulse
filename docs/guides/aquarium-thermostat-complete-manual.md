# 水温監視+ファン自動制御システム 完全実装マニュアル

**最終更新:** 2026-07-11 (スキーマ更新)  
**対象システム:** ESP32 + GCP + Tapo P300  
**想定期間:** 4週間（お盆前完成）  
**難易度:** 初心者OK（超詳細説明）

**⚠️ 重要: 新スキーマ対応 (2026-07-11)**

このマニュアルは、因果推論分析に対応した新しいBigQueryスキーマで更新されています。主な変更点：

1. **`sensor_readings` テーブル拡張**: `sensor_type`, `location`, `device_id`, `firmware_version` フィールド追加
2. **`control_events` テーブル新規作成**: ファン制御イベントと手動介入イベントを記録
3. **因果推論対応**: ファンの冷却効果や水換えの影響を分析可能な設計

詳細は [ADR-0006: Simplified Schema Design](../decisions/0006-simplified-schema-design.md) を参照してください。

---

## 📑 目次

### 🚀 [はじめに](#はじめに)
- [このマニュアルについて](#このマニュアルについて)
- [全体像](#全体像)
- [実装ルート選択](#実装ルート選択)
- [必要なもの](#必要なもの)

### 📦 [Part A: ハードウェア編](#part-a-ハードウェア編)
- [A1. 環境準備（ハードウェア）](#a1-環境準備ハードウェア)
- [A2. ESP32配線実装](#a2-esp32配線実装)
- [A3. MicroPython セットアップ](#a3-micropython-セットアップ)
- [A4. センサー動作確認](#a4-センサー動作確認)
- [A5. WiFi接続実装](#a5-wifi接続実装)

### ☁️ [Part B: クラウド編](#part-b-クラウド編)
- [B1. 環境準備（クラウド）](#b1-環境準備クラウド)
- [B2. GCP プロジェクト作成](#b2-gcp-プロジェクト作成)
- [B3. Cloud Functions デプロイ](#b3-cloud-functions-デプロイ)
- [B4. BigQuery セットアップ](#b4-bigquery-セットアップ)
- [B5. Grafana セットアップ](#b5-grafana-セットアップ)
- [B6. Tapo P300 設定](#b6-tapo-p300-設定)

### 🔗 [Part C: 統合編](#part-c-統合編)
- [C1. ESP32からデータ送信](#c1-esp32からデータ送信)
- [C2. サーモスタット動作確認](#c2-サーモスタット動作確認)
- [C3. 統合テスト](#c3-統合テスト)
- [C4. 長期運用準備](#c4-長期運用準備)

### 📚 [付録](#付録)
- [コマンド集](#コマンド集)
- [コード全文](#コード全文)
- [トラブルシューティング総合](#トラブルシューティング総合)
- [よくある質問FAQ](#よくある質問faq)
- [リファレンス](#リファレンス)

---

## はじめに

### このマニュアルについて

#### 📖 このマニュアルの特徴

**1. 超詳細説明**
- コマンド1つ1つに期待される出力を記載
- 「なぜこの設定が必要か」も説明
- エラーパターンと解決策を豊富に掲載

**2. 疎結合設計**
- 各セクションが独立して実行可能
- クラウドだけ先に設定してもOK
- ハードウェアだけ先に組んでもOK

**3. 実践的**
- コピペで動くコマンド
- 実際に遭遇するエラーを網羅
- チェックリストで進捗確認

#### 🎯 達成目標

このマニュアル完遂で以下が実現します：

✅ ESP32で水温を60秒ごとに測定  
✅ GCPに自動送信してBigQueryに保存  
✅ Grafanaでリアルタイム可視化  
✅ 水温28℃でファン自動ON  
✅ 水温26℃でファン自動OFF  
✅ LINE通知で状態確認  
✅ お盆1週間不在でも安心

#### ⏱️ 所要時間

| フェーズ | 所要時間 | 実施タイミング |
|---------|---------|--------------|
| Part A (ハードウェア) | 4-6時間 | 週末1日 |
| Part B (クラウド) | 4-6時間 | 平日夜×3 or 週末1日 |
| Part C (統合) | 2-3時間 | 週末半日 |
| **合計** | **10-15時間** | **1-2週間** |

---

### 全体像

#### システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                      水槽（Physical）                        │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐         │
│  │ DS18B20  │      │   ESP32  │      │ Tapo P300│         │
│  │水温センサー│─────│ + WiFi   │      │ファン接続 │         │
│  └──────────┘      └─────┬────┘      └─────▲────┘         │
│                          │                  │               │
└──────────────────────────┼──────────────────┼───────────────┘
                           │                  │
                    WiFi (HTTPS POST)    WiFi (制御)
                           │                  │
                           ▼                  │
              ┌────────────────────────┐      │
              │  Cloud Functions       │      │
              │  (HTTP endpoint)       │      │
              └──────┬─────────────────┘      │
                     │                        │
         ┌───────────┴──────────┐             │
         │                      │             │
         ▼                      ▼             │
  ┌─────────────┐      ┌──────────────┐      │
  │  BigQuery   │      │ Thermostat   │──────┘
  │  (データ保存)│      │ (温度判定)    │
  └──────┬──────┘      └──────────────┘
         │
         ▼
  ┌─────────────┐
  │  Grafana    │
  │  (可視化)    │
  └─────────────┘
```

#### データフロー

**1. 測定（60秒ごと）**
```
ESP32 → DS18B20から温度読み取り → JSON形式で準備
```

**2. 送信（WiFi経由）**
```
ESP32 → HTTPS POST → Cloud Functions (ingest)
```

**3. 保存**
```
Cloud Functions → BigQuery (sensor_readings テーブル)
```

**4. 制御判定**
```
Cloud Functions (thermostat) → 
  - 温度 ≥ 28℃ → Tapo P300 ON
  - 温度 ≤ 26℃ → Tapo P300 OFF
  - LINE通知送信
```

**5. 可視化**
```
Grafana → BigQuery → グラフ表示
```

---

### 実装ルート選択

あなたの状況に合わせて選んでください。

#### 🎯 ルート1: 順番通り実装（推奨）

```
Part A → Part B → Part C
```

**こんな人におすすめ:**
- 週末に集中して実装したい
- 初めてなのでステップバイステップが良い

**スケジュール例:**
- **土曜日**: Part A（ハードウェア）
- **日曜日**: Part B（クラウド）
- **次の週末**: Part C（統合）

**所要時間:** 2日間（集中すれば1日でも可）

---

#### ☁️ ルート2: クラウド先行

```
Part B → Part A → Part C
```

**こんな人におすすめ:**
- 今日は外出先でクラウド設定だけ進めたい
- ESP32がまだ届いていない
- 先にクラウド環境を整えておきたい

**メリット:**
- ESP32なしでもクラウド設定完了
- 後でハードウェア接続するだけ
- 移動時間を有効活用

**スケジュール例:**
- **平日夜1**: B1, B2（GCP環境構築）
- **平日夜2**: B3, B4（Cloud Functions, BigQuery）
- **平日夜3**: B5, B6（Grafana, Tapo）
- **週末**: Part A, Part C（ハードウェア + 統合）

**所要時間:** 3日間（分散）

---

#### 🔧 ルート3: ハードウェア先行

```
Part A → Part B → Part C
```

**こんな人におすすめ:**
- まず物理的に動作確認したい
- クラウドは後でゆっくり設定
- センサーの動作が不安

**メリット:**
- ハードウェアの動作確認が先
- 問題があれば早期発見
- クラウド設定は後で落ち着いて

**スケジュール例:**
- **週末1**: Part A（ハードウェア）
- **平日**: Part B（クラウド）
- **週末2**: Part C（統合）

**所要時間:** 2週間（分散）

---

#### 🔀 ルート4: 分散実装（忙しい人向け）

```
B1, B2 → A1, A2 → A3 → B3, B4 → B5, B6 → C
```

**こんな人におすすめ:**
- 平日は1時間ずつしか時間がない
- 週末もまとまった時間がない
- コツコツ進めたい

**スケジュール例:**
- **月曜夜 (1h)**: B1（GCP環境構築）
- **火曜夜 (1h)**: B2（プロジェクト作成）
- **水曜夜 (1h)**: A1, A2（部品準備、配線）
- **木曜夜 (1h)**: A3（MicroPython）
- **金曜夜 (2h)**: B3, B4（Cloud Functions, BigQuery）
- **土曜 (2h)**: B5, B6（Grafana, Tapo）
- **日曜 (3h)**: Part C（統合テスト）

**所要時間:** 1週間（分散）

---

### 必要なもの

#### 📦 ハードウェア（合計 ¥3,100）

| 項目 | 数量 | 単価 | 小計 | 購入先 | 必須度 |
|-----|-----|-----|------|--------|-------|
| ESP32-DevKitC (38ピン) | 1 | ¥1,500 | ¥1,500 | Amazon, 秋月電子 | ✅ 必須 |
| DS18B20 防水温度センサー | 1 | ¥500 | ¥500 | Amazon, Switch Science | ✅ 必須 |
| ブレッドボード 830穴 | 1 | ¥800 | ¥800 | Amazon | ✅ 必須 |
| ジャンパーワイヤー M-M | 1セット | ¥200 | ¥200 | Amazon | ✅ 必須 |
| 4.7kΩ 抵抗 | 1 | ¥10 | ¥10 | 秋月電子 | ✅ 必須 |
| USB Type-C ケーブル | 1 | ¥500 | - | 手持ちでOK | ✅ 必須 |
| Tapo P300 電源タップ | 1 | ¥3,000 | - | 既存 | ✅ 必須 |
| **小計** | - | - | **¥3,010** | - | - |

**購入リンク例（2026年7月時点）:**
- ESP32: Amazon「ESP32-DevKitC」で検索
- DS18B20: Amazon「DS18B20 防水」で検索
- ブレッドボード: Amazon「ブレッドボード 830穴」で検索

---

#### 💻 ソフトウェア（すべて無料）

| 項目 | バージョン | 用途 | インストール先 |
|-----|----------|------|---------------|
| Python | 3.8+ | ツール実行 | PC/Mac |
| esptool | 4.7+ | ESP32フラッシュ | PC/Mac |
| ampy | 1.1+ | ファイル転送 | PC/Mac |
| screen (Mac/Linux) | - | REPL接続 | PC/Mac |
| PuTTY (Windows) | - | REPL接続 | PC |
| gcloud CLI | latest | GCP操作 | PC/Mac |
| MicroPython | 1.21+ | ESP32ファームウェア | ESP32 |

---

#### ☁️ クラウドアカウント（すべて無料枠で運用可）

| サービス | 用途 | 無料枠 | 月額コスト |
|---------|------|--------|-----------|
| GCP | インフラ全般 | 各種あり | ¥0 |
| Grafana Cloud | 可視化 | 3ユーザー | ¥0 |
| LINE Notify | 通知 | 無制限 | ¥0 |

**事前準備:**
- [ ] Google アカウント（Gmail）
- [ ] クレジットカード（GCP課金用、実際の請求は¥0）
- [ ] LINE アカウント（通知用、オプション）

---

## Part A: ハードウェア編

### A1. 環境準備（ハードウェア）

#### 📋 前提条件

- [ ] PC/Mac が使える
- [ ] WiFi環境がある
- [ ] USB Type-C ケーブルがある

#### ⏱️ 所要時間

- **初回:** 30分
- **2回目以降:** 5分

#### 🎯 このセクションで達成すること

- [ ] Python インストール
- [ ] esptool インストール
- [ ] ampy インストール
- [ ] REPL接続ツール準備

---

#### 📝 手順

##### 1. Python インストール確認

**Mac/Linux:**
```bash
python3 --version
# 期待される出力: Python 3.8.x 以上
```

**Windows:**
```cmd
python --version
# 期待される出力: Python 3.8.x 以上
```

**インストールされていない場合:**
- Mac: `brew install python3`
- Windows: https://www.python.org/downloads/ からインストーラーダウンロード
- Linux: `sudo apt install python3 python3-pip`

---

##### 2. esptool インストール

```bash
pip3 install esptool

# 確認
esptool.py version
```

**期待される出力:**
```
esptool.py v4.7.0
```

**エラーが出る場合:**
```bash
# PATH が通っていない場合
python3 -m esptool version

# 権限エラーの場合（Mac/Linux）
pip3 install --user esptool

# Windowsでパスが通らない場合
# 環境変数に以下を追加:
# C:\Users\<ユーザー名>\AppData\Local\Programs\Python\Python3X\Scripts
```

---

##### 3. ampy インストール

```bash
pip3 install adafruit-ampy

# 確認
ampy --version
```

**期待される出力:**
```
ampy, version 1.1.0
```

---

##### 4. REPL接続ツール

**Mac/Linux:**
```bash
# screen は通常プリインストール済み
which screen
# 期待される出力: /usr/bin/screen
```

**Windows:**
- PuTTY をダウンロード: https://www.putty.org/
- インストーラー実行

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] `python3 --version` でPython 3.8以上が表示される
- [ ] `esptool.py version` でesptoolのバージョンが表示される
- [ ] `ampy --version` でampyのバージョンが表示される
- [ ] REPL接続ツール（screen or PuTTY）が使える

---

#### 🔧 トラブルシューティング

**問題1: `pip3: command not found`**

**原因:** pip3 がインストールされていない

**解決策:**
```bash
# Mac
brew install python3

# Ubuntu/Debian
sudo apt install python3-pip

# Windows
# Python インストーラーを再実行し、"pip をインストール" にチェック
```

---

**問題2: `esptool.py: command not found`**

**原因:** PATH が通っていない

**解決策:**
```bash
# フルパスで実行
python3 -m esptool version

# または、エイリアス設定（Mac/Linux）
echo 'alias esptool.py="python3 -m esptool"' >> ~/.bashrc
source ~/.bashrc
```

---

**問題3: Permission denied (Mac/Linux)**

**原因:** 管理者権限が必要

**解決策:**
```bash
# --user オプションを追加
pip3 install --user esptool
pip3 install --user adafruit-ampy
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [A2. ESP32配線実装](#a2-esp32配線実装)
- **一旦終わる場合**: ここまでで開発環境準備完了！
- **クラウドを先に進める場合**: [Part B: クラウド編](#part-b-クラウド編)

---

### A2. ESP32配線実装

#### 📋 前提条件

- [ ] ESP32-DevKitC を入手済み
- [ ] DS18B20 センサーを入手済み
- [ ] ブレッドボード 830穴を入手済み
- [ ] ジャンパーワイヤーを入手済み
- [ ] 4.7kΩ 抵抗を入手済み

⚠️ **クラウド環境は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 30-45分（慎重に配線）
- **2回目以降:** 10分

#### 🎯 このセクションで達成すること

- [ ] ESP32 をブレッドボードに配置
- [ ] DS18B20 センサーを接続
- [ ] プルアップ抵抗を追加
- [ ] 配線の動作確認

---

#### 📝 手順

##### 1. ブレッドボードの理解

**830穴ブレッドボードの構造:**

```
   電源レール(+)  ━━━━━━━━━━━━━━━━━━━━━━━━━
   電源レール(-)  ━━━━━━━━━━━━━━━━━━━━━━━━━
                 ┌──────────────┬──────────────┐
                 │  A B C D E   │  F G H I J   │
   Row 1         │  ● ● ● ● ●   │  ● ● ● ● ●   │
   Row 2         │  ● ● ● ● ●   │  ● ● ● ● ●   │
      ...        │     ...      │     ...      │
   Row 63        │  ● ● ● ● ●   │  ● ● ● ● ●   │
                 └──────────────┴──────────────┘
   電源レール(+)  ━━━━━━━━━━━━━━━━━━━━━━━━━
   電源レール(-)  ━━━━━━━━━━━━━━━━━━━━━━━━━
```

**重要:**
- A-E列は横につながっている
- F-J列は横につながっている
- A-E列とF-J列は**つながっていない**（中央で分離）
- 電源レールは縦につながっている

---

##### 2. ESP32 の配置

**ESP32-DevKitCのピン配置（38ピン版）:**

```
                    USB端子
                       ▼
    ┌──────────────────────────────────┐
    │  EN                        3V3   │ ← 電源出力（3.3V）
    │  VP                        GND   │ ← グランド
    │  VN                        D15   │
    │  D34                       D2    │
    │  D35                       D4    │ ← DS18B20 接続
    │  D32                       RX2   │
    │  D33                       TX2   │
    │  D25                       D5    │
    │  D26                       D18   │
    │  D27                       D19   │
    │  D14                       D21   │
    │  D12                       RX0   │
    │  D13                       TX0   │
    │  GND                       D22   │
    │  VIN                       D23   │
    │  3V3                       GND   │
    └──────────────────────────────────┘
```

**配置手順:**

1. **ESP32 をブレッドボードの中央に配置**
   - USB端子を上（または下）に向ける
   - 左側のピンを**列E**に配置
   - 右側のピンを**列F**に配置
   - Row 10〜28 あたりを使用（例）

2. **挿入の確認**
   - すべてのピンが穴に入っていることを確認
   - ピンが曲がっていないか確認
   - 左右が対称に配置されているか確認

---

##### 3. 電源レールの接続

**手順:**

1. **3.3V → 電源レール(+)**
   - ESP32 の **3V3 ピン**（右側上から1番目）
   - ブレッドボードの **電源レール(+)**（赤いライン）
   - **赤色ジャンパーワイヤー**で接続

2. **GND → 電源レール(-)**
   - ESP32 の **GND ピン**（右側上から2番目）
   - ブレッドボードの **電源レール(-)**（青いライン）
   - **黒色ジャンパーワイヤー**で接続

**配線図（文字表現）:**
```
ESP32           ブレッドボード
┌─────┐         ┌─────────────┐
│ 3V3 │────────→│ 電源(+) ━━━ │ 赤ワイヤー
│ GND │────────→│ 電源(-) ━━━ │ 黒ワイヤー
└─────┘         └─────────────┘
```

---

##### 4. DS18B20 センサーの接続

**DS18B20 のピン配置:**

```
┌─────────────┐
│   DS18B20   │
│  (正面から) │
│             │
│  ┌───┬───┬──┐│
│  │赤 │黄 │黒││
│  └─┬─┴─┬─┴┬─┘│
│    │   │  │   │
│   VDD DATA GND │
└────┴───┴───┴──┘
```

**ピンの役割:**
- **赤 (VDD):** 電源（3.3V）
- **黄 (DATA):** データ通信（GPIO4 に接続）
- **黒 (GND):** グランド

**接続手順:**

1. **赤ワイヤー (VDD) → 電源レール(+)**
   - DS18B20 の赤ワイヤー
   - ブレッドボードの **電源レール(+)**
   - （または、ブレッドボードの空いている穴に挿入）

2. **黒ワイヤー (GND) → 電源レール(-)**
   - DS18B20 の黒ワイヤー
   - ブレッドボードの **電源レール(-)**

3. **黄ワイヤー (DATA) → GPIO4**
   - DS18B20 の黄ワイヤー
   - ESP32 の **D4 ピン**（右側上から5番目）
   - ジャンパーワイヤーで接続

**配線図（文字表現）:**
```
DS18B20                  ESP32
┌──────┐                ┌──────┐
│ VDD  │───────────────→│ 3V3  │ (電源レール経由)
│ DATA │───────────────→│ D4   │ (GPIO4)
│ GND  │───────────────→│ GND  │ (電源レール経由)
└──────┘                └──────┘
```

---

##### 5. プルアップ抵抗の追加

**なぜ必要か:**
DS18B20 は1-Wire通信を使用します。1-Wire通信では、DATA線にプルアップ抵抗（4.7kΩ）が必要です。これがないと、センサーが正しく検出されません。

**接続手順:**

1. **4.7kΩ 抵抗を準備**
   - 抵抗の値を確認（黄紫赤金）
   - 向きはどちらでもOK

2. **抵抗の接続**
   - 抵抗の一方の足: **DATA線**（GPIO4につながっている穴）
   - 抵抗のもう一方の足: **電源レール(+)**（3.3V）

**配線図（文字表現）:**
```
     VDD (+3.3V)
        │
        │
       [R] 4.7kΩ
        │
        ├──────→ DATA (GPIO4)
        │
      DS18B20
```

---

##### 6. 最終配線チェック

**チェックリスト:**

- [ ] ESP32 が中央に配置されている
- [ ] ESP32 の 3V3 → 電源レール(+) が赤ワイヤーで接続
- [ ] ESP32 の GND → 電源レール(-) が黒ワイヤーで接続
- [ ] DS18B20 の赤 → 電源レール(+)
- [ ] DS18B20 の黒 → 電源レール(-)
- [ ] DS18B20 の黄 → ESP32 の D4
- [ ] 4.7kΩ 抵抗が DATA線 と 電源(+) の間に接続
- [ ] ワイヤーが他のピンと接触していない
- [ ] すべての接続がしっかり挿さっている

**写真で確認（イメージ）:**
- すべてのワイヤーがしっかり挿さっているか
- ワイヤーが絡まっていないか
- ブレッドボードがきれいに整理されているか

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] ESP32 がブレッドボードに正しく配置されている
- [ ] 電源レール(+)と(-)が正しく接続されている
- [ ] DS18B20 が正しく接続されている（3本のワイヤー）
- [ ] プルアップ抵抗が正しく配置されている
- [ ] すべての配線がチェックリストと一致している
- [ ] ワイヤーの接触や短絡がない

---

#### 🔧 トラブルシューティング

**問題1: ESP32 がブレッドボードに入らない**

**原因:** ピンが曲がっている、または穴がずれている

**解決策:**
1. ESP32 を一度外す
2. すべてのピンが真っすぐか確認
3. 曲がっているピンがあれば、慎重に真っすぐにする
4. 再度挿入（少し力を入れて押し込む）

---

**問題2: ジャンパーワイヤーが抜ける**

**原因:** ワイヤーの接触不良

**解決策:**
1. ワイヤーを一度抜く
2. ワイヤーの先端が変形していないか確認
3. しっかり奥まで挿入する
4. 別のワイヤーに交換してみる

---

**問題3: 4.7kΩ 抵抗の値がわからない**

**原因:** カラーコードの読み方がわからない

**抵抗のカラーコード:**
```
4.7kΩ = 黄(4) 紫(7) 赤(×100) 金(±5%)
```

**確認方法:**
- テスターで抵抗値を測定（4.5kΩ〜5.0kΩならOK）
- カラーコード表で確認

---

**問題4: DS18B20 のワイヤーが短い**

**原因:** 水槽まで届かない

**解決策:**
- ジャンパーワイヤー（メス-メス）で延長
- または、DS18B20 を水槽の近くに配置
- （本格運用時はケーブルを長いものに交換）

---

#### ➡️ 次のステップ

- **続けて進む場合**: [A3. MicroPython セットアップ](#a3-micropython-セットアップ)
- **一旦終わる場合**: ここまででハードウェア配線完了！
- **配線を再確認したい場合**: [A2. 最終配線チェック](#6-最終配線チェック)

---

### A3. MicroPython セットアップ

#### 📋 前提条件

- [ ] [A1. 環境準備](#a1-環境準備ハードウェア) 完了
- [ ] [A2. ESP32配線実装](#a2-esp32配線実装) 完了
- [ ] USB Type-C ケーブルがある

⚠️ **クラウド環境は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 30分
- **2回目以降:** 10分

#### 🎯 このセクションで達成すること

- [ ] MicroPython ファームウェアをダウンロード
- [ ] ESP32 にフラッシュ
- [ ] REPL接続確認
- [ ] 基本動作テスト

---

#### 📝 手順

##### 1. MicroPython ファームウェアのダウンロード

**手順:**

1. **公式サイトにアクセス**
   - https://micropython.org/download/esp32/

2. **最新の安定版をダウンロード**
   - ファイル名: `esp32-20231005-v1.21.0.bin`（例）
   - サイズ: 約1.8MB
   - 保存先: `~/Downloads/` など

**確認:**
```bash
ls -lh ~/Downloads/esp32-*.bin
# 期待される出力: esp32-20231005-v1.21.0.bin  1.8M
```

---

##### 2. ESP32 の接続とシリアルポート確認

**ESP32 をPCに接続:**

1. USB Type-C ケーブルで ESP32 とPCを接続
2. ESP32 の LED が点灯することを確認

**シリアルポートの確認:**

**Mac:**
```bash
ls /dev/tty.usb*
# 期待される出力: /dev/tty.usbserial-XXXXX
```

**Linux:**
```bash
ls /dev/ttyUSB*
# 期待される出力: /dev/ttyUSB0
```

**Windows:**
- デバイスマネージャーを開く
- 「ポート (COM と LPT)」を展開
- 「USB Serial Port (COM3)」などを確認

**ポートが見つからない場合:**
- USB ケーブルを抜き差ししてみる
- 別の USB ポートを試す
- USB ケーブルがデータ転送対応か確認（充電専用ではNG）
- ドライバーが必要な場合: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers

---

##### 3. ESP32 のフラッシュメモリを消去

**重要:** 既存のデータをすべて消去します（初回のみ）。

**コマンド（Mac/Linux）:**
```bash
esptool.py --port /dev/tty.usbserial-XXXXX erase_flash
```

**コマンド（Windows）:**
```cmd
esptool.py --port COM3 erase_flash
```

**実行例:**
```bash
$ esptool.py --port /dev/tty.usbserial-0001 erase_flash
esptool.py v4.7.0
Serial port /dev/tty.usbserial-0001
Connecting....
Detecting chip type... Unsupported detection protocol, switching and trying again...
Connecting...
Detecting chip type... ESP32
Chip is ESP32-D0WD-V3 (revision v3.0)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: a4:cf:12:xx:xx:xx
Uploading stub...
Running stub...
Stub running...
Erasing flash (this may take a while)...
Chip erase completed successfully in 10.2s
Hard resetting via RTS pin...
```

**期待される出力:**
- `Erasing flash (this may take a while)...`
- `Chip erase completed successfully`
- 所要時間: 10-20秒

---

##### 4. MicroPython ファームウェアの書き込み

**コマンド（Mac/Linux）:**
```bash
esptool.py --chip esp32 --port /dev/tty.usbserial-XXXXX \
  write_flash -z 0x1000 ~/Downloads/esp32-20231005-v1.21.0.bin
```

**コマンド（Windows）:**
```cmd
esptool.py --chip esp32 --port COM3 ^
  write_flash -z 0x1000 C:\Users\YourName\Downloads\esp32-20231005-v1.21.0.bin
```

**実行例:**
```bash
$ esptool.py --chip esp32 --port /dev/tty.usbserial-0001 \
  write_flash -z 0x1000 ~/Downloads/esp32-20231005-v1.21.0.bin
esptool.py v4.7.0
Serial port /dev/tty.usbserial-0001
Connecting...
Chip is ESP32-D0WD-V3 (revision v3.0)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: a4:cf:12:xx:xx:xx
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Flash will be erased from 0x00001000 to 0x001c3fff...
Compressed 1837952 bytes to 1214848...
Wrote 1837952 bytes (1214848 compressed) at 0x00001000 in 107.3 seconds (effective 137.1 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

**期待される出力:**
- `Wrote XXXXXX bytes ... in XX.X seconds`
- `Hash of data verified.`
- 所要時間: 1-2分

---

##### 5. REPL 接続テスト

**REPL とは:**
Read-Eval-Print Loop の略。MicroPython のインタラクティブシェル（Python を直接実行できる）。

**接続方法（Mac/Linux）:**
```bash
screen /dev/tty.usbserial-XXXXX 115200
```

**接続方法（Windows）:**
1. PuTTY を起動
2. Connection type: Serial
3. Serial line: COM3
4. Speed: 115200
5. Open をクリック

**接続後:**

1. **Enter キーを数回押す**
   - MicroPython のプロンプトが表示される

**期待される表示:**
```
>>>
```

2. **Python コードを実行してみる**
```python
>>> print("Hello from ESP32!")
Hello from ESP32!

>>> 1 + 1
2

>>> import sys
>>> sys.version
'3.4.0; MicroPython v1.21.0 on 2023-10-05'
```

3. **LED を点滅させてみる**
```python
>>> from machine import Pin
>>> import time
>>> led = Pin(2, Pin.OUT)  # GPIO2 (内蔵LED)
>>> led.on()   # LED点灯
>>> led.off()  # LED消灯
>>> 
>>> # 点滅
>>> for i in range(5):
...     led.on()
...     time.sleep(0.5)
...     led.off()
...     time.sleep(0.5)
... 
```

**期待される動作:**
- ESP32 の内蔵LED（青）が5回点滅する

---

##### 6. REPL の終了方法

**Mac/Linux (screen):**
```
Ctrl-A → K → Y
```

1. `Ctrl-A` を押す
2. `K` を押す
3. `Really kill this window [y/n]` と表示されたら `Y`

**Windows (PuTTY):**
- ウィンドウを閉じるだけ

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] MicroPython ファームウェアをダウンロードした
- [ ] ESP32 のフラッシュを消去した
- [ ] MicroPython を書き込んだ
- [ ] REPL に接続できた
- [ ] `>>>` プロンプトが表示された
- [ ] `print()` が動作した
- [ ] 内蔵LED が点滅した

---

#### 🔧 トラブルシューティング

**問題1: シリアルポートが見つからない**

**症状:**
```
ls /dev/tty.usb*
# 何も表示されない
```

**原因:** USBドライバーがインストールされていない

**解決策:**
1. **USB ケーブルを確認**
   - データ転送対応のケーブルか確認（充電専用NG）
   - 別のケーブルを試す

2. **ドライバーをインストール**
   - ESP32 のチップ: CP2102 または CH340
   - CP2102 ドライバー: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
   - CH340 ドライバー: http://www.wch-ic.com/downloads/CH341SER_MAC_ZIP.html

3. **再起動**
   - PC を再起動
   - USB ケーブルを抜き差し

---

**問題2: `Failed to connect`**

**症状:**
```
esptool.py --port /dev/tty.usbserial-0001 erase_flash
...
A fatal error occurred: Failed to connect to ESP32: Timed out waiting for packet header
```

**原因:** ESP32 がブートモードに入っていない

**解決策:**

1. **BOOT ボタンを押しながらコマンド実行**
   - ESP32 の `BOOT` ボタンを押す
   - 押したまま、`esptool.py erase_flash` を実行
   - `Connecting...` が表示されたらボタンを離す

2. **EN ボタンでリセット**
   - `EN` ボタンを押してリセット
   - すぐにコマンド実行

3. **USB ケーブルを抜き差し**
   - USB ケーブルを抜く
   - 5秒待つ
   - 再度接続

---

**問題3: `Hash of data verified` の後に何も表示されない**

**症状:**
```
Hash of data verified.
Leaving...
Hard resetting via RTS pin...
（ここで止まる）
```

**原因:** 正常です。書き込み完了。

**解決策:**
- `Ctrl-C` で終了
- 次のステップ（REPL接続）に進む

---

**問題4: REPL で `>>>` が表示されない**

**症状:**
```
screen /dev/tty.usbserial-0001 115200
（黒い画面のまま何も表示されない）
```

**解決策:**

1. **Enter キーを数回押す**
   - `>>>` が表示される

2. **EN ボタンでリセット**
   - ESP32 の `EN` ボタンを押す
   - ブート画面が表示される
   - `>>>` が表示される

3. **screen を再接続**
   - `Ctrl-A` → `K` → `Y` で終了
   - 再度 `screen` コマンド実行

---

**問題5: 内蔵LED が点滅しない**

**原因:** GPIO2 に内蔵LEDがない機種

**解決策:**
```python
# 外部LEDで確認（配線不要、センサーのLEDで代用）
>>> from machine import Pin
>>> import time
>>> # GPIO4（DS18B20接続）を使う
>>> pin = Pin(4, Pin.OUT)
>>> for i in range(5):
...     pin.on()
...     time.sleep(0.5)
...     pin.off()
...     time.sleep(0.5)
... 
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [A4. センサー動作確認](#a4-センサー動作確認)
- **一旦終わる場合**: ここまででMicroPythonセットアップ完了！
- **REPL で遊びたい場合**: [MicroPython チュートリアル](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

---

### A4. センサー動作確認

#### 📋 前提条件

- [ ] [A2. ESP32配線実装](#a2-esp32配線実装) 完了
- [ ] [A3. MicroPython セットアップ](#a3-micropython-セットアップ) 完了

⚠️ **クラウド環境は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 20分
- **2回目以降:** 5分

#### 🎯 このセクションで達成すること

- [ ] DS18B20 センサーが検出される
- [ ] 温度が正しく読み取れる
- [ ] 温度が安定している

---

#### 📝 手順

##### 1. REPL に接続

```bash
# Mac/Linux
screen /dev/tty.usbserial-XXXXX 115200

# Windows: PuTTY で接続
```

**Enter キーを押して `>>>` プロンプトを表示**

---

##### 2. DS18B20 の検出

**コード:**
```python
>>> import machine
>>> import onewire
>>> import ds18x20
>>> 
>>> # GPIO4 に接続されたセンサーをスキャン
>>> dat = machine.Pin(4)
>>> ds = ds18x20.DS18X20(onewire.OneWire(dat))
>>> roms = ds.scan()
>>> 
>>> # センサーが見つかったか確認
>>> print('Found DS18B20:', len(roms))
>>> print('ROM:', roms)
```

**期待される出力:**
```python
Found DS18B20: 1
ROM: [bytearray(b'(\xab\xcd\x12\x34\x56\x78\x90')]
```

**説明:**
- `Found DS18B20: 1` → センサーが1個検出された
- `ROM: [bytearray(...)]` → センサーの固有ID（64ビット）

---

##### 3. 温度の読み取り

**コード:**
```python
>>> import time
>>> 
>>> # 温度変換を開始
>>> ds.convert_temp()
>>> time.sleep_ms(750)  # 変換完了まで待つ
>>> 
>>> # 温度を読み取る
>>> temp = ds.read_temp(roms[0])
>>> print(f'Temperature: {temp:.2f} C')
```

**期待される出力:**
```python
Temperature: 25.31 C
```

**説明:**
- `convert_temp()`: センサーに温度測定を指示
- `sleep_ms(750)`: 測定完了まで750ms待つ（必須）
- `read_temp()`: 測定結果を読み取る

---

##### 4. 連続測定テスト

**コード:**
```python
>>> # 5回測定してみる
>>> for i in range(5):
...     ds.convert_temp()
...     time.sleep_ms(750)
...     temp = ds.read_temp(roms[0])
...     print(f'{i+1}: {temp:.2f} C')
...     time.sleep(2)
... 
```

**期待される出力:**
```python
1: 25.31 C
2: 25.37 C
3: 25.34 C
4: 25.31 C
5: 25.34 C
```

**確認ポイント:**
- 温度が妥当な範囲か（室温なら20-30℃程度）
- 変動が小さいか（±0.5℃以内）
- エラーが出ないか

---

##### 5. センサーを水に入れてテスト（オプション）

**手順:**

1. **水を用意**
   - コップに水を入れる
   - 水温: 常温でOK

2. **センサーを水に浸す**
   - DS18B20 の先端（防水部分）を水に入れる
   - ケーブル部分は水に入れない

3. **温度を測定**
```python
>>> ds.convert_temp()
>>> time.sleep_ms(750)
>>> temp = ds.read_temp(roms[0])
>>> print(f'Water temperature: {temp:.2f} C')
```

4. **お湯を少し足してみる**
   - 温度が上がることを確認

**期待される動作:**
- 水温が表示される（例: 22.5℃）
- お湯を足すと温度が上がる（例: 25.0℃）

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] `ds.scan()` でセンサーが検出された（`Found DS18B20: 1`）
- [ ] `read_temp()` で温度が読み取れた
- [ ] 温度が妥当な範囲（15-35℃）
- [ ] 連続測定で温度が安定している（±0.5℃以内）
- [ ] 水に入れると温度が変化する（オプション）

---

#### 🔧 トラブルシューティング

**問題1: `Found DS18B20: 0`（センサーが検出されない）**

**原因:** 配線ミスまたは接触不良

**解決策:**

1. **配線を再確認**
   - DS18B20 の赤ワイヤー → 電源(+)
   - DS18B20 の黒ワイヤー → GND(-)
   - DS18B20 の黄ワイヤー → GPIO4
   - 4.7kΩ 抵抗が DATA と 電源(+) の間にある

2. **プルアップ抵抗を確認**
   - 抵抗が正しく接続されているか
   - 抵抗値が4.7kΩか（テスターで測定）

3. **ワイヤーの接触を確認**
   - すべてのワイヤーがしっかり挿さっているか
   - ブレッドボードの接触不良がないか
   - ジャンパーワイヤーを交換してみる

4. **センサーの故障を疑う**
   - 別のDS18B20があれば交換してみる
   - センサーのケーブルが断線していないか

---

**問題2: `OSError: [Errno 2] ENOENT`**

**症状:**
```python
>>> temp = ds.read_temp(roms[0])
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
OSError: [Errno 2] ENOENT
```

**原因:** `convert_temp()` を実行していない、または待機時間が短い

**解決策:**
```python
>>> # 必ず convert_temp() → sleep → read_temp() の順で実行
>>> ds.convert_temp()
>>> time.sleep_ms(750)  # 750ms以上待つ
>>> temp = ds.read_temp(roms[0])
```

---

**問題3: 温度が `-127.0 C` と表示される**

**原因:** センサーとの通信エラー

**解決策:**

1. **再度測定**
```python
>>> ds.convert_temp()
>>> time.sleep(1)  # 少し長めに待つ
>>> temp = ds.read_temp(roms[0])
```

2. **配線を確認**
   - プルアップ抵抗が正しく接続されているか
   - ワイヤーの接触不良がないか

3. **ESP32 をリセット**
   - `EN` ボタンを押す
   - 再度 REPL で実行

---

**問題4: 温度が不安定（±5℃以上変動する）**

**原因:** 接触不良またはノイズ

**解決策:**

1. **ワイヤーを短くする**
   - 長いワイヤーはノイズを拾いやすい
   - 短いジャンパーワイヤーに交換

2. **0.1µF コンデンサを追加**（上級者向け）
   - DS18B20 の VDD-GND 間にコンデンサを追加
   - ノイズ除去効果

3. **複数回測定して平均を取る**
```python
>>> temps = []
>>> for i in range(10):
...     ds.convert_temp()
...     time.sleep_ms(750)
...     temps.append(ds.read_temp(roms[0]))
...     time.sleep(0.5)
... 
>>> avg = sum(temps) / len(temps)
>>> print(f'Average: {avg:.2f} C')
```

---

**問題5: 複数のセンサーが検出される**

**症状:**
```python
Found DS18B20: 2
ROM: [bytearray(b'(...)'), bytearray(b'(...)')]
```

**原因:** 複数のDS18B20が同じバスに接続されている（問題なし）

**解決策:**
```python
>>> # すべてのセンサーから温度を読み取る
>>> for i, rom in enumerate(roms):
...     ds.convert_temp()
...     time.sleep_ms(750)
...     temp = ds.read_temp(rom)
...     print(f'Sensor {i+1}: {temp:.2f} C')
... 
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [A5. WiFi接続実装](#a5-wifi接続実装)
- **一旦終わる場合**: ここまででセンサー動作確認完了！
- **Part B に進む場合**: [Part B: クラウド編](#part-b-クラウド編)

---

### A5. WiFi接続実装

#### 📋 前提条件

- [ ] [A3. MicroPython セットアップ](#a3-micropython-セットアップ) 完了
- [ ] WiFi環境（SSID、パスワード）

⚠️ **センサー配線は不要**（このセクションは独立）  
⚠️ **クラウド環境は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 15分
- **2回目以降:** 5分

#### 🎯 このセクションで達成すること

- [ ] ESP32 がWiFiに接続できる
- [ ] IPアドレスが取得できる
- [ ] インターネット接続確認

---

#### 📝 手順

##### 1. REPL に接続

```bash
screen /dev/tty.usbserial-XXXXX 115200
```

**Enter キーを押して `>>>` プロンプトを表示**

---

##### 2. WiFi接続テスト（手動）

**コード:**
```python
>>> import network
>>> import time
>>> 
>>> # WiFi設定（自分の環境に合わせて変更）
>>> SSID = "YourWiFiSSID"      # WiFiのSSID
>>> PASSWORD = "YourPassword"  # WiFiのパスワード
>>> 
>>> # WiFiインターフェースを有効化
>>> wlan = network.WLAN(network.STA_IF)
>>> wlan.active(True)
>>> 
>>> # WiFiに接続
>>> print(f'Connecting to {SSID}...')
>>> wlan.connect(SSID, PASSWORD)
>>> 
>>> # 接続完了まで待つ
>>> while not wlan.isconnected():
...     print('...', end='')
...     time.sleep(1)
... 
>>> print('\nConnected!')
>>> 
>>> # IPアドレスを表示
>>> print('IP address:', wlan.ifconfig()[0])
```

**期待される出力:**
```python
Connecting to YourWiFiSSID...
.........
Connected!
IP address: 192.168.1.123
```

**説明:**
- `wlan.active(True)`: WiFiを有効化
- `wlan.connect()`: WiFiに接続
- `wlan.isconnected()`: 接続状態を確認
- `wlan.ifconfig()[0]`: IPアドレスを取得

---

##### 3. インターネット接続確認

**コード:**
```python
>>> import socket
>>> 
>>> # DNS解決テスト
>>> addr = socket.getaddrinfo('www.google.com', 80)[0][-1]
>>> print('Google IP:', addr)
>>> 
>>> # HTTPリクエストテスト
>>> s = socket.socket()
>>> s.connect(addr)
>>> s.send(b'GET / HTTP/1.0\r\nHost: www.google.com\r\n\r\n')
>>> data = s.recv(100)
>>> s.close()
>>> print('Response:', data.decode()[:50])
```

**期待される出力:**
```python
Google IP: ('142.250.207.36', 80)
Response: HTTP/1.0 200 OK
Date: Sat, 11 Jul 2026 09:00:00
```

---

##### 4. WiFi接続スクリプトの作成

**ファイルを作成（PC上で）:**

```bash
# ファイル名: wifi_test.py
cat > wifi_test.py << 'EOF'
import network
import time

def connect_wifi(ssid, password, timeout=30):
    """WiFiに接続"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print('Already connected')
        print('IP:', wlan.ifconfig()[0])
        return wlan
    
    print(f'Connecting to {ssid}...')
    wlan.connect(ssid, password)
    
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            print('Connection timeout!')
            return None
        print('.', end='')
        time.sleep(1)
    
    print('\nConnected!')
    print('IP:', wlan.ifconfig()[0])
    print('Netmask:', wlan.ifconfig()[1])
    print('Gateway:', wlan.ifconfig()[2])
    print('DNS:', wlan.ifconfig()[3])
    return wlan

# テスト実行
if __name__ == '__main__':
    SSID = "YourWiFiSSID"
    PASSWORD = "YourPassword"
    wlan = connect_wifi(SSID, PASSWORD)
EOF
```

---

##### 5. スクリプトをESP32にアップロード

```bash
# ESP32にアップロード
ampy --port /dev/tty.usbserial-XXXXX put wifi_test.py
```

**確認:**
```bash
# ファイルがアップロードされたか確認
ampy --port /dev/tty.usbserial-XXXXX ls
# 期待される出力: /wifi_test.py
```

---

##### 6. スクリプトの実行

**REPL で実行:**
```python
>>> import wifi_test
Connecting to YourWiFiSSID...
..........
Connected!
IP: 192.168.1.123
Netmask: 255.255.255.0
Gateway: 192.168.1.1
DNS: 192.168.1.1
```

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] WiFiに接続できた
- [ ] IPアドレスが表示された（192.168.x.x）
- [ ] Google.com に接続できた
- [ ] `wifi_test.py` がESP32にアップロードされた
- [ ] スクリプトで接続できた

---

#### 🔧 トラブルシューティング

**問題1: `OSError: -202`（WiFiに接続できない）**

**症状:**
```python
>>> wlan.connect(SSID, PASSWORD)
Traceback (most recent call last):
OSError: -202
```

**原因:** SSIDまたはパスワードが間違っている

**解決策:**

1. **SSID を確認**
```python
>>> wlan.scan()
# WiFi一覧が表示される
# (ssid, bssid, channel, RSSI, authmode, hidden)
```

2. **SSID、パスワードを再入力**
   - 大文字小文字を区別
   - スペースに注意

3. **WiFiの周波数を確認**
   - ESP32は **2.4GHz のみ** 対応
   - 5GHz WiFi には接続できない
   - ルーターで2.4GHzが有効か確認

---

**問題2: 接続がタイムアウトする**

**症状:**
```python
Connecting to YourWiFiSSID...
..........................
(30秒経っても接続できない)
```

**原因:** WiFiの電波が弱い、または設定ミス

**解決策:**

1. **電波強度を確認**
```python
>>> wlan.scan()
# RSSI (4番目の値) を確認
# -50 以上: 強い
# -70 前後: 普通
# -80 以下: 弱い
```

2. **ESP32をルーターに近づける**
   - 2-3m以内に配置
   - 障害物を減らす

3. **ルーターの設定を確認**
   - MACアドレスフィルタリングがOFFか
   - ゲストネットワークではないか

---

**問題3: `ECONNRESET`（接続が切れる）**

**原因:** WiFiの電波が不安定

**解決策:**

1. **再接続ロジックを追加**
```python
def ensure_wifi(wlan, ssid, password):
    """WiFi接続を維持"""
    if not wlan.isconnected():
        print('Reconnecting...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
        print('Reconnected')
```

2. **WiFiチャンネルを変更**
   - ルーター側でチャンネルを固定
   - 推奨チャンネル: 1, 6, 11

---

**問題4: `getaddrinfo failed`（DNS解決エラー）**

**原因:** DNSサーバーが設定されていない

**解決策:**
```python
>>> # DNS設定を手動で指定
>>> wlan.ifconfig(('192.168.1.123', '255.255.255.0', '192.168.1.1', '8.8.8.8'))
# (IP, Netmask, Gateway, DNS)
```

---

#### ➡️ 次のステップ

- **Part A 完了！ おめでとうございます🎉**
- **続けて進む場合**: [Part B: クラウド編](#part-b-クラウド編)
- **統合テストに進む場合**: [Part C: 統合編](#part-c-統合編)
- **一旦終わる場合**: ここまでで ESP32 の基本実装完了！

---

## Part B: クラウド編

### B1. 環境準備（クラウド）

#### 📋 前提条件

- [ ] Google アカウント（Gmail）
- [ ] クレジットカード（GCP課金用、実際の請求は¥0）
- [ ] PC/Mac でブラウザが使える

⚠️ **ESP32は不要**（このセクションは独立）  
⚠️ **センサー配線は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 30分
- **2回目以降:** 5分

#### 🎯 このセクションで達成すること

- [ ] gcloud CLI インストール
- [ ] GCP アカウント作成
- [ ] 課金アカウント設定
- [ ] gcloud 認証

---

#### 📝 手順

##### 1. gcloud CLI のインストール

**Mac:**
```bash
# Homebrewでインストール（推奨）
brew install google-cloud-sdk

# または、手動インストール
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Linux:**
```bash
# スナップでインストール
sudo snap install google-cloud-cli --classic

# または、手動インストール
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
- https://cloud.google.com/sdk/docs/install からインストーラーダウンロード
- インストーラー実行
- PowerShell または CMD を再起動

---

**確認:**
```bash
gcloud version
```

**期待される出力:**
```
Google Cloud SDK 472.0.0
bq 2.1.0
core 2024.04.01
gcloud-crc32c 1.0.0
gsutil 5.27
```

---

##### 2. GCP アカウントの作成

**手順:**

1. **GCP Console にアクセス**
   - https://console.cloud.google.com/

2. **Google アカウントでログイン**
   - Gmail アドレスとパスワード

3. **利用規約に同意**
   - チェックボックスにチェック
   - 「同意して続行」をクリック

4. **無料トライアル開始**
   - 「無料で開始」をクリック
   - または「試す」をクリック

---

##### 3. 課金アカウントの設定

**手順:**

1. **国を選択**
   - 「日本」を選択

2. **利用規約に同意**
   - チェックボックスにチェック

3. **クレジットカード情報を入力**
   - カード番号
   - 有効期限
   - セキュリティコード
   - 請求先住所

4. **確認して送信**

**重要:**
- クレジットカードは本人確認のために必要
- **無料枠内であれば請求は発生しない**
- 無料トライアルで $300 のクレジットが付与される

---

##### 4. gcloud の初期化

```bash
gcloud init
```

**実行例:**
```
Welcome to the Google Cloud CLI!

Pick configuration to use:
 [1] Re-initialize this configuration [default] with new settings
 [2] Create a new configuration
Please enter your numeric choice: 2

Enter configuration name: aquapulse

Choose the account you would like to use to perform operations for this configuration:
 [1] your.email@gmail.com
 [2] Log in with a new account
Please enter your numeric choice: 1

Pick cloud project to use:
 [1] Create a new project
Please enter numeric choice or text value (must exactly match list item): 1

Enter a Project ID. Note that a Project ID CANNOT be changed later.
Project IDs must be 6-30 characters (lowercase ASCII, digits, or hyphens) in length
and start with a lowercase letter. aquapulse-XXXXX
Your current project has been set to: [aquapulse-XXXXX].

Do you want to configure a default Compute Region and Zone? (Y/n)? n

Your Google Cloud SDK is configured and ready to use!
```

---

##### 5. gcloud 認証の確認

```bash
# 現在の設定を確認
gcloud config list

# 期待される出力:
# [core]
# account = your.email@gmail.com
# disable_usage_reporting = True
# project = aquapulse-XXXXX

# アカウント情報を確認
gcloud auth list

# 期待される出力:
#          Credentialed Accounts
# ACTIVE  ACCOUNT
# *       your.email@gmail.com
```

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] `gcloud version` でバージョンが表示される
- [ ] GCP Console にログインできる
- [ ] 課金アカウントが設定されている
- [ ] `gcloud config list` でプロジェクトが表示される
- [ ] `gcloud auth list` でアカウントが表示される

---

#### 🔧 トラブルシューティング

**問題1: `gcloud: command not found`**

**原因:** PATH が通っていない

**解決策（Mac/Linux）:**
```bash
# PATHを確認
echo $PATH

# gcloud のパスを追加
export PATH=$PATH:$HOME/google-cloud-sdk/bin

# .bashrc または .zshrc に追記
echo 'export PATH=$PATH:$HOME/google-cloud-sdk/bin' >> ~/.bashrc
source ~/.bashrc
```

**解決策（Windows）:**
- 環境変数 PATH に以下を追加:
- `C:\Users\<ユーザー名>\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`

---

**問題2: 課金アカウントが作成できない**

**原因:** クレジットカードの認証エラー

**解決策:**
1. カード情報を再確認
2. 別のクレジットカードを試す
3. デビットカードまたはプリペイドカードは使えない場合がある
4. GCP サポートに問い合わせ: https://cloud.google.com/support

---

**問題3: `gcloud init` で Project ID が重複している**

**症状:**
```
The project ID you entered is already taken.
```

**解決策:**
```bash
# プロジェクトIDを変更（末尾に日付を追加）
# 例: aquapulse-20260711
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [B2. GCP プロジェクト作成](#b2-gcp-プロジェクト作成)
- **一旦終わる場合**: ここまででGCP環境準備完了！
- **Part A に戻る場合**: [Part A: ハードウェア編](#part-a-ハードウェア編)

---

### B2. GCP プロジェクト作成

#### 📋 前提条件

- [ ] [B1. 環境準備（クラウド）](#b1-環境準備クラウド) 完了

⚠️ **ESP32は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 30分
- **2回目以降:** 10分

#### 🎯 このセクションで達成すること

- [ ] GCPプロジェクト作成（またはgcloud initで作成済みを確認）
- [ ] 必要なAPI有効化
- [ ] サービスアカウント作成
- [ ] Secrets Manager 設定

---

#### 📝 手順

##### 1. プロジェクトの確認または作成

**現在のプロジェクトを確認:**
```bash
gcloud config get-value project
```

**期待される出力:**
```
aquapulse-XXXXX
```

**新しいプロジェクトを作成する場合:**
```bash
# プロジェクトID（一意である必要がある）
PROJECT_ID="aquapulse-$(date +%Y%m%d)"

# プロジェクト作成
gcloud projects create $PROJECT_ID \
  --name="AquaPulse Thermostat" \
  --set-as-default

# 確認
gcloud config get-value project
```

---

##### 2. 課金アカウントのリンク

```bash
# 課金アカウントIDを取得
BILLING_ACCOUNT=$(gcloud billing accounts list --format='value(name)' | head -n 1)

# プロジェクトにリンク
gcloud billing projects link $(gcloud config get-value project) \
  --billing-account=$BILLING_ACCOUNT

# 確認
gcloud billing projects describe $(gcloud config get-value project)
```

**期待される出力:**
```
billingAccountName: billingAccounts/XXXXXX-XXXXXX-XXXXXX
billingEnabled: true
name: projects/aquapulse-XXXXX/billingInfo
projectId: aquapulse-XXXXX
```

---

##### 3. 必要なAPIの有効化

```bash
# 一括で有効化
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  bigquery.googleapis.com \
  secretmanager.googleapis.com \
  run.googleapis.com
```

**実行例:**
```
Operation "operations/acat.XXXX" finished successfully.
```

**確認:**
```bash
gcloud services list --enabled
```

**期待される出力（一部）:**
```
NAME                              TITLE
bigquery.googleapis.com           BigQuery API
cloudbuild.googleapis.com         Cloud Build API
cloudfunctions.googleapis.com     Cloud Functions API
run.googleapis.com                Cloud Run API
secretmanager.googleapis.com      Secret Manager API
```

---

##### 4. サービスアカウントの作成

**サービスアカウント作成:**
```bash
# サービスアカウント作成
gcloud iam service-accounts create aquapulse-functions \
  --display-name="AquaPulse Cloud Functions"

# 確認
gcloud iam service-accounts list
```

**期待される出力:**
```
DISPLAY NAME                  EMAIL                                           DISABLED
AquaPulse Cloud Functions     aquapulse-functions@aquapulse-XXXXX.iam.gserviceaccount.com  False
```

---

**必要な権限を付与:**
```bash
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT="aquapulse-functions@${PROJECT_ID}.iam.gserviceaccount.com"

# BigQuery データ編集者
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/bigquery.dataEditor"

# Secret Manager シークレットアクセサ
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

# 確認
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:${SERVICE_ACCOUNT}"
```

---

##### 5. Secrets Manager 設定（Tapo認証情報）

**シークレット作成:**

```bash
# Tapo ユーザー名（メールアドレス）
echo -n "your.email@example.com" | \
  gcloud secrets create tapo-username \
  --data-file=- \
  --replication-policy="automatic"

# Tapo パスワード
echo -n "YourTapoPassword" | \
  gcloud secrets create tapo-password \
  --data-file=- \
  --replication-policy="automatic"

# Tapo P300 IPアドレス
echo -n "192.168.1.10" | \
  gcloud secrets create tapo-p300-ip \
  --data-file=- \
  --replication-policy="automatic"
```

**確認:**
```bash
gcloud secrets list
```

**期待される出力:**
```
NAME            CREATED              REPLICATION_POLICY
tapo-password   2026-07-11T09:00:00  automatic
tapo-p300-ip    2026-07-11T09:00:00  automatic
tapo-username   2026-07-11T09:00:00  automatic
```

**シークレット値の確認:**
```bash
gcloud secrets versions access latest --secret="tapo-username"
# 出力: your.email@example.com
```

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] `gcloud config get-value project` でプロジェクトIDが表示される
- [ ] 課金が有効化されている
- [ ] 必要なAPIが有効化されている（5つ）
- [ ] サービスアカウントが作成されている
- [ ] シークレットが作成されている（3つ）

---

#### 🔧 トラブルシューティング

**問題1: `Billing must be enabled`**

**原因:** 課金アカウントがリンクされていない

**解決策:**
```bash
# 課金アカウントを確認
gcloud billing accounts list

# リンク
gcloud billing projects link $(gcloud config get-value project) \
  --billing-account=XXXXXX-XXXXXX-XXXXXX
```

---

**問題2: `Permission denied`（APIの有効化）**

**原因:** 権限不足

**解決策:**
1. GCP Console でオーナー権限があるか確認
2. `gcloud auth login` で再認証
3. 別のアカウントで試す

---

**問題3: シークレットが作成できない**

**症状:**
```
ERROR: (gcloud.secrets.create) PERMISSION_DENIED: Permission 'secretmanager.secrets.create' denied
```

**原因:** Secret Manager API が有効化されていない

**解決策:**
```bash
gcloud services enable secretmanager.googleapis.com
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [B3. Cloud Functions デプロイ](#b3-cloud-functions-デプロイ)
- **一旦終わる場合**: ここまででGCPプロジェクト作成完了！
- **Part A に戻る場合**: [Part A: ハードウェア編](#part-a-ハードウェア編)

---

### B3. Cloud Functions デプロイ

#### 📋 前提条件

- [ ] [B2. GCP プロジェクト作成](#b2-gcp-プロジェクト作成) 完了

⚠️ **ESP32は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 60分
- **2回目以降:** 20分

#### 🎯 このセクションで達成すること

- [ ] データ保存用Cloud Function作成
- [ ] サーモスタット制御用Cloud Function作成
- [ ] デプロイ
- [ ] テスト

---

#### 📝 手順

##### 1. 作業ディレクトリの作成

```bash
# ホームディレクトリに作業フォルダ作成
mkdir -p ~/aquapulse-functions
cd ~/aquapulse-functions
```

---

##### 2. データ保存用Cloud Function の作成

**ディレクトリ作成:**
```bash
mkdir -p ingest
cd ingest
```

**main.py 作成:**
```python
# ファイル: ingest/main.py
import functions_framework
import json
from datetime import datetime
from google.cloud import bigquery

# BigQuery クライアント初期化
client = bigquery.Client()
PROJECT_ID = "YOUR_PROJECT_ID"  # 後で置換
TABLE_ID = f"{PROJECT_ID}.aquapulse.sensor_readings"

@functions_framework.http
def ingest(request):
    """
    HTTP エンドポイント: ESP32からデータを受信してBigQueryに保存
    
    新スキーマ対応:
    - sensor_id, sensor_type, location, value, unit, device_id, firmware_version
    """
    # CORS 対応
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # リクエストボディを取得
        request_json = request.get_json(silent=True)
        
        if not request_json:
            return ('Missing JSON body', 400, headers)
        
        # 必須フィールド確認
        required_fields = ['sensor_id', 'sensor_type', 'location', 'value', 'unit', 'device_id']
        for field in required_fields:
            if field not in request_json:
                return (f'Missing field: {field}', 400, headers)
        
        # BigQuery に挿入するデータ（新スキーマ）
        row = {
            'timestamp': datetime.utcnow().isoformat(),
            'sensor_id': request_json['sensor_id'],
            'sensor_type': request_json['sensor_type'],
            'location': request_json['location'],
            'value': float(request_json['value']),
            'unit': request_json['unit'],
            'device_id': request_json['device_id'],
            'firmware_version': request_json.get('firmware_version')  # NULLable
        }
        
        # BigQuery に挿入
        errors = client.insert_rows_json(TABLE_ID, [row])
        
        if errors:
            print(f'BigQuery insert errors: {errors}')
            return (f'BigQuery error: {errors}', 500, headers)
        
        print(f'Inserted: {row}')
        return (json.dumps({'status': 'ok', 'inserted': row}), 200, headers)
        
    except Exception as e:
        print(f'Error: {e}')
        return (f'Internal error: {str(e)}', 500, headers)
```

**⚠️ 新スキーマ対応について:**

このコードは新しいBigQueryスキーマに対応しています。ESP32から以下のフィールドを受信します：

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `sensor_id` | ✅ | センサーID |
| `sensor_type` | ✅ | センサータイプ |
| `location` | ✅ | 測定場所 |
| `value` | ✅ | 測定値 |
| `unit` | ✅ | 単位 |
| `device_id` | ✅ | デバイスID |
| `firmware_version` | ❌ | ファームウェアバージョン（省略可） |

`timestamp` はCloud Functions側で自動生成されます（UTC）。

**requirements.txt 作成:**
```bash
cat > requirements.txt << 'EOF'
functions-framework==3.*
google-cloud-bigquery==3.*
EOF
```

---

##### 3. サーモスタット制御用Cloud Function の作成

```bash
cd ~/aquapulse-functions
mkdir -p thermostat
cd thermostat
```

**main.py 作成:**
```python
# ファイル: thermostat/main.py
import functions_framework
import asyncio
import json
import os
import uuid
from datetime import datetime
from kasa import Discover
from google.cloud import secretmanager, bigquery

# Secrets Manager クライアント
secret_client = secretmanager.SecretManagerServiceClient()
PROJECT_ID = "YOUR_PROJECT_ID"  # 後で置換

# BigQuery クライアント（イベント記録用）
bq_client = bigquery.Client()
EVENTS_TABLE_ID = f"{PROJECT_ID}.aquapulse.control_events"

def get_secret(secret_id):
    """Secrets Manager からシークレット取得"""
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = secret_client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

# 閾値（ヒステリシス付き）
THRESHOLD_HIGH = 27.0  # ファンON
THRESHOLD_LOW = 26.0   # ファンOFF

# 状態管理（メモリ内、簡易版）
fan_state = {'is_on': False}

def record_event(event_type, action, trigger_value, trigger_threshold, success, error_message=None, duration_ms=None):
    """
    control_events テーブルにイベントを記録
    """
    event_id = str(uuid.uuid4())
    row = {
        'event_id': event_id,
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'device_id': 'cloud_function_thermostat_v1',
        'action': action,
        'action_details': {'hysteresis_upper': THRESHOLD_HIGH, 'hysteresis_lower': THRESHOLD_LOW},
        'trigger_type': 'threshold_exceeded' if success else 'error',
        'trigger_sensor_id': 'ds18b20_001',  # 温度センサーのID（仮）
        'trigger_value': trigger_value,
        'trigger_threshold': trigger_threshold,
        'success': success,
        'error_message': error_message,
        'duration_ms': duration_ms
    }
    
    try:
        errors = bq_client.insert_rows_json(EVENTS_TABLE_ID, [row])
        if errors:
            print(f'BigQuery event insert errors: {errors}')
        else:
            print(f'Event recorded: {event_id} - {action}')
    except Exception as e:
        print(f'Error recording event: {e}')

async def control_fan_async(temperature):
    """
    温度に応じてファンをON/OFF
    """
    start_time = datetime.utcnow()
    
    try:
        # Tapo 認証情報取得
        tapo_username = get_secret('tapo-username')
        tapo_password = get_secret('tapo-password')
        tapo_ip = get_secret('tapo-p300-ip')
        
        # Tapo P300 に接続
        dev = await Discover.discover_single(
            tapo_ip,
            username=tapo_username,
            password=tapo_password,
            timeout=10
        )
        await dev.update()
        
        # ファン用ソケット（0番目と仮定）
        fan = dev.children[0]
        
        # サーモスタットロジック（ヒステリシス）
        if temperature >= THRESHOLD_HIGH and not fan.is_on:
            await fan.turn_on()
            fan_state['is_on'] = True
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            print(f'🔥 温度 {temperature}℃ → ファンON')
            
            # イベント記録
            record_event('automated_thermostat', 'fan_on', temperature, THRESHOLD_HIGH, True, duration_ms=duration_ms)
            
            # TODO: LINE通知
            return {'action': 'turn_on', 'temperature': temperature, 'threshold': THRESHOLD_HIGH}
        
        elif temperature <= THRESHOLD_LOW and fan.is_on:
            await fan.turn_off()
            fan_state['is_on'] = False
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            print(f'❄️ 温度 {temperature}℃ → ファンOFF')
            
            # イベント記録
            record_event('automated_thermostat', 'fan_off', temperature, THRESHOLD_LOW, True, duration_ms=duration_ms)
            
            # TODO: LINE通知
            return {'action': 'turn_off', 'temperature': temperature, 'threshold': THRESHOLD_LOW}
        
        else:
            print(f'温度 {temperature}℃ → 変更なし（現在: {"ON" if fan.is_on else "OFF"}）')
            return {'action': 'no_change', 'temperature': temperature, 'fan_is_on': fan.is_on}
    
    except Exception as e:
        # エラーイベント記録
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        record_event('automated_thermostat', 'error', temperature, None, False, error_message=str(e), duration_ms=duration_ms)
        raise

@functions_framework.http
def thermostat(request):
    """
    HTTP エンドポイント: 温度データを受け取ってファン制御
    """
    # CORS 対応
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        request_json = request.get_json(silent=True)
        
        if not request_json or 'value' not in request_json:
            return ('Missing temperature value', 400, headers)
        
        temperature = float(request_json['value'])
        
        # 非同期関数を実行
        result = asyncio.run(control_fan_async(temperature))
        
        return (json.dumps(result), 200, headers)
        
    except Exception as e:
        print(f'Error: {e}')
        return (f'Internal error: {str(e)}', 500, headers)
```

**⚠️ control_events テーブル対応について:**

このコードは、ファンのON/OFFイベントを `control_events` テーブルに自動記録します。

記録される情報：
- `event_id`: UUID（自動生成）
- `timestamp`: イベント発生時刻（UTC）
- `event_type`: 'automated_thermostat'
- `action`: 'fan_on', 'fan_off', 'error'
- `action_details`: ヒステリシスの閾値情報
- `trigger_value`: 温度値（介入前の状態）
- `trigger_threshold`: 閾値（27℃ or 26℃）
- `success`: 成功/失敗
- `duration_ms`: 実行時間

これにより、将来的に因果推論分析（ファンの冷却効果など）が可能になります。

**requirements.txt 作成:**
```bash
cat > requirements.txt << 'EOF'
functions-framework==3.*
python-kasa==0.10.*
google-cloud-secret-manager==2.*
google-cloud-bigquery==3.*
EOF
```

---

##### 4. プロジェクトIDの置換

```bash
# 現在のプロジェクトIDを取得
PROJECT_ID=$(gcloud config get-value project)

# ingest/main.py の置換
cd ~/aquapulse-functions/ingest
sed -i.bak "s/YOUR_PROJECT_ID/${PROJECT_ID}/g" main.py

# thermostat/main.py の置換
cd ~/aquapulse-functions/thermostat
sed -i.bak "s/YOUR_PROJECT_ID/${PROJECT_ID}/g" main.py
```

---

##### 5. Cloud Functions のデプロイ

**ingest Function デプロイ:**
```bash
cd ~/aquapulse-functions/ingest

gcloud functions deploy ingest \
  --gen2 \
  --runtime=python312 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=ingest \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=60s \
  --memory=256Mi \
  --max-instances=10
```

**実行時間: 3-5分**

**期待される出力:**
```
Deploying function (may take a while - up to 2 minutes)...done.
availableMemoryMb: 256
buildId: XXXX-XXXX-XXXX
entryPoint: ingest
httpsTrigger:
  url: https://asia-northeast1-aquapulse-XXXXX.cloudfunctions.net/ingest
...
state: ACTIVE
timeout: 60s
```

**URL を保存:**
```bash
INGEST_URL=$(gcloud functions describe ingest --region=asia-northeast1 --gen2 --format='value(serviceConfig.uri)')
echo "Ingest URL: $INGEST_URL"
```

---

**thermostat Function デプロイ:**
```bash
cd ~/aquapulse-functions/thermostat

gcloud functions deploy thermostat \
  --gen2 \
  --runtime=python312 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=thermostat \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=120s \
  --memory=512Mi \
  --max-instances=5
```

**実行時間: 3-5分**

**URL を保存:**
```bash
THERMOSTAT_URL=$(gcloud functions describe thermostat --region=asia-northeast1 --gen2 --format='value(serviceConfig.uri)')
echo "Thermostat URL: $THERMOSTAT_URL"
```

---

##### 6. 動作テスト

**ingest Function のテスト:**
```bash
curl -X POST $INGEST_URL \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "test_sensor",
    "value": 25.5,
    "unit": "celsius"
  }'
```

**期待される出力:**
```json
{"status":"ok","inserted":{"timestamp":"2026-07-11T09:00:00.000000","sensor_id":"test_sensor","value":25.5,"unit":"celsius"}}
```

---

**thermostat Function のテスト（ファンON）:**
```bash
curl -X POST $THERMOSTAT_URL \
  -H "Content-Type: application/json" \
  -d '{
    "value": 29.0
  }'
```

**期待される出力:**
```json
{"action":"turn_on","temperature":29.0}
```

---

**ログ確認:**
```bash
# ingest のログ
gcloud functions logs read ingest --region=asia-northeast1 --gen2 --limit=20

# thermostat のログ
gcloud functions logs read thermostat --region=asia-northeast1 --gen2 --limit=20
```

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] ingest Function がデプロイされた
- [ ] thermostat Function がデプロイされた
- [ ] 両方のURLが取得できた
- [ ] ingest のテストが成功した
- [ ] thermostat のテストが成功した（Tapo接続必要）
- [ ] ログにエラーがない

---

#### 🔧 トラブルシューティング

**問題1: `BUILD FAILED`**

**原因:** requirements.txt の依存関係エラー

**解決策:**
```bash
# ローカルでテスト
cd ~/aquapulse-functions/ingest
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

**問題2: `Permission denied`**

**原因:** サービスアカウントの権限不足

**解決策:**
```bash
# Cloud Functions のサービスアカウントに権限付与
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/bigquery.dataEditor"
```

---

**問題3: thermostat で Tapo 接続エラー**

**原因:** Secrets が正しく設定されていない

**解決策:**
```bash
# Secrets を確認
gcloud secrets versions access latest --secret="tapo-username"
gcloud secrets versions access latest --secret="tapo-password"
gcloud secrets versions access latest --secret="tapo-p300-ip"

# 間違っていたら再作成
echo -n "correct_value" | gcloud secrets versions add tapo-username --data-file=-
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [B4. BigQuery セットアップ](#b4-bigquery-セットアップ)
- **一旦終わる場合**: ここまででCloud Functions デプロイ完了！

---

### B4. BigQuery セットアップ

#### 📋 前提条件

- [ ] [B2. GCP プロジェクト作成](#b2-gcp-プロジェクト作成) 完了

⚠️ **ESP32は不要**（このセクションは独立）  
⚠️ **Cloud Functions は独立して設定可能**

#### ⏱️ 所要時間

- **初回:** 20分
- **2回目以降:** 5分

#### 🎯 このセクションで達成すること

- [ ] BigQuery データセット作成
- [ ] テーブル作成
- [ ] パーティション設定
- [ ] クエリテスト

---

#### 📝 手順

##### 1. データセットの作成

```bash
# データセット作成
bq mk --dataset \
  --location=asia-northeast1 \
  --description="AquaPulse sensor data" \
  $(gcloud config get-value project):aquapulse
```

**確認:**
```bash
bq ls
```

**期待される出力:**
```
  datasetId  
 ----------- 
  aquapulse  
```

---

##### 2. テーブルスキーマの定義

**sensor_readings テーブル用 schema.json 作成:**
```bash
cat > ~/aquapulse-sensor-schema.json << 'EOF'
[
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "データ記録時刻（UTC）"
  },
  {
    "name": "sensor_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "センサーID（例: ds18b20_001, tapo_t310_room）"
  },
  {
    "name": "sensor_type",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "センサータイプ（temperature, tds, ph, room_temperature, room_humidity）"
  },
  {
    "name": "location",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "測定場所（aquarium, room）"
  },
  {
    "name": "value",
    "type": "FLOAT",
    "mode": "REQUIRED",
    "description": "測定値"
  },
  {
    "name": "unit",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "単位（celsius, ppm, pH, percent）"
  },
  {
    "name": "device_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "デバイスID（esp32_001, tapo_t310_abc123）"
  },
  {
    "name": "firmware_version",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "ファームウェア/ソフトウェアバージョン"
  }
]
EOF
```

**control_events テーブル用 schema.json 作成:**
```bash
cat > ~/aquapulse-events-schema.json << 'EOF'
[
  {
    "name": "event_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "イベント識別子（UUID）"
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "イベント発生時刻（UTC）"
  },
  {
    "name": "event_type",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "イベントタイプ（automated_thermostat, manual_maintenance, manual_dosing）"
  },
  {
    "name": "device_id",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "実行デバイスID（手動の場合はNULL）"
  },
  {
    "name": "action",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "実行アクション（fan_on, fan_off, water_change, fertilizer_add等）"
  },
  {
    "name": "action_details",
    "type": "JSON",
    "mode": "NULLABLE",
    "description": "アクション詳細（量、製品名、メモ等）"
  },
  {
    "name": "trigger_type",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "トリガータイプ（threshold_exceeded, manual, scheduled）"
  },
  {
    "name": "trigger_sensor_id",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "トリガーとなったセンサーID"
  },
  {
    "name": "trigger_value",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "トリガー時のセンサー値（介入前の状態）"
  },
  {
    "name": "trigger_threshold",
    "type": "FLOAT",
    "mode": "NULLABLE",
    "description": "閾値"
  },
  {
    "name": "success",
    "type": "BOOLEAN",
    "mode": "REQUIRED",
    "description": "実行成功/失敗"
  },
  {
    "name": "error_message",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "エラーメッセージ"
  },
  {
    "name": "duration_ms",
    "type": "INTEGER",
    "mode": "NULLABLE",
    "description": "実行時間（ミリ秒）"
  }
]
EOF
```

---

##### 3. テーブルの作成

**sensor_readings テーブル作成:**
```bash
bq mk --table \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=sensor_id,sensor_type \
  --description="Sensor readings with daily partitioning" \
  $(gcloud config get-value project):aquapulse.sensor_readings \
  ~/aquapulse-sensor-schema.json
```

**control_events テーブル作成:**
```bash
bq mk --table \
  --time_partitioning_field=timestamp \
  --time_partitioning_type=DAY \
  --clustering_fields=event_type,action \
  --description="Control events and manual interventions" \
  $(gcloud config get-value project):aquapulse.control_events \
  ~/aquapulse-events-schema.json
```

**確認:**
```bash
bq show aquapulse.sensor_readings
bq show aquapulse.control_events
```

**期待される出力（sensor_readings）:**
```
Table project:aquapulse.sensor_readings

   Last modified         Schema         Total Rows   Total Bytes   Expiration   Time Partitioning   Clustered Fields          Labels  
 ----------------- ------------------- ------------ ------------- ------------ ------------------- ------------------------- -------- 
  11 Jul 09:00:00   |- timestamp: ...   0            0                          DAY (field: ...     sensor_id, sensor_type             
                    |- sensor_id: ...                                            timestamp)                                             
                    |- sensor_type: ...                                                                                                 
                    |- location: ...                                                                                                    
                    |- value: ...                                                                                                       
                    |- unit: ...                                                                                                        
                    |- device_id: ...                                                                                                   
                    |- firmware_version: ...                                                                                            
```

**期待される出力（control_events）:**
```
Table project:aquapulse.control_events

   Last modified         Schema         Total Rows   Total Bytes   Expiration   Time Partitioning   Clustered Fields      Labels  
 ----------------- ------------------- ------------ ------------- ------------ ------------------- --------------------- -------- 
  11 Jul 09:00:00   |- event_id: ...    0            0                          DAY (field: ...     event_type, action             
                    |- timestamp: ...                                            timestamp)                                         
                    |- event_type: ...                                                                                              
                    |- device_id: ...                                                                                               
                    |- action: ...                                                                                                  
                    |- action_details: ...                                                                                          
                    |- trigger_type: ...                                                                                            
                    ...                                                                                                             
```

---

##### 4. テストデータの挿入

**sensor_readings テストデータ:**
```bash
# テストデータ作成
cat > ~/test-sensor-data.json << 'EOF'
{"timestamp": "2026-07-11T09:00:00", "sensor_id": "ds18b20_001", "sensor_type": "temperature", "location": "aquarium", "value": 25.5, "unit": "celsius", "device_id": "esp32_001", "firmware_version": "v1.0.0"}
{"timestamp": "2026-07-11T09:01:00", "sensor_id": "ds18b20_001", "sensor_type": "temperature", "location": "aquarium", "value": 25.7, "unit": "celsius", "device_id": "esp32_001", "firmware_version": "v1.0.0"}
{"timestamp": "2026-07-11T09:02:00", "sensor_id": "ds18b20_001", "sensor_type": "temperature", "location": "aquarium", "value": 25.6, "unit": "celsius", "device_id": "esp32_001", "firmware_version": "v1.0.0"}
{"timestamp": "2026-07-11T09:00:00", "sensor_id": "tapo_t310_room", "sensor_type": "room_temperature", "location": "room", "value": 28.2, "unit": "celsius", "device_id": "tapo_t310_abc123", "firmware_version": null}
EOF

# 挿入
bq insert aquapulse.sensor_readings ~/test-sensor-data.json
```

**control_events テストデータ:**
```bash
# テストデータ作成
cat > ~/test-events-data.json << 'EOF'
{"event_id": "550e8400-e29b-41d4-a716-446655440000", "timestamp": "2026-07-11T09:30:00", "event_type": "automated_thermostat", "device_id": "cloud_function_thermostat_v1", "action": "fan_on", "action_details": {"hysteresis_upper": 27.0}, "trigger_type": "threshold_exceeded", "trigger_sensor_id": "ds18b20_001", "trigger_value": 27.2, "trigger_threshold": 27.0, "success": true, "error_message": null, "duration_ms": 1250}
{"event_id": "660e8400-e29b-41d4-a716-446655440001", "timestamp": "2026-07-11T10:00:00", "event_type": "manual_maintenance", "device_id": null, "action": "water_change", "action_details": {"volume_liters": 5.0, "notes": "週次メンテナンス"}, "trigger_type": "manual", "trigger_sensor_id": null, "trigger_value": null, "trigger_threshold": null, "success": true, "error_message": null, "duration_ms": null}
EOF

# 挿入
bq insert aquapulse.control_events ~/test-events-data.json
```

**確認:**
```bash
# sensor_readings 確認
bq query --use_legacy_sql=false \
  'SELECT * FROM `aquapulse.sensor_readings` ORDER BY timestamp DESC LIMIT 5'

# control_events 確認
bq query --use_legacy_sql=false \
  'SELECT event_id, timestamp, event_type, action, trigger_value FROM `aquapulse.control_events` ORDER BY timestamp DESC LIMIT 5'
```

**期待される出力（sensor_readings）:**
```
+---------------------+---------------+-------------+----------+-------+---------+------------+------------------+
|      timestamp      |   sensor_id   | sensor_type | location | value |  unit   | device_id  | firmware_version |
+---------------------+---------------+-------------+----------+-------+---------+------------+------------------+
| 2026-07-11 09:02:00 | ds18b20_001   | temperature | aquarium |  25.6 | celsius | esp32_001  | v1.0.0           |
| 2026-07-11 09:01:00 | ds18b20_001   | temperature | aquarium |  25.7 | celsius | esp32_001  | v1.0.0           |
| 2026-07-11 09:00:00 | tapo_t310_... | room_temp...| room     |  28.2 | celsius | tapo_t3... | NULL             |
| 2026-07-11 09:00:00 | ds18b20_001   | temperature | aquarium |  25.5 | celsius | esp32_001  | v1.0.0           |
+---------------------+---------------+-------------+----------+-------+---------+------------+------------------+
```

**期待される出力（control_events）:**
```
+--------------------------------------+---------------------+---------------------+--------------+---------------+
|               event_id               |      timestamp      |     event_type      |    action    | trigger_value |
+--------------------------------------+---------------------+---------------------+--------------+---------------+
| 660e8400-e29b-41d4-a716-446655440001 | 2026-07-11 10:00:00 | manual_maintenance  | water_change |          NULL |
| 550e8400-e29b-41d4-a716-446655440000 | 2026-07-11 09:30:00 | automated_thermostat| fan_on       |          27.2 |
+--------------------------------------+---------------------+---------------------+--------------+---------------+
```

---

##### 5. 便利なクエリ例

**最新の温度:**
```sql
SELECT 
  timestamp,
  sensor_id,
  sensor_type,
  location,
  value as temperature,
  unit
FROM `aquapulse.sensor_readings`
WHERE sensor_type = 'temperature'
  AND location = 'aquarium'
ORDER BY timestamp DESC
LIMIT 1
```

**過去24時間の平均:**
```sql
SELECT 
  sensor_id,
  AVG(value) as avg_temp,
  MIN(value) as min_temp,
  MAX(value) as max_temp
FROM `aquapulse.sensor_readings`
WHERE sensor_type = 'temperature'
  AND location = 'aquarium'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY sensor_id
```

**1時間ごとの平均:**
```sql
SELECT 
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  AVG(value) as avg_temp
FROM `aquapulse.sensor_readings`
WHERE sensor_type = 'temperature'
  AND location = 'aquarium'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY hour
ORDER BY hour DESC
```

**ファン制御イベントの履歴:**
```sql
SELECT 
  timestamp,
  action,
  trigger_value,
  trigger_threshold,
  success
FROM `aquapulse.control_events`
WHERE event_type = 'automated_thermostat'
ORDER BY timestamp DESC
LIMIT 10
```

**手動介入イベントの履歴:**
```sql
SELECT 
  timestamp,
  event_type,
  action,
  JSON_EXTRACT_SCALAR(action_details, '$.notes') as notes
FROM `aquapulse.control_events`
WHERE trigger_type = 'manual'
ORDER BY timestamp DESC
LIMIT 10
```

**因果推論用: ファンON後30分の温度変化:**
```sql
WITH fan_events AS (
  SELECT
    event_id,
    timestamp AS event_time,
    trigger_value AS pre_temp
  FROM `aquapulse.control_events`
  WHERE event_type = 'automated_thermostat'
    AND action = 'fan_on'
    AND success = true
)
SELECT
  e.event_id,
  e.event_time,
  e.pre_temp,
  AVG(s.value) AS post_temp_30min,
  e.pre_temp - AVG(s.value) AS cooling_effect
FROM fan_events e
LEFT JOIN `aquapulse.sensor_readings` s
ON s.sensor_type = 'temperature'
  AND s.location = 'aquarium'
  AND s.timestamp BETWEEN TIMESTAMP_ADD(e.event_time, INTERVAL 25 MINUTE)
                      AND TIMESTAMP_ADD(e.event_time, INTERVAL 35 MINUTE)
GROUP BY e.event_id, e.event_time, e.pre_temp
ORDER BY e.event_time DESC
```

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] データセット `aquapulse` が作成された
- [ ] テーブル `sensor_readings` が作成された
- [ ] テーブル `control_events` が作成された
- [ ] テストデータが両テーブルに挿入できた
- [ ] クエリでデータが表示された
- [ ] 因果推論用クエリが実行できた

---

#### 🔧 トラブルシューティング

**問題1: `Dataset already exists`**

**解決策:** 既存のデータセットを使う（問題なし）

---

**問題2: `Permission denied`**

**解決策:**
```bash
gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
  --member="user:$(gcloud config get-value account)" \
  --role="roles/bigquery.admin"
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [B5. Grafana セットアップ](#b5-grafana-セットアップ)
- **一旦終わる場合**: ここまででBigQuery セットアップ完了！

---

### B5. Grafana セットアップ

#### 📋 前提条件

- [ ] [B4. BigQuery セットアップ](#b4-bigquery-セットアップ) 完了
- [ ] Grafana Cloud アカウント（無料）

⚠️ **ESP32は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 30分
- **2回目以降:** 10分

#### 🎯 このセクションで達成すること

- [ ] Grafana Cloud アカウント作成
- [ ] BigQuery データソース接続
- [ ] ダッシュボード作成
- [ ] 温度グラフ表示

---

#### 📝 手順

##### 1. Grafana Cloud アカウント作成

1. **Grafana Cloud にアクセス**
   - https://grafana.com/

2. **Sign up をクリック**

3. **情報を入力**
   - Email
   - Name
   - Company（オプション）

4. **無料プラン選択**
   - Free Forever プラン

5. **Stack 名を設定**
   - 例: `aquapulse-monitoring`

6. **Region 選択**
   - Asia Pacific (Tokyo) 推奨

---

##### 2. サービスアカウントキーの作成（GCP側）

```bash
# サービスアカウント作成（Grafana用）
gcloud iam service-accounts create grafana-bigquery \
  --display-name="Grafana BigQuery Reader"

# BigQuery データ閲覧者権限を付与
PROJECT_ID=$(gcloud config get-value project)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:grafana-bigquery@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:grafana-bigquery@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

# キーを作成
gcloud iam service-accounts keys create ~/grafana-bigquery-key.json \
  --iam-account=grafana-bigquery@${PROJECT_ID}.iam.gserviceaccount.com

# キーの内容を確認
cat ~/grafana-bigquery-key.json
```

---

##### 3. BigQuery データソースの追加（Grafana側）

1. **Grafana にログイン**
   - https://aquapulse-monitoring.grafana.net/

2. **Data sources に移動**
   - サイドバー > Connections > Data sources

3. **Add data source をクリック**

4. **Google BigQuery を選択**

5. **設定を入力**
   - **Name**: `AquaPulse BigQuery`
   - **Authentication Type**: `GCE Default Service Account` → **JWT file** を選択
   - **Upload Service Account Key**: `~/grafana-bigquery-key.json` をアップロード
   - **Default Project**: プロジェクトID（例: `aquapulse-20260711`）
   - **Default Dataset**: `aquapulse`

6. **Save & test をクリック**

**期待される表示:**
```
✅ Data source is working
```

---

##### 4. ダッシュボードの作成

1. **Dashboards に移動**
   - サイドバー > Dashboards

2. **New > New Dashboard をクリック**

3. **Add visualization をクリック**

4. **データソース選択**: `AquaPulse BigQuery`

---

##### 5. 温度グラフの作成

**Query 設定:**

1. **Format**: `Time series`

2. **SQL を入力**:
```sql
SELECT 
  timestamp as time,
  value as temperature
FROM `aquapulse.sensor_readings`
WHERE sensor_id = 'esp32_water_temp'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
ORDER BY timestamp ASC
```

3. **Panel settings**:
   - **Title**: `水温（過去24時間）`
   - **Unit**: `Celsius (°C)`
   - **Y-axis**: Min: 20, Max: 35
   - **Threshold**: 
     - 28℃ (赤): High temperature
     - 26℃ (黄): Normal temperature

4. **Apply をクリック**

---

##### 6. ダッシュボードの保存

1. **Save dashboard をクリック**

2. **名前を入力**: `AquaPulse Monitoring`

3. **Save をクリック**

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] Grafana Cloud アカウントが作成された
- [ ] BigQuery データソースが接続された
- [ ] ダッシュボードが作成された
- [ ] 温度グラフが表示された

---

#### 🔧 トラブルシューティング

**問題1: `Authentication failed`**

**原因:** サービスアカウントキーが正しくない

**解決策:**
1. キーを再作成
2. 権限を再確認（`bigquery.dataViewer`, `bigquery.jobUser`）

---

**問題2: `No data` が表示される**

**原因:** データがまだない、またはクエリが間違っている

**解決策:**
```bash
# BigQuery でデータ確認
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM `aquapulse.sensor_readings`'
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [B6. Tapo P300 設定](#b6-tapo-p300-設定)
- **一旦終わる場合**: ここまでで Grafana セットアップ完了！
- **Part C に進む場合**: [Part C: 統合編](#part-c-統合編)

---

### B6. Tapo P300 設定

#### 📋 前提条件

- [ ] Tapo P300 を入手済み
- [ ] WiFi 環境（2.4GHz）
- [ ] スマートフォン（Tapo アプリ用）

⚠️ **ESP32は不要**（このセクションは独立）  
⚠️ **GCP環境は不要**（このセクションは独立）

#### ⏱️ 所要時間

- **初回:** 20分
- **2回目以降:** 5分

#### 🎯 このセクションで達成すること

- [ ] Tapo P300 を WiFi に接続
- [ ] Tapo アプリで動作確認
- [ ] IPアドレス確認
- [ ] ファンを接続

---

#### 📝 手順

##### 1. Tapo アプリのインストール

**iOS:**
- App Store で「Tapo」を検索
- TP-Link Corporation のアプリをインストール

**Android:**
- Google Play で「Tapo」を検索
- TP-Link Corporation のアプリをインストール

---

##### 2. Tapo アカウント作成

1. **Tapo アプリを開く**

2. **Sign Up をタップ**

3. **メールアドレスとパスワードを入力**
   - このアカウント情報が Cloud Functions で必要

4. **認証メール確認**

5. **ログイン**

---

##### 3. Tapo P300 の追加

1. **P300 を電源に接続**
   - LEDが点滅（オレンジ/緑）

2. **Tapo アプリで「+」をタップ**

3. **「Smart Plug」を選択**

4. **P300 を選択**

5. **WiFi 設定**
   - SSID を選択（2.4GHz）
   - パスワード入力

6. **接続完了まで待つ**（1-2分）

7. **デバイス名を設定**
   - 例: `水槽ファン`

---

##### 4. IPアドレスの確認

1. **Tapo アプリで P300 をタップ**

2. **設定アイコン（歯車）をタップ**

3. **デバイス情報 をタップ**

4. **IPアドレス を確認**
   - 例: `192.168.1.10`
   - このIPアドレスをメモ

---

##### 5. ファンの接続

1. **P300 の1番ソケットにファンを接続**

2. **Tapo アプリで ON/OFF テスト**
   - 1番ソケットをタップ → ON
   - ファンが動作することを確認
   - 1番ソケットをタップ → OFF

---

##### 6. GCP Secrets の更新

```bash
# Tapo IPアドレスを更新
echo -n "192.168.1.10" | \
  gcloud secrets versions add tapo-p300-ip --data-file=-

# 確認
gcloud secrets versions access latest --secret="tapo-p300-ip"
```

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] Tapo P300 が WiFi に接続された
- [ ] Tapo アプリで ON/OFF できる
- [ ] IPアドレスが確認できた
- [ ] ファンが接続されて動作する
- [ ] GCP Secrets が更新された

---

#### 🔧 トラブルシューティング

**問題1: WiFi に接続できない**

**原因:** 5GHz WiFi を選択している

**解決策:**
- 2.4GHz WiFi を選択
- ルーターの設定で 2.4GHz を有効化

---

**問題2: IPアドレスが変わる**

**原因:** DHCP で動的にIPが割り当てられている

**解決策:**
1. **ルーターで固定IP設定（推奨）**
   - ルーターの管理画面にアクセス
   - DHCP予約設定
   - P300 の MAC アドレスに固定IPを割り当て

2. **または、Cloud Functions で複数IP対応**
   - 環境変数に複数IPをカンマ区切りで設定

---

#### ➡️ 次のステップ

- **Part B 完了！おめでとうございます🎉**
- **続けて進む場合**: [Part C: 統合編](#part-c-統合編)
- **Part A に戻る場合**: [Part A: ハードウェア編](#part-a-ハードウェア編)

---

## Part C: 統合編

### C1. ESP32からデータ送信

#### 📋 前提条件

- [ ] [Part A: ハードウェア編](#part-a-ハードウェア編) 完了
- [ ] [B3. Cloud Functions デプロイ](#b3-cloud-functions-デプロイ) 完了
- [ ] [B4. BigQuery セットアップ](#b4-bigquery-セットアップ) 完了

#### ⏱️ 所要時間

- **初回:** 45分
- **2回目以降:** 15分

#### 🎯 このセクションで達成すること

- [ ] ESP32 からCloud Functions にデータ送信
- [ ] BigQuery にデータが保存される
- [ ] Grafana でグラフ表示

---

#### 📝 手順

##### 1. Cloud Functions URL の確認

```bash
# ingest Function の URL
gcloud functions describe ingest --region=asia-northeast1 --gen2 --format='value(serviceConfig.uri)'

# 出力例:
# https://asia-northeast1-aquapulse-XXXXX.cloudfunctions.net/ingest
```

**この URL をメモ**

---

##### 2. ESP32 メインスクリプトの作成

**PC上でファイル作成:**

```python
# ファイル名: main.py
import network
import time
import machine
import onewire
import ds18x20
import urequests
import json

# 設定
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourPassword"
CLOUD_FUNCTION_URL = "https://asia-northeast1-aquapulse-XXXXX.cloudfunctions.net/ingest"
DEVICE_ID = "esp32_001"  # ESP32の識別ID
SENSOR_ID = "ds18b20_001"  # DS18B20センサーのID
FIRMWARE_VERSION = "v1.0.0"  # ファームウェアバージョン
INTERVAL = 60  # 60秒ごと

# DS18B20 初期化
dat = machine.Pin(4)
ds = ds18x20.DS18X20(onewire.OneWire(dat))
roms = ds.scan()

if not roms:
    print("ERROR: No DS18B20 found!")
else:
    print(f"Found {len(roms)} sensor(s)")

# WiFi 接続
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print(f'Already connected: {wlan.ifconfig()[0]}')
        return wlan
    
    print(f'Connecting to {WIFI_SSID}...')
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    timeout = 30
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            print('Connection timeout!')
            return None
        time.sleep(1)
    
    print(f'Connected: {wlan.ifconfig()[0]}')
    return wlan

# 温度読み取り
def read_temperature():
    if not roms:
        return None
    
    ds.convert_temp()
    time.sleep_ms(750)
    temp = ds.read_temp(roms[0])
    return temp

# データ送信（新スキーマ対応）
def send_data(temperature):
    # 新しいスキーマに対応したペイロード
    data = {
        "sensor_id": SENSOR_ID,
        "sensor_type": "temperature",  # センサータイプ
        "location": "aquarium",  # 測定場所
        "value": temperature,
        "unit": "celsius",
        "device_id": DEVICE_ID,  # デバイスID
        "firmware_version": FIRMWARE_VERSION  # ファームウェアバージョン
    }
    
    try:
        response = urequests.post(
            CLOUD_FUNCTION_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=10
        )
        
        print(f'Response: {response.status_code}')
        print(f'Body: {response.text}')
        response.close()
        
        return response.status_code == 200
        
    except Exception as e:
        print(f'Error sending data: {e}')
        return False

# メインループ
def main():
    # WiFi 接続
    wlan = connect_wifi()
    if not wlan:
        print('WiFi connection failed. Rebooting...')
        time.sleep(5)
        machine.reset()
    
    print('Starting main loop...')
    
    while True:
        try:
            # WiFi 再接続チェック
            if not wlan.isconnected():
                print('WiFi disconnected. Reconnecting...')
                wlan = connect_wifi()
                if not wlan:
                    time.sleep(60)
                    continue
            
            # 温度読み取り
            temp = read_temperature()
            if temp is None:
                print('Sensor read error')
                time.sleep(INTERVAL)
                continue
            
            print(f'Temperature: {temp:.2f} C')
            
            # データ送信
            success = send_data(temp)
            if success:
                print('✓ Data sent successfully')
            else:
                print('✗ Data send failed')
            
            # 待機
            time.sleep(INTERVAL)
            
        except Exception as e:
            print(f'Error in main loop: {e}')
            time.sleep(10)

# 起動
if __name__ == '__main__':
    main()
```

**⚠️ 重要: スキーマ変更について**

このコードは新しいBigQueryスキーマに対応しています。以下のフィールドを送信します：

| フィールド | 値 | 説明 |
|-----------|-----|------|
| `sensor_id` | `"ds18b20_001"` | センサー識別子 |
| `sensor_type` | `"temperature"` | センサータイプ（temperature, tds, ph等） |
| `location` | `"aquarium"` | 測定場所（aquarium, room） |
| `value` | `25.5` | 測定値 |
| `unit` | `"celsius"` | 単位 |
| `device_id` | `"esp32_001"` | ESP32デバイスID |
| `firmware_version` | `"v1.0.0"` | ファームウェアバージョン |

**カスタマイズポイント:**
- `DEVICE_ID`: 複数のESP32を使う場合は、各デバイスに固有のIDを設定
- `SENSOR_ID`: センサーを追加する場合は、固有のIDを設定
- `FIRMWARE_VERSION`: コードを更新したらバージョンを上げる

---

##### 3. スクリプトをESP32にアップロード

```bash
# WiFi SSID、パスワード、URLを編集
nano main.py

# アップロード
ampy --port /dev/tty.usbserial-XXXXX put main.py

# 確認
ampy --port /dev/tty.usbserial-XXXXX ls
```

---

##### 4. ESP32 を再起動

```bash
# REPL に接続
screen /dev/tty.usbserial-XXXXX 115200

# Ctrl-D で再起動（または EN ボタン）
```

**期待される出力:**
```
Found 1 sensor(s)
Connecting to YourWiFiSSID...
Connected: 192.168.1.123
Starting main loop...
Temperature: 25.31 C
Response: 200
Body: {"status":"ok","inserted":{...}}
✓ Data sent successfully
```

---

##### 5. BigQuery でデータ確認

```bash
# 最新10件取得
bq query --use_legacy_sql=false \
  'SELECT * FROM `aquapulse.sensor_readings` WHERE sensor_id = "esp32_water_temp" ORDER BY timestamp DESC LIMIT 10'
```

**期待される出力:**
```
+---------------------+--------------------+-------+---------+
|      timestamp      |     sensor_id      | value |  unit   |
+---------------------+--------------------+-------+---------+
| 2026-07-11 09:05:00 | esp32_water_temp   |  25.3 | celsius |
| 2026-07-11 09:04:00 | esp32_water_temp   |  25.4 | celsius |
...
```

---

##### 6. Grafana でグラフ確認

1. **Grafana にアクセス**

2. **ダッシュボードを開く**

3. **グラフに温度データが表示される**
   - 60秒ごとに更新
   - リアルタイムグラフ

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] ESP32 がWiFiに接続した
- [ ] 温度が読み取れた
- [ ] Cloud Functions にデータ送信できた
- [ ] BigQuery にデータが保存された
- [ ] Grafana でグラフが表示された

---

#### 🔧 トラブルシューティング

**問題1: `Response: 400`**

**原因:** JSON形式が間違っている

**解決策:**
- `sensor_id`, `value`, `unit` が含まれているか確認
- `value` が数値か確認

---

**問題2: `ECONNRESET`**

**原因:** WiFi 接続が不安定

**解決策:**
- ESP32 をルーターに近づける
- 再接続ロジックを追加（既存コードに含まれる）

---

**問題3: BigQuery にデータがない**

**原因:** Cloud Functions でエラー

**解決策:**
```bash
# ログ確認
gcloud functions logs read ingest --region=asia-northeast1 --gen2 --limit=50
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [C2. サーモスタット動作確認](#c2-サーモスタット動作確認)
- **一旦終わる場合**: ここまでで基本的なデータ収集完了！

---

### C2. サーモスタット動作確認

#### 📋 前提条件

- [ ] [C1. ESP32からデータ送信](#c1-esp32からデータ送信) 完了
- [ ] [B3. Cloud Functions デプロイ](#b3-cloud-functions-デプロイ) 完了
- [ ] [B6. Tapo P300 設定](#b6-tapo-p300-設定) 完了

#### ⏱️ 所要時間

- **初回:** 30分
- **2回目以降:** 10分

#### 🎯 このセクションで達成すること

- [ ] ESP32 からサーモスタット Cloud Function を呼び出し
- [ ] 水温28℃でファンON
- [ ] 水温26℃でファンOFF
- [ ] 動作確認

---

#### 📝 手順

##### 1. サーモスタット呼び出しの追加

**main.py を編集（PC上）:**

```python
# THERMOSTAT_URLを追加
THERMOSTAT_URL = "https://asia-northeast1-aquapulse-XXXXX.cloudfunctions.net/thermostat"

# send_data 関数の後に追加
def control_thermostat(temperature):
    """サーモスタット制御"""
    data = {
        "value": temperature
    }
    
    try:
        response = urequests.post(
            THERMOSTAT_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data),
            timeout=30
        )
        
        print(f'Thermostat response: {response.status_code}')
        print(f'Body: {response.text}')
        response.close()
        
        return response.status_code == 200
        
    except Exception as e:
        print(f'Error controlling thermostat: {e}')
        return False

# メインループ内で send_data の後に追加
# データ送信
success = send_data(temp)
if success:
    print('✓ Data sent successfully')
    
    # サーモスタット制御
    thermostat_success = control_thermostat(temp)
    if thermostat_success:
        print('✓ Thermostat controlled')
    else:
        print('✗ Thermostat control failed')
else:
    print('✗ Data send failed')
```

---

##### 2. 更新したスクリプトをアップロード

```bash
ampy --port /dev/tty.usbserial-XXXXX put main.py
```

---

##### 3. ESP32 を再起動して動作確認

```bash
screen /dev/tty.usbserial-XXXXX 115200
# Ctrl-D で再起動
```

**期待される出力:**
```
Temperature: 25.31 C
Response: 200
✓ Data sent successfully
Thermostat response: 200
Body: {"action":"no_change","temperature":25.31,"fan_is_on":false}
✓ Thermostat controlled
```

---

##### 4. 温度を上げてテスト

**手動で温度を上げる方法:**

1. **センサーを温める**
   - 手で握る
   - または、お湯に入れる

2. **REPL で確認**
```
Temperature: 29.0 C
Response: 200
✓ Data sent successfully
Thermostat response: 200
Body: {"action":"turn_on","temperature":29.0}
✓ Thermostat controlled
```

3. **ファンが動作することを確認**

---

##### 5. 温度を下げてテスト

1. **センサーを冷やす**
   - 常温の水に入れる
   - または、氷水に入れる

2. **REPL で確認**
```
Temperature: 25.0 C
Response: 200
✓ Data sent successfully
Thermostat response: 200
Body: {"action":"turn_off","temperature":25.0}
✓ Thermostat controlled
```

3. **ファンが停止することを確認**

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] ESP32 からサーモスタット呼び出しができた
- [ ] 温度28℃以上でファンがONになった
- [ ] 温度26℃以下でファンがOFFになった
- [ ] Tapo アプリでも状態が反映されている

---

#### 🔧 トラブルシューティング

**問題1: `Timeout`**

**原因:** Cloud Function の実行時間が長い

**解決策:**
- タイムアウトを30秒に延長（既存コードに含まれる）
- Tapo P300 のIPアドレスを確認

---

**問題2: ファンが動作しない**

**原因:** Tapo P300 の接続エラー

**解決策:**
```bash
# Cloud Functions のログを確認
gcloud functions logs read thermostat --region=asia-northeast1 --gen2 --limit=50
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [C3. 統合テスト](#c3-統合テスト)
- **一旦終わる場合**: ここまででサーモスタット実装完了！

---

### C3. 統合テスト

#### 📋 前提条件

- [ ] [C1. ESP32からデータ送信](#c1-esp32からデータ送信) 完了
- [ ] [C2. サーモスタット動作確認](#c2-サーモスタット動作確認) 完了

#### ⏱️ 所要時間

- **1週間**（連続動作テスト）

#### 🎯 このセクションで達成すること

- [ ] 24時間連続動作確認
- [ ] 1週間連続動作確認
- [ ] エラーログ確認
- [ ] お盆前最終チェック

---

#### 📝 手順

##### 1. 24時間連続動作テスト

**手順:**

1. **ESP32 を起動**

2. **24時間放置**

3. **BigQuery でデータ確認**
```bash
bq query --use_legacy_sql=false \
  'SELECT 
     COUNT(*) as total_records,
     MIN(timestamp) as first_record,
     MAX(timestamp) as last_record,
     TIMESTAMP_DIFF(MAX(timestamp), MIN(timestamp), MINUTE) as duration_minutes
   FROM `aquapulse.sensor_readings` 
   WHERE sensor_id = "esp32_water_temp"
     AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)'
```

**期待される結果:**
- `total_records`: 約1440件（60秒ごと × 24時間）
- `duration_minutes`: 1440分（24時間）

---

##### 2. エラーログの確認

```bash
# ESP32 のログ（REPL で確認）
# エラーメッセージがないか確認

# Cloud Functions のログ
gcloud functions logs read ingest --region=asia-northeast1 --gen2 --limit=100 | grep ERROR

gcloud functions logs read thermostat --region=asia-northeast1 --gen2 --limit=100 | grep ERROR
```

---

##### 3. Grafana でグラフ確認

1. **24時間グラフを確認**
   - データ欠損がないか
   - 温度が妥当な範囲か

2. **ファン制御ログを確認**
   - 28℃でONになっているか
   - 26℃でOFFになっているか

---

##### 4. 1週間連続動作テスト

**手順:**

1. **ESP32 を起動**

2. **1週間放置**

3. **毎日チェック**
   - データが送信されているか
   - ファンが動作しているか
   - エラーがないか

4. **1週間後に確認**
```bash
bq query --use_legacy_sql=false \
  'SELECT 
     DATE(timestamp) as date,
     COUNT(*) as records_per_day,
     AVG(value) as avg_temp,
     MIN(value) as min_temp,
     MAX(value) as max_temp
   FROM `aquapulse.sensor_readings` 
   WHERE sensor_id = "esp32_water_temp"
     AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
   GROUP BY date
   ORDER BY date DESC'
```

**期待される結果:**
- 7日間すべてにデータがある
- 各日に約1440件のデータ

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] 24時間連続動作OK
- [ ] 1週間連続動作OK
- [ ] データ欠損が5%未満
- [ ] エラーログが少ない（1日10件未満）
- [ ] Grafana でグラフが正常
- [ ] ファン制御が動作している

---

#### 🔧 トラブルシューティング

**問題1: データ欠損が多い**

**原因:** WiFi 接続が不安定

**解決策:**
1. ESP32 をルーターに近づける
2. WiFiチャンネルを固定
3. 再接続ロジックを強化（既存コードに含まれる）

---

**問題2: ESP32 が再起動を繰り返す**

**原因:** メモリ不足

**解決策:**
```python
# メモリ解放を追加
import gc
gc.collect()
```

---

#### ➡️ 次のステップ

- **続けて進む場合**: [C4. 長期運用準備](#c4-長期運用準備)
- **完了**: おめでとうございます！システムが完成しました🎉

---

### C4. 長期運用準備

#### 📋 前提条件

- [ ] [C3. 統合テスト](#c3-統合テスト) 完了

#### ⏱️ 所要時間

- **1時間**

#### 🎯 このセクションで達成すること

- [ ] 日常監視チェックリスト作成
- [ ] 緊急時対応手順作成
- [ ] お盆前最終確認

---

#### 📝 手順

##### 1. 日常監視チェックリスト

**毎日（5分）:**
- [ ] Grafana でグラフ確認（データ送信されているか）
- [ ] 水温が正常範囲か（20-30℃）
- [ ] ファンが動作しているか（必要に応じて）

**毎週（10分）:**
- [ ] ESP32 の動作確認（LEDが点灯しているか）
- [ ] エラーログ確認（Cloud Functions）
- [ ] データ欠損率確認（BigQuery）

---

##### 2. 緊急時対応手順

**水温30℃超過の場合:**

1. **すぐに確認**
   - Grafana でリアルタイム温度確認
   - ファンが動作しているか確認

2. **手動でファンON**
   - Tapo アプリでファンON

3. **原因調査**
   - ファンが故障していないか
   - 部屋が暑すぎないか
   - 水槽の照明が強すぎないか

4. **応急処置**
   - 氷を水槽に入れる（ビニール袋に入れて）
   - エアコンで部屋を冷やす

---

**ESP32 が停止した場合:**

1. **REPL で確認**
```bash
screen /dev/tty.usbserial-XXXXX 115200
```

2. **エラーメッセージ確認**

3. **再起動**
   - EN ボタンを押す
   - または USB ケーブルを抜き差し

4. **WiFi 再接続確認**

---

##### 3. お盆前最終確認

**1週間前:**
- [ ] 1週間連続動作テスト完了
- [ ] データ欠損率 < 5%
- [ ] エラーログ < 10件/日
- [ ] ファン制御動作OK

**3日前:**
- [ ] ESP32 再起動
- [ ] Tapo P300 動作確認
- [ ] Cloud Functions 動作確認
- [ ] Grafana アラート設定

**前日:**
- [ ] 最終動作確認
- [ ] 緊急連絡先確認
- [ ] 予備プラン確認（手動でファンON）

**出発当日:**
- [ ] 最終温度確認
- [ ] ファン動作確認
- [ ] Grafana URL をスマホに保存
- [ ] Tapo アプリでファン制御確認

---

#### ✅ 確認事項

このセクション完了時、以下がすべてOKになっていること：

- [ ] 日常監視チェックリストを作成した
- [ ] 緊急時対応手順を作成した
- [ ] お盆前最終確認を実施した
- [ ] 安心してお盆に出発できる状態

---

**🎉 完成おめでとうございます！**

お盆も安心して過ごせます。良い夏休みを！

---

## 付録

### コマンド集

#### GCP

```bash
# プロジェクト確認
gcloud config get-value project

# API 有効化
gcloud services enable cloudfunctions.googleapis.com bigquery.googleapis.com

# Cloud Functions デプロイ
gcloud functions deploy FUNCTION_NAME \
  --gen2 \
  --runtime=python312 \
  --region=asia-northeast1 \
  --source=. \
  --entry-point=ENTRY_POINT \
  --trigger-http \
  --allow-unauthenticated

# BigQuery クエリ
bq query --use_legacy_sql=false 'SELECT * FROM `dataset.table` LIMIT 10'

# Secrets 作成
echo -n "value" | gcloud secrets create SECRET_NAME --data-file=-
```

---

#### ESP32

```bash
# シリアルポート確認
ls /dev/tty.usb*

# MicroPython フラッシュ
esptool.py --port /dev/tty.usbserial-XXX erase_flash
esptool.py --chip esp32 --port /dev/tty.usbserial-XXX write_flash -z 0x1000 esp32.bin

# ファイル転送
ampy --port /dev/tty.usbserial-XXX put main.py

# REPL 接続
screen /dev/tty.usbserial-XXX 115200
```

---

### よくある質問FAQ

**Q1: 費用はどれくらいかかりますか？**

A: 無料枠内で運用可能です（月額¥0）。初期費用は約¥3,100（ESP32、センサー等）。

---

**Q2: WiFi がないと動きませんか？**

A: WiFi必須です。ただし、ESP32にSDカードを追加すればオフラインでもデータ保存可能（将来拡張）。

---

**Q3: 複数の水槽に対応できますか？**

A: 可能です。ESP32を各水槽に1台ずつ設置し、sensor_idを変更すればOK。

---

**Q4: スマホから温度を確認できますか？**

A: Grafana Cloud のURLをスマホブラウザで開けば確認可能です。

---

**Q5: LINE通知は設定できますか？**

A: 可能です。LINE Notify APIを使ってCloud Functionsから通知を送信できます（本マニュアルでは未実装）。

---

### リファレンス

- **MicroPython公式**: https://docs.micropython.org/
- **GCP Cloud Functions**: https://cloud.google.com/functions/docs
- **BigQuery**: https://cloud.google.com/bigquery/docs
- **Grafana**: https://grafana.com/docs/
- **python-kasa**: https://python-kasa.readthedocs.io/
- **DS18B20データシート**: https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf

---

**マニュアル作成者:** Cloud Agent  
**最終更新:** 2026-07-11  
**バージョン:** 1.0  
**ステータス:** ✅ 完成

---

このマニュアルで不明な点があれば、各セクションのトラブルシューティングを参照してください。

Happy monitoring! 🐠💧
