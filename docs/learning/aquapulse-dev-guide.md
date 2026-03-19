# AquaPulse 開発学習ガイド

**開発初心者向け・網羅的な技術解説書**

---

## はじめに

### 本書の目的

このガイドは、**AquaPulse という実際に動いている IoT プロジェクト**を通じて、開発の全体像を学ぶためのものです。

「センサーからデータを取って、グラフにする」という一連の流れを、**なぜそうするか**と**実際のコードがどこで何をしているか**を紐づけながら理解できるように書いています。

### 本書の読み方：1本のストーリーで最初から最後まで

**前提知識は不要です。** 「3.3V ってなに？」「GND ってなに？」「`for` ってなに？」——そうした疑問は、**出てきたその場で**説明します。別の章に飛ばず、この本を上から順に読めば、必要な知識がすべて手に入るように書いています。

各章の冒頭には、**この章が終わると何が読める・何ができるようになるか**と、**この章がないと何が困るか**を書いています。ストーリーの途中で「で、これ何のため？」とならないように、常に「なぜ」を添えています。

各章の末尾には、**学びの確認**（「この一文を自分の言葉で説明できるか」）や**実践のヒント**（試すコマンド、確認の手順）を置いています。読み終えたあと、手を止めて「自分は説明できるか？」と問いかけると、理解が定着しやすくなります。

### 読了後にできること

- センサー → DB → グラフ のデータの流れを説明できる
- 本プロジェクトの**全ファイル**（main.py, notify.py, sources/*, scripts/*, db/migrations, kiosk, grafana/dashboards）の役割がわかる
- sensor_readings と ops_metrics の違い、collect_with_health と system_stats の役割がわかる
- 3.3V、GND、プルアップ、`for`、`def`、Docker、SQL などの用語の意味と、本プロジェクトでの役割がわかる
- トラブル時に「どこを疑うか」がわかる
- 設計・運用・ハードウェアの詳細がどのドキュメントにあるかがわかる

### 実践しやすくするための工夫

各章には**実践のヒント**を入れています。「環境がある場合は〇〇を試してみてください」「このコマンドで確認できます」といった、**手を動かして確かめる**ための案内です。手元に Raspberry Pi や Docker がなくても、プロジェクトのファイルを開いて該当箇所を探すだけでも、解説と実コードの対応がつかめます。また、**実際のスクリプトから抜き出したコード**を掲載しているので、「本の説明」と「実装」が乖離しないようにしています。

### 想定読者

- プログラミングや IoT に興味があるが、実プロジェクトを読んだことがない
- 「Docker って何？」「GND って何？」という状態から始める人
- 手を動かす環境はなくても、読むだけで理解を深めたい人

### 本書の構成（O'Reilly 風の工夫）

- **1本の流れで読み戻しを減らす**：目次は「この順に読む」を推奨。第6章（コード）のあとに第17章（Python 文法）、第9章（通知）のあとに第21章（main.py 1行ずつ）を置き、必要な知識がその直後に来るようにしています
- **用語集**：巻末に 3.3V、GND、hypertable などの用語を一覧。忘れたときに引ける
- **やってみる演習**：第 10 章に 5 つの演習。モックで動かす、Grafana にグラフを追加する、新しいソースを追加するなど
- **トラブルシューティング**：第 12 章に具体的なエラーメッセージと対処を記載。ログに出る例、診断コマンド一覧あり
- **Tip / 警告**：重要な箇所に 💡 ヒントや ⚠️ 警告のコールアウトを配置

---

<a id="目次"></a>

## 目次

**この順に読む**（読み戻しを減らすため。第6章のあと→第17章、第9章のあと→第21章）

1. [第1章 プロジェクト概要](#第1章-プロジェクト概要)
2. [第2章 技術スタックと技術選定](#第2章-技術スタックと技術選定)
3. [第3章 アーキテクチャ](#第3章-アーキテクチャ)
4. [第4章 物理的なセンサー接続](#第4章-物理的なセンサー接続)
5. [第5章 ディレクトリ構成](#第5章-ディレクトリ構成)
6. [第6章 コードのロジックとライブラリ](#第6章-コードのロジックとライブラリ)
7. **[第17章 Python 文法](#第17章-python-文法リファレンス)** ← 第6章で出た for, def, while をここで確認
8. [第7章 Docker とコンテナ](#第7章-docker-とコンテナ)
9. [第8章 データベース設計](#第8章-データベース設計)
10. [第9章 通知と運用](#第9章-通知と運用)
11. **[第21章 main.py 1行ずつ](#第21章-mainpy-主要部分の1行ずつ解説)** ← コードの流れを追う
12. **[第22章 gpio_temp.py 1行ずつ](#第22章-gpio_temppy-1行ずつ解説)**
13. **[第23章 db/writer.py 1行ずつ](#第23章-dbwriterpy-1行ずつ解説)**
14. [第10章 学習のための次のステップ](#第10章-学習のための次のステップ)
15. [第11章 環境変数リファレンス](#第11章-環境変数リファレンス)
16. [第12章 トラブルシューティング](#第12章-トラブルシューティング)
17. [第13章 コードの詳細解説（発展）](#第13章-コードの詳細解説発展)
18. [第14章 TimescaleDB の Continuous Aggregates](#第14章-timescaledb-の-continuous-aggregates将来の-ml-用)
19. [第15章 外から・スマホから読む方法](#第15章-外からスマホから読む方法)
20. [第16章 まとめ](#第16章-まとめ)

**その他**（必要に応じて）: [第18章 docker-compose](#第18章-docker-composeyml-完全解説) | [第20章 SQL](#第20章-sql-完全解説) | [第38章 notify.py](#第38章-notifypy-の仕組み) | [用語集](#用語集glossary)

---

## 第1章 プロジェクト概要

**この章が終わると**: 「AquaPulse が何をするシステムか」「1本の水温データがどこを通ってグラフになるか」が説明できるようになります。

**この章がないと**: 第2章以降で「TimescaleDB」「Docker」が出てきても「で、何のため？」となり、技術の話が頭に残りません。まず**完成形のイメージ**をつかむことが、その後の理解の土台になります。

### 1.1 問題：何が課題か

アクアリウム（淡水の水槽）では、水温・気温・湿度・照明の時間帯などが、魚や水草の健康に影響します。

水温が高すぎると酸欠になりやすく、夏場は冷却ファンやクーラーを検討する必要があります。照明の ON/OFF 時間は水草の光合成に直結し、長すぎるとコケが増え、短すぎると水草が弱ります。「昨日より今日の水温が高い」といった変化を、感覚ではなく**データで見たい**——そう思っても、温度計を毎日メモするのは面倒です。数日続けると挫折しがちです。

**自動で測って、グラフにしてくれる**仕組みがあれば、スマホや PC で過去の推移を一目で確認できます。換水やエサやりのタイミングと水温の関係も、データとして残せます。

**IoT とは**：IoT（Internet of Things）は「モノのインターネット」と訳されますが、ここでは**センサーが物理世界の値をデジタル化し、コンピュータで扱える形にする**という意味で使います。温度計の「針」を読む代わりに、センサーがデジタル値（25.3）を出力し、プログラムがそれを保存・可視化する。この流れは、工場の設備監視、家庭のスマートホーム、気象観測など、多くの IoT プロジェクトで共通しています。AquaPulse は、その**小さな一例**として、アクアリウムという身近な題材で同じ流れを理解できるようにしています。

### 1.2 解決：AquaPulse がすること

**AquaPulse** は、その「自動で測って、グラフにする」システムです。

1. **センサー**が水温・気温・湿度・照明 ON/OFF を取得
2. **データベース**に時系列で保存
3. **Grafana** というツールでグラフ化し、PC や 7 インチタッチディスプレイに表示

完成すると、例えば「過去 24 時間の水温の推移」がグラフで見られます。将来は、このデータを使って「何が水質に効くか」を分析したり、異常を検知したりする予定です。

**具体的な使用シーン**：朝起きて PC やスマホで Grafana を開くと、夜間の水温変化が一目でわかります。ヒーターが止まっていても、グラフが下がっていれば気づけます。**照明の ON/OFF 時間**も記録されるので、「水草が調子悪い」と感じたとき、直近 1 週間の照明時間が足りなかったかどうかを確認できます。**TDS（総溶解固形物）** を測っていれば、換水のタイミングの目安にもなります。**気温・湿度**は、水槽周辺の環境を把握し、夏場の蒸発量や冬場の乾燥の傾向を追うのに役立ちます。つまり、**データがあることで、感覚ではなく根拠を持って判断**できるようになります。

### 1.3 完成形のイメージ：1本のデータの流れ

「水温 25.3℃」という 1 件のデータが、どこで生まれてどこに届くかを追ってみましょう。

```
① DS18B20 水温センサー（水槽内）
   → 物理的に温度を検知

② collector/src/sources/gpio_temp.py
   → /sys/bus/w1/devices/28-*/w1_slave を読んで 25.3 を取得

③ collector/src/main.py
   → gpio_temp を 60 秒ごとに呼び出し、結果をまとめる

④ collector/src/db/writer.py
   → sensor_readings テーブルに INSERT

⑤ TimescaleDB（PostgreSQL）
   → ディスクに保存

⑥ Grafana
   → SQL で SELECT し、グラフに表示
```

この流れを頭に入れておくと、第 6 章以降のコード解説が「あの流れのこの部分か」と理解しやすくなります。

**データパイプラインという考え方**：この「センサー → 処理 → 保存 → 可視化」の流れは、**データパイプライン**と呼ばれるパターンです。データが一方通行で流れ、各段階で役割が分担されています。ビッグデータの世界では Kafka や Spark といった大規模なツールが使われますが、AquaPulse では Python のスクリプトと DB だけで同じ構成を実現しています。規模は違っても、**「データの流れ」を追う**という考え方は同じです。

**入口となる関数**：水温取得の入口は `get_readings` です。実コードは次のとおりです。

```python
# gpio_temp.py 43〜48行目
def get_readings():
    """DS18B20 から水温を取得し、共通フォーマットの辞書リストで返す。"""
    return asyncio.run(_get_readings_async())
```

`get_readings()` を呼ぶと、内部で `_get_readings_async` が動き、DS18B20 の値を読んで共通フォーマットのリストで返します。第 6 章で `_get_readings_async` の中身を読むときの**目印**になります。

### 1.4 実際のコードで流れを確認する

抽象的な説明だけではイメージが湧きにくいので、**実際のスクリプトから抜き出したコード**を少し見てみましょう。今は細部を理解する必要はありません。「こういう形で書かれている」という**感触**をつかめれば十分です。

**② gpio_temp.py が水温を返す部分**：`_get_readings_async` の中で、読み取った温度を共通フォーマットでリストに追加しています。

```python
# gpio_temp.py 67〜73行目
readings.append({
    "time": now,
    "sensor_id": sensor_id,      # ← 例: "ds18b20_water_28_00001117a4e0"
    "metric": "temperature",      # ← 測定項目
    "value": temp,               # ← ここに 25.3 が入る
})
```

`temp` が 25.3 なら、`{"time": ..., "sensor_id": "ds18b20_water_28_00001117a4e0", "metric": "temperature", "value": 25.3}` という辞書が 1 件、リストに追加されます。これが「共通フォーマット」の実体です。

**④ writer.py が DB に保存する部分**：`save_reading` の中で、辞書を SQL に変換して INSERT しています。

```python
# writer.py 21〜26行目
with conn.cursor() as cur:
    cur.execute(
        f"INSERT INTO sensor_readings ({col_list}) VALUES ({placeholders})",
        tuple(vals),   # ← reading の time, sensor_id, metric, value がここに入る
    )
