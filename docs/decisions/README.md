# 意思決定記録（Architecture Decision Records）

このディレクトリには、AquaPulseプロジェクトの重要な技術的・アーキテクチャ的決定を記録します。

## なぜADRを書くのか

- **プロジェクト固有のコンテキストを保存**: ネット検索では分からない「なぜこの選択をしたのか」を記録
- **同じ議論の繰り返しを防ぐ**: 「なぜこうなっているのか」を毎回説明する必要がない
- **新しいAIセッションへのオンボーディング**: コンテキスト喪失を防ぐ
- **意思決定の振り返り**: 「あの判断は正しかったか」を検証

## ADRを書くタイミング

以下の条件を満たす決定に対してADRを作成:

- **取り戻すのが難しい決定**: アーキテクチャの変更、技術スタックの選択
- **複数の選択肢を検討した決定**: トレードオフが明確
- **将来の決定に影響する決定**: 他の選択肢を制約する
- **なぜそうしたのか説明が必要な決定**: 一見奇妙に見える選択

**書かなくていい決定**: 
- 1スプリントで取り戻せる選択
- 明らかな選択（例: JSONライブラリの選択）
- 個人的な好み

## アクティブな決定

- [ADR-0002](2026-07-05-archive-directory-structure.md): アーカイブディレクトリ構造（承認済み）
- [ADR-0001](2026-07-05-migrate-to-esp32-gcp.md): Raspberry PiからESP32+GCPへの移行（承認済み）

## 置き換え済み

なし

## 書き方

1. [template.md](template.md)をコピー
2. ファイル名: `YYYY-MM-DD-title.md`
3. 5-10分で書く（これ以上なら詳細すぎる）
4. このREADMEに追加

## ステータスの意味

- **提案中**: 議論中、まだ決定していない
- **承認済み**: 採用された決定
- **廃止**: もう使わない決定（理由を記録）
- **置き換え済み**: 新しいADRに置き換えられた（リンクを記載）

## 参考資料

- [MADR（Markdown Any Decision Records）](https://adr.github.io/madr/)
- [Architecture Decision Records - ThoughtWorks](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