conn.commit()   # ← ここでディスクに確定
```

上記の辞書が `vals` に変換され、`sensor_readings` テーブルに INSERT されます。`commit()` で確定し、ディスクに書き込まれます。

### 1.5 ハードウェア構成（何がどこにあるか）

| 機器 | 役割 | 本プロジェクトでのコード |
|------|------|--------------------------|
| Raspberry Pi 5 | すべてを動かすコンピュータ | Docker で db, grafana, collector を実行 |
| DS18B20 | 水温センサー（水槽に沈める） | `collector/src/sources/gpio_temp.py` で読み取り |
| MCP3424 | アナログ→デジタル変換（TDS・pH 用） | `collector/src/sources/gpio_tds.py` で読み取り |
| Tapo H100 + T310 | 気温・湿度センサー（Wi-Fi） | `collector/src/sources/tapo_sensors.py` |
| Tapo P300 | 照明用電源タップ（Wi-Fi） | `collector/src/sources/tapo_lighting.py` |
| Pi Touch Display | 7 インチ画面に Grafana を常時表示 | [Grafana キオスク](../display/grafana-kiosk.md) |

**ハードウェアの役割の補足**：**Raspberry Pi** は「すべてを動かす脳」です。Docker で db、grafana、collector の 3 コンテナを走らせ、1-Wire や I2C のピンに直接アクセスします。**DS18B20** は水槽に沈める防水型の温度センサーで、1-Wire で Raspberry Pi と通信します。**MCP3424** はアナログ電圧をデジタル値に変換する ADC で、TDS や pH センサー（電圧出力）の値を読むために必要です。**Tapo H100** は Wi-Fi ハブで、子デバイス T310 が気温・湿度を測定。**Tapo P300** は電源タップで、各口の ON/OFF を取得できます。**Pi Touch Display** は 7 インチのタッチパネルで、Grafana を全画面表示してキオスクのように使います。それぞれ**接続方式**（1-Wire、I2C、Wi-Fi）が異なり、それに応じてコード（gpio_temp、gpio_tds、tapo_sensors、tapo_lighting）も分かれています。

### 1.6 この章のまとめ

- **問題**: 水温などを手動でメモするのは面倒
- **解決**: センサー → DB → グラフ で自動化
- **1本のデータ**: gpio_temp → main.py → writer.py → DB → Grafana
- **次章**: この流れを実現するために、なぜ Python / TimescaleDB / Docker / Grafana を選んだかを学ぶ

**学びの確認**：この章を読み終えた時点で、次のことが言えれば理解できています。「水温 25.3℃ という 1 件のデータは、gpio_temp.py で取得され、main.py でまとめられ、writer.py で DB に INSERT され、Grafana が SQL で SELECT してグラフにしている」。この一文を自分の言葉で説明できるか、確認してみてください。

↑ [目次へ戻る](#目次)

---

## 第2章 技術スタックと技術選定

**この章が終わると**: 「Python / TimescaleDB / Docker / Grafana が、1本のデータの流れのどこで使われるか」が説明できるようになります。なぜその技術を選んだかの**理由**もわかります。

**この章がないと**: 第6章でコードを読んでも「なぜ Python なのか」「なぜこの DB なのか」が浮かばず、設計の意図が伝わりません。技術選定の理由を知ることで、コードの**背景**が理解できるようになります。

### 2.1 全体マップ：技術がどこで使われるか

第1章の「1本のデータの流れ」に、技術を当てはめるとこうなります。

**技術選定の考え方**：プロジェクトでは「何を選ぶか」が重要な判断になります。**正解は一つ**ではありません。同じ機能を実現する技術は複数あり、**「何を優先するか」**（開発速度、学習コスト、パフォーマンス、運用のしやすさなど）によって選び方が変わります。AquaPulse は「個人・小規模」「Raspberry Pi で動く」「将来の拡張を想定」という前提で選んでいます。別の前提なら、別の選択肢が有効になります。

| 流れの段階 | 使う技術 | 本プロジェクトでのファイル・役割 |
|------------|----------|----------------------------------|
| センサー読み取り | Python, smbus2, 1-Wire | `gpio_temp.py`, `gpio_tds.py`, `tapo_sensors.py` |
| データ収集の制御 | Python (main.py) | `collector/src/main.py` のループとスレッド |
| DB への保存 | psycopg2, TimescaleDB | `db/writer.py` → `db/init/00_schema.sql` |
| 実行環境 | Docker | `docker-compose.yml` で db, grafana, collector を起動 |
| グラフ表示 | Grafana | `grafana/` のダッシュボード設定 |

### 2.2 なぜ Python か

**役割**: センサーから値を読み、DB に書き込む「つなぎ」のプログラムを書く。

- **ライブラリが豊富**: 1-Wire（`/sys` を読む）、I2C（smbus2）、Tapo（python-kasa）、PostgreSQL（psycopg2）がすべて Python で扱える
- **書きやすい**: 初心者にも読みやすく、試行錯誤しやすい
- **本プロジェクトでは**: `collector/src/main.py` がエントリポイント。`sources/` 配下の各ファイルがセンサーごとの読み取りを担当

**Python がなかったら**：C や C++ で書くこともできますが、センサーごとのライブラリが少なく、開発が重くなります。Node.js や Go でも可能ですが、1-Wire や I2C の成熟したライブラリが Python ほど多くありません。**IoT やデータ収集の現場では Python がよく使われる**理由の一つです。

**代替案との比較**：**Node.js** は JavaScript で IoT にもよく使われますが、1-Wire や smbus2 相当のライブラリが Python より少なく、AquaPulse では採用しませんでした。**Go** はコンパイル型で高速ですが、Raspberry Pi 上のセンサー読み取りは 1 分に 1 回程度なので、速度の差は無視できます。**C/C++** はハードウェアに近いですが、将来の ML や分析を考えると Python の方が有利です。**結論**：ライブラリの豊富さ、将来の拡張性、学習コストのバランスで Python を選んでいます。

### 2.3 なぜ TimescaleDB か

**役割**: 「いつ、どのセンサーが、どんな値を取ったか」を時系列で保存する。

- **時系列に特化**: タイムスタンプでデータを分割し、大量になっても検索が速い
- **PostgreSQL の拡張**: 普通の SQL がそのまま使える。Grafana も PostgreSQL に対応
- **本プロジェクトでは**: `db/init/00_schema.sql` で `sensor_readings` テーブルを定義。`create_hypertable` で時系列テーブルにしている

**通常の PostgreSQL だけではダメなのか**：通常のテーブルでも動きますが、1日あたり数千〜数万件のデータが溜まると、`WHERE time >= ... AND time < ...` の検索が遅くなりがちです。TimescaleDB は `time` 列で内部パーティションを作り、**時間範囲の検索を高速化**します。また、将来の ML 用に「1分粒度の平均」などを事前計算する Continuous Aggregates も使えます。

**代替案との比較**：**InfluxDB** は時系列データベースの代表格ですが、PostgreSQL とは別のクエリ言語（Flux）を覚える必要があり、既存の PostgreSQL ツールが使えません。**SQLite** は軽量で単純ですが、時系列のパーティションや集約の自動化がなく、長期運用でテーブルが肥大化しがちです。**結論**：PostgreSQL の拡張なので既存の知識を活かしつつ、時系列に最適化された TimescaleDB を選んでいます。

### 2.4 なぜ Docker か

**役割**: Python、TimescaleDB、Grafana を「同じ環境で、再現可能に」動かす。

- **環境の再現性**: 「手元では動くが本番で動かない」を防ぐ。Python のバージョンやライブラリをコンテナ内に閉じ込める
- **1コマンドで起動**: `docker compose up -d` で db, grafana, collector がまとめて起動
- **本プロジェクトでは**: `docker-compose.yml` が全体の定義。`collector/Dockerfile` が collector 用のイメージをビルドする

**Docker がなかったら**：Raspberry Pi に直接 Python 3.11、PostgreSQL、Grafana をインストールし、バージョンの違いや依存関係の衝突と格闘することになります。また、OS を再インストールしたとき、同じ環境を再現するのが大変です。Docker で**コンテナ**にまとめておくと、`docker compose up -d` で同じ状態に戻せます。

### 2.5 なぜ Grafana か

**役割**: DB に溜まったデータをグラフで表示する。

- **時系列グラフが得意**: センサーデータの可視化に最適
- **SQL で自由に取得**: 「水温だけ」「気温と湿度」など、欲しいデータを SQL で指定
- **キオスクモード**: ログインなしで 7 インチ画面に常時表示できる
- **本プロジェクトでは**: Grafana が PostgreSQL に接続し、`sensor_readings` を SELECT してグラフ化。ダッシュボードは `grafana/dashboards/` に JSON で保存可能

**Grafana がなかったら**：DB にデータは溜まりますが、グラフを見るには自分で SQL を書いて CSV にエクスポートし、Excel や Python で可視化する必要があります。Grafana は「時間範囲を選ぶ」「SQL を書く」「グラフの種類を選ぶ」だけで、リアルタイムに近い形でデータを表示してくれます。**ダッシュボード**として複数のグラフを並べられるので、水温・気温・湿度・照明を一画面で確認できます。

### 2.6 この章のまとめ

- 各技術は「1本のデータの流れ」の**特定の段階**で使われる
- 選定理由は「時系列に強い」「ライブラリが豊富」など、**問題に合っているか**で決まる
- **次章**: これらの技術がどう組み合わさって「アーキテクチャ」になるかを学ぶ

**学びの確認**：この章を読み終えた時点で、次のことが言えれば理解できています。「Python はセンサー読み取りと DB 書き込みのつなぎ。TimescaleDB は時系列データの保存。Docker は環境の再現性。Grafana はグラフ表示。それぞれ『1本の流れ』のどこで使われているか」を説明できるか、確認してみてください。

↑ [目次へ戻る](#目次)

---

## 第3章 アーキテクチャ

**この章が終わると**: 「水温は60秒、気温は300秒」のように間隔が違う理由がわかります。`main.py` のメインループとスレッドの**役割分担**が理解できるようになります。

**この章がないと**: 第6章でコードを読んでも「なぜ gpio_temp と tapo_sensors で別の書き方になっているのか」がわかりません。**設計の意図**を知ることで、コードの構造が「なるほど」と腹落ちします。

**アーキテクチャとは**：**アーキテクチャ**は、システムの**全体構成**や**部品の役割分担**を指します。家の設計図が「どこに部屋があるか」「どうつながるか」を示すように、ソフトウェアのアーキテクチャは「どのコンポーネントが何を担当し、どう連携するか」を表します。AquaPulse では、**センサー**（データの発生源）、**collector**（集約・保存）、**DB**（永続化）、**Grafana**（可視化）が明確に分かれており、**変更の影響範囲**を限定しやすくなっています。たとえば Grafana の表示を変えても、collector のコードは触りません。

### 3.1 全体図

```
┌─────────────────────────────────────────────────────────────────┐
│                     Raspberry Pi (Edge)                           │
├─────────────────────────────────────────────────────────────────┤
│  Sensors                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │ gpio_temp   │ │ gpio_tds    │ │ tapo_sensors│ │tapo_lighting│ │
│  │ (1-Wire)    │ │ (I2C)       │ │ (Wi-Fi)     │ │ (Wi-Fi)     │ │
│  │ 60s         │ │ 60s         │ │ 300s        │ │ 300s        │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ │
│         │               │               │               │        │
│         └───────────────┴───────────────┴───────────────┘        │
│                                 │                                 │
│                         collector/main.py                         │
│                    (メインループ + 独立スレッド)                     │
│                                 │                                 │
│                                 ▼                                 │
│                         db/writer.py                              │
│                    (sensor_readings, ops_metrics)                 │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  TimescaleDB (PostgreSQL)                                         │
│  sensor_readings (Raw)  /  ops_metrics (ヘルス)                    │
└─────────────────────────────────┼─────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  Grafana (PC / 7" Touch Display)                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 設計思想（なぜこうなっているか）

| 方針 | 理由 | 本プロジェクトでの対応 |
|------|------|------------------------|
| **非同期・独立間隔** | Tapo は API 制限がある（5分間隔）。水温は高頻度で取得したい。同期させると複雑になる | `main.py`: gpio_temp, gpio_tds は別スレッドで60秒。Tapo はメインループで300秒 |
| **Raw データをそのまま保存** | 取得時刻を丸めない。後から別の時間窓で分析できる | `writer.py` の `save_reading` は取得した `time` をそのまま INSERT |
| **特徴量は DB で生成** | 1分・5分粒度の集約は DB 側の方が効率的 | 第14章の Continuous Aggregates（将来実装） |
| **学習は PC、推論はエッジ** | 学習は計算資源が必要。推論は軽量でリアルタイム性が重要 | 現状は収集のみ。将来 ML を追加する際の設計方針 |

**Raw データの意味**：センサーが「2026-03-17 10:23:45.123 UTC」に 25.3℃ を返したら、その時刻を**丸めずに**そのまま DB に保存します。もし「1分ごとの平均」に丸めてしまうと、後から「30秒窓で分析したい」「異常検知でサブ秒の変動を見たい」といった要望に対応できません。**生データを残す**ことで、将来の分析の選択肢を広げています。**特徴量は DB で**：1分・5分の平均や最大値は、Python で計算するより **TimescaleDB の time_bucket** や **Continuous Aggregates** で集約する方が、大量データを効率的に扱えます。**学習は PC、推論はエッジ**：機械学習のモデル訓練は GPU やメモリを多く使うため PC やクラウドで行い、学習済みモデルだけを Raspberry Pi に載せて推論する、という将来の構成を想定しています。

### 3.3 本プロジェクトでの対応ファイル

- **メインループ・スレッド**: `collector/src/main.py` の `while True:` と `_gpio_temp_loop`, `_gpio_tds_loop`
- **設計の詳細**: [design/architecture.md](../design/architecture.md)

**なぜ水温は60秒、気温は300秒なのか**：Tapo の API には呼び出し頻度の制限があり、5分（300秒）間隔が安全です。一方、水温は魚の健康に直結するため、より高頻度（60秒）で監視したい。**同じループで両方を動かすと**、水温を60秒で取るために Tapo も60秒で呼ぶことになり、API 制限に引っかかる可能性があります。そこで、gpio_temp を**別スレッド**で動かし、メインループは Tapo 用の 300 秒間隔にしています。

**スレッドの起動**：`main.py` の `if __name__ == "__main__":` 内で、gpio_temp 用のスレッドをこうやって起動しています。

```python
# main.py 254〜258行目
if "gpio_temp" in SOURCES:
    t = threading.Thread(target=_gpio_temp_loop, args=(stop_event,), daemon=True)
    t.start()   # ← ここで別スレッドが動き始める
    threads.append(("gpio_temp", t, GPIO_TEMP_INTERVAL))
```

**ループ内の待機**：`_gpio_temp_loop` の中では、1回読み取ったあと `stop_event.wait(GPIO_TEMP_INTERVAL)` で 60 秒待ってから次の読み取りに進みます。

```python
# main.py 166〜188行目（_gpio_temp_loop 内）
while not stop_event.is_set():
    try:
        readings = get_readings()           # ← gpio_temp の水温取得
        for r in readings:
            save_reading(conn, r)           # ← DB に保存
            # ... ログ出力 ...
    except Exception as e:
        print(f"[gpio_temp] Failed: {e}", flush=True)
    stop_event.wait(GPIO_TEMP_INTERVAL)     # ← ここで 60 秒待つ
```

**学びの確認**：この章を読み終えた時点で、次のことが言えれば理解できています。「水温と気温で間隔が違うのは、Tapo の API 制限と水温の監視頻度の要望が違うから。gpio_temp は別スレッドで 60 秒、メインループは Tapo 用に 300 秒」。

↑ [目次へ戻る](#目次)

---

## 第4章 物理的なセンサー接続

**この章が終わると**: 配線図の「3.3V」「GND」が何を意味するか、なぜ 3.3V でなければならないかがわかります。1-Wire、I2C、Wi-Fi の違いと、それぞれが**どのコードで読み取られるか**の対応関係も理解できます。

**この章がないと**: 配線図を見ても「何をつなげばいいのか」がわかりません。トラブル時に「配線が原因か、プログラムが原因か」の切り分けもできません。**電気の基礎**を知ることで、センサーとコンピュータの「つながり方」が理解できます。

### 4.1 まず知っておく：3.3V と GND とは

センサーは**電気**で動きます。配線図には必ず「3.3V」と「GND」が出てきます。これらが何かを理解しないと、配線の意味がわかりません。

**GND（グラウンド）**とは、**電圧の基準点**です。ゼロボルトの「地面」のようなものです。電気の流れは「高い電圧から低い電圧へ」と流れるので、GND は「流れの行き先」です。Raspberry Pi のピンには「GND」と書かれた穴が複数あり、そこにセンサーの GND 線をつなぎます。

**3.3V**とは、**3.3 ボルトの電源**です。Raspberry Pi は内部で 3.3V を供給しており、センサーに「この電圧で動いてください」と渡します。**なぜ 3.3V なのか**——多くのセンサー（DS18B20、MCP3424 など）は 3.3V 用に設計されているからです。5V のピンを使うと、センサーが壊れる可能性があります。逆に、3.3V 用のセンサーに 1.5V しか渡さないと、正しく動きません。**データシート（製品の仕様書）で「動作電圧」を確認し、それに合わせる**のが基本です。

**まとめ**: 3.3V = センサー用の電源。GND = 電圧の基準（ゼロ）。この 2 本があって初めて、センサーは動き、データ線で値をやり取りできます。

> **⚠️ 警告**: 3.3V と GND を**逆に接続**すると、センサーが壊れる可能性があります。配線前にピン番号を必ず確認してください。

### 4.2 接続方式の種類

センサーとコンピュータの「つなぎ方」には、いくつかの方式があります。それぞれ**長所・短所**があり、用途に応じて選ばれます。

| 方式 | 説明 | 本プロジェクトでの使用例 |
|------|------|--------------------------|
| **1-Wire** | 1本のデータ線で通信。GPIO 1本で複数デバイス | DS18B20 水温センサー |
| **I2C** | 2本（SDA, SCL）で複数デバイス。アドレスで識別 | MCP3424 ADC（TDS・pH） |
| **Wi-Fi** | 無線。IP アドレスで通信 | Tapo H100, P300 |

**なぜ方式が違うのか**：1-Wire は**配線が少なくて済む**（1本で複数センサーがつながる）が、速度は遅い。I2C は**複数デバイスを同じバスで扱える**（アドレスで識別）が、配線が長いとノイズに弱い。Wi-Fi は**配線不要**だが、電源やネットワークが必要で、家庭用の Tapo は「既製品」として使う。AquaPulse は、水温は 1-Wire（安価で水槽に沈めやすい）、TDS は I2C（精密な電圧測定が必要）、気温・照明は Wi-Fi（既製品の Tapo）と、**用途に合わせて使い分け**ています。

**本プロジェクトでの対応**: 1-Wire → `gpio_temp.py`（`/sys/bus/w1/devices/` を読む）。I2C → `gpio_tds.py`（smbus2 で MCP3424 にアクセス）。Wi-Fi → `tapo_sensors.py`, `tapo_lighting.py`（python-kasa で IP 経由）。

**実践のヒント**: 1-Wire の場合、Raspberry Pi 上で `ls /sys/bus/w1/devices/` を実行すると、`28-00001117a4e0` のようなフォルダが表示されます。これが DS18B20 のデバイス ID です。`gpio_temp.py` は次のようにパスを組み立てて `w1_slave` を読んでいます。

```python
# gpio_temp.py 51〜53行目
pattern = os.path.join(W1_DEVICES_PATH, W1_SLAVE_GLOB)   # "/sys/bus/w1/devices/28-*/w1_slave"
device_files = glob.glob(pattern)   # 例: ["/sys/bus/w1/devices/28-00001117a4e0/w1_slave"]
```

環境がある場合は、`cat /sys/bus/w1/devices/28-*/w1_slave` で「センサーが認識されているか」を確認できます。

### 4.3 Raspberry Pi のピン配置（v2.0）

| 物理ピン | BCM GPIO | 役割 | 接続先 |
|:--------:|:--------:|------|--------|
| 1 | - | 3.3V | DS18B20 VDD |
| 6 | - | GND | DS18B20 GND |
| 7 | 4 | 1-Wire データ | DS18B20 データ |
| 3 | 2 | I2C SDA | MCP3424 SDA |
| 5 | 3 | I2C SCL | MCP3424 SCL |
| 17 | - | 3.3V | ブレッドボード（TDS/pH 用） |
| 9 | - | GND | ブレッドボード GND |

**物理ピンと BCM GPIO の違い**：Raspberry Pi のピンには**物理ピン番号**（1, 2, 3... と並ぶ順番）と**BCM GPIO 番号**（プログラムで参照する番号）の 2 があります。配線図では「物理ピン 7 = BCM GPIO 4」のように書きます。**プログラム**（`gpio_temp.py` や `config.txt` の `w1-gpio`）は BCM 番号を使い、**配線**は「物理ピン 7 の穴に挿す」と覚えます。ピン配置図は、**USB コネクタが下**の向きで、左上がピン 1 です。**ピン 1 は 3.3V なので、ここを間違えるとセンサーが壊れます**。必ず図と実物の向きを確認してください。

### 4.4 DS18B20（水温センサー）

- **配線**: 3.3V, GND, データ（GPIO 4）

**DS18B20 の特徴**：Dallas Semiconductor（現 Maxim）が開発した**デジタル温度センサー**です。アナログ温度センサー（熱電対やサーミスタ）とは違い、**すでにデジタル化された値**を出力するため、ADC（アナログ→デジタル変換）が不要です。1-Wire というプロトコルで、1本の線で複数のセンサーを接続できます。水槽に沈める**防水型**のモジュールが市販されており、アクアリウムに適しています。

**プルアップ抵抗とは**: 1-Wire のデータ線は、センサーが何も送っていないとき**浮いた状態**になります。浮くと電気的に不安定になり、誤った値が読まれることがあります。そこで、データ線と 3.3V の間に**抵抗（4.7kΩ）**を入れておくと、何も送っていないときは 3.3V に「引っ張られた」状態になります。これを**プルアップ**といいます。DS18B20 のモジュール（基板）によっては、この抵抗が内蔵されている場合があり、そのときは外付けは不要です。

- **config.txt**: `dtoverlay=w1-gpio` で 1-Wire を有効化
- **読み取り**: `/sys/bus/w1/devices/28-*/w1_slave` を読む。`t=12345` がミリ度

**実際の読み取りコード**：`_read_temperature_sync` の中で、`w1_slave` ファイルを読んで温度を抽出しています。

```python
# gpio_temp.py 23〜37行目
with open(device_path, "r") as f:
    content = f.read()
for line in content.strip().split("\n"):
    if line.strip().endswith("YES") and "crc=" in line:
        pass   # CRC チェック成功
    elif "t=" in line:
        temp_str = line.split("t=")[-1].strip()   # ← "t=25312" から "25312" を取り出す
        temp_millideg = int(temp_str)
        return round(temp_millideg / 1000.0, 2)   # ← 25312 → 25.312 → 25.31℃
```

`device_path` は例えば `/sys/bus/w1/devices/28-00001117a4e0/w1_slave` です。ファイルを開いて読み、`t=12345` のような形式を探し、12345 を 1000 で割って摂氏（12.345℃）にしています。`round(..., 2)` で小数点以下 2 桁に丸めます。

**実践のヒント**: 環境がある場合は、`cat /sys/bus/w1/devices/28-*/w1_slave` を実行してみてください。2 行目に `t=25312` のような形式で温度（ミリ度）が表示されます。25312 ÷ 1000 = 25.312℃ です。

### 4.5 MCP3424（I2C ADC）

- **アドレス**: 0x68（Adr0, Adr1 を GND に接続）
- **CH1**: TDS センサーの電圧 → ppm 換算
- **CH2**: pH センサー（将来）
- **重要**: CH1- (Pin 2) は GND に接続すること。浮いていると不安定

**ADC とは**：**ADC（Analog-to-Digital Converter）** は、**アナログの電圧をデジタル値に変換**する IC です。TDS センサーは「水中の導電率」に応じて**電圧**を出力しますが、コンピュータは**数値**でしか扱えません。MCP3424 は、その電圧を 18 ビットのデジタル値に変換し、I2C で Raspberry Pi に渡します。**差分入力**（CH+ と CH- の差）を測るため、CH1- を GND に接続しないと、ノイズの影響で値が不安定になります。

### 4.6 Tapo（Wi-Fi）

- **H100**: ハブ。子デバイス T310/T315 で気温・湿度を取得
- **P300**: マルチタップ。各口の ON/OFF を取得
- **認証**: メールアドレス + パスワード（Tapo アプリと同じ）

**本プロジェクトでの対応**: [hardware/wiring/v2.0.md](../hardware/wiring/v2.0.md) に配線の詳細。Tapo の IP は DHCP で変わるため、`tapo_sensors.py` は `TAPO_IP_CANDIDATES` で複数 IP を順に試す「ローラー作戦」を採用。

**ローラー作戦とは**：Tapo の IP は DHCP で割り当てられるため、ルーターの再起動などで**変わることがあります**。`TAPO_HUB_IP` に固定 IP を指定すれば確実ですが、DHCP 予約をしていない場合、IP が変わると接続できなくなります。**ローラー作戦**は、`TAPO_IP_CANDIDATES` に「ありそうな IP」を複数（例: 192.168.3.6, 192.168.3.7, 192.168.3.8）列挙し、**順番に試す**方式です。接続に成功した IP が H100 か P300 かは、デバイスの応答（`_is_h100_device` など）で判定します。**DHCP で IP が入れ替わっても**、候補に含まれていれば運用を継続できます。

**配線の手順（DS18B20 の例）**：(1) Raspberry Pi の電源を**オフ**にする。(2) 配線図（[hardware/wiring/v2.0.md](../hardware/wiring/v2.0.md)）を開き、**USB コネクタが下**の向きでピン 1 の位置を確認。(3) DS18B20 の VDD（赤）を物理ピン 1（3.3V）、GND（黒）を物理ピン 6、データ（黄または緑）を物理ピン 7 に接続。**モジュール内蔵のプルアップ抵抗**があればそのままでよい。なければデータ線と 3.3V の間に 4.7kΩ を入れる。(4) `/boot/firmware/config.txt`（または `/boot/config.txt`）に `dtoverlay=w1-gpio` を追加し、**再起動**。(5) `ls /sys/bus/w1/devices/` で `28-*` が表示されれば認識成功。**MCP3424 の場合は**、先に `raspi-config` で I2C を有効化し、SDA→ピン 3、SCL→ピン 5、VDD→3.3V、GND→GND、CH1-→GND を接続。`i2cdetect -y 1` で 0x68 が表示されれば OK。

**実践のヒント**: 配線を確認するときは、**3.3V と GND を間違えない**ことが最も重要です。逆にするとセンサーが壊れる可能性があります。テスターやマルチメーターがある場合は、ピン 1 と 6 の間の電圧を測り、約 3.3V が出ていれば正しく接続されています。また、配線図の「左から何番目のピン」と実物の向きを確認し、回転して挿していないか注意してください。

↑ [目次へ戻る](#目次)

---

## 第5章 ディレクトリ構成

**この章が終わると**: 「このファイルはどこにあるか」「このフォルダは Docker のどのサービスに対応するか」がわかります。コードを読むときの**地図**が頭に入ります。

**この章がないと**: 第6章で「main.py を読む」と言われても、プロジェクトのどこにあるか探すところから始まります。また、`docker-compose.yml` の `build: ./collector` が何を指しているか、`db/init` がいつ実行されるかがわかりません。

**プロジェクト構成の考え方**：ソフトウェアプロジェクトでは、**役割ごとにフォルダを分ける**のが一般的です。`collector/` は「データを集める」、`db/` は「データベースの定義」、`grafana/` は「表示の設定」というように。こうすると、変更したいとき「どこをいじればよいか」がすぐわかります。AquaPulse は小規模なので 1 ファイルにまとめることもできますが、**役割を分ける**ことで、将来の拡張や他人が読むときの理解が楽になります。

```
aquapulse/
├── collector/           # センサー収集モジュール
│   ├── src/
│   │   ├── main.py      # エントリポイント
│   │   ├── notify.py    # 通知（Email、IP変更、収集失敗）
│   │   ├── db/writer.py # DB 書き込み
│   │   └── sources/     # 各センサーソース
│   ├── scripts/         # 診断・テスト用
│   ├── Dockerfile
│   └── requirements.txt
├── db/
│   ├── init/            # 初期スキーマ（コンテナ初回起動時に実行）
│   └── migrations/      # マイグレーション
├── grafana/
│   └── dashboards/      # ダッシュボード JSON
├── kiosk/               # キオスクモード用スクリプト
├── docs/
│   ├── design/          # 設計ドキュメント
│   ├── hardware/        # 配線図
│   ├── operations/      # 運用ログ
│   └── learning/        # 本ガイド
├── docker-compose.yml
└── .env                 # 環境変数（Git に含めない）
```

**本プロジェクトでの対応**: `docker-compose.yml` の `build: ./collector` が `collector/` をビルド。`volumes: ./db/init:/docker-entrypoint-initdb.d` が `db/init/` の SQL を初回起動時に実行。`collector_data/` は `notify.py` の状態ファイル（IP 変更履歴など）を保存。

### 5.2 プロジェクトファイル一覧（網羅）

**collector/src/**（本番のデータ収集）

| ファイル | 役割 |
|----------|------|
| `main.py` | エントリポイント。メインループ、スレッド起動、ソースの動的ロード、`collect_with_health` |
| `notify.py` | IP 変更・収集失敗の通知（Email / LINE）。状態の永続化（tapo-ip-state.json 等） |
| `db/writer.py` | `save_reading`（sensor_readings）、`save_ops_metric` / `save_ops_metrics_batch`（ops_metrics） |

**collector/src/sources/**（センサーごとの読み取り）

| ファイル | ソース名 | 役割 |
|----------|----------|------|
| `gpio_temp.py` | gpio_temp | DS18B20 水温（1-Wire） |
| `gpio_tds.py` | gpio_tds | TDS（MCP3424 I2C CH1） |
| `tapo_sensors.py` | tapo_sensors | Tapo H100 + T310/T315 温湿度（python-kasa） |
| `tapo_sensors_tapo.py` | tapo_sensors | 上記の代替実装（tapo ライブラリ）。`TAPO_BACKEND=tapo` で切り替え |
| `tapo_lighting.py` | tapo_lighting | Tapo P300 照明 ON/OFF（python-kasa） |
| `mock.py` | mock | 開発・テスト用モックデータ |
| `system_stats.py` | system_stats | CPU・メモリ・ディスク・温度（ops_metrics に保存） |

**collector/scripts/**（診断・検証用。ホスト上で実行）

| ファイル | 役割 |
|----------|------|
| `test_tapo.py` | Tapo (H100, P300) の接続・データ取得を診断。`docker compose run ... python /app/scripts/test_tapo.py` |
| `read_mcp3424_ch1.py` | MCP3424 CH1 の生電圧を読む（配線確認用） |
| `measure_tds_bottle.py` | TDS 瓶測定。ppm 表示。`--save` で DB に保存（暫定運用用） |

**collector その他**

| ファイル | 役割 |
|----------|------|
| `mock_collector.py` | **単独で動く古いモック**。main.py の mock ソースとは別。DB スキーマも古い形式。現在は `SOURCES=mock` で `sources/mock.py` を使う |
| `Dockerfile` | collector イメージのビルド定義 |
| `requirements.txt` | Python 依存パッケージ |

**db/**

| ファイル | 役割 |
|----------|------|
| `init/00_schema.sql` | 初回起動時に実行。sensor_readings テーブル作成 |
| `migrations/001_add_source_column.sql` | 既存 DB に `source` カラムを追加 |
| `migrations/002_ops_metrics.sql` | ops_metrics テーブル作成（システム監視・収集ヘルス） |

**マイグレーションとは**：既に DB が存在する環境で、スキーマを後から変更するための SQL。`db/init` は**新規インストール時のみ**実行されるため、既存 DB には `migrations/` の SQL を手動で適用する（例: `docker compose exec db psql -U postgres -d aquapulse -f /path/to/001_add_source_column.sql`）。

**grafana/dashboards/**

| ファイル | 用途 |
|----------|------|
| `aquapulse-pc.json` | PC（13 インチ等）向け。6 つの Stats + 詳細グラフ |
| `aquapulse-display.json` | 7 インチ Touch Display 向け。4 つの Stats + コンパクト表示 |
| `aquapulse-operations.json` | 運用監視。CPU・メモリ・収集成功率・レイテンシ |
| `aquapulse-aquarium.json` | 水槽データ専用（水温・TDS・照明等） |

**kiosk/**（Pi Touch Display に Grafana を全画面表示）

| ファイル | 役割 |
|----------|------|
| `install.sh` | cage, chromium, seatd のインストール。systemd サービス登録 |
| `start-kiosk.sh` | Chromium で Grafana を全画面起動。cage が Wayland コンポジタ |
| `brightness.sh` | ディスプレイ輝度の手動調整（day / night / dim） |
| `brightness-schedule.sh` | 時間帯別の自動輝度調整 |

**docs/**（設計・運用・ハードウェア）

| フォルダ | 内容 |
|----------|------|
| `design/` | アーキテクチャ、評価指標、Collector ソース一覧、ops-metrics |
| `hardware/` | 配線図（v1.0, v2.0）、改善計画 |
| `operations/` | 日次ログ、復旧手順、Tapo ステータス、SSD 移行 |
| `display/` | Grafana キオスクのセットアップ |

**フォルダとコードの対応**：`collector/src/main.py` がエントリポイントなので、ここから読むと全体の流れがつかめます。`sources/` 配下はセンサーごとにファイルが分かれており、`gpio_temp.py` が 1-Wire、`gpio_tds.py` が I2C、`tapo_sensors.py` が Tapo 温湿度、`tapo_lighting.py` が Tapo 照明です。`db/writer.py` はどのソースから来たデータも同じ `save_reading` で DB に書き込みます。

**なぜこのフォルダ構成か**：`sources/` にセンサーごとのファイルを分けることで、**新しいセンサーを追加するとき**は `sources/` に 1 ファイル追加し、`_load_source` に 1 行足すだけで済みます。`main.py` や `writer.py` の変更は最小限です。`db/init/` と `db/migrations/` を分けているのは、**新規インストール**（init）と**既存 DB のスキーマ変更**（migrations）で実行タイミングが違うためです。`scripts/` は**本番のデータ収集には使わない**診断・検証用なので、`src/` とは分けています。`grafana/dashboards/` に JSON を置くことで、**ダッシュボードのバージョン管理**ができ、環境を移すときも同じ表示を再現できます。

**実践のヒント**：プロジェクトのルートで `find . -name "*.py" -path "./collector/*" | head -20` を実行すると、Python ファイルの一覧が出ます。`db/init/` の `00_schema.sql` を開くと、`sensor_readings` テーブルの定義が確認できます。ディレクトリ構成図と照らし合わせながら、各ファイルの役割を追っていくと理解が深まります。

**学びの確認**：この章を読み終えた時点で、次のことが言えれば理解できています。「main.py は collector の入口。sources/ にセンサーごとの読み取り、db/writer.py に保存処理。db/init の SQL はコンテナ初回起動時に実行される。scripts/ は診断用、migrations/ は既存 DB のスキーマ変更用」。

↑ [目次へ戻る](#目次)

---

## 第6章 コードのロジックとライブラリ

**この章が終わると**: `main.py` のメインループとスレッドの役割、各センサーソース（gpio_temp, tapo_sensors など）が**同じ形のデータ**を返す理由がわかります。コードに出てくる `for`、`def`、`while` の**基本的な意味**も、この章で必要な分だけ説明します。

**この章がないと**: 第21章や第22章で「1行ずつ解説」を見ても、全体の流れがわからず、断片の知識だけが残ります。**設計の意図**（なぜ共通フォーマットか、なぜスレッドを分けるか）を知ることで、コードが「意味のある塊」として理解できます。

### 6.1 共通フォーマット（reading）

全ソース（gpio_temp, gpio_tds, tapo_sensors, tapo_lighting など）は、**同じ形の辞書**を返します。こうすることで、`main.py` は「どのセンサーから来たか」を気にせず、同じ `save_reading()` で DB に保存できます。

**補足：辞書（dict）とは**——Python では、`{"キー": 値}` の形でデータをまとめる**辞書**という型があります。`reading["time"]` で「time キーに対応する値」を取り出せます。ここでは「1件のセンサーデータ」を辞書 1 個で表しています。

**なぜ共通フォーマットが必要か**——もし gpio_temp が `{"temp": 25.3}`、tapo_sensors が `{"temperature": 24.0, "humidity": 60}` のようにバラバラの形で返すと、main.py は「gpio_temp のときは save_reading に temp を渡す」「tapo のときは temperature と humidity を別々に保存」といった**分岐**を大量に書くことになります。共通フォーマットにすることで、main.py は「辞書のリストが来たら、1件ずつ save_reading に渡す」だけで済み、コードが単純になります。

**共通フォーマットは設計パターンの一つ**：この「複数のソースが同じ形のデータを返す」考え方は、**アダプタパターン**や**正規化**に近いものです。データベースの世界では、異なるテーブルから同じ形でデータを取得する**ビュー**があります。AquaPulse では、各センサーソースが「共通フォーマット」という**契約**を守ることで、main.py は「契約を守ったデータが来る」と信じて処理できます。**新しいセンサーを追加する**ときも、この契約を守るだけで、main.py の変更は最小限で済みます。

```python
{
    "time": datetime (UTC),
    "sensor_id": str,   # 例: "ds18b20_water_28_00001117a4e0"
    "metric": str,      # 例: "temperature", "humidity", "tds", "power_state"
    "value": float,
    "source": str       # オプション。例: "python-kasa"
}
```

### 6.2 ソースの動的ロード（main.py）

環境変数 `SOURCES` で有効なソースを指定し、動的に import します。**実際のコード**（`main.py` の 16〜42 行目）は次のとおりです。

```python
SOURCES_RAW = os.getenv("SOURCES", os.getenv("SOURCE", "mock"))
SOURCES = [s.strip() for s in SOURCES_RAW.split(",") if s.strip()]

def _load_source(name):
    if name == "tapo_sensors":
        if os.getenv("TAPO_BACKEND") == "tapo":
            from sources.tapo_sensors_tapo import get_readings
        else:
            from sources.tapo_sensors import get_readings
        return get_readings
    elif name == "tapo_lighting":
        from sources.tapo_lighting import get_readings
        return get_readings
    elif name == "gpio_temp":
        from sources.gpio_temp import get_readings
        return get_readings
    elif name == "gpio_tds":
        from sources.gpio_tds import get_readings
        return get_readings
    elif name == "mock":
        from sources.mock import get_readings
        return get_readings
    else:
        raise ValueError(f"Unknown source: {name}")

SOURCE_LOADERS = {name: _load_source(name) for name in SOURCES}
```

**1行目**：`os.getenv("SOURCES", ...)` は環境変数 `SOURCES` を取得します。なければ `SOURCE`、それもなければ `"mock"` を使います。`.env` に `SOURCES=gpio_temp,tapo_sensors` と書けば、その値が使われます。

**2行目**：`SOURCES_RAW.split(",")` でカンマ区切りに分割し、`s.strip()` で各要素の前後の空白を削除。空文字は `if s.strip()` で除外されます。結果は `["gpio_temp", "tapo_sensors"]` のようなリストになります。

**gpio_temp の読み込み**：`_load_source("gpio_temp")` が呼ばれると、次の分岐で `get_readings` を返します。

```python
# main.py 513〜515行目
elif name == "gpio_temp":
    from sources.gpio_temp import get_readings
    return get_readings   # ← この関数が SOURCE_LOADERS["gpio_temp"] に入る
```

**SOURCE_LOADERS**：各ソース名に対して `_load_source` を呼び、`get_readings` 関数を取得した辞書です。`SOURCE_LOADERS["gpio_temp"]()` と呼ぶと、gpio_temp の水温取得が実行されます。

**本プロジェクトでは**: `main.py` の `_load_source` 関数と `SOURCE_LOADERS`。`SOURCES` 環境変数（例: `gpio_temp,tapo_sensors`）で有効なソースを指定。`mock` だけにするとセンサーなしで DB と Grafana の動作確認ができる。

**補足：`def` とは**——`def 関数名(引数):` で**関数**を定義します。関数は「まとまった処理」に名前を付けたものです。`_load_source("gpio_temp")` と呼ぶと、その関数が実行され、`get_readings` という別の関数を返します。ここでは「ソース名を受け取り、そのソース用の読み取り関数を返す」役割です。

> **💡 ヒント**: `.env` を編集して `SOURCES=mock` にし、`docker compose restart collector` で再起動すると、センサーに触れずに DB と Grafana の動作確認ができます。mock は 25℃前後のランダムな水温を生成します。本番では `SOURCES=gpio_temp,gpio_tds,tapo_sensors,tapo_lighting` のように必要なソースを列挙します。

### 6.3 メインループと独立スレッド

Tapo 等はメインループで 5 分間隔。gpio_temp, gpio_tds は別スレッドで 60 秒間隔。

```python
# メインループ（Tapo 等）
while True:
    for name, get_readings_fn in other_sources.items():
        readings, health = collect_with_health(name, get_readings_fn, conn, ops_conn)
        all_readings.extend(readings)
        all_health.extend(health)
    for r in all_readings:
        save_reading(conn, r)
    save_ops_metrics_batch(ops_conn, all_health)
    time.sleep(SAMPLE_INTERVAL)  # 300 秒

# 独立スレッド（gpio_temp）
def _gpio_temp_loop(stop_event):
    while not stop_event.is_set():
        try:
            readings = get_readings()
            for r in readings:
                save_reading(conn, r)
        except Exception as e:
            print(f"[gpio_temp] Failed: {e}")
        stop_event.wait(GPIO_TEMP_INTERVAL)  # 60 秒
```

**本プロジェクトでは**: `main.py` の `while True:` がメインループ、`_gpio_temp_loop` が水温用の独立スレッド。`stop_event.wait(GPIO_TEMP_INTERVAL)` で 60 秒（デフォルト）待つ。

**補足：`while` と `for` とは**——`while True:` は「条件が真の間、繰り返す」という意味で、`True` は常に真なので**無限ループ**になります。`for r in readings:` は「readings の各要素を r に代入して、1つずつ処理する」という意味です。`readings` はセンサーデータのリストで、`r` が 1 件ずつの辞書になります。

**実際の main.py のメインループ**：Tapo 等は次のように動いています。

```python
# main.py 273〜291行目
while True:
    all_readings = []
    for name, get_readings_fn in other_sources.items():   # ← tapo_sensors, tapo_lighting 等
        try:
            all_readings.extend(get_readings_fn())         # ← 各ソースから読み取り
        except Exception as e:
            print(f"[{name}] Failed: {e}", flush=True)

    for r in all_readings:
        save_reading(conn, r)   # ← ここで DB に保存（gpio_temp と同じ save_reading）
        # ... ログ出力 ...

    time.sleep(SAMPLE_INTERVAL)   # ← 300 秒待ってから次のループ
```

`other_sources` には gpio_temp と gpio_tds 以外（tapo_sensors, tapo_lighting, mock など）が入っています。各ソースの `get_readings_fn()` を呼び、返ってきた辞書のリストを `all_readings` に溜め、`save_reading` で 1 件ずつ DB に保存。最後に `time.sleep(SAMPLE_INTERVAL)` で 300 秒待ってから次のループに進みます。

**実践のヒント**：`docker compose logs -f collector` でログを追跡すると、60 秒ごとに `{"sensor_id": "ds18b20_water_...", "metric": "temperature", "value": 25.3}` のような JSON が出力されます。これが gpio_temp スレッドの成果です。300 秒ごとに Tapo のデータも混ざります。

**学びの確認**：この節を読み終えた時点で、次のことが言えれば理解できています。「main.py は Tapo 用のメインループ（300秒）と、gpio_temp 用の独立スレッド（60秒）を並行して動かしている。共通フォーマットの辞書が来たら、main.py は save_reading に渡すだけで、どのセンサーかは気にしない」。

### 6.4 1-Wire 読み取り（gpio_temp.py）

**温度読み取り**（`_read_temperature_sync`、17〜40 行目）:

```python
def _read_temperature_sync(device_path: str) -> Optional[float]:
    try:
        with open(device_path, "r") as f:
            content = f.read()
    except (OSError, IOError):
        return None

    for line in content.strip().split("\n"):
        if line.strip().endswith("YES") and "crc=" in line:
            pass   # CRC チェック成功
        elif "t=" in line:
            try:
                temp_str = line.split("t=")[-1].strip()
                temp_millideg = int(temp_str)
                return round(temp_millideg / 1000.0, 2)  # ミリ度 → 摂氏
            except (ValueError, IndexError):
                return None
    return None
```

**共通フォーマットへの変換**（`_get_readings_async`、61〜74 行目）:

```python
for device_path in device_files:
    temp = await asyncio.to_thread(_read_temperature_sync, device_path)
    if temp is not None:
        device_id = os.path.basename(os.path.dirname(device_path)).replace("-", "_")
        sensor_id = f"ds18b20_water_{device_id}"
        readings.append({
            "time": now,
            "sensor_id": sensor_id,
            "metric": "temperature",
            "value": temp,
        })
```

**ポイント**：`device_path` は `/sys/bus/w1/devices/28-00001117a4e0/w1_slave` のようなパス。`os.path.dirname` で親ディレクトリを取り、`os.path.basename` で `28-00001117a4e0` を得て、`-` を `_` に置換して `sensor_id` にしています。`asyncio.to_thread` でブロッキングなファイル I/O を別スレッドで実行し、メインスレッドをブロックしないようにしています。

**本プロジェクトでは**: `collector/src/sources/gpio_temp.py`。Docker で `/sys/bus/w1/devices` をマウントしているため、コンテナ内からも読めます。

### 6.5 I2C 読み取り（gpio_tds.py）

```python
I2C_BUS = 1
MCP3424_ADDR = 0x68

def _read_ch1_voltage() -> float:
    bus = smbus.SMBus(I2C_BUS)
    try:
        bus.write_byte(MCP3424_ADDR, 0x80)  # 設定: 18bit, 1x gain, one-shot
        time.sleep(0.1)
        raw = bus.read_i2c_block_data(MCP3424_ADDR, 0, 4)
        val = ((raw[0] & 0x03) << 16) | (raw[1] << 8) | raw[2]
        if val & 0x20000:  # 符号拡張
            val -= 0x40000
        return val * 2.048 / 262144  # LSB → 電圧(V)
    finally:
        bus.close()
```

**本プロジェクトでは**: `collector/src/sources/gpio_tds.py` の `_read_ch1_voltage`。電圧を `TDS_K` 倍して ppm に換算。`TDS_K` は環境変数でキャリブレーション可能。

**コードの読み方**：`0x80` は MCP3424 への**設定コマンド**。18bit 分解能、1x ゲイン、ワンショット変換を指定しています。`raw` の 4 バイトから 18 ビットの値を組み立てる**ビット演算**（`<<` は左シフト、`|` は OR、`&` は AND）で、ADC の生データを抽出。`val * 2.048 / 262144` は、MCP3424 の仕様（LSB = 2.048V / 262144）に従って電圧に変換しています。TDS センサーは「導電率に応じた電圧」を出力するため、この電圧を `TDS_K`（キャリブレーション係数）で ppm に換算します。**キャリブレーション**が必要な理由は、センサーの個体差や水温による補正のためです。

### 6.6 非同期処理（tapo_sensors.py）

Tapo はネットワーク I/O のため `asyncio` を使用。

**H100 と T310 の関係**：**Tapo H100** は「ハブ」で、子デバイス **T310**（または T315）が気温・湿度を測定します。H100 に接続すると、`dev.children` で子デバイスのリストが取得でき、各子の `temperature` と `humidity` が読めます。`tapo_sensors.py` は H100 の IP に接続し、子デバイスから気温・湿度を取得して `tapo_sensors_{device_id}` という sensor_id で DB に保存します。**P300 とは別**：H100 は温湿度用、P300 は照明用電源タップなので、別のソース（`tapo_lighting.py`）で扱います。

```python
async def _get_readings_async():
    for hub_ip in ip_list:
        try:
            dev = await Discover.discover_single(hub_ip, username=..., password=...)
            await dev.update()
            if not _is_h100_device(dev):
                continue  # 別デバイス → 次を試す（ローラー作戦）
            break
        except Exception as e:
            last_error = e
            continue
    else:
        raise last_error
    # dev から T310/T315 の temperature, humidity を抽出
    ...

def get_readings():
    return asyncio.run(_get_readings_async())
```

**本プロジェクトでは**: `collector/src/sources/tapo_sensors.py`。`Discover.discover_single(ip, ...)` で各 IP に接続を試み、`_is_h100_device(dev)` で H100 かどうか判定。接続成功時に `notify_ip_change` で IP 変更を通知します。呼び出しは次のように行われます。

```python
# tapo_sensors.py 内（接続成功後）
from notify import notify_ip_change
notify_ip_change("tapo_sensors", hub_ip, "H100")   # ← IP が前回と違えば通知
```

**tapo_sensors_tapo.py とは**：`TAPO_BACKEND=tapo` のとき、`tapo_sensors` の代わりに `tapo_sensors_tapo.py` が使われます。**tapo** ライブラリと **python-kasa** の 2 つが Tapo 温湿度に対応しており、互換性の問題（tapo で P300 が動かない、python-kasa で H100 の temperature_unit バグ等）があるため、環境変数で切り替えられます。詳細は [tapo-status-report.md](../operations/tapo-status-report.md) を参照。

### 6.7 DB 書き込み（db/writer.py）

`save_reading` は gpio_temp、tapo_sensors、tapo_lighting など**すべてのソース**から呼ばれます。共通フォーマットの辞書をそのまま SQL に変換します。

```python
# writer.py 10〜26行目
def save_reading(conn, reading):
    cols = ["time", "sensor_id", "metric", "value"]
    vals = [reading["time"], reading["sensor_id"], reading["metric"], reading["value"]]
    if "source" in reading and reading["source"]:
        cols.append("source")
        vals.append(reading["source"])
    placeholders = ", ".join(["%s"] * len(cols))
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO sensor_readings ({', '.join(cols)}) VALUES ({placeholders})",
            tuple(vals),   # ← 値を直接 SQL に埋め込まず、プレースホルダで渡す（SQL インジェクション対策）
        )
    conn.commit()
```

**呼び出し元**：`_gpio_temp_loop` の `for r in readings: save_reading(conn, r)`、メインループの `for r in all_readings: save_reading(conn, r)` で使われています。どちらのソースから来たデータも、同じ `save_reading` 1 つで処理されます。

### 6.8 Tapo P300（照明）の読み取り（tapo_lighting.py）

```python
for child in dev.children or []:
    sensor_id = f"tapo_lighting_{child.device_id}"
    value = 1.0 if child.is_on else 0.0
    readings.append({
        "time": now,
        "sensor_id": sensor_id,
        "metric": "power_state",
        "value": value,
        "source": "python-kasa",
    })
```

**ポイント**: P300 は複数の電源口（children）を持つ。各口の `is_on` で ON=1.0, OFF=0.0 を記録。Grafana で照明の ON/OFF 時間帯を可視化できます。

**なぜ ON/OFF を数値で記録するか**：`is_on` は True/False ですが、共通フォーマットでは `value` が数値なので、ON のとき 1.0、OFF のとき 0.0 に変換しています。こうすることで、Grafana で「照明が ON だった時間帯」を折れ線グラフで表示できます。1.0 の区間が照明 ON、0.0 の区間が OFF と一目でわかります。**H100 との違い**：H100 は気温・湿度という**連続値**を返しますが、P300 は各口の**ON/OFF という離散値**を返します。同じ Tapo でも、データの性質が異なるため、別のソースファイルで扱っています。

実コードでは次のようにループしています。

```python
# tapo_lighting.py 内
for child in dev.children or []:
    sensor_id = f"tapo_lighting_{child.device_id}"
    value = 1.0 if child.is_on else 0.0   # ← ON=1.0, OFF=0.0
    readings.append({
        "time": now,
        "sensor_id": sensor_id,
        "metric": "power_state",
        "value": value,
        "source": "python-kasa",
    })
```

### 6.9 モックソース（mock.py）

```python
def get_readings():
    base_temp = 25.0
    random_fluctuation = random.uniform(-1, 1)
    temperature = base_temp + random_fluctuation
    return [{
        "time": datetime.datetime.now(datetime.timezone.utc),
        "sensor_id": "mock_temperature",
        "metric": "temperature",
        "value": round(temperature, 2),
    }]
```

**用途**: センサーなしでパイプラインをテスト。`SOURCES=mock` で DB と Grafana の動作確認が可能。

**モックの使いどころ**：**モック**は「本物のセンサーの代わりに、それっぽいデータを返す」仕組みです。**いつ使うか**——(1) Raspberry Pi やセンサーがなくても、PC や Mac 上で Docker を動かして**全体の流れを確認**したいとき。(2) 新しい Grafana のダッシュボードや SQL を**試したい**とき。(3) **CI（継続的インテグレーション）** で自動テストを回すとき。`mock` は 25℃前後に `random.uniform(-1, 1)` でランダムな揺らぎを加えているので、**グラフが動いているように見える**ため、表示の確認に適しています。本番では `SOURCES=gpio_temp,gpio_tds,tapo_sensors,tapo_lighting` のように必要なソースを列挙し、`mock` は含めません。

### 6.10 システムメトリクス（system_stats.py）

`OPS_METRICS_ENABLED=true` のとき、`_system_stats_loop` が 60 秒ごとに `system_stats.get_metrics()` を呼び、`save_ops_metric` で ops_metrics に保存します。**sensor_readings とは別テーブル**です。

```python
# system_stats.py 36〜44行目
cpu_percent = psutil.cpu_percent(interval=1)
metrics.append({
    "time": now,
    "host": host,
    "category": "system",      # ← sensor_readings と区別
    "metric": "cpu_percent",
    "value": cpu_percent,
})
# 同様に memory_percent, disk_percent, load_1m, cpu_temp を追加
```

**Raspberry Pi の CPU 温度**（`/sys/class/thermal/thermal_zone0/temp`）は gpio_temp と同様にミリ度で読んで 1000 で割ります。`ops_metrics` に `category: system` で保存され、Grafana の `aquapulse-operations.json` ダッシュボードでラズパイの負荷・温度を監視できます。

### 6.11 使用ライブラリ一覧

| パッケージ | 用途 |
|------------|------|
| psycopg2-binary | PostgreSQL 接続 |
| python-kasa | Tapo デバイス制御（H100, P300） |
| tapo | Tapo 温湿度の代替実装（互換性問題あり） |
| smbus2 | I2C 通信（MCP3424） |
| psutil | CPU・メモリ・ディスク取得 |

**次に読む**：第6章で `for`、`def`、`while` が出てきました。**第17章（Python 文法）** でこれらの構文を詳しく確認すると、コードの理解が深まります。読み戻しを減らすため、第17章を読んでから第7章（Docker）に進むことを推奨します。

↑ [目次へ戻る](#目次)

---

## 第7章 Docker とコンテナ

**この章が終わると**: 「イメージ」「コンテナ」「ボリューム」が何を意味するか、`docker compose up -d` で何が起きるかがわかります。`network_mode: host` がなぜ必要かも理解できます。

**この章がないと**: 「Docker で動かす」と言われても、何が起きているか想像できません。DB に接続できない、Tapo に届かないといったトラブルのとき、「コンテナの中と外」「ホストのネットワーク」の違いがわからず、切り分けができません。

**コンテナとは何か**：**コンテナ**は、**アプリケーションとその依存関係をまとめた実行環境**です。たとえるなら、引っ越し用の段ボール箱に「Python 3.11」「必要なライブラリ」「main.py」を詰めて、どこでも同じように開けて使えるようにしたものです。**仮想マシン**（VM）は OS ごと丸ごとエミュレートするため重いですが、コンテナは**カーネルを共有**し、**プロセスとして動く**ため軽量です。AquaPulse では、db、grafana、collector がそれぞれ**別のコンテナ**で動き、`docker compose up -d` で一括起動します。**イメージ**はコンテナの「設計図」、**ボリューム**はコンテナの外にデータを残す**引き出し**のようなものです。

### 7.1 docker-compose.yml の構造

本プロジェクトの `docker-compose.yml` の主要部分は次のとおりです。

```yaml
services:
  db:
    image: timescale/timescaledb:latest-pg14
    volumes:
      - ./db_data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d   # 初回のみ SQL 実行
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
    # ...

  grafana:
    image: grafana/grafana:latest
    depends_on:
      db:
        condition: service_healthy
    # ...

  collector:
    build: ./collector
    network_mode: host   # ホストのネットワークをそのまま使用（Tapo 接続用）
    volumes:
      - /sys/bus/w1/devices:/sys/bus/w1/devices:ro  # 1-Wire
      - ./collector_data:/app/data                  # 通知状態
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      TAPO_USERNAME: ${TAPO_USERNAME}
      SOURCES: ${SOURCES:-${SOURCE:-mock}}
      # ...
```

**ポイント**：`volumes` の `./db/init:/docker-entrypoint-initdb.d` は「ホストの `db/init` をコンテナの初期化ディレクトリにマウント」する意味です。PostgreSQL の公式イメージは、このディレクトリ内の `.sql` を**初回起動時のみ**実行します。2回目以降は `db_data` にデータがあるためスキップされます。`environment` の `${TAPO_USERNAME}` は `.env` の値がそのまま渡されます。

### 7.2 network_mode: host の理由

- collector は Tapo（Wi-Fi）に接続するため、ホストと同じネットワークが必要
- `127.0.0.1:5432` で DB に接続（ホスト経由）
- 1-Wire は `/sys/bus/w1/devices` をマウントしてアクセス

**なぜ network_mode: host が必要か**：Docker のデフォルトは**bridge ネットワーク**です。各コンテナに仮想の IP が割り当てられ、コンテナ同士はコンテナ名で通信できます。しかし、**Tapo は家庭の LAN（192.168.x.x）上**にあります。bridge ネットワークのコンテナからは、**ホストの外（LAN）に直接届かない**場合があります。**network_mode: host** にすると、コンテナは**ホストのネットワークをそのまま使う**ため、Raspberry Pi と同じ 192.168.x.x のアドレスで Tapo に届きます。**トレードオフ**として、ポートの競合（複数コンテナが同じポートを使えない）などの制約がありますが、AquaPulse では collector が Tapo に届くことが最優先のため、host を採用しています。

### 7.3 環境変数の渡し方

```yaml
environment:
  TAPO_USERNAME: ${TAPO_USERNAME}
  TAPO_IP_CANDIDATES: ${TAPO_IP_CANDIDATES:-}  # 未設定時は空
```

`.env` ファイルの値が `${VAR}` に展開される。`:-` は未設定時のデフォルト。

### 7.4 Collector の Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY src/ ./src/
COPY scripts/ ./scripts/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "src/main.py"]
```

**各行の意味**：`FROM python:3.11-slim` は Python 3.11 が入った軽量なベースイメージを使います。`slim` は最小限のパッケージだけを含むため、イメージサイズが小さくなります。`WORKDIR /app` はコンテナ内の作業ディレクトリを `/app` に設定。以降の `COPY` や `RUN` はこのディレクトリで実行されます。`COPY requirements.txt .` は依存パッケージ一覧を先にコピーし、`COPY src/` と `scripts/` でソースコードをコピー。**COPY の順序**が重要で、`requirements.txt` を先にコピーすることで、ソースだけ変更したときは `pip install` のキャッシュが使われ、ビルドが速くなります。`RUN pip install` で psycopg2、python-kasa などをインストール。`--no-cache-dir` は pip のキャッシュを残さず、イメージを軽くします。`CMD ["python", "-u", "src/main.py"]` はコンテナ起動時に実行するコマンド。`-u` は**バッファリングなし**で標準出力を出すため、`docker compose logs -f collector` でログがリアルタイムに表示されます。

- **python:3.11-slim**: 軽量な Python イメージ。slim は標準ライブラリ最小限
- **-u**: バッファリング無効で `print()` が即ログに出力される
- **scripts/**: 診断用スクリプト（test_tapo.py 等）もコンテナに含める

**本プロジェクトでは**: `docker-compose.yml` が全体の定義。`collector` は `network_mode: host` でホストのネットワークをそのまま使用（Tapo 接続のため）。`docker compose logs -f collector` でログを追跡できる。

**実践のヒント**：`docker compose up -d` のあと、`docker compose ps` で 3 つのサービス（db, grafana, collector）が `running` になっているか確認してください。`docker compose exec db psql -U postgres -d aquapulse -c "\dt"` でテーブル一覧が出れば、`db/init` の SQL が実行されています。`collector` が起動しない場合は、`docker compose logs collector` でエラーメッセージを確認し、環境変数（`POSTGRES_*`, `TAPO_*` など）が正しく渡っているか `.env` を確認します。

**学びの確認**：この章を読み終えた時点で、次のことが言えれば理解できています。「db は TimescaleDB のイメージを使い、`db/init` の SQL を初回のみ実行する。collector は `network_mode: host` で Tapo に届き、`/sys/bus/w1/devices` をマウントして 1-Wire を読む」。

↑ [目次へ戻る](#目次)

---

## 第8章 データベース設計

**この章が終わると**: センサーデータが**どのような形**で DB に保存されているかがわかります。Grafana で「どの SQL を書けば水温のグラフが出るか」も理解できます。

**この章がないと**: `writer.py` が INSERT している「sensor_readings」がどんなテーブルか想像できません。Grafana の SQL も、`SELECT` や `WHERE` の意味がわからず、コピペするだけになってしまいます。**データの形**を知ることで、コードとグラフがつながります。

**時系列データの保存の考え方**：センサーデータは**時間とともに増えていく**ため、**時系列データ**と呼ばれます。通常のテーブルでも保存できますが、**「いつ」「何が」「いくつ」**という 3 要素（時刻、識別子、値）が揃うと、検索や集約のパターンが決まってきます。TimescaleDB は、このパターンに特化した**パーティション**（時間で分割）と**圧縮**を自動で行い、**データが増えても検索が遅くなりにくい**ようにしています。気象データ、株価、IoT データなど、多くの分野で同じ考え方が使われています。

### 8.1 sensor_readings（センサーデータ）

**実際のスキーマ**（`db/init/00_schema.sql` より）:

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE sensor_readings (
    time        TIMESTAMPTZ NOT NULL,
    sensor_id   TEXT NOT NULL,
    metric      TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    source      TEXT
);

SELECT create_hypertable('sensor_readings', 'time');

CREATE INDEX idx_sensor_readings_sensor_time ON sensor_readings (sensor_id, time DESC);
```

**インデックスの意味**：`idx_sensor_readings_sensor_time` は `(sensor_id, time DESC)` の複合インデックスです。Grafana の典型的なクエリは「特定の sensor_id で、時間範囲内のデータを time 順に取得」なので、このインデックスが使われます。`time DESC` で降順に並べているのは、「直近のデータを先に返す」クエリが多いためです。インデックスがないと、テーブル全体をスキャンすることになり、データが増えると遅くなります。

**各列の意味**：`time` は取得時刻（UTC）。`sensor_id` はセンサーの識別子（例：`ds18b20_water_28_00001117a4e0`）。`metric` は測定項目（`temperature`, `humidity`, `tds`, `power_state` など）。`value` は数値。`source` はオプションで、取得元（例：`python-kasa`）を記録します。

**create_hypertable**：TimescaleDB の関数で、このテーブルを時系列用に最適化します。内部で `time` 列でパーティションが作られ、大量データでも検索が速くなります。

**writer.py が INSERT する様子**：gpio_temp や tapo_sensors から渡された `reading` を、そのまま SQL に変換しています。

```python
# writer.py 10〜26行目
def save_reading(conn, reading):
    cols = ["time", "sensor_id", "metric", "value"]
    vals = [reading["time"], reading["sensor_id"], reading["metric"], reading["value"]]
    if "source" in reading and reading["source"]:
        cols.append("source")
        vals.append(reading["source"])
    placeholders = ", ".join(["%s"] * len(cols))
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO sensor_readings ({', '.join(cols)}) VALUES ({placeholders})",
            tuple(vals),   # ← 値をここで渡す。SQL 文字列に直接埋め込まない（インジェクション対策）
        )
    conn.commit()
```

`reading` が共通フォーマットの辞書です。`cols` と `vals` を組み立て、`%s` をプレースホルダにした SQL で INSERT します。値を直接 SQL 文字列に埋め込まないことで、**SQL インジェクション**を防いでいます。

> **💡 ヒント**: `f"INSERT ... VALUES ({value})"` のように値を直接埋め込むと、`sensor_id` に `"; DROP TABLE sensor_readings; --` のような悪意ある文字列が入ったときに攻撃される可能性があります。`%s` と `tuple(vals)` を使えば安全です。

- **hypertable**: TimescaleDB の時系列テーブル。`time` で自動パーティション
- **metric**: temperature, humidity, tds, power_state など

### 8.2 ops_metrics（運用メトリクス）

`sensor_readings` は**アクアリウムのデータ**（水温・気温等）を保存します。一方、`ops_metrics` は**システムの健全性**を記録する別テーブルです。CPU 使用率、収集の成功/失敗、処理時間などを Grafana で監視できます。

**テーブル構造**（`db/migrations/002_ops_metrics.sql`）:

```sql
CREATE TABLE ops_metrics (
    time        TIMESTAMPTZ NOT NULL,
    host        TEXT NOT NULL DEFAULT 'raspi5',
    category    TEXT NOT NULL,   -- 'system' | 'collector'
    metric      TEXT NOT NULL,
    source      TEXT,            -- collector の場合はソース名
    value       DOUBLE PRECISION NOT NULL
);
```

**category = 'system'**（`system_stats.py` が 60 秒ごとに取得）:

| metric | 説明 |
|--------|------|
| cpu_percent | CPU 使用率 |
| memory_percent | メモリ使用率 |
| disk_percent | ディスク使用率（/） |
| load_1m | ロードアベレージ（1分） |
| cpu_temp | Raspberry Pi の CPU 温度 |

**category = 'collector'**（`collect_with_health` が各ソースの読み取り時に記録）:

| metric | 説明 |
|--------|------|
| collection_success | 成功=1.0, 失敗=0.0 |
| collection_duration_ms | 収集にかかった時間（ミリ秒） |
| readings_count | 取得したデータ件数 |

**collect_with_health の流れ**（`main.py` 95〜149 行目）: 各ソースの `get_readings_fn()` を呼ぶ前後で時間を計測し、成功時は `collection_success=1`、`readings_count`、`duration_ms` を、失敗時は `collection_success=0` を `ops_metrics` に保存。`save_ops_metrics_batch` で一括 INSERT します。このデータが「収集失敗通知」の判定（連続 2 回失敗で通知）に使われます。

**環境変数**: `OPS_METRICS_ENABLED=true`（デフォルト）で有効。`false` にすると ops_metrics の収集・保存をスキップします。

### 8.3 Grafana での SQL 例

Grafana のパネルでは、**Query** 欄に SQL を書きます。`$__timeFrom()` と `$__timeTo()` は、ダッシュボードの時間範囲に応じて Grafana が自動で置き換えます。

**水温の時系列グラフ**:

```sql
SELECT time, value
FROM sensor_readings
WHERE sensor_id LIKE 'ds18b20_%' AND metric = 'temperature'
  AND time >= $__timeFrom() AND time < $__timeTo()
ORDER BY time
```

**この SQL の意味**：`sensor_id LIKE 'ds18b20_%'` で DS18B20 のデータだけに絞り、`metric = 'temperature'` で水温に限定。`ORDER BY time` で時系列順に並べます。Grafana はこの結果を折れ線グラフで表示します。

**各句の役割**：`SELECT time, value` は「どの列を取得するか」。`FROM sensor_readings` は「どのテーブルから」。`WHERE` は「どの行を対象にするか」の条件。`LIKE 'ds18b20_%'` の `%` は「任意の文字列」にマッチするワイルドカードです。`$__timeFrom()` と `$__timeTo()` は、Grafana のダッシュボードで「過去 24 時間」などを選んだとき、その範囲に自動で置き換わります。`ORDER BY time` で時系列順に並べないと、グラフがバラバラになります。

**実践のヒント**：Grafana にログインし、新規パネルを作成して上記の SQL を貼り、**Visualization** で「Time series」を選んでください。データがあればグラフが表示されます。`sensor_id` を `tds_ch1` に変えれば TDS、`tapo_%` にすれば気温・湿度が表示されます。

**気温・湿度（Tapo）**:

```sql
SELECT time, sensor_id, metric, value
FROM sensor_readings
WHERE sensor_id LIKE 'tapo_%' AND metric IN ('temperature', 'humidity')
  AND time >= $__timeFrom() AND time < $__timeTo()
ORDER BY time
```

**照明 ON/OFF**:

```sql
SELECT time, sensor_id, value
FROM sensor_readings
WHERE metric = 'power_state'
  AND time >= $__timeFrom() AND time < $__timeTo()
ORDER BY time
```

`$__timeFrom()`, `$__timeTo()` は Grafana のダッシュボードの時間範囲に自動で置換される。

**本プロジェクトでは**: `db/init/00_schema.sql` がテーブル定義。Grafana の Data Source で PostgreSQL に接続し、上記の SQL をパネルの Query に書く。グラフの種類は「Time series」を選択。

**データの流れの確認**：Grafana でグラフが表示されないときは、(1) collector が動いているか `docker compose ps` で確認、(2) DB にデータが入っているか `docker compose exec db psql -U postgres -d aquapulse -c "SELECT COUNT(*) FROM sensor_readings;"` で確認、(3) Grafana の Data Source 設定（ホスト、DB 名、認証）が正しいか確認、の順で切り分けます。

**学びの確認**：この章を読み終えた時点で、次のことが言えれば理解できています。「sensor_readings は time, sensor_id, metric, value の 4 列（+ source）で、create_hypertable で時系列最適化。Grafana は PostgreSQL に SQL を投げ、sensor_id と metric で絞ってグラフにする。writer.py は %s プレースホルダで SQL インジェクションを防いでいる」。

↑ [目次へ戻る](#目次)

---

## 第9章 通知と運用

**この章が終わると**: 「Tapo の IP が変わった」「センサー収集が失敗した」といった事象が、どの条件でメールや LINE に通知されるかがわかります。状態が `collector_data/` の JSON に保存されることも理解できます。

**この章がないと**: 通知が来たときに「なぜ今？」がわかりません。また、通知を止めたい・変えたいときに、どこをいじればよいかがわかりません。**運用の仕組み**を知ることで、システムを「使う」側の理解が深まります。

**通知設計の考え方**：運用中のシステムでは、**異常を検知して人に知らせる**ことが重要です。しかし、**通知が多すぎる**と「またか」と無視され、**少なすぎる**と見逃します。AquaPulse では、**IP 変更**は「変わったときだけ」、**収集失敗**は「連続 2 回」で通知し、**クールダウン**（1時間以内の重複を避ける）で「通知の嵐」を防いでいます。また、**状態を JSON ファイルに保存**することで、コンテナを再起動しても「前回の IP」「連続失敗回数」を保持し、**過剰な通知**を抑えています。**通知文に「前回から何時間」「過去7日で何回」を含める**ことで、**根本対策**（DHCP 予約など）の判断材料にもなります。

### 9.1 通知の種類

| 種類 | トリガー | 内容 |
|------|----------|------|
| IP 変更 | Tapo の接続 IP が変わった | 何から何に、前回からの経過、頻度、ペース |
| 収集失敗 | 連続 2 回失敗 | 期待値 vs 実際、前回成功からの経過、ヒント |

### 9.2 状態の永続化

- `collector_data/tapo-ip-state.json`: IP 変更履歴
- `collector_data/collector-failure-state.json`: 連続失敗回数、最終通知時刻

**状態 JSON の具体例**：`tapo-ip-state.json` は次のような形です。`last_ip_tapo_sensors` に前回接続成功した H100 の IP、`last_ip_tapo_lighting` に P300 の IP が入ります。`change_history` には直近 50 件の IP 変更履歴が入り、通知文の「過去7日で何回」の計算に使われます。`collector-failure-state.json` には `fail_count_gpio_temp` などの連続失敗回数と、`last_notified_at_gpio_temp` などの最終通知時刻が入ります。コンテナを再起動してもこれらのファイルが残っていれば、**過剰な通知**（例：再起動のたびに「初回」として IP 変更通知が飛ぶ）を防げます。

```json
// tapo-ip-state.json の例
{"last_ip_tapo_sensors": "192.168.3.6", "last_ip_tapo_lighting": "192.168.3.7", "change_history": [...]}
```

### 9.3 メール送信（標準ライブラリのみ）

`notify.py` の `send_email` は、標準ライブラリの `smtplib` と `email.mime` だけでメールを送ります。

```python
# notify.py 84〜101行目
to_addr = os.getenv("NOTIFY_EMAIL", "").strip()
host = os.getenv("SMTP_HOST", "").strip()
# ...
if not all([to_addr, host, user, password]):
    return False   # ← 未設定なら送信しない
try:
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("AquaPulse", user))
    msg["To"] = to_addr
    with smtplib.SMTP(host, port, timeout=10) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.sendmail(user, [to_addr], msg.as_string())   # ← ここで送信
    return True
except Exception:
    return False
```

**ポイント**：`NOTIFY_EMAIL` や `SMTP_HOST` が未設定なら送信しない（`return False`）。Gmail の場合は `SMTP_HOST=smtp.gmail.com`、`SMTP_PORT=587`、**アプリパスワード**を使います。

**メール vs LINE の違い**：`_send_notification` は**メールを優先**し、`NOTIFY_EMAIL` と SMTP が設定されていればメールで送ります。メールが使えない（未設定や送信失敗）場合、`LINE_NOTIFY_TOKEN` が設定されていれば **LINE Notify** で送ります。**メール**は SMTP サーバー経由で届くため、Gmail のアプリパスワードなど設定が必要です。**LINE** は LINE Notify のトークンを取得すれば、HTTP API 1 本で送れます。スマホで LINE を見る習慣がある人には LINE の方が気づきやすい場合があります。両方設定すると、メールが成功した時点で LINE は呼ばれません（重複送信を避けるため）。

### 9.4 IP 変更通知のロジック（notify.py）

IP が変わったときの通知は `notify_ip_change` で行います。tapo_sensors や tapo_lighting が接続成功したあと、この関数を呼びます。

```python
# notify.py 140〜165行目
def notify_ip_change(source: str, new_ip: str, device_name: str = "") -> bool:
    state = _load_state()   # tapo-ip-state.json を読む
    key = f"last_ip_{source}"
    old_ip = state.get(key)

    if old_ip == new_ip:
        return False   # ← 変更なし → 通知しない

    # 履歴に追加し、state を更新して保存
    history = state.get("change_history", [])
    history.append({"source": source, "old_ip": old_ip, "new_ip": new_ip, "at": now_iso})
    state["change_history"] = history[-_HISTORY_MAX:]   # 最大50件に制限
    state[key] = new_ip
    _save_state(state)   # ← collector_data/tapo-ip-state.json に書き込み

    # 本文を構築（前回からの経過、過去7日・30日の変更回数など）
    lines = [f"【{name}】", f"  {old_ip or '(初回)'} → {new_ip}", ...]
    _send_notification(subject, "\n".join(lines))   # ← Email 優先、なければ LINE
    return True
```

**ポイント**：`old_ip == new_ip` なら何もしない。変更があったときだけ履歴を追加し、`_save_state` で JSON に永続化。通知文には「前回からの経過」「過去7日・30日の変更回数」を含め、DHCP の不安定さを判断しやすくしています。

> **💡 ヒント**: Tapo の IP が頻繁に変わる場合は、ルーターで DHCP 予約（固定 IP 割り当て）を設定すると、通知が減り運用が楽になります。

### 9.5 収集失敗通知のロジック

連続 2 回失敗で通知する仕組みは、`check_and_notify_collection_failure` で実装されています。核心部分は次のとおりです。

```python
# notify.py 228〜259行目
key_count = f"fail_count_{source}"
fail_count = state.get(key_count, 0) + 1
state[key_count] = fail_count

# クールダウン中（前回通知から1時間以内）は重複通知しない
if last_notified:
    if (now - t).total_seconds() < _FAILURE_COOLDOWN_SEC:  # 3600秒
        return

if fail_count < _FAILURE_THRESHOLD:   # 2 未満ならまだ通知しない
    return

# ここで通知送信
state[key_notified] = now_iso
_send_notification(subject, body)
```

`collector-failure-state.json` に `fail_count_gpio_temp` などのキーで連続失敗回数を保存。2 回に達し、かつ前回通知から 1 時間以上経っていれば通知します。詳細は第38章（notify.py の仕組み）を参照してください。

**実践のヒント**：通知を試すには、`NOTIFY_EMAIL` と SMTP 設定、または `LINE_NOTIFY_TOKEN` を `.env` に設定します。`collector_data/tapo-ip-state.json` を削除して collector を再起動すると、Tapo 接続成功時に「初回」として IP 変更通知が飛ぶ場合があります（環境による）。

**学びの確認**：この章を読み終えた時点で、次のことが言えれば理解できています。「IP 変更は `tapo-ip-state.json` の `last_ip_*` と比較し、変わったときだけ通知。収集失敗は連続 2 回で通知し、1時間のクールダウンで重複を防ぐ」。

**次に読む**：ここまでで「何がどこで動いているか」の全体像はつかめました。**第21章（main.py 1行ずつ）** と **第22章（gpio_temp.py 1行ずつ）** で、実際のコードを1行ずつ追うと、理解が定着します。読み戻しを減らすため、第21章・第22章を読んでから第10章（次のステップ）に進むことを推奨します。

↑ [目次へ戻る](#目次)

---

## 第10章 学習のための次のステップ

**この章が終わると**: 第 I 部のストーリーを一通り読み終えたあと、**次に何を深掘りするか**の道しるべがわかります。

**この章がないと**: 第1〜9章を読んだあと、「で、次は？」となりがちです。コードを 1 行ずつ理解したい、Python の文法をもっと知りたい、といった**興味に応じた次の一歩**を、この章で案内しています。

### 10.1 おすすめの読み進め方

**推奨順で読んでいる場合**：第21章・第22章・第23章まで読み終えているはずです。以下は、特定のトピックをさらに深掘りしたいときの案内です。

| 興味 | 次に読む章 | 理由 |
|------|------------|------|
| Python の他の構文（lambda, スライス等） | 第24章（その他の Python 構文） | 第17章で触れていない構文 |
| Docker の用語がわからない | 第25章（Docker 完全解説） | イメージ、コンテナ、ボリュームの意味 |
| SQL の `SELECT` や `WHERE` がわからない | 第20章（SQL 完全解説） | 各句の意味を1つずつ |
| 通知の仕組みをもっと知りたい | 第38章（notify.py） | IP 変更・収集失敗の判定ロジック |

### 10.2 やってみる演習

手を動かして理解を深めるための演習です。環境がなくても、コードを読むだけでも挑戦できます。

| 演習 | 内容 | 確認方法 |
|------|------|----------|
| **1. モックで動かす** | `.env` の `SOURCES=mock` にし、`docker compose up -d` で起動 | `docker compose logs -f collector` で 60 秒ごとに `mock_temperature` のログが出る。Grafana でグラフが表示される |
| **2. Grafana に新しいグラフを追加** | 新規パネルを作成し、`SELECT time, value FROM sensor_readings WHERE sensor_id LIKE 'mock_%'` を Query に書く | 「Time series」で折れ線グラフが表示される |
| **3. コードの流れを追う** | `gpio_temp.py` の `get_readings` から `writer.py` の `save_reading` まで、1 件のデータがどう渡るか追う | 第 1 章の「1 本のデータの流れ」を自分の言葉で説明できる |
| **4. トラブルを再現する** | `SOURCES=gpio_temp` のまま 1-Wire センサーを外す（または未接続の状態で起動） | `[gpio_temp] Failed:` のログが出る。2 回連続で失敗すると通知が飛ぶ（通知設定時） |
| **5. 新しいソースを追加する** | `_load_source` に `elif name == "my_source":` を追加し、`get_readings` を返すダミー関数を作る | `SOURCES=my_source` で起動し、ログに期待した出力が出る |

**演習 1 のステップ**：(1) プロジェクトルートで `.env` を開き、`SOURCES=mock` を設定（または `SOURCE=mock`）。(2) `docker compose up -d` で起動。(3) `docker compose ps` で db, grafana, collector が `running` か確認。(4) `docker compose logs -f collector` でログを追い、60 秒ごとに `{"sensor_id": "mock_temperature", ...}` が出るか確認。(5) ブラウザで `http://localhost:3000` を開き、Grafana にログイン（デフォルト admin/admin）。(6) 既存のダッシュボードか新規パネルで、mock のデータがグラフになっているか確認。**期待される結果**：グラフに 24〜26℃ 付近で揺らぐ折れ線が表示される。

**演習 5 のヒント**: `sources/mock.py` を参考に、`get_readings` が `[{"time": ..., "sensor_id": "my_sensor", "metric": "temperature", "value": 25.0}]` のようなリストを返す関数を作ります。`main.py` の `_load_source` に分岐を追加し、`SOURCE_LOADERS` に登録されれば、メインループから自動的に呼ばれます。

### 10.3 参考リンク

- [TimescaleDB ドキュメント](https://docs.timescale.com/)
- [Raspberry Pi GPIO](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)
- [python-kasa](https://github.com/python-kasa/python-kasa)

### 10.4 関連ドキュメント（設計・運用・ハードウェア）

本ガイドは**学習用**です。設計の詳細・運用手順・ハードウェアの試行錯誤は、次のドキュメントにあります。**プロジェクトの全体像と細部を理解する**には、必要に応じてこれらも参照してください。

| 種類 | ドキュメント | 内容 |
|------|--------------|------|
| **設計** | [design/architecture.md](../design/architecture.md) | データ基盤・ML 設計方針 |
| **設計** | [design/collector-sources.md](../design/collector-sources.md) | ソース一覧・環境変数・sensor_id の対応 |
| **設計** | [design/ops-metrics.md](../design/ops-metrics.md) | ops_metrics のメトリクス一覧・Grafana クエリ例 |
| **設計** | [design/metrics.md](../design/metrics.md) | KGI/KPI・評価指標の設計 |
| **ハードウェア** | [hardware/wiring/v2.0.md](../hardware/wiring/v2.0.md) | 最新の配線図・ピン配置 |
| **ハードウェア** | [hardware/improvement-plan.md](../hardware/improvement-plan.md) | ハードウェア改善の計画 |
| **運用** | [operations/recovery-runbook.md](../operations/recovery-runbook.md) | **OS 再インストール後の復旧手順**（重要） |
| **運用** | [operations/daily-log.md](../operations/daily-log.md) | 日次作業記録・トラブル対応 |
| **運用** | [operations/tapo-status-report.md](../operations/tapo-status-report.md) | Tapo 互換性・エラー調査ログ |
| **ディスプレイ** | [display/grafana-kiosk.md](../display/grafana-kiosk.md) | Pi Touch Display に Grafana を全画面表示する手順 |

**復旧手順**（recovery-runbook）は、Raspberry Pi の OS を再インストールしたあと、Docker・containerd を SSD に寄せて AquaPulse を再稼働させる手順です。実際の復旧で成功した方法を記録しています。

↑ [目次へ戻る](#目次)

---

## 第11章 環境変数リファレンス

**この章が終わると**: 本プロジェクトで使う**環境変数**の一覧と意味がわかります。運用時に「どの変数を設定すればよいか」を調べるときに使います。

**この章がないと**: `.env` に何を書けばよいか、`docker-compose.yml` の `environment` が何を渡しているかがわかりません。**設定の一覧**として、必要なときに参照できます。

**環境変数とは**：**環境変数**は、プログラムの**外から渡す設定値**です。コードに直接書くのではなく、OS や Docker が「このプログラムには POSTGRES_PASSWORD=xxx を渡す」と指定します。**なぜこうするか**——パスワードや API キーをコードに書くと、Git にコミットしたときに漏洩します。環境変数なら、**本番と開発で異なる値**を簡単に切り替えられ、**秘密情報をコードから分離**できます。AquaPulse では `.env` に設定を書き、`docker-compose.yml` の `environment` でコンテナに渡しています。

### 11.1 必須（本番運用時）

| 変数 | 説明 | 例 |
|------|------|-----|
| POSTGRES_USER | DB ユーザー | postgres |
| POSTGRES_PASSWORD | DB パスワード | （強力なパスワード） |
| POSTGRES_DB | DB 名 | aquapulse |
| SOURCES | 有効なソース（カンマ区切り） | gpio_temp,gpio_tds,tapo_sensors,tapo_lighting |
| TAPO_USERNAME | Tapo アプリのメールアドレス | user@example.com |
| TAPO_PASSWORD | Tapo アプリのパスワード | （アプリと同じ） |

### 11.2 オプション（Tapo 関連）

| 変数 | 説明 | デフォルト |
|------|------|------------|
| TAPO_HUB_IP | H100 の固定 IP（優先） | - |
| TAPO_LIGHTING_IP | P300 の固定 IP | - |
| TAPO_IP_CANDIDATES | ローラー作戦用 IP リスト（カンマ区切り） | 192.168.3.2〜12 |
| TAPO_BACKEND | python-kasa または tapo | python-kasa |

### 11.3 オプション（収集間隔・運用メトリクス）

| 変数 | 説明 | デフォルト |
|------|------|------------|
| SAMPLE_INTERVAL | Tapo 等のメインループ間隔（秒） | Tapo 使用時 300、それ以外 5 |
| GPIO_TEMP_INTERVAL | 水温取得間隔（秒） | 60 |
| TDS_INTERVAL | TDS 取得間隔（秒） | 60 |
| OPS_METRICS_ENABLED | ops_metrics 収集を有効化（system_stats, collect_with_health） | true |
| SYSTEM_STATS_INTERVAL | システムメトリクス取得間隔（秒） | 60 |

### 11.4 オプション（通知）

| 変数 | 説明 |
|------|------|
| NOTIFY_EMAIL | 通知先メールアドレス |
| SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD | SMTP 設定（Gmail はアプリパスワード） |
| LINE_NOTIFY_TOKEN | LINE Notify トークン（Email 未設定時） |
| NOTIFY_STATE_DIR | 状態ファイルのディレクトリ | /app/data |

### 11.5 オプション（TDS キャリブレーション）

| 変数 | 説明 | デフォルト |
|------|------|------------|
| TDS_SENSOR_ID | sensor_id の上書き（テスト用） | tds_ch1 |
| TDS_K | 電圧→ppm の係数 | 500 |

**環境変数の相互関係の例**：**SOURCES** で有効なソースを指定すると、そのソースが要求する変数が必要になります。例：`SOURCES=gpio_temp,tapo_sensors` なら、gpio_temp は 1-Wire の設定（config.txt）のみ、tapo_sensors は **TAPO_USERNAME** と **TAPO_PASSWORD** が必須です。**TAPO_HUB_IP** を設定すると **TAPO_IP_CANDIDATES** は無視され、その IP だけを試します。**SAMPLE_INTERVAL** は Tapo を含むとき 300 秒、含まないとき 5 秒がデフォルトです。**NOTIFY_EMAIL** と **LINE_NOTIFY_TOKEN** の両方がある場合、メールが優先され、メール送信に成功すれば LINE は呼ばれません。**具体例**：モックだけで試すなら `SOURCES=mock` だけで十分。本番で全センサーを使うなら `SOURCES=gpio_temp,gpio_tds,tapo_sensors,tapo_lighting` に加え、TAPO 認証、TAPO_IP_CANDIDATES（または固定 IP）、必要なら TDS_K を設定します。

↑ [目次へ戻る](#目次)

---

## 第12章 トラブルシューティング

**この章が終わると**: センサーが検出されない、Tapo に接続できない、DB に接続できないといった**よくある事象**に対する、切り分けの手順がわかります。

**この章がないと**: トラブル時に「どこを疑えばいいか」がわからず、手当たり次第に試すことになります。**チェックリスト**として、問題が起きたときに参照できます。

**トラブルシューティングの考え方**：問題が起きたとき、**原因は一つとは限りません**。配線、設定、ソフトウェア、ネットワーク……可能性は複数あります。**切り分け**とは、**「ここは大丈夫」「ここが怪しい」を絞り込んでいく**作業です。AquaPulse では、**データの流れ**（センサー → collector → DB → Grafana）を逆にたどり、「どこまで届いているか」を確認します。ログやエラーメッセージは**手がかり**です。焦らず、**一つずつ仮説を立てて確認**する習慣が、運用の勘所になります。

**切り分けの流れ（例：Grafana にグラフが出ない）**：(1) **collector が動いているか** → `docker compose ps` で `running` か確認。止まっていれば `docker compose logs collector` でエラーを確認。(2) **DB にデータが入っているか** → `docker compose exec db psql -U postgres -d aquapulse -c "SELECT COUNT(*) FROM sensor_readings;"` で件数確認。0 なら collector か DB 接続に問題。(3) **Grafana の Data Source が正しいか** → ホスト名（db または 127.0.0.1）、DB 名 aquapulse、認証情報を確認。(4) **SQL がデータと一致しているか** → `sensor_id LIKE 'ds18b20_%'` で絞っているのに、実際は `mock_temperature` しか入っていない場合、グラフは出ません。`SELECT DISTINCT sensor_id FROM sensor_readings LIMIT 20;` で実際の sensor_id を確認。この順で**上流から下流**に確認すると、原因を早く特定できます。

### 12.1 DS18B20 が検出されない

1. **config.txt の確認**: `dtoverlay=w1-gpio` が追加されているか
2. **再起動**: 設定変更後は再起動が必要
3. **デバイス確認**: `ls /sys/bus/w1/devices/` で `28-*` が表示されるか
4. **配線**: 3.3V, GND, データ（GPIO 4）が正しいか。プルアップ抵抗（4.7kΩ）がモジュール内蔵でない場合は必要

**ログに出る例**: `[gpio_temp] Failed: [Errno 2] No such file or directory: '/sys/bus/w1/devices/28-...'` → デバイスが認識されていない。config.txt と再起動を確認。

### 12.2 MCP3424 / I2C が応答しない

1. **I2C 有効化**: `raspi-config` → Interface Options → I2C → Enable
2. **デバイス確認**: `i2cdetect -y 1` で 0x68 が表示されるか
3. **CH1- の接続**: MCP3424 Pin 2 (CH1-) を GND に接続。浮いていると不安定

**ログに出る例**: `[gpio_tds] Failed: [Errno -121] Remote I/O error` → I2C 通信失敗。配線、アドレス、CH1- の GND 接続を確認。

### 12.3 Tapo に接続できない

1. **認証**: TAPO_USERNAME, TAPO_PASSWORD がアプリと同じか
2. **ネットワーク**: collector は `network_mode: host` でホストと同じネットワーク。Tapo と同一 LAN か
3. **ローラー作戦**: TAPO_IP_CANDIDATES に候補 IP を追加。`test_tapo.py` で診断

**よくあるエラーメッセージと対処**:

| エラー | 原因 | 対処 |
|--------|------|------|
| `Device response did not match our challenge on ip 192.168.x.x` | 認証失敗。メールアドレス・パスワードが誤り | `.env` の TAPO_USERNAME, TAPO_PASSWORD を確認。大文字小文字も区別される。Tapo アプリで同じアカウントでログインできるか確認 |
| `H100 が見つかりませんでした` / `P300 が見つかりませんでした` | 候補 IP のいずれにも接続できなかった | TAPO_IP_CANDIDATES に正しい IP を追加。`test_tapo.py` で手動テスト: `docker compose run --rm --no-deps collector python /app/scripts/test_tapo.py` |
| `TAPO_IP_CANDIDATES` が未設定 | 環境変数が空 | `.env` に `TAPO_IP_CANDIDATES=192.168.3.6,192.168.3.7,192.168.3.8` など候補を追加 |

**⚠️ TAPO_HUB_IP と TAPO_LIGHTING_IP の混同**: H100（温湿度ハブ）と P300（マルチタップ）は別デバイス。両方同じ IP にすると P300 の照明データが取れない。H100 用と P300 用で正しい IP を指定するか、ローラー作戦（両方未設定）で自動検出する。

### 12.4 DB に接続できない

1. **ホスト**: collector が `network_mode: host` の場合、DB_HOST=127.0.0.1 でホスト経由
2. **起動順**: db の healthcheck が通るまで collector は待機。`docker compose logs db` で確認
3. **ポート**: 5432 が他プロセスで使用されていないか

**ログに出る例**: `DB connection failed (attempt 1/6): connection refused. Retrying in 5s...` → db がまだ起動していない、または DB_HOST が誤っている。`docker compose ps` で db が `running` か確認。`network_mode: host` なら DB_HOST=127.0.0.1 でホスト経由の接続になる。

### 12.5 Grafana でグラフが表示されない

1. **collector が動いているか**: `docker compose ps` で collector が `running`
2. **DB にデータがあるか**: `docker compose exec db psql -U postgres -d aquapulse -c "SELECT COUNT(*) FROM sensor_readings;"`
3. **Data Source 設定**: Grafana の Data Source で PostgreSQL のホスト、DB 名、認証が正しいか
4. **sensor_id / metric**: SQL の `WHERE sensor_id LIKE 'ds18b20_%'` が実際のデータと一致するか

**エラー例**: `Failed to load dashboard forbidden` → 匿名アクセス（キオスク）時、ダッシュボードに Viewer ロールのパーミッションが未設定。Grafana の UI でパーミッションを追加するか、API で設定。

### 12.6 診断コマンド一覧

| 確認したいこと | コマンド |
|----------------|----------|
| 全サービス状態 | `docker compose ps` |
| collector のログ | `docker compose logs -f collector` |
| Tapo 診断 | `docker compose run --rm --no-deps collector python /app/scripts/test_tapo.py` |
| 1-Wire デバイス | `ls /sys/bus/w1/devices/` |
| I2C デバイス | `i2cdetect -y 1` |
| DB データ件数 | `docker compose exec db psql -U postgres -d aquapulse -c "SELECT COUNT(*) FROM sensor_readings;"` |
| MCP3424 生電圧（配線確認） | `python3 collector/scripts/read_mcp3424_ch1.py`（要 `sudo modprobe i2c-dev`） |
| TDS 瓶測定 | `python3 collector/scripts/measure_tds_bottle.py`（`--save` で DB に保存） |

↑ [目次へ戻る](#目次)

---

## 第13章 コードの詳細解説（発展）

**この章が終わると**: 「なぜ asyncio.to_thread を使うのか」「遅延 import の意図」など、**設計の背景**が深く理解できます。

**この章がないと**: コードを読んで「なんでこう書いてあるんだろう？」と思ったときに、理由がわかりません。**発展的な理解**として、余力があれば読んでください。

**「発展」とは**：本編では**何をしているか**を説明しました。この章では**なぜそう書くか**——設計の**トレードオフ**や**背景知識**を扱います。プログラミングでは「動けばいい」だけでなく、**保守性**（将来の変更がしやすいか）、**パフォーマンス**（無駄な待ちがないか）、**依存関係**（不要なライブラリを読み込まないか）を考えることがあります。AquaPulse のコードにも、そうした**意図**が込められています。

### 13.1 asyncio.to_thread の使い方（gpio_temp.py）

`gpio_temp.py` は `get_readings()` が `asyncio.run(_get_readings_async())` を呼び、内部で `asyncio.to_thread(_read_temperature_sync, device_path)` を使っています。

```python
# ファイル I/O はブロッキングなので、スレッドプールで実行
temp = await asyncio.to_thread(_read_temperature_sync, device_path)
```

**なぜこうするか**: `open()` や `f.read()` はブロッキング。メインスレッドで実行すると他のタスクを止める。`asyncio.to_thread()` でスレッドプールに投げ、イベントループをブロックしない。

### 13.2 遅延 import の意図

```python
def _load_source(name):
    if name == "tapo_sensors":
        from sources.tapo_sensors import get_readings  # ここで初めて import
        return get_readings
```

**理由**: `SOURCES=mock` のとき、tapo_sensors を import すると python-kasa がロードされ、不要な依存が起動時に読み込まれる。遅延 import で、実際に使うソースのモジュールだけをロードする。

### 13.3 ヘルスメトリクスの設計

`collect_with_health` は成功・失敗どちらでもメトリクスを返します。

- **collection_success**: 1.0 = 成功, 0.0 = 失敗
- **collection_duration_ms**: 収集にかかった時間（デバッグ・パフォーマンス監視用）
- **readings_count**: 取得件数（期待値との比較で通知判定）

Grafana で `collection_success == 0` のアラートを張れば、収集失敗を可視化できます。

### 13.4 状態の永続化（notify.py）

```python
state = {
    "last_ip_tapo_sensors": "192.168.3.5",
    "last_change_at_tapo_sensors": "2026-03-17T10:00:00Z",
    "change_history": [
        {"source": "tapo_sensors", "old_ip": "192.168.3.4", "new_ip": "192.168.3.5", "at": "..."}
    ]
}
```

JSON ファイルで永続化し、コンテナ再起動後も「前回の IP」「変更履歴」を保持。通知文に「前回から何時間」「過去7日で何回」を含めることで、根本対策（DHCP 予約など）の判断材料にします。

↑ [目次へ戻る](#目次)

---

## 第14章 TimescaleDB の Continuous Aggregates（将来の ML 用）

**この章が終わると**: 第3章で述べた「特徴量は DB で生成」の具体例として、**Continuous Aggregates**（1分・5分粒度の事前集約）が理解できます。

**この章がないと**: 将来 ML を追加するとき、「なぜ DB で集約するのか」がわかりません。現状の AquaPulse では未実装ですが、**設計の先**を知っておくと役立ちます。

**時系列データの集約とは**：センサーデータは**秒単位**で溜まっていますが、機械学習や分析では**1分平均**や**5分最大**といった**集約値**を使うことが多いです。**生データをそのまま集約**すると、毎回のクエリで大量の行を集計するため遅くなります。**Continuous Aggregates** は、**バックグラウンドで事前に集約**しておき、クエリ時はその結果を読むだけです。**「生データは保存するが、集約は DB 側で自動計算」**という設計は、時系列 DB の典型的な使い方です。

時系列データを 1 分・5 分粒度で集約するビューを事前計算しておくと、ML の特徴量として使いやすくなります。

```sql
-- 1 分粒度の平均（例）
CREATE MATERIALIZED VIEW sensor_readings_1m
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 minute', time) AS bucket,
    sensor_id,
    metric,
    avg(value) AS value
FROM sensor_readings
GROUP BY bucket, sensor_id, metric;
```

- **time_bucket**: 指定間隔でタイムスタンプを丸める
- **WITH (timescaledb.continuous)**: バックグラウンドで自動更新
- クエリ時は `SELECT * FROM sensor_readings_1m` で高速にアクセス

**なぜ Continuous Aggregates か**：**生データ**（sensor_readings）は 1 分に 1 件程度なので、1 日で約 1,440 件、1 年で約 52 万件になります。**1 分粒度の平均**を毎回 `SELECT time_bucket('1 minute', time), AVG(value) ... GROUP BY ...` で計算すると、1 年分のデータをスキャンすることになり、クエリが遅くなります。**Continuous Aggregates** は、**新しいデータが INSERT されるたびに**（またはバッチで）集約を更新するため、クエリ時はすでに集約済みの**少数の行**を読むだけです。**refresh_interval** で更新頻度を設定できます。**ML での活用**：機械学習では、生の時系列データではなく**特徴量**（1分平均、5分最大、1時間の変動など）を入力にすることが多いです。Continuous Aggregates で事前に集約しておけば、Python の pandas や scikit-learn で `SELECT * FROM sensor_readings_1m WHERE ...` で取得し、そのまま特徴量として使えます。**現状**：AquaPulse ではまだ未実装です。将来、ML や異常検知を追加する際に導入する予定です。

↑ [目次へ戻る](#目次)

---

## 第15章 外から・スマホから読む方法

**この章が終わると**: 本ガイドを**外から・スマホから**どう読めるかがわかります。

**この章がないと**: GitHub に push したあと、どこからアクセスすればよいか迷うかもしれません。**閲覧の方法**として、必要に応じて参照してください。

### 15.1 GitHub / GitLab で Markdown を表示

- このファイルをリポジトリに push すると、GitHub の Web 画面で Markdown がレンダリングされます
- スマホのブラウザでも同様に閲覧可能
- **Private リポジトリ**: ログインすれば同じように閲覧可能

### 15.2 GitHub Pages（Public の場合）

- リポジトリを Public にし、Settings → Pages で有効化
- `docs/` をソースにすると、`https://<user>.github.io/<repo>/learning/aquapulse-dev-guide` でアクセス可能
- **注意**: Private リポジトリでは GitHub Pro が必要

### 15.3 他の選択肢

- **PDF に変換**: `pandoc aquapulse-dev-guide.md -o aquapulse-dev-guide.pdf` で PDF 化し、Google Drive 等にアップロード
- **Obsidian / Notion**: Markdown をインポートして、リンクや目次を活用した閲覧が可能
- **VS Code**: プレビュー機能（Ctrl+Shift+V または Cmd+Shift+V）で Markdown を表示。目次リンクでクリックしてジャンプできる

**Grafana を外から見る方法**：本ガイドとは別に、**Grafana のダッシュボード**を外から見たい場合は、**リバースプロキシ**（nginx や Caddy）や **Tailscale** などの VPN を使います。**ポートを直接公開**するのはセキュリティ上リスクが高いため、**認証**（Basic 認証、OAuth）や **SSH トンネル**（`ssh -L 3000:localhost:3000 user@raspberrypi`）を検討してください。**Tailscale** は、同じアカウントのデバイス間で VPN を張り、`192.168.x.x` のようなプライベート IP で Raspberry Pi にアクセスできます。スマホに Tailscale を入れておけば、外出先から Grafana を閲覧可能です。
- **Notion / Obsidian**: Markdown をインポートしてクラウド同期
- **Gist**: 長文は分割が必要だが、Public Gist なら URL 共有で誰でも閲覧可能

↑ [目次へ戻る](#目次)

---

## 第16章 まとめ

**この章が終わると**: 第 I 部のストーリーを一通り読み終えた達成感と、学んだことの振り返りが得られます。

**この章の役割**: 第 I 部の締めくくりとして、ここまで学んだことを整理し、第 II 部（深掘り用の章）への橋渡しをします。

**学びの振り返り**：ここまでで、**「センサーが物理世界の値をデジタル化し、プログラムがそれを保存・可視化する」**という IoT の基本パターンを、AquaPulse という具体例で追ってきました。技術選定の**理由**、アーキテクチャの**役割分担**、共通フォーマットの**設計意図**、コンテナの**概念**、時系列データの**保存の考え方**、通知の**設計思想**——それぞれに**背景**があり、**なぜそうするか**を理解することで、単なる「コードの説明」ではなく**設計の勘所**が身につきます。

本ガイドでは、AquaPulse プロジェクトの技術スタック、アーキテクチャ、物理センサー接続、**全ファイルの役割**（collector/src, scripts, db/migrations, kiosk, grafana/dashboards）、コードのロジック、ops_metrics、環境変数、トラブルシューティングまでを網羅しました。

開発初心者の方は、まず「データの流れ」を追い、次に `gpio_temp.py` のような短いソースから読むことをお勧めします。Docker と TimescaleDB の基礎が分かれば、全体像の理解が深まります。**設計の詳細**（architecture.md）、**復旧手順**（recovery-runbook.md）、**キオスク設定**（display/grafana-kiosk.md）などは第 10 章の関連ドキュメントから参照してください。

↑ [目次へ戻る](#目次)

---

# 第 II 部 詳細リファレンス

## 第17章 Python 文法リファレンス

**この章で学ぶこと**: `import`、`def`、`for`、`while`、`try/except` など、AquaPulse のコードで使う Python の構文を1つずつ理解する。

第6章でコードの流れを見たとき、`for` や `def` といった**構文**が出てきました。ここでは、それらが**何を意味するか**を、AquaPulse の実例と結びつけながら説明します。**プログラミング言語の文法**は、人間の文法のように「主語・述語」のルールがあり、それを守らないとプログラムは動きません。ただし、**全部を一度に覚える必要はありません**。AquaPulse で実際に使っている構文に絞り、**「この行はこういう意味だ」**がわかれば、コードが読めるようになります。

### A.1 インポート（import）

```python
import datetime
import os
```

- **import**: 他のモジュール（ライブラリ）を読み込む。`datetime` は日付・時刻、`os` は OS 関連（環境変数、パスなど）を扱う。

```python
from db.writer import save_reading, save_ops_metric
```

- **from ... import**: モジュールの一部だけを読み込む。`db.writer` から `save_reading` と `save_ops_metric` を直接使えるようにする。

### A.2 変数と代入（=）

```python
SOURCES_RAW = os.getenv("SOURCES", os.getenv("SOURCE", "mock"))
```

- **=**: 代入。左辺に右辺の値を入れる。**定数**（大文字）は慣例で「変更しない」ことを示す。
- **os.getenv("SOURCES", "mock")**: 環境変数 `SOURCES` の値を取得。なければ第2引数 `"mock"` を返す。

### A.3 リスト内包表記（list comprehension）

```python
SOURCES = [s.strip() for s in SOURCES_RAW.split(",") if s.strip()]
```

- **for s in ...**: `SOURCES_RAW.split(",")` でカンマ区切りに分割した各要素を `s` に代入してループ。
- **s.strip()**: 文字列の前後の空白を削除。
- **if s.strip()**: 空白削除後も中身が残るものだけを残す（空文字を除外）。
- **[...]**: 結果をリストにする。`["gpio_temp", "gpio_tds"]` のような形式。

### A.4 関数定義（def）

```python
def _load_source(name):
    if name == "tapo_sensors":
        from sources.tapo_sensors import get_readings
        return get_readings
```

- **def**: 関数を定義する。`def 関数名(引数):` の形式。
- **name**: 引数。呼び出し時に渡される値。
- **return**: 関数の戻り値を返して終了する。`return get_readings` で、`get_readings` という関数オブジェクトを返す。

**よくある疑問：なぜ `return get_readings` で括弧がないのか**：`get_readings` は**関数オブジェクト**です。`get_readings()` と書くと「関数を呼び出す」意味になり、その戻り値が返されます。`return get_readings` は「関数そのもの」を返すので、呼び出し元で `fn = _load_source("gpio_temp")` としたあと、`fn()` で実際に実行できます。**遅延実行**のパターンです。

### A.5 条件分岐（if / elif / else）

```python
if name == "tapo_sensors":
    ...
elif name == "gpio_temp":
    ...
else:
    raise ValueError(f"Unknown source: {name}")
```

- **if**: 条件が真なら実行。`==` は「等しいか」の比較。
- **elif**: 前の if が偽で、この条件が真なら実行。else if の略。
- **else**: 上のどれにも当てはまらないなら実行。
- **raise ValueError(...)**: 例外を発生させる。`f"..."` は f-string（変数を埋め込む）。

### A.6 辞書（dict）とキーアクセス

```python
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "172.28.0.2"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
}
```

- **{ }**: 辞書（dict）。キーと値のペア。`"host"` がキー、`os.getenv(...)` が値。
- **reading["time"]**: 辞書のキーで値を取得。`reading` の `"time"` キーに対応する値。

### A.7 ループ（for ... in）

```python
for name, get_readings_fn in other_sources.items():
    readings, health = collect_with_health(name, get_readings_fn, conn, ops_conn)
```

- **for ... in**: 反復処理。`other_sources.items()` は `(キー, 値)` のタプルのリスト。`name` にキー、`get_readings_fn` に値が入る。
- **.items()**: 辞書のキーと値のペアを返す。

```python
for r in readings:
    save_reading(conn, r)
```

- **for r in readings**: リスト `readings` の各要素を `r` に代入してループ。

**よくある疑問：`for k, v in d.items()` の `k, v` とは**：`d.items()` は `(キー, 値)` のタプルのリストを返します。`for 変数 in ...` の変数がタプルなら、**アンパック**で `k` にキー、`v` に値が入ります。例：`{"a": 1, "b": 2}.items()` → `[("a", 1), ("b", 2)]`。`for k, v in ...` で `k="a", v=1`、次に `k="b", v=2` とループします。

**例：AquaPulse での for の使い方**：`for r in readings: save_reading(conn, r)` は、`readings` が `[{"time": ..., "sensor_id": "ds18b20_...", ...}, {...}]` のようなリストのとき、各辞書を `r` に代入し、1件ずつ DB に保存します。`readings` が空リスト `[]` なら、ループは一度も実行されません。

### A.8 無限ループ（while True）

```python
while True:
    # 処理
    time.sleep(SAMPLE_INTERVAL)
```

- **while**: 条件が真の間、繰り返す。`True` は常に真なので、**無限ループ**。`break` や `return`、例外で抜ける。
- **time.sleep(秒)**: 指定秒数だけプログラムを停止する。

### A.9 条件付き while

```python
while not stop_event.is_set():
    try:
        readings = get_readings()
    except Exception as e:
        print(f"Failed: {e}")
    stop_event.wait(GPIO_TEMP_INTERVAL)
```

- **not stop_event.is_set()**: `stop_event` が set されていない間、ループ。`not` は否定。
- **stop_event.wait(秒)**: 指定秒数待つか、`set()` が呼ばれるまで待つ。

### A.10 例外処理（try / except）

```python
try:
    readings = get_readings_fn()
    duration_ms = (time.perf_counter() - start_time) * 1000
except Exception as e:
    print(f"[{name}] Failed: {e}")
    return [], health_metrics
```

- **try**: ここで例外が起きる可能性がある処理を書く。
- **except Exception as e**: 例外が発生したらここに入る。`e` に例外オブジェクトが入る。
- **Exception**: ほぼすべての例外の親クラス。`except Exception` で多くのエラーを捕捉できる。

**よくある疑問：なぜ `except Exception` で広く捕捉するのか**：AquaPulse では、センサー読み取りで「ファイルがない」「I2C エラー」「ネットワークタイムアウト」など**様々な例外**が起き得ます。それぞれ `except FileNotFoundError`、`except OSError` と書くと長くなります。`except Exception` で一括捕捉し、`print(f"Failed: {e}")` でログに出すことで、**ループを止めずに次の収集に進む**ことができます。**注意**：本当に捕捉すべきでないエラー（KeyboardInterrupt など）も捕まえてしまうため、重要な処理ではより狭い例外を指定する方がよい場合もあります。

**例：try の外側と内側**：`_gpio_temp_loop` では、外側の `try/finally` で `conn.close()` を保証し、内側の `try/except` で 1 回の収集失敗を処理しています。こうすることで、「1回失敗しても 60 秒後にリトライする」「ループを抜けるときは必ず DB 接続を閉じる」が実現できます。

### A.11 コンテキストマネージャ（with）

```python
with open(device_path, "r") as f:
    content = f.read()
```

- **with**: リソースの取得・解放を自動で行う。`open()` で開いたファイルは、ブロックを抜けると自動で閉じる。
- **as f**: 開いたファイルオブジェクトを `f` という変数に代入。
- **f.read()**: ファイルの内容を全部読み込む。

```python
with conn.cursor() as cur:
    cur.execute("INSERT INTO ...", ...)
```

- **conn.cursor()**: DB のカーソル（カーソルで SQL を実行）。`with` で閉じるのを自動化。

### A.12 辞書内包表記

```python
SOURCE_LOADERS = {name: _load_source(name) for name in SOURCES}
```

- **{ }**: 辞書を作る。`{キー: 値 for 変数 in 反復可能}` の形式。
- 例: `SOURCES = ["gpio_temp", "mock"]` なら → `{"gpio_temp": get_readings関数, "mock": get_readings関数}`

### A.13 三項演算子（条件式）

```python
DEFAULT_INTERVAL = 300 if any(s in SOURCES for s in TAPO_SOURCES) else 5
```

- **A if 条件 else B**: 条件が真なら A、偽なら B を返す。1行で書ける条件分岐。
- **any(...)**: 引数のうち1つでも真なら True。`s in SOURCES` が1つでも True なら 300 秒。

### A.14 タプル（tuple）

```python
cfg = ("水温", 1, "DS18B20 の接続・配線確認")
display_name, expected_min, hint = cfg
```

- **()**: タプル。リストと似ているが変更不可（イミュータブル）。
- **display_name, expected_min, hint = cfg**: アンパック。`cfg` の3要素をそれぞれの変数に代入。

### A.15 ラムダ（lambda）

```python
other_sources = {"mock": SOURCE_LOADERS.get("mock", lambda: [])}
```

- **lambda: []**: 無名関数。引数なしで `[]` を返す。`get("mock", デフォルト値)` で `mock` がなければ `lambda: []` が使われる。

### A.16 スライスとインデックス

```python
history[-_HISTORY_MAX:]
```

- **[-_HISTORY_MAX:]**: リストの末尾から `_HISTORY_MAX` 件を取得。`[-50:]` なら最後の50件。

### A.17 ビット演算

```python
val = ((raw[0] & 0x03) << 16) | (raw[1] << 8) | raw[2]
if val & 0x20000:
    val -= 0x40000
```

- **&**: ビット AND。`raw[0] & 0x03` で下位2ビットだけ取り出す。
- **<<**: 左シフト。`<< 16` で16ビット左にずらす（2^16 倍）。
- **|**: ビット OR。複数の値を1つにまとめる。
- **0x03, 0x20000**: 16進数。`0x` が16進のプレフィックス。

**よくある疑問：リスト内包表記と普通の for の違いは**：`[s.strip() for s in SOURCES_RAW.split(",") if s.strip()]` は、同じことを for で書くと `result = []; for s in SOURCES_RAW.split(","): x = s.strip(); if x: result.append(x)` になります。リスト内包表記は**1行で簡潔**に書け、Python ではよく使われます。**辞書内包表記** `{k: v for k, v in ...}` も同様です。

**よくある疑問：`if s.strip()` の truthy とは**：Python では、空文字 `""` は**偽**、非空文字は**真**として扱われます。`if s.strip()` は「空白を削ったあと、まだ文字が残っていれば」という意味。空行や `"  "` だけの要素を除外できます。

**次に読む**：Python の構文が確認できたら、**第7章（Docker とコンテナ）** に進み、実行環境の仕組みを学びます。

↑ [目次へ戻る](#目次)

---

## 第18章 docker-compose.yml 完全解説

```yaml
services:
```

- **services**: この Compose ファイルで定義するサービス（コンテナ）の一覧。ここから下に各サービスを書く。

---

### db サービス

```yaml
  db:
```

- **db**: サービス名。`docker compose up db` でこのサービスだけ起動できる。

```yaml
    image: timescale/timescaledb:latest-pg14
```

- **image**: 使う Docker イメージ。`リポジトリ名:タグ`。`timescale/timescaledb` の `latest-pg14` タグ（PostgreSQL 14 ベース）。

```yaml
    restart: always
```

- **restart**: コンテナ終了時の再起動ポリシー。`always` は常に再起動（クラッシュ時も）。

```yaml
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      TS_TUNE_MEMORY: 512MB
```

- **environment**: コンテナ内の環境変数。`key: value` の形式。
- **${POSTGRES_USER}**: `.env` ファイルの `POSTGRES_USER` の値に置き換わる。
- **TS_TUNE_MEMORY**: TimescaleDB 用のメモリ設定。512MB を指定。

```yaml
    volumes:
      - ./db_data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d
```

- **volumes**: ホストとコンテナのディレクトリをマウント。`ホストのパス:コンテナのパス`。
- **./db_data:/var/lib/postgresql/data**: DB のデータをホストの `db_data` に保存。コンテナ再作成してもデータは残る。
- **./db/init:/docker-entrypoint-initdb.d**: 初回起動時に `db/init` 内の SQL ファイルが自動実行される。

```yaml
    ports:
      - "5432:5432"
```

- **ports**: ポートの公開。`ホストのポート:コンテナのポート`。ホストの 5432 からコンテナの 5432 に接続できる。

```yaml
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
```

- **healthcheck**: コンテナの健全性チェック。
- **test**: 実行するコマンド。`pg_isready -U postgres` で PostgreSQL の準備ができているか確認。
- **interval**: 5秒ごとにチェック。
- **timeout**: 1回のチェックのタイムアウト 5秒。
- **retries**: 5回連続失敗で unhealthy と判定。

```yaml
    networks:
      aquapulse_net:
```

- **networks**: このサービスを接続するネットワーク。`aquapulse_net` に接続。

---

### grafana サービス

```yaml
  grafana:
    image: grafana/grafana:latest
```

- **grafana/grafana:latest**: Grafana の最新版イメージ。

```yaml
    environment:
      GF_AUTH_ANONYMOUS_ENABLED: "true"
      GF_AUTH_ANONYMOUS_ORG_NAME: "Main Org."
      GF_AUTH_ANONYMOUS_ORG_ROLE: "Viewer"
```

- **GF_AUTH_ANONYMOUS_ENABLED**: 匿名アクセスを有効化。ログインなしで閲覧可能（キオスク用）。
- **GF_AUTH_ANONYMOUS_ORG_ROLE**: 匿名ユーザーの権限。`Viewer` は閲覧のみ。

```yaml
    depends_on:
      db:
        condition: service_healthy
```

- **depends_on**: 起動順序の指定。`db` の後に起動。
- **condition: service_healthy**: `db` の healthcheck が通るまで待つ。

---

### collector サービス

```yaml
  collector:
    image: aquapulse-collector 
    build: ./collector
```

- **image**: ビルド後に付けるイメージ名。
- **build**: ビルドコンテキスト。`./collector` の Dockerfile でイメージをビルドする。

```yaml
    container_name: aquapulse_collector
```

- **container_name**: コンテナ名を固定。指定しないと `プロジェクト名_サービス名_番号` になる。

```yaml
    network_mode: host 
```

- **network_mode: host**: コンテナがホストのネットワークをそのまま使う。Tapo（Wi-Fi）に接続するため必要。`ports` は無効になる。

```yaml
    volumes:
      - /sys/bus/w1/devices:/sys/bus/w1/devices:ro
      - ./collector_data:/app/data
```

- **/sys/bus/w1/devices:...:ro**: 1-Wire デバイス用のホストの `/sys` をマウント。`ro` は読み取り専用。
- **./collector_data:/app/data**: 通知状態の JSON を永続化する。

```yaml
    environment:
      DB_HOST: 127.0.0.1 
      TAPO_IP_CANDIDATES: ${TAPO_IP_CANDIDATES:-}
```

- **DB_HOST: 127.0.0.1**: `network_mode: host` のため、DB はホスト経由で `127.0.0.1` に接続。
- **${TAPO_IP_CANDIDATES:-}**: 未設定なら空文字。`:-` は「未設定時のデフォルト」の意味。

```yaml
      GPIO_TEMP_INTERVAL: ${GPIO_TEMP_INTERVAL:-1}
```

- **:-1**: 未設定なら `1` をデフォルトに。`docker-compose.yml` では `:-` の後に値を書く。

---

### networks セクション

```yaml
networks:
  aquapulse_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/16
```

- **networks**: プロジェクト全体で使うネットワークの定義。
- **driver: bridge**: ブリッジネットワーク。コンテナ同士が通信できる。
- **ipam**: IP アドレス管理。`subnet` で 172.28.0.0/16 を割り当て。

**実践のヒント**：`docker-compose.yml` を編集したあとは `docker compose up -d` で再起動すれば反映されます。**環境変数**（`.env`）を変えただけなら `docker compose restart collector` で collector だけ再起動できます。**volumes** のパスは、`docker compose` を実行する**カレントディレクトリ**からの相対パスです。別のディレクトリから `docker compose -f /path/to/docker-compose.yml up -d` と実行すると、パスがずれることがあるので注意。**depends_on の condition: service_healthy** は、db の `pg_isready` が成功するまで grafana と collector の起動を待つため、「DB に接続できない」エラーを減らします。

↑ [目次へ戻る](#目次)

---

## 第19章 Dockerfile 完全解説

```dockerfile
FROM python:3.11-slim
```

- **FROM**: ベースイメージ。`python:3.11-slim` は Python 3.11 が入った軽量イメージ。
- **slim**: 最小限のパッケージで、イメージサイズを小さくする。

```dockerfile
WORKDIR /app
```

- **WORKDIR**: 作業ディレクトリ。以降の `COPY` や `RUN`、`CMD` はこのディレクトリで実行される。

```dockerfile
COPY requirements.txt .
COPY src/ ./src/
COPY scripts/ ./scripts/
```

- **COPY**: ホストのファイルをコンテナにコピー。`./build` のコンテキスト（Dockerfile の場所）から見た相対パス。
- **requirements.txt .**: `requirements.txt` を `WORKDIR`（`/app`）にコピー。
- **src/ ./src/**: `src` ディレクトリを `/app/src` にコピー。

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

- **RUN**: ビルド時に実行するコマンド。
- **pip install**: Python パッケージをインストール。
- **--no-cache-dir**: キャッシュを使わない（イメージを小さくする）。
- **-r requirements.txt**: `requirements.txt` に書かれたパッケージをすべてインストール。

```dockerfile
CMD ["python", "-u", "src/main.py"]
```

- **CMD**: コンテナ起動時に実行するコマンド。`exec` 形式（JSON 配列）で書く。
- **python**: Python インタプリタを起動。
- **-u**: バッファリング無効。`print()` がすぐにログに出力される。
- **src/main.py**: 実行するスクリプト。

↑ [目次へ戻る](#目次)

---

## 第20章 SQL 完全解説

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

- **CREATE EXTENSION**: PostgreSQL の拡張機能を有効にする。
- **IF NOT EXISTS**: 既に存在する場合はエラーにしない。
- **timescaledb**: 時系列データ用の TimescaleDB 拡張。

```sql
CREATE TABLE sensor_readings (
    time        TIMESTAMPTZ NOT NULL,
    sensor_id   TEXT NOT NULL,
    metric      TEXT NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    source      TEXT
);
```

- **CREATE TABLE**: テーブルを作成。
- **time TIMESTAMPTZ**: タイムスタンプ型（タイムゾーン付き）。UTC で保存。
- **NOT NULL**: この列に NULL を入れられない。
- **TEXT**: 可変長文字列。
- **DOUBLE PRECISION**: 浮動小数点数（64 ビット）。
- **source TEXT**: NULL 許容。`NOT NULL` がないので省略可能。

```sql
SELECT create_hypertable('sensor_readings', 'time');
```

- **SELECT create_hypertable(...)**: TimescaleDB の関数呼び出し。
- **'sensor_readings'**: 対象テーブル名。
- **'time'**: パーティションのキー。`time` 列で時系列データとして管理する。

```sql
CREATE INDEX idx_sensor_readings_sensor_time ON sensor_readings (sensor_id, time DESC);
```

- **CREATE INDEX**: インデックスを作成。検索を高速化。
- **idx_sensor_readings_sensor_time**: インデックス名。
- **ON sensor_readings (sensor_id, time DESC)**: `sensor_id` と `time` の組み合わせでインデックス。`DESC` は降順。

```sql
SELECT time, value
FROM sensor_readings
WHERE sensor_id LIKE 'ds18b20_%' AND metric = 'temperature'
  AND time >= $__timeFrom() AND time < $__timeTo()
ORDER BY time
```

- **SELECT time, value**: 取得する列。
- **FROM sensor_readings**: 対象テーブル。
- **WHERE**: 条件。`sensor_id` が `ds18b20_` で始まり、`metric` が `temperature` の行だけ。
- **LIKE 'ds18b20_%'**: `%` は任意の文字列、`_` は任意の1文字にマッチ。
- **$__timeFrom(), $__timeTo()**: Grafana の変数。ダッシュボードの時間範囲に置換される。
- **ORDER BY time**: `time` の昇順で並べる。

**INSERT の例**（writer.py が実行する形）:

```sql
INSERT INTO sensor_readings (time, sensor_id, metric, value) VALUES ('2026-03-17 10:00:00+00', 'ds18b20_water_28_00001117a4e0', 'temperature', 25.3);
```

- **INSERT INTO テーブル名 (列1, 列2, ...) VALUES (値1, 値2, ...)**: 1行を追加。列の順序と値の順序を一致させる。
- **TIMESTAMPTZ**: `+00` は UTC を表す。タイムゾーン付きで保存される。

**time_bucket で1分粒度に集約**（TimescaleDB の関数）:

```sql
SELECT time_bucket('1 minute', time) AS bucket, sensor_id, AVG(value) AS avg_value
FROM sensor_readings
WHERE sensor_id LIKE 'ds18b20_%' AND metric = 'temperature'
  AND time >= $__timeFrom() AND time < $__timeTo()
GROUP BY bucket, sensor_id
ORDER BY bucket;
```

- **time_bucket('1 minute', time)**: `time` を 1 分単位に丸める。例：10:23:45 → 10:23:00。
- **AVG(value)**: そのバケット内の `value` の平均。
- **GROUP BY bucket, sensor_id**: 同じバケット・同じ sensor_id の行をまとめて集約。

**直近1件を取得**（最新の水温）:

```sql
SELECT time, sensor_id, value
FROM sensor_readings
WHERE sensor_id LIKE 'ds18b20_%' AND metric = 'temperature'
ORDER BY time DESC
LIMIT 1;
```

- **ORDER BY time DESC**: 新しい順に並べる。
- **LIMIT 1**: 先頭の1行だけ返す。

**COUNT で件数確認**（トラブルシューティング用）:

```sql
SELECT sensor_id, COUNT(*) AS cnt
FROM sensor_readings
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY sensor_id
ORDER BY cnt DESC;
```

- **NOW() - INTERVAL '24 hours'**: 24時間前の時刻。
- **COUNT(*)**: 行数。どの sensor_id が何件入っているか確認できる。

↑ [目次へ戻る](#目次)

---

## 第21章 main.py 主要部分の1行ずつ解説

**この章で学ぶこと**: `main.py` の主要な部分を**1行ずつ**理解する。第6章で全体の流れを把握したあと、ここで細部を追う。

**1行ずつ読む意味**：プログラミングの学習では、**「全体像」と「細部」の往復**が重要です。第6章で「メインループはこう動く」と理解したあと、**実際のコード**を 1 行ずつ追うと、「この行がその処理をしているのか」と腹落ちします。また、**変数名**や**コメント**の意図、**例外処理**の入れ方など、**良いコードの書き方**も学べます。焦らず、**1 行ずつ「何をしているか」を自分に説明できるか**を確認しながら読んでください。

### 冒頭（1〜17行目）

```python
import datetime
```
日付・時刻を扱うモジュール。

```python
import os
```
OS 関連（環境変数、パスなど）。

```python
import sys
```
システム関連（`sys.path` など）。

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```
- **__file__**: このスクリプトのパス。
- **os.path.abspath(__file__)**: 絶対パスに変換。
- **os.path.dirname(...)**: ディレクトリ部分を取得。
- **sys.path.insert(0, ...)**: そのディレクトリをモジュール検索パスの先頭に追加。`db` や `sources` を import できるようにする。

```python
SOURCES_RAW = os.getenv("SOURCES", os.getenv("SOURCE", "mock"))
```
環境変数 `SOURCES` を取得。なければ `SOURCE`。なければ `"mock"`。

```python
SOURCES = [s.strip() for s in SOURCES_RAW.split(",") if s.strip()]
```
カンマ区切りをリストにし、各要素の前後の空白を削除。空文字は除外。

### _load_source 関数（20〜40行目）

```python
def _load_source(name):
```
- **def**: 関数定義。
- **_load_source**: 先頭の `_` は「内部用」の慣例。
- **name**: ソース名（例: `"gpio_temp"`）。

```python
    if name == "tapo_sensors":
```
`name` が `"tapo_sensors"` なら次のブロックを実行。

```python
        if os.getenv("TAPO_BACKEND") == "tapo":
            from sources.tapo_sensors_tapo import get_readings
        else:
            from sources.tapo_sensors import get_readings
        return get_readings
```
- **TAPO_BACKEND** が `"tapo"` なら `tapo_sensors_tapo`、そうでなければ `tapo_sensors` を import。
- **return get_readings**: 読み込んだ `get_readings` 関数を返す。

```python
    elif name == "gpio_temp":
        from sources.gpio_temp import get_readings
        return get_readings
```
`gpio_temp` の場合は `gpio_temp` モジュールから `get_readings` を取得して返す。

```python
    else:
        raise ValueError(f"Unknown source: {name}")
```
どの条件にも当てはまらない場合は、`ValueError` を発生させる。

### _gpio_temp_loop 関数（154〜189行目）

```python
def _gpio_temp_loop(stop_event):
```
- **stop_event**: `threading.Event` オブジェクト。`set()` で終了シグナルを送る。

```python
    if "gpio_temp" not in SOURCES:
        return
```
`gpio_temp` が有効でなければ、何もせずに終了。

```python
    conn = connect_db()
```
DB 接続を取得。

```python
    get_readings = SOURCE_LOADERS["gpio_temp"]
```
`gpio_temp` 用の `get_readings` 関数を取得。

```python
    try:
        while not stop_event.is_set():
```
- **try**: 後続の `finally` で確実に `conn.close()` するため。
- **while not stop_event.is_set()**: `stop_event` が set されていない間、ループ。`is_set()` は「イベントが set されているか」を返す。

```python
            try:
                readings = get_readings()
                for r in readings:
                    save_reading(conn, r)
```
- 内側の **try**: 1回の収集で例外が起きてもループを継続するため。
- **readings**: センサーから取得したデータのリスト。
- **for r in readings**: 各要素を `r` に代入してループ。
- **save_reading(conn, r)**: DB に1件ずつ保存。

```python
            except Exception as e:
                print(f"[gpio_temp] Failed: {e}", flush=True)
```
例外が発生したらエラーメッセージを出力。`flush=True` で即座に表示。

```python
            stop_event.wait(GPIO_TEMP_INTERVAL)
```
`GPIO_TEMP_INTERVAL` 秒待つ。その間に `stop_event.set()` されればすぐに抜ける。

```python
    finally:
        conn.close()
```
ループを抜けた後、必ず DB 接続を閉じる。

### メインループ（271〜321行目）

```python
if __name__ == "__main__":
```
- **__name__**: スクリプトが直接実行されたときは `"__main__"`。import されたときはモジュール名。
- 直接実行時だけこのブロックを実行する（import 時には実行しない）。

```python
    other_sources = {k: v for k, v in SOURCE_LOADERS.items() if k not in ("gpio_temp", "gpio_tds")}
```
`gpio_temp` と `gpio_tds` 以外のソースを辞書で取得。これらは別スレッドで動くため。

```python
    if not other_sources:
        other_sources = {"mock": SOURCE_LOADERS.get("mock", lambda: [])}
```
`other_sources` が空なら、`mock` をデフォルトで使う。

```python
    stop_event = threading.Event()
```
終了用のイベントオブジェクトを作成。

```python
    t = threading.Thread(target=_gpio_temp_loop, args=(stop_event,), daemon=True)
```
- **threading.Thread**: 新しいスレッドを作成。
- **target=_gpio_temp_loop**: 実行する関数。
- **args=(stop_event,)**: 引数。タプルなので `,` が必要。
- **daemon=True**: メインスレッドが終了したら、このスレッドも自動で終了する。

```python
    t.start()
```
スレッドを起動。

```python
    try:
        while True:
            all_readings = []
            all_health = []
            
            for name, get_readings_fn in other_sources.items():
```
- **try**: 後続の `finally` でクリーンアップするため。
- **while True**: 無限ループ。
- **all_readings = []**: ループごとに空のリストで初期化。
- **for name, get_readings_fn in other_sources.items()**: 各ソースの名前と関数を取得。

```python
                if OPS_METRICS_ENABLED:
                    readings, health = collect_with_health(name, get_readings_fn, conn, ops_conn)
                    all_readings.extend(readings)
                    all_health.extend(health)
```
- **collect_with_health**: 収集とヘルスメトリクス取得。
- **extend**: リストに別のリストの要素を追加。

```python
            try:
                from notify import check_and_notify_collection_failure
                ...
            except Exception as e:
                print(f"[notify] ... failed: {e}", flush=True)
```
通知処理で例外が起きても、メインループは止めない。

```python
            time.sleep(SAMPLE_INTERVAL)
```
`SAMPLE_INTERVAL` 秒（例: 300秒）待ってから次のループへ。

```python
    except KeyboardInterrupt:
        print("\n--- Stopped by User ---")
```
Ctrl+C で `KeyboardInterrupt` が発生したら、メッセージを表示してループを抜ける。

```python
    finally:
        stop_event.set()
        for name, thread, interval in threads:
            thread.join(timeout=interval + 2)
        conn.close()
```
- **stop_event.set()**: 各スレッドに終了を通知。
- **thread.join(timeout=...)**: スレッドの終了を最大 `interval + 2` 秒待つ。
- **conn.close()**: DB 接続を閉じる。

**次に読む**：main.py の流れがつかめたら、**第22章（gpio_temp.py 1行ずつ）** と **第23章（writer.py 1行ずつ）** で、センサー読み取りと DB 書き込みの実装を追います。その後 **第10章（学習のための次のステップ）** に進みます。

↑ [目次へ戻る](#目次)

---

## 第22章 gpio_temp.py 1行ずつ解説

```python
"""
DS18B20 水温センサー（1-Wire / GPIO）からデータを取得する。
"""
```
- **"""..."""**: ドキュメント文字列（docstring）。モジュールの説明。

```python
import asyncio
import datetime
import glob
import os
from typing import Optional
```
- **asyncio**: 非同期処理用。
- **glob**: ファイル名のパターンマッチ（`glob.glob("28-*/w1_slave")` など）。
- **typing.Optional**: 型ヒント。「None または float」を表す。

```python
def _read_temperature_sync(device_path: str) -> Optional[float]:
```
- **device_path: str**: 型ヒント。`device_path` は文字列。
- **-> Optional[float]**: 戻り値の型。`float` または `None`。

```python
    try:
        with open(device_path, "r") as f:
            content = f.read()
```
- **open(device_path, "r")**: ファイルを読み取りモードで開く。`"r"` は read。
- **f.read()**: ファイル全体を文字列で読み込む。

```python
    except (OSError, IOError):
        return None
```
- **except (A, B)**: 複数の例外をまとめて捕捉。ファイルが存在しない場合など。

```python
    for line in content.strip().split("\n"):
```
- **content.strip()**: 前後の空白・改行を削除。
- **.split("\n")**: 改行で分割してリストにする。1行ずつ `line` に代入。

```python
        if line.strip().endswith("YES") and "crc=" in line:
            pass
```
- **endswith("YES")**: 文字列が "YES" で終わるか。DS18B20 の CRC チェック成功を示す。
- **"crc=" in line**: 行に "crc=" が含まれるか。
- **pass**: 何もしない。条件に合う行はスキップして次へ。

```python
        elif "t=" in line:
            temp_str = line.split("t=")[-1].strip()
            temp_millideg = int(temp_str)
            return round(temp_millideg / 1000.0, 2)
```
- **line.split("t=")[-1]**: "t=" で分割し、最後の要素（温度値の部分）を取得。
- **[-1]**: リストの最後の要素。
- **int(temp_str)**: 文字列を整数に変換。例: "12345" → 12345（ミリ度）。
- **round(..., 2)**: 小数点以下2桁に丸める。

```python
def get_readings():
    return asyncio.run(_get_readings_async())
```
- **asyncio.run()**: 非同期関数を同期的に実行。イベントループを起動して完了まで待つ。

```python
async def _get_readings_async():
```
- **async def**: 非同期関数。`await` で他の非同期処理を待てる。

```python
    pattern = os.path.join(W1_DEVICES_PATH, W1_SLAVE_GLOB)
    device_files = glob.glob(pattern)
```
- **os.path.join()**: パスを結合。例: `/sys/bus/w1/devices` + `28-*/w1_slave`。
- **glob.glob()**: パターンにマッチするファイルのリストを返す。

```python
    for device_path in device_files:
        temp = await asyncio.to_thread(_read_temperature_sync, device_path)
```
- **await**: 非同期処理の完了を待つ。
- **asyncio.to_thread()**: 同期関数を別スレッドで実行。ブロッキング I/O をブロックしない。

```python
            sensor_id = f"ds18b20_water_{device_id}"
```
- **f"..."**: f-string。`{device_id}` を変数の値に置き換える。

↑ [目次へ戻る](#目次)

---

## 第23章 db/writer.py 1行ずつ解説

```python
def save_reading(conn, reading):
```
- **conn**: psycopg2 の接続オブジェクト。
- **reading**: 共通フォーマットの辞書（time, sensor_id, metric, value, source）。

```python
    cols = ["time", "sensor_id", "metric", "value"]
    vals = [reading["time"], reading["sensor_id"], reading["metric"], reading["value"]]
```
- **cols**: INSERT する列名のリスト。
- **vals**: 対応する値のリスト。`reading` のキーで値を取得。

```python
    if "source" in reading and reading["source"]:
        cols.append("source")
        vals.append(reading["source"])
```
- **"source" in reading**: 辞書に "source" キーが存在するか。
- **reading["source"]**: 値が truthy（空でない）か。
- **.append()**: リストの末尾に要素を追加。

```python
    placeholders = ", ".join(["%s"] * len(cols))
```
- **["%s"] * len(cols)**: `["%s", "%s", "%s", "%s"]` のようなリスト。`%s` は psycopg2 のプレースホルダ。
- **", ".join(...)**: カンマ+スペースで連結。`"%s, %s, %s, %s"` になる。

```python
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO sensor_readings ({', '.join(cols)}) VALUES ({placeholders})",
            tuple(vals),
        )
    conn.commit()
```
- **conn.cursor()**: カーソルを取得。SQL 実行に使う。
- **cur.execute(sql, params)**: SQL を実行。`%s` が `tuple(vals)` で置換される。**SQL インジェクション対策**のため、値を直接埋め込まない。
- **conn.commit()**: 変更を確定。INSERT を反映させる。

```python
def save_ops_metric(conn, metric):
    cols = ["time", "host", "category", "metric", "value"]
    vals = [
        metric["time"],
        metric.get("host", "raspi5"),
        metric["category"],
        metric["metric"],
        metric["value"],
    ]
```
- **metric.get("host", "raspi5")**: "host" キーの値を取得。なければ `"raspi5"` をデフォルトに。

```python
    if metric.get("source"):
        cols.append("source")
        vals.append(metric["source"])
```
- **metric.get("source")**: "source" があれば truthy、なければ None（falsy）。オプション列の扱い。

**次に読む**：gpio_temp と writer の 1 行ずつ解説まで読めたら、**第10章（学習のための次のステップ）** に進み、演習や関連ドキュメントを確認します。

↑ [目次へ戻る](#目次)

---

## 第24章 その他の Python 構文まとめ

| 構文 | 意味 | 例 |
|------|------|-----|
| **in** | 含まれるか | `"a" in "abc"` → True |
| **not in** | 含まれないか | `"x" not in "abc"` → True |
| **or** | 論理 OR | `a or b`（a が偽なら b） |
| **and** | 論理 AND | `a and b`（両方真なら b） |
| **is** | 同一オブジェクトか | `x is None` |
| **is not** | 同一でないか | `x is not None` |
| **.get(key, default)** | 辞書の値取得（なければ default） | `d.get("x", 0)` |
| **.items()** | 辞書の (キー, 値) のリスト | `for k, v in d.items()` |
| **.keys()** | 辞書のキーのリスト | `d.keys()` |
| **.values()** | 辞書の値のリスト | `d.values()` |
| **len(x)** | 要素数 | `len([1,2,3])` → 3 |
| **range(n)** | 0 から n-1 の数列 | `range(6)` → 0,1,2,3,4,5 |
| **str(x)** | 文字列に変換 | `str(123)` → "123" |
| **int(x)** | 整数に変換 | `int("42")` → 42 |
| **float(x)** | 浮動小数に変換 | `float("3.14")` → 3.14 |
| **round(x, n)** | 小数点以下 n 桁に丸める | `round(3.14159, 2)` → 3.14 |

**AquaPulse での使用例**：

- **`"gpio_temp" in SOURCES`**：SOURCES が `["gpio_temp", "tapo_sensors"]` のとき True。gpio_temp 用のスレッドを起動するかどうかの判定に使う。
- **`d.get("source", "")`**：`reading` に `source` キーがあればその値、なければ空文字。オプション列を扱うとき、KeyError を避けるために使う。
- **`x is None`**：`x == None` でも動くが、`is` は「同じオブジェクトか」を調べる。None は1つしかないので `is None` が慣例。
- **`any(s in SOURCES for s in TAPO_SOURCES)`**：TAPO_SOURCES のいずれかが SOURCES に含まれていれば True。Tapo を使うかどうかで SAMPLE_INTERVAL のデフォルトを 300 秒にする判定に使う。

**スライスの応用**：`lst[1:4]` は 1 番目〜3 番目（4 は含まない）。`lst[-1]` は最後の要素。`lst[-50:]` は最後の 50 件。notify.py の `history[-_HISTORY_MAX:]` は、履歴を最大 50 件に制限するために使っています。

↑ [目次へ戻る](#目次)

---

## 第25章 Docker 完全解説

**この章で学ぶこと**: イメージ、コンテナ、ボリューム、ネットワークとは何か。Docker の用語と主要コマンドを理解する。

### 25.1 Docker とは何か

**Docker** は、アプリケーションを「コンテナ」という単位でパッケージ化し、どこでも同じように動かすための技術です。

- **従来の問題**: 「手元では動くが、本番サーバーでは動かない」→ OS やライブラリの違い
- **Docker の解決**: アプリとその依存（Python バージョン、ライブラリ、設定）をまとめて「イメージ」にし、それを「コンテナ」として実行。環境の違いを吸収する。

### 25.2 用語集

| 用語 | 意味 |
|------|------|
| **イメージ (Image)** | アプリとその依存を固めたテンプレート。読み取り専用。例: `python:3.11-slim` |
| **コンテナ (Container)** | イメージを実行した実体。1つのイメージから複数コンテナを起動できる |
| **レジストリ (Registry)** | イメージの保管場所。Docker Hub が代表例 |
| **Dockerfile** | イメージをビルドするための手順書。1行ずつ命令を書く |
| **docker-compose.yml** | 複数コンテナの定義と連携をまとめた設定ファイル |
| **ボリューム (Volume)** | コンテナ外にデータを永続化する仕組み。コンテナ削除後も残る |
| **ネットワーク** | コンテナ同士の通信経路。同じネットワークなら名前でアクセス可能 |

### 25.3 イメージとコンテナの関係

```
イメージ (設計図)  →  docker run  →  コンテナ (実行中のインスタンス)
     ↑                                    ↓
  Dockerfile でビルド             docker stop で停止
  docker pull で取得             docker rm で削除
```

### 25.4 主要コマンド一覧

| コマンド | 意味 | 例 |
|----------|------|-----|
| **docker build** | イメージをビルド | `docker build -t myapp ./collector` |
| **docker run** | コンテナを起動 | `docker run -d --name mydb postgres` |
| **docker ps** | 実行中のコンテナ一覧 | `docker ps` |
| **docker ps -a** | 停止中含む全コンテナ | `docker ps -a` |
| **docker stop** | コンテナを停止 | `docker stop mydb` |
| **docker rm** | コンテナを削除 | `docker rm mydb` |
| **docker images** | ローカルのイメージ一覧 | `docker images` |
| **docker logs** | コンテナのログ表示 | `docker logs -f aquapulse_collector` |
| **docker exec** | 実行中のコンテナでコマンド実行 | `docker exec -it db psql -U postgres` |
| **docker compose up** | compose で定義した全サービスを起動 | `docker compose up -d` |
| **docker compose down** | 全サービスを停止・削除 | `docker compose down` |
| **docker compose logs** | 全サービスのログ | `docker compose logs -f` |

### 25.5 オプションの意味

| オプション | 意味 |
|------------|------|
| **-d** | バックグラウンドで実行（デタッチ） |
| **-t** | 疑似 TTY を割り当て（対話用） |
| **-i** | 標準入力を開いたまま（`-it` で対話シェル） |
| **--name** | コンテナ名を指定 |
| **-p ホスト:コンテナ** | ポートをマッピング。例: `-p 5432:5432` |
| **-v ホスト:コンテナ** | ボリュームをマウント。例: `-v ./data:/var/lib/postgresql/data` |
| **-e** | 環境変数を渡す。例: `-e POSTGRES_PASSWORD=secret` |
| **--rm** | 停止時にコンテナを自動削除 |

### 25.6 ネットワークの種類

| 種類 | 説明 |
|------|------|
| **bridge** | デフォルト。同一ホスト内のコンテナ同士が通信可能 |
| **host** | ホストのネットワークをそのまま使用。ポートマッピング不要 |
| **none** | ネットワークなし |

### 25.7 ボリュームの種類

| 種類 | 説明 |
|------|------|
| **バインドマウント** | ホストの特定パスをマウント。`./db_data:/var/lib/postgresql/data` |
| **名前付きボリューム** | Docker が管理する領域。`volumes: db_data` で定義 |
| **tmpfs** | メモリ上に一時領域。再起動で消える |

### 25.8 ライフサイクル

```
docker compose up -d
    ↓
各サービスが起動（db → healthcheck → grafana, collector）
    ↓
depends_on で db の起動完了を待つ
    ↓
docker compose down
    ↓
全コンテナ停止・削除（ボリュームは残る）
```

### 25.9 よくある操作とトラブル

**イメージを再ビルドする**：`collector` のコードを変更したあと、`docker compose up -d --build` でイメージを再ビルドしてから起動します。`--build` がないと古いイメージのままです。

**ログが多すぎるとき**：`docker compose logs -f collector` でリアルタイム表示。`--tail 100` で直近 100 行だけ表示：`docker compose logs --tail 100 collector`。

**コンテナの中に入る**：`docker compose exec collector sh` で collector コンテナ内のシェルに入れます。`ls /sys/bus/w1/devices/` など、コンテナ内のファイルシステムを確認するときに便利です。`exit` で抜けます。

**ボリュームのデータを消す**：`docker compose down -v` で**名前付きボリューム**も削除されます。`./db_data` のようなバインドマウントは、`down` では消えず、手動で `rm -rf db_data` する必要があります。**注意**：DB のデータが消えます。

**ポートが使われている**：`Address already in use` と出たら、他プロセスが 5432 や 3000 を使っています。`ss -tlnp | grep 5432` で確認。既存の PostgreSQL や Grafana を止めるか、`docker-compose.yml` の `ports` を `5433:5432` のように変えて競合を避けます。

### 25.10 AquaPulse 特有の注意点

- **collector は network_mode: host**：bridge ネットワークを使わないため、`DB_HOST=127.0.0.1` でホスト経由で DB に接続します。`db` というコンテナ名では解決できません。
- **1-Wire のマウント**：`/sys/bus/w1/devices` を読み取り専用でマウント。ホストの 1-Wire デバイスがコンテナから見えるようにしています。
- **collector_data**：通知の状態ファイル（tapo-ip-state.json 等）をホストの `./collector_data` に保存。コンテナを再作成しても状態が残ります。

↑ [目次へ戻る](#目次)

---

## 第26章 ライブラリ完全解説

**この章で学ぶこと**: psycopg2、python-kasa、smbus2、psutil の役割と主な使い方。各ライブラリが何をしてくれるかを理解する。

### 26.1 psycopg2（PostgreSQL 接続）

| 用途 | 説明 |
|------|------|
| **PostgreSQL 接続** | Python から PostgreSQL に接続する標準的なライブラリ |
| **psycopg2-binary** | pip で入るビルド済み版。`psycopg2` はソースからビルドが必要 |

**主な使い方**:

```python
import psycopg2

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    dbname="aquapulse",
    user="postgres",
    password="password"
)
cur = conn.cursor()
cur.execute("SELECT 1")
conn.commit()
cur.close()
conn.close()
```

| メソッド | 意味 |
|----------|------|
| **connect()** | DB に接続。失敗時は OperationalError |
| **conn.cursor()** | SQL 実行用のカーソルを取得 |
| **cur.execute(sql, params)** | SQL を実行。`%s` が params で置換（SQL インジェクション対策） |
| **conn.commit()** | 変更を確定。INSERT/UPDATE/DELETE は commit しないと反映されない |
| **conn.rollback()** | 変更を破棄 |
| **conn.close()** | 接続を閉じる |

### 26.2 python-kasa（Tapo デバイス制御）

| 用途 | 説明 |
|------|------|
| **TP-Link / Tapo デバイス** | スマートプラグ、スイッチ、センサーなどを Python から制御 |
| **H100, P300 対応** | 気温・湿度センサー（H100+T310）、電源タップ（P300）を扱える |

**AquaPulse での典型的な流れ**：`Discover.discover_single(ip, username=..., password=...)` で IP を指定して接続。`await dev.update()` でデバイスの状態を取得（**必須**。呼ばないと temperature などが None のまま）。`_is_h100_device(dev)` で H100 かどうか判定し、H100 なら `dev.children` から T310 の temperature, humidity を取得。P300 の場合は `dev.children` の各 child の `is_on` で ON/OFF を取得。**認証失敗**時は `AuthenticationError` や `Device response did not match our challenge` が発生。Tapo アプリと同じメールアドレス・パスワードを使う必要があります。

**主な使い方**:

```python
from kasa import Discover

dev = await Discover.discover_single("192.168.3.5", username="...", password="...")
await dev.update()
# dev.children で子デバイス（T310, P300 の各口）にアクセス
```

| 概念 | 意味 |
|------|------|
| **Discover** | ネットワーク上のデバイスを検出 |
| **discover_single(ip, ...)** | 指定 IP のデバイスに接続 |
| **dev.update()** | デバイスの状態を取得（必須） |
| **dev.children** | 子デバイス（H100 の T310, P300 の各口）のリスト |
| **child.is_on** | 電源の ON/OFF 状態 |
| **child.features** | センサーの各種値（temperature, humidity など） |

### 26.3 tapo（Tapo 公式ライブラリ）

| 用途 | 説明 |
|------|------|
| **Tapo 公式 API** | TP-Link の公式 API で Tapo デバイスを制御 |
| **python-kasa との違い** | 別の実装。InvalidRequest など互換性問題あり。TAPO_BACKEND=tapo で切り替え可能 |

### 26.4 smbus2（I2C 通信）

| 用途 | 説明 |
|------|------|
| **I2C 通信** | Raspberry Pi の I2C バスでデバイスと通信。MCP3424 などの ADC を制御 |
| **純 Python** | システムの smbus がなければ smbus2 を使用。pip でインストール可能 |

**主な使い方**:

```python
import smbus2 as smbus

bus = smbus.SMBus(1)  # I2C バス 1（Raspberry Pi は通常 1）
bus.write_byte(0x68, 0x80)  # アドレス 0x68 に 0x80 を書き込み
raw = bus.read_i2c_block_data(0x68, 0, 4)  # 4 バイト読み取り
bus.close()
```

| メソッド | 意味 |
|----------|------|
| **SMBus(バス番号)** | I2C バスを開く。Raspberry Pi は 1 |
| **write_byte(addr, data)** | 1 バイト書き込み |
| **read_i2c_block_data(addr, cmd, length)** | 指定アドレスから length バイト読み取り |
| **close()** | バスを閉じる。必ず呼ぶ |

**MCP3424 との通信の流れ**：gpio_tds.py では、(1) `write_byte(0x68, 0x80)` で MCP3424 に変換開始を指示（0x80 は 18bit, 1x gain, ワンショット, CH1 の設定）、(2) 変換完了を待つ（約 260ms）、(3) `read_i2c_block_data(0x68, 0, 4)` で 4 バイト読み取り、(4) 4 バイトから 18 ビットの値を組み立て、電圧に変換。**I2C アドレス 0x68** は MCP3424 のデフォルト（Adr0, Adr1 を GND に接続した場合）。**SMBus(1)** の 1 は Raspberry Pi の I2C バスで、ピン 3（SDA）と 5（SCL）に対応。`/dev/i2c-1` が使われます。**権限**：I2C にアクセスするには root または `i2c` グループに所属している必要があります。Docker では `privileged` や `device` のマウントが必要な場合がありますが、AquaPulse の collector は `network_mode: host` でホストのデバイスにアクセスするため、ホストで I2C が有効ならコンテナからも利用可能です。ただし、**gpio_tds は I2C デバイスへの直接アクセス**が必要なため、Raspberry Pi 上で動かす前提です。

### 26.5 psutil（システム情報）

| 用途 | 説明 |
|------|------|
| **CPU・メモリ・ディスク** | プロセスやシステムのリソース使用状況を取得 |
| **クロスプラットフォーム** | 同じ API で Windows / Linux / macOS に対応 |

**主な使い方**:

```python
import psutil

psutil.cpu_percent(interval=1)  # CPU 使用率（1秒間の平均）
psutil.virtual_memory()         # メモリ情報。.percent で使用率
psutil.disk_usage("/")          # ディスク使用量。.percent で使用率
```

| 関数 | 戻り値 |
|------|--------|
| **cpu_percent(interval=1)** | 1 秒間の CPU 使用率（0〜100） |
| **virtual_memory()** | メモリ情報。`.percent`, `.used`, `.total` など |
| **disk_usage(path)** | 指定パスのディスク使用量。`.percent`, `.used`, `.total` |

**AquaPulse での psutil の使い方**：`system_stats.py` では、`cpu_percent(interval=1)` で 1 秒間の CPU 使用率を取得（`interval=1` がないと即座に返り、値が 0 になることがある）。`virtual_memory().percent` でメモリ使用率、`disk_usage("/").percent` でルートディスクの使用率。**Raspberry Pi の CPU 温度**は `/sys/class/thermal/thermal_zone0/temp` を読んで 1000 で割ります（ミリ度で格納されているため）。psutil には CPU 温度の API はないため、ファイルから直接読み取っています。**load_1m**（1 分間のロードアベレージ）は `psutil.getloadavg()[0]` で取得。Linux のみ。`ops_metrics` に `category: system` で保存され、Grafana の `aquapulse-operations.json` で監視できます。

↑ [目次へ戻る](#目次)

---

## 第27章 Python 標準ライブラリ

### K.1 os（OS 関連）

| 関数・変数 | 意味 |
|------------|------|
| **os.getenv(key, default)** | 環境変数の値を取得。なければ default |
| **os.path.join(a, b)** | パスを結合。OS に応じた区切り文字を使う |
| **os.path.dirname(path)** | パスのディレクトリ部分 |
| **os.path.abspath(path)** | 絶対パスに変換 |
| **os.path.exists(path)** | パスが存在するか |
| **os.path.basename(path)** | パスのファイル名部分 |
| **os.getloadavg()** | ロードアベレージ（Linux）。(1分, 5分, 15分) |

### K.2 sys（システム）

| 変数・関数 | 意味 |
|------------|------|
| **sys.path** | モジュール検索パスのリスト |
| **sys.path.insert(0, path)** | パスを検索パスの先頭に追加 |
| **sys.exit(code)** | プログラムを終了。code 0 は正常 |
| **__file__** | 現在のスクリプトのパス |

### K.3 json（JSON 処理）

| 関数 | 意味 |
|------|------|
| **json.dumps(obj)** | オブジェクトを JSON 文字列に変換 |
| **json.loads(s)** | JSON 文字列をオブジェクトに変換 |
| **json.load(f)** | ファイルから JSON を読み込み |
| **ensure_ascii=False** | 日本語をエスケープしない |

### K.4 datetime（日付・時刻）

| クラス・メソッド | 意味 |
|------------------|------|
| **datetime.datetime.now(tz)** | 現在の日時。tz はタイムゾーン |
| **datetime.timezone.utc** | UTC タイムゾーン |
| **datetime.timedelta(days=1)** | 時間差の表現 |
| **.isoformat()** | ISO 8601 形式の文字列（例: `2026-03-17T10:00:00+00:00`） |

### K.5 time（時間）

| 関数 | 意味 |
|------|------|
| **time.sleep(秒)** | 指定秒数だけ停止 |
| **time.perf_counter()** | 高精度の経過時間計測用 |

### K.6 threading（スレッド）

| クラス・メソッド | 意味 |
|------------------|------|
| **threading.Event()** | スレッド間のシグナル用オブジェクト |
| **event.set()** | イベントを設定（終了シグナルなど） |
| **event.is_set()** | 設定されているか |
| **event.wait(秒)** | 設定されるか、指定秒数まで待つ |
| **threading.Thread(target=fn, args=(...), daemon=True)** | スレッドを作成 |
| **thread.start()** | スレッドを起動 |
| **thread.join(timeout=秒)** | スレッドの終了を待つ |

### K.7 asyncio（非同期）

| 関数 | 意味 |
|------|------|
| **asyncio.run(coro)** | 非同期関数を同期的に実行。イベントループを起動 |
| **asyncio.to_thread(fn, *args)** | 同期関数を別スレッドで実行。await 可能 |
| **await** | 非同期処理の完了を待つ |

### K.8 glob（ファイルパターン）

| 関数 | 意味 |
|------|------|
| **glob.glob(pattern)** | パターンにマッチするパスのリスト。例: `28-*/w1_slave` |

### K.9 smtplib・email（メール）

| 用途 | 意味 |
|------|------|
| **smtplib.SMTP(host, port)** | SMTP サーバーに接続 |
| **smtp.starttls()** | TLS 暗号化を開始 |
| **smtp.login(user, pass)** | 認証 |
| **smtp.sendmail(from, to, msg)** | メール送信 |
| **email.mime.text.MIMEText(body, "plain", "utf-8")** | 本文を作成 |

### K.10 urllib（HTTP リクエスト）

| 用途 | 意味 |
|------|------|
| **urllib.request.Request(url, data=..., headers=...)** | HTTP リクエストを構築 |
| **urllib.request.urlopen(req)** | リクエストを送信。LINE Notify などで使用 |

### K.11 pathlib（パス操作）

| クラス・メソッド | 意味 |
|------------------|------|
| **Path(path)** | パスをオブジェクトとして扱う |
| **path.exists()** | 存在するか |
| **path.read_text()** | テキストを読み込み |
| **path.write_text(s)** | テキストを書き込み |
| **path.parent** | 親ディレクトリ |
| **path.mkdir(parents=True, exist_ok=True)** | ディレクトリを作成 |

↑ [目次へ戻る](#目次)

---

## 第28章 YAML 文法

### L.1 基本

| 構文 | 意味 |
|------|------|
| **キー: 値** | キーと値のペア。コロン後にスペース必須 |
| **インデント** | スペースで階層を表現。タブは不可 |
| **-** | リストの要素。ハイフンで始める |
| **"..."** | 文字列。特殊文字を含む場合は引用符で囲む |

### L.2 例

```yaml
# キーと値
name: aquapulse
port: 5432

# リスト
items:
  - a
  - b
  - c

# ネスト
db:
  host: localhost
  port: 5432

# 複数行文字列
description: |
  複数行の
  テキスト
```

### L.3 docker-compose でよく使う構文

| 構文 | 意味 |
|------|------|
| **${VAR}** | 環境変数 VAR の値に置換 |
| **${VAR:-default}** | VAR が未設定なら default |
| **"true"** | 文字列。YAML の true と区別するため引用符 |

↑ [目次へ戻る](#目次)

---

## 第29章 requirements.txt と pip

### M.1 requirements.txt とは

Python パッケージの一覧を書いたファイル。`pip install -r requirements.txt` で一括インストール。

### M.2 記法

| 記法 | 意味 | 例 |
|------|------|-----|
| **パッケージ名** | 最新版をインストール | `psycopg2-binary` |
| **パッケージ名>=バージョン** | 指定バージョン以上 | `psycopg2-binary>=2.9.9` |
| **パッケージ名==バージョン** | 指定バージョン exactly | `psycopg2-binary==2.9.9` |

### M.3 本プロジェクトの requirements.txt

```
psycopg2-binary>=2.9.9   # PostgreSQL 接続
python-kasa>=0.10.0      # Tapo デバイス制御
tapo>=0.8.11             # Tapo 公式 API（別実装）
smbus2>=0.4.0            # I2C 通信
psutil>=5.9.0            # システムメトリクス
```

### M.4 pip コマンド

| コマンド | 意味 |
|----------|------|
| **pip install パッケージ** | パッケージをインストール |
| **pip install -r requirements.txt** | requirements.txt から一括インストール |
| **pip install --no-cache-dir** | キャッシュを使わない（Docker ビルドで軽量化） |
| **pip list** | インストール済みパッケージ一覧 |
| **pip freeze** | 現在の環境を requirements 形式で出力 |

↑ [目次へ戻る](#目次)

---

## 第30章 通信プロトコル（1-Wire, I2C）

### N.1 1-Wire（ワンライン）

| 項目 | 説明 |
|------|------|
| **概要** | 1本のデータ線で通信。電源・GND・データの3本で動作 |
| **代表デバイス** | DS18B20（温度センサー） |
| **アドレス** | 各デバイスに64ビットの一意 ID。例: `28-00001117a4e0` |
| **Linux の扱い** | `dtoverlay=w1-gpio` で有効化。`/sys/bus/w1/devices/28-*/w1_slave` で読み取り |
| **データ形式** | 2行目に `t=12345`（ミリ度）。1000 で割って摂氏に |

### N.2 I2C（アイ・スクエアド・シー）

| 項目 | 説明 |
|------|------|
| **概要** | 2本の線（SDA: データ）と（SCL: クロック）で複数デバイスと通信 |
| **アドレス** | 7ビット。各デバイスに固有。MCP3424 は 0x68 など |
| **Raspberry Pi** | `raspi-config` で I2C を有効化。`/dev/i2c-1` が使える |
| **確認** | `i2cdetect -y 1` で接続デバイスのアドレスを確認 |

### N.3 MCP3424 のレジスタ

| 設定 | 値 | 意味 |
|------|-----|------|
| **18bit** | 0x80 の上位ビット | 分解能 |
| **1x gain** | デフォルト | 入力電圧範囲 |
| **one-shot** | 0x80 | 1回変換して停止 |
| **チャンネル** | CH1=0x80 | チャンネル1で変換 |

**1-Wire と I2C の使い分け**：**1-Wire** は配線が少なく（3本：VDD, GND, データ）、複数の DS18B20 を同じバスに接続できます。ただし通信速度は遅く、長距離ではノイズに弱いです。**I2C** は SDA・SCL の 2 本で複数デバイスと通信でき、アドレスで識別します。MCP3424 のような ADC は I2C で制御するのが一般的です。AquaPulse では、水温は 1-Wire（DS18B20 が 1-Wire 専用）、TDS は I2C（MCP3424 が I2C で電圧を読む）と、**センサーの仕様に合わせて**使い分けています。

**w1_slave の読み方**：`/sys/bus/w1/devices/28-00001117a4e0/w1_slave` を読むと、1行目に CRC チェック、2行目に `t=25123` のような形式で温度（ミリ度）が入ります。`25123` を 1000 で割ると 25.123℃。1行目に `YES` が含まれていれば CRC 成功、`NO` なら再読み取りが必要です。

↑ [目次へ戻る](#目次)

---

## 第31章 Grafana の基礎

### O.1 概要

Grafana は時系列データを可視化するダッシュボードツール。PostgreSQL に接続して SQL でクエリし、グラフを表示する。

### O.2 主要概念

| 概念 | 意味 |
|------|------|
| **DataSource** | データソース（PostgreSQL など）の接続設定 |
| **Dashboard** | 複数のパネルをまとめた画面 |
| **Panel** | 1つのグラフや表示。SQL でデータを取得 |
| **Query** | パネルで実行する SQL |

### O.3 接続設定（PostgreSQL）

```yaml
Host: db:5432  # または 127.0.0.1（network_mode: host のとき）
Database: aquapulse
User: postgres
Password: （設定した値）
SSL Mode: disable  # ローカルなら
```

### O.4 変数

| 変数 | 意味 |
|------|------|
| **$__timeFrom()** | ダッシュボードの時間範囲の開始 |
| **$__timeTo()** | ダッシュボードの時間範囲の終了 |
| **$__interval** | 自動計算された間隔 |

### O.5 キオスクモード

- 匿名アクセスを有効化。ログインなしで閲覧可能
- 7インチタッチディスプレイで常時表示する用途に最適

### O.6 パネルの作成手順（初めての場合）

1. Grafana にログイン（デフォルト admin / admin。初回でパスワード変更を促される）
2. 左メニュー「Dashboards」→「New」→「New Dashboard」
3. 「Add visualization」で新規パネル作成
4. Data source で PostgreSQL を選択
5. Query に SQL を書く（例：`SELECT time, value FROM sensor_readings WHERE sensor_id LIKE 'ds18b20_%' AND metric = 'temperature' AND time >= $__timeFrom() AND time < $__timeTo() ORDER BY time`）
6. Visualization で「Time series」を選択
7. 右上の時間範囲で「Last 24 hours」などを選ぶ
8. 「Apply」で保存

**よくある失敗**：Data source が未設定、またはホスト名・DB 名が誤っていると「Failed to load data」になります。`network_mode: host` の環境では、Grafana がコンテナ内で動く場合、DB への接続先は `host.docker.internal` や `172.17.0.1` になることがあります。AquaPulse では db と grafana が同じ docker-compose ネットワークにいるため、`db:5432` で接続できます。

↑ [目次へ戻る](#目次)

---

## 第32章 ターミナル・シェル・環境変数

### P.1 ターミナルとは

**ターミナル**（端末）は、キーボードでコマンドを入力し、テキストで結果を受け取るインターフェース。GUI の代わりに CUI（Character User Interface）で操作する。

### P.2 シェルとは

**シェル**は、コマンドを解釈して実行するプログラム。Linux では **bash** が標準。

| コマンド | 意味 |
|----------|------|
| **cd パス** | ディレクトリを移動 |
| **ls** | ファイル一覧 |
| **pwd** | 現在のディレクトリを表示 |
| **cat ファイル** | ファイル内容を表示 |
| **echo $VAR** | 環境変数を表示 |
| **export VAR=値** | 環境変数を設定 |

### P.3 環境変数

| 概念 | 説明 |
|------|------|
| **環境変数** | プロセスに渡されるキーと値。子プロセスに継承される |
| **.env ファイル** | プロジェクト用の環境変数。`docker compose` が自動で読み込む |
| **os.getenv("KEY", "default")** | Python で環境変数を取得 |

### P.4 よく使うコマンド（AquaPulse）

| コマンド | 意味 |
|----------|------|
| **docker compose up -d** | バックグラウンドで全サービス起動 |
| **docker compose down** | 全サービス停止・削除 |
| **docker compose logs -f collector** | collector のログを追跡表示 |
| **docker compose ps** | サービスの状態一覧 |
| **ls /sys/bus/w1/devices/** | 1-Wire デバイス一覧 |
| **i2cdetect -y 1** | I2C デバイスのアドレス一覧 |

↑ [目次へ戻る](#目次)

---

## 第33章 Raspberry Pi の基礎

### Q.1 Raspberry Pi とは

シングルボードコンピュータ。Linux が動き、GPIO ピンで電子部品と接続できる。IoT や組み込み向け。

### Q.2 GPIO（General Purpose I/O）

| 項目 | 説明 |
|------|------|
| **GPIO** | 汎用入出力ピン。プログラムで制御可能 |
| **3.3V / 5V** | 電源ピン。センサーは 3.3V が多い |
| **GND** | 接地。回路の基準電位 |
| **BCM / WiringPi** | ピン番号の方式。BCM が一般的 |

### Q.3 config.txt

`/boot/firmware/config.txt`（または `/boot/config.txt`）でハードウェアを有効化。

```ini
dtoverlay=w1-gpio    # 1-Wire 有効化（GPIO 4 がデフォルト）
```

変更後は再起動が必要。

**Raspberry Pi 5 での注意点**：AquaPulse は Raspberry Pi 5 で動作確認済み。Pi 5 では `/boot/firmware/config.txt` が設定ファイルの場所（Pi 4 以前は `/boot/config.txt`）。**I2C** は `raspi-config` → Interface Options → I2C → Enable で有効化。**1-Wire** は `dtoverlay=w1-gpio` を config.txt に追加。gpiopin を指定しない場合、GPIO 4 が使われます。**電源**：Pi 5 は 5V 5A の USB-C 電源が必要。センサーを複数接続する場合、電源不足で不安定になることがあるため、十分な容量の電源アダプタを使います。**熱**：Pi 5 は発熱が大きいため、ヒートシンクやファンがあると安心です。`/sys/class/thermal/thermal_zone0/temp` で CPU 温度を監視できます（system_stats が ops_metrics に記録）。

### Q.4 /sys と /dev

| パス | 意味 |
|------|------|
| **/sys/bus/w1/devices/** | 1-Wire デバイスの情報。`28-*` が DS18B20 |
| **/sys/class/thermal/thermal_zone0/temp** | CPU 温度（ミリ度） |
| **/dev/i2c-1** | I2C バス 1 のデバイスファイル |

↑ [目次へ戻る](#目次)

---

## 第34章 ネットワークの基礎

### R.1 IP アドレス

| 種類 | 説明 |
|------|------|
| **IPv4** | 例: `192.168.3.5`。LAN 内で一意 |
| **127.0.0.1** | ループバック。自分自身を指す |
| **サブネット** | 例: `172.28.0.0/16`。`/16` は上位 16 ビットがネットワーク部 |

### R.2 ポート

| ポート | 用途 |
|--------|------|
| **5432** | PostgreSQL のデフォルト |
| **3000** | Grafana のデフォルト |
| **587** | SMTP（メール送信） |

### R.3 DHCP

動的に IP を割り当てる仕組み。ルーターが担当。Tapo の IP が変わる原因。**DHCP 予約**で固定できる。

↑ [目次へ戻る](#目次)

---

## 第35章 例外・エラーハンドリング

### S.1 例外とは

プログラム実行中に起きた「想定外の事態」。捕捉しないとプログラムが停止する。

### S.2 主な例外クラス

| 例外 | 発生例 |
|------|--------|
| **ValueError** | 不正な値。`int("abc")` |
| **KeyError** | 辞書に存在しないキー参照 |
| **TypeError** | 型の不一致。`"a" + 1` |
| **OSError / IOError** | ファイルが見つからない、読み取り失敗 |
| **Exception** | ほぼすべての例外の親。`except Exception` で広く捕捉 |
| **KeyboardInterrupt** | Ctrl+C で発生 |

### S.3 try / except / finally

```python
try:
    risky_operation()
except ValueError as e:
    print(f"値エラー: {e}")
except Exception as e:
    print(f"その他: {e}")
finally:
    cleanup()  # 成功・失敗どちらでも実行
```

### S.4 raise

```python
raise ValueError("Invalid source")
```
意図的に例外を発生させる。呼び出し元にエラーを伝える。

**AquaPulse での例外の流れ**：`_load_source("unknown")` が呼ばれると `raise ValueError(f"Unknown source: unknown")` でプログラムが止まります。これは**起動時**の設定ミスを早期に検出するためです。一方、`get_readings()` 内でセンサー読み取りに失敗した場合は `except Exception` で捕捉し、ログに出力して**ループを継続**します。**起動時の致命的エラー**と**実行中の一時的な失敗**で、例外の扱いを変えているのがポイントです。**finally** は `conn.close()` のように、成功・失敗どちらでも確実に実行したい処理に使います。`_gpio_temp_loop` では `try/finally` で DB 接続のクローズを保証しています。

↑ [目次へ戻る](#目次)

---

## 第36章 型ヒントと typing

### T.1 型ヒントとは

変数や関数の引数・戻り値に「型」を注釈として書く。実行時には無視されるが、IDE や mypy でチェックできる。

### T.2 基本

```python
def func(x: int, s: str) -> bool:
    return len(s) > x
```

- **x: int** - 引数 x は int
- **-> bool** - 戻り値は bool

### T.3 typing モジュール

| 型 | 意味 |
|------|------|
| **Optional[T]** | T または None |
| **List[T]** | T のリスト |
| **Dict[K, V]** | キー K、値 V の辞書 |
| **Tuple[T1, T2]** | 固定長タプル |

```python
from typing import Optional, List

def get_readings() -> List[dict]:
    ...

def parse(s: str) -> Optional[float]:
    ...
```

↑ [目次へ戻る](#目次)

---

## 第37章 PostgreSQL・TimescaleDB 詳細

### U.1 PostgreSQL とは

オープンソースのリレーショナルデータベース。SQL でデータを管理。AquaPulse では TimescaleDB（PostgreSQL 拡張）を使用。

### U.2 基本用語

| 用語 | 意味 |
|------|------|
| **テーブル** | 行と列で構成されたデータの入れ物 |
| **カラム（列）** | 1つの属性。例: time, sensor_id, value |
| **行（レコード）** | 1件のデータ |
| **スキーマ** | テーブル構造の定義 |
| **インデックス** | 検索を高速化するための索引 |
| **トランザクション** | 複数 SQL をまとめて実行。commit で確定、rollback で破棄 |

### U.3 データ型

| 型 | 意味 |
|------|------|
| **TIMESTAMPTZ** | タイムゾーン付き日時。UTC で保存推奨 |
| **TEXT** | 可変長文字列 |
| **DOUBLE PRECISION** | 64ビット浮動小数 |
| **INTEGER** | 整数 |
| **BOOLEAN** | 真偽値 |

### U.4 TimescaleDB の hypertable

| 概念 | 意味 |
|------|------|
| **hypertable** | 時系列データ用のテーブル。内部で時間でパーティション |
| **create_hypertable('テーブル', '時間列')** | 既存テーブルを hypertable に変換 |
| **メリット** | 大量データでも高速。古いデータの削除・圧縮が容易 |

**hypertable の内部の動き**：`create_hypertable('sensor_readings', 'time')` を実行すると、TimescaleDB は `time` 列の値に基づいて**チャンク**（時間範囲ごとのパーティション）を自動的に作成します。例：1 日分のデータが 1 チャンクに入るように分割。クエリで `WHERE time >= '2026-03-01' AND time < '2026-03-02'` のように指定すると、その範囲のチャンクだけを読み、**フルスキャン**を避けられます。**chunk_time_interval** でチャンクの時間幅を調整できます（デフォルトは 7 日）。AquaPulse では 1 分に 1 件程度なので、デフォルトで十分です。**Continuous Aggregates**（第14章）は、この hypertable を元に 1 分・5 分粒度の集約を事前計算する機能で、将来の ML 用に使う予定です。

### U.5 psql コマンド

```bash
psql -U postgres -d aquapulse
```

| コマンド | 意味 |
|----------|------|
| **\dt** | テーブル一覧 |
| **\d テーブル名** | テーブル構造 |
| **SELECT * FROM sensor_readings LIMIT 10;** | データ取得 |

↑ [目次へ戻る](#目次)

---

## 第38章 notify.py の仕組み

### V.1 役割

- **IP 変更通知**: Tapo の接続 IP が変わったらメール/LINE で通知
- **収集失敗通知**: センサー収集が連続失敗したら通知

### V.2 状態ファイル

| ファイル | 内容 |
|----------|------|
| **tapo-ip-state.json** | 最後の IP、変更履歴、変更時刻 |
| **collector-failure-state.json** | 連続失敗回数、最終通知時刻、最終成功時刻 |

### V.3 通知の流れ（IP 変更）

1. Tapo に接続成功 → 接続した IP を取得
2. 状態ファイルの「前回の IP」と比較
3. 変わっていれば履歴を更新し、メール/LINE 送信
4. 通知文に「前回からの経過」「過去7日・30日の変更回数」を含める

### V.4 通知の流れ（収集失敗）

1. 収集失敗時、連続失敗回数を +1
2. 閾値（2回）に達したら通知
3. クールダウン（1時間）中は重複通知しない
4. 成功したら連続失敗回数を 0 にリセット

### V.5 送信先の優先順位

1. **Email**（NOTIFY_EMAIL, SMTP_* が設定されていれば）
2. **LINE Notify**（Email 未設定で LINE_NOTIFY_TOKEN があれば）

### V.6 通知をテストする方法

**IP 変更通知**：`collector_data/tapo-ip-state.json` を削除（または `last_ip_tapo_sensors` を別の値に変更）して collector を再起動すると、Tapo 接続成功時に「初回」または「IP 変更」として通知が飛ぶ場合があります。**収集失敗通知**：`SOURCES=gpio_temp` のまま 1-Wire センサーを外すか、存在しないデバイスパスを指定すると、2 回連続で失敗した時点で通知されます。**注意**：クールダウン（1時間）中は同じ種類の通知は送られません。`collector-failure-state.json` の `last_notified_at_*` を削除すると、クールダウンをリセットできます（本番では慎重に）。

### V.7 通知文のカスタマイズ

通知の本文は `notify.py` の `notify_ip_change` や `check_and_notify_collection_failure` 内で構築されています。`lines = [f"【{name}】", ...]` の部分を編集すると、通知文の形式を変えられます。例えば、前回からの経過時間や過去7日の変更回数を増減したり、絵文字を追加したりできます。変更後は `docker compose up -d --build collector` でイメージを再ビルドする必要があります。

↑ [目次へ戻る](#目次)

---

## 第39章 tapo_sensors / tapo_lighting の仕組み

### W.1 ローラー作戦

Tapo の IP が DHCP で変わる可能性があるため、複数 IP を順に試す。

```python
ip_list = ["192.168.3.2", "192.168.3.3", ...]  # TAPO_IP_CANDIDATES
for ip in ip_list:
    try:
        dev = await Discover.discover_single(ip, ...)
        await dev.update()
        if _is_h100_device(dev):  # H100 かどうか判定
            break  # 成功
    except:
        continue  # 次を試す
else:
    raise ...  # 全部失敗
```

### W.2 デバイス判定

| 関数 | 判定方法 |
|------|----------|
| **_is_h100_device(dev)** | `dev.children` に T310/T315 が含まれるか |
| **_is_p300_device(dev)** | `dev.children[0]` に `is_on` があるか（電源口） |

### W.3 データ取得（H100）

- **dev.children**: 子デバイス（T310, T315）のリスト
- **child.features**: センサーの値。`temperature`, `humidity` など
- **child.model**: モデル名。`"T310"` を含むかでフィルタ

### W.4 データ取得（P300）

- **dev.children**: 各電源口
- **child.is_on**: True=ON, False=OFF
- **value**: 1.0（ON）または 0.0（OFF）で DB に保存

### W.5 エラー時の挙動

**接続失敗**：`Discover.discover_single` が例外を投げる。タイムアウト、認証失敗、デバイスが応答しないなど。ローラー作戦では次の IP を試し、全部失敗すると `H100 が見つかりませんでした` のようなエラーで終了。**デバイス種別の誤判定**：`_is_h100_device` は `dev.children` に T310/T315 が含まれるかで判定。P300 を H100 として誤認識すると、`child.features` に temperature がなくエラーになる可能性があります。**TAPO_BACKEND=tapo** のときは `tapo_sensors_tapo.py` が使われ、python-kasa とは別の API で接続します。互換性の問題がある場合は [tapo-status-report.md](../operations/tapo-status-report.md) を参照してください。

↑ [目次へ戻る](#目次)

---

## 第40章 Git の基礎

### X.1 Git とは

バージョン管理システム。ファイルの変更履歴を記録し、過去の状態に戻したり、ブランチで並行開発したりできる。

### X.2 基本用語

| 用語 | 意味 |
|------|------|
| **リポジトリ** | プロジェクトの履歴を格納する場所 |
| **コミット** | 変更を1つの単位として記録 |
| **ブランチ** | 並行して開発するための分岐。main が標準 |
| **リモート** |  GitHub など外部のリポジトリ |
| **push** | ローカルの変更をリモートに送る |
| **pull** | リモートの変更をローカルに取り込む |

### X.3 主要コマンド

| コマンド | 意味 |
|----------|------|
| **git status** | 変更状況を表示 |
| **git add ファイル** | ステージング（コミット対象に追加） |
| **git commit -m "メッセージ"** | コミットを作成 |
| **git push origin main** | main ブランチをリモートに push |
| **git pull** | リモートの変更を取得 |
| **git log** | コミット履歴を表示 |

### X.4 .gitignore

Git で追跡しないファイルを指定。`.env`（機密情報）や `db_data/`（大量データ）を除外する。

### X.5 AquaPulse で .gitignore に含めるべきもの

| パターン | 理由 |
|---------|------|
| **.env** | パスワード、API キー、メールアドレスが含まれる |
| **db_data/** | PostgreSQL のデータディレクトリ。バイナリで大きく、環境ごとに異なる |
| **collector_data/** | 通知状態の JSON。本番と開発で異なる。任意 |
| **grafana_data/** | Grafana の内部データ。ダッシュボードは `grafana/dashboards/` に JSON で管理するなら含めてもよい |
| **__pycache__/** | Python のバイトコードキャッシュ。自動生成 |
| **.venv/** | 仮想環境。ローカルで作成するため |

**初回セットアップ**：`git clone` したあと、`.env.example` をコピーして `.env` を作成し、必要な値を編集します。`.env.example` は Git に含め、実際の値はプレースホルダ（`your_password` など）にしておきます。

↑ [目次へ戻る](#目次)

---

---

## 第41章 クラスとオブジェクト

**この章で学ぶこと**: Python の「クラス」と「オブジェクト」とは何か。オブジェクト指向の基礎を理解する。

### 41.1 オブジェクトとは

**オブジェクト**は、データ（属性）と振る舞い（メソッド）をまとめたもの。Python では「ほぼすべてがオブジェクト」。数値、文字列、リスト、辞書もオブジェクト。

```python
s = "hello"
s.upper()   # メソッド呼び出し。オブジェクトに紐づいた関数
```

### 41.2 クラスとは

**クラス**はオブジェクトの設計図。同じ構造のオブジェクトを量産するための型定義。

```python
class Sensor:
    def __init__(self, name):
        self.name = name  # 属性
    def read(self):
        return 25.0      # メソッド

s = Sensor("水温")
s.read()  # 25.0
```

### 41.3 本プロジェクトでの使用

AquaPulse ではクラスをほとんど使っていない。関数と辞書で十分。python-kasa の `dev`、`child` はライブラリが提供するオブジェクト。

**なぜクラスを使わないのか**：AquaPulse の collector は**データの流れ**が単純で、センサーごとに `get_readings()` という関数を返し、共通フォーマットの辞書のリストを返すだけで済みます。**状態**（例：前回の IP）は `notify.py` で JSON ファイルに保存しており、クラスのインスタンス変数として持つ必要がありません。**関数と辞書**の組み合わせで十分表現できるため、クラスを導入するとかえって複雑になります。**python-kasa のオブジェクト**（`dev`、`child`）は、ライブラリが Tapo の API を抽象化したもので、`dev.children`、`child.temperature` のように属性でアクセスします。自分でクラスを書かなくても、こうしたオブジェクトを**使う**側では、属性とメソッドの概念が役に立ちます。

↑ [目次へ戻る](#目次)

---

## 第42章 文字列・リスト・辞書の詳細

**この章で学ぶこと**: Python の基本データ型の使い方を深く理解する。

### 42.1 文字列（str）

| メソッド | 意味 | 例 |
|----------|------|-----|
| **.strip()** | 前後の空白を削除 | `"  a  ".strip()` → `"a"` |
| **.split(区切り)** | 区切りで分割してリストに | `"a,b,c".split(",")` → `["a","b","c"]` |
| **.join(リスト)** | リストを連結して文字列に | `",".join(["a","b"])` → `"a,b"` |
| **.format()** | プレースホルダに値を埋める | `"{}度".format(25)` → `"25度"` |
| **f"..."** | 変数を直接埋め込む（f-string） | `f"{temp}度"` |

### 42.2 リスト（list）

| 操作 | 例 |
|------|-----|
| **追加** | `lst.append(x)` |
| **結合** | `lst.extend(other)` または `lst + other` |
| **長さ** | `len(lst)` |
| **スライス** | `lst[1:3]`（1番目〜2番目）、`lst[-1]`（最後） |

### 42.3 辞書（dict）

| 操作 | 例 |
|------|-----|
| **取得** | `d["key"]`（なければ KeyError）、`d.get("key", デフォルト)` |
| **存在確認** | `"key" in d` |
| **キー・値** | `d.keys()`、`d.values()`、`d.items()` |

**AquaPulse での辞書の典型パターン**：共通フォーマットの `reading` は `{"time": ..., "sensor_id": ..., "metric": ..., "value": ...}` の形。`reading["time"]` で取得します。**オプションのキー**（`source`）は `if "source" in reading and reading["source"]` で存在チェックしてから使うか、`reading.get("source", "")` でデフォルト値を指定します。`d["key"]` はキーがなければ **KeyError** になるため、存在が不明なときは `.get()` を使うのが安全です。**リストの結合**：`all_readings.extend(readings)` で、`readings` の要素を `all_readings` に追加。`all_readings + readings` は新しいリストを返し、元は変更しません。**f-string**：`f"[{name}] Failed: {e}"` は変数を文字列に埋め込む。`{e}` は `str(e)` が自動で呼ばれ、例外メッセージが表示されます。

↑ [目次へ戻る](#目次)

---

## 第43章 同期と非同期の違い

**この章で学ぶこと**: 「同期」と「非同期」の違い。なぜ Tapo で asyncio を使うのかを理解する。

### 43.1 同期処理（ブロッキング）

処理が終わるまで次の行に進まない。ファイル読み取り、DB 接続、ネットワーク通信は「待ち」が発生する。

```python
content = f.read()  # 読み終わるまでここで止まる
```

### 43.2 非同期処理（ノンブロッキング）

待ち時間の間に別の処理を実行できる。ネットワーク I/O が複数ある場合に有効。

```python
async def fetch():
    await asyncio.sleep(1)  # 待ちの間、他のタスクを実行可能
```

### 43.3 本プロジェクトでの使い分け

- **gpio_temp**: ファイル I/O はブロッキングだが、`asyncio.to_thread` で別スレッドに逃がす
- **tapo_sensors**: ネットワーク I/O が主。`async/await` で効率的に待つ

**なぜ gpio_temp は asyncio.to_thread を使うのか**：`open()` や `f.read()` は**ブロッキング**です。メインスレッドで実行すると、その間他の処理が止まります。`asyncio.to_thread(_read_temperature_sync, device_path)` は、**スレッドプール**でブロッキング処理を実行し、メインのイベントループを止めません。複数の DS18B20 がある場合、`asyncio.gather` で並列に読み取れるため、全体の待ち時間が短くなります。**tapo_sensors** は最初から `async` で書かれているため、`await Discover.discover_single(...)` の待ち時間のあいだ、イベントループは他のタスクを実行できます。

**よくある疑問：async と threading の違いは**：**threading** は OS のスレッドを複数使い、**並行**に実行します。**async** は 1 つのスレッドで、待ち時間のあいだに別のタスクに切り替える**協調的マルチタスク**です。I/O 待ちが多い処理（ネットワーク、ファイル）では async の方が効率的で、Python では `asyncio` が標準です。AquaPulse では gpio_temp がファイル I/O（ブロッキング）のため `to_thread` で逃がし、tapo がネットワーク（非同期対応）のため `async/await` を直接使っています。

↑ [目次へ戻る](#目次)

---

## 第44章 セキュリティと運用の基本

**この章で学ぶこと**: パスワードや API キーを安全に扱う方法、運用の基本を理解する。

### 44.1 .env を Git に含めない理由

- **.env** にはパスワード、API キー、メールアドレスなど**機密情報**が含まれる
- Git に push すると**履歴に残り、取り消しが困難**
- リポジトリが Public なら**全世界に漏洩**する
- **.gitignore** に `.env` を追加し、絶対にコミットしない

> **⚠️ 警告**: `.env` を誤ってコミットしてしまった場合、`git rm --cached .env` で追跡から外しても、**履歴には残ります**。すでに push した場合は、パスワードを変更することを強く推奨します。

### 44.2 環境変数で渡す理由

- コードにパスワードを書かない
- 本番・開発で異なる値を簡単に切り替えられる
- Docker の `environment` でコンテナに渡す

### 44.3 バックアップの考え方

- **db_data/**: TimescaleDB のデータ。定期的にバックアップを取る
- **grafana_data/**: ダッシュボード設定。同様にバックアップ推奨

**バックアップの具体例**：`pg_dump` で DB をダンプする場合、`docker compose exec db pg_dump -U postgres aquapulse > backup_$(date +%Y%m%d).sql` で SQL 形式のバックアップが取れます。復元は `docker compose exec -T db psql -U postgres aquapulse < backup_20260317.sql`。**grafana/dashboards/** に JSON を置いている場合は、そのディレクトリを Git で管理するか、定期的にコピーしておくと、ダッシュボードの再作成が楽になります。**collector_data/** の tapo-ip-state.json や collector-failure-state.json は、削除すると「初回」として通知が飛ぶ可能性がありますが、データの整合性には影響しません。必要ならバックアップしておくと、IP 変更履歴を残せます。

### 44.4 運用時のチェックリスト

| 確認項目 | 頻度 | コマンド・方法 |
|----------|------|----------------|
| 全サービス稼働 | 日次 | `docker compose ps` で db, grafana, collector が running |
| ディスク容量 | 週次 | `df -h` で db_data の増加を確認。長期運用ではパーティションの肥大化に注意 |
| ログの異常 | 日次 | `docker compose logs --tail 50 collector` で Failed や Error がないか |
| Grafana 表示 | 日次 | ダッシュボードでグラフが更新されているか |
| 通知の動作 | 月次 | テストで IP 変更や収集失敗を意図的に発生させ、通知が届くか確認 |

↑ [目次へ戻る](#目次)

---

## 用語集（Glossary）

本ガイドで使う用語を一覧にしました。初出時に説明していますが、忘れたときにここで引けます。

| 用語 | 意味 |
|------|------|
| **3.3V** | Raspberry Pi が供給する電源電圧。多くのセンサー（DS18B20, MCP3424）の動作電圧。5V ピンはセンサーによっては危険。 |
| **GND（グラウンド）** | 電圧の基準点（0V）。電気の流れの「行き先」。 |
| **プルアップ** | データ線を抵抗で 3.3V に引き上げ、浮いた状態を防ぐ。1-Wire では 4.7kΩ が一般的。 |
| **1-Wire** | 1本のデータ線で通信するプロトコル。DS18B20 が使用。`/sys/bus/w1/devices/` で読み取り。 |
| **I2C** | 2本（SDA, SCL）で複数デバイスと通信。アドレスで識別。MCP3424 が使用。 |
| **hypertable** | TimescaleDB の時系列テーブル。`time` 列でパーティションし、検索を高速化。 |
| **create_hypertable** | 既存テーブルを hypertable に変換する TimescaleDB の関数。 |
| **sensor_id** | センサーの識別子。例: `ds18b20_water_28_00001117a4e0`。 |
| **metric** | 測定項目。`temperature`, `humidity`, `tds`, `power_state` など。 |
| **共通フォーマット** | 全ソースが返す辞書の形。`time`, `sensor_id`, `metric`, `value`（+ `source`）で統一。 |
| **イメージ** | Docker のテンプレート。`docker build` で作成。 |
| **コンテナ** | イメージから起動した実行環境。`docker compose up` で起動。 |
| **ボリューム** | コンテナ外にデータを永続化する仕組み。`./db_data:/var/lib/postgresql/data` など。 |
| **network_mode: host** | コンテナがホストのネットワークをそのまま使う設定。Tapo 接続に必要。 |
| **SQL インジェクション** | 悪意ある入力を SQL に埋め込む攻撃。`%s` プレースホルダで対策。 |
| **ops_metrics** | システム監視・収集ヘルス用テーブル。sensor_readings とは別。CPU、メモリ、collection_success 等。 |
| **collect_with_health** | main.py の関数。各ソースの読み取りを実行し、成功/失敗・件数・処理時間を ops_metrics に記録。 |
| **マイグレーション** | 既存 DB のスキーマを後から変更する SQL。`db/migrations/` に格納。新規インストール時は `db/init` が実行されるため不要。 |
| **BCM GPIO** | Raspberry Pi のプログラムで参照するピン番号。物理ピン番号とは異なる。例：物理ピン 7 = BCM GPIO 4。 |
| **LSB** | Least Significant Bit。ADC の最小単位。MCP3424 の 18bit では LSB = 2.048V / 262144。 |
| **Continuous Aggregates** | TimescaleDB の機能。時系列データを事前に集約（1分平均など）して保存し、クエリを高速化。 |
| **クールダウン** | 通知の重複を防ぐため、前回通知から一定時間（1時間）は同じ種類の通知を送らない仕組み。 |

↑ [目次へ戻る](#目次)

---

*本ガイドは AquaPulse プロジェクトの実装に基づいて作成しました。*
