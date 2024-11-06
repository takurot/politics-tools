# DietTrendVisualizer

DietTrendVisualizer は、国会会議録 API と OpenAI API を使用して、指定した年の国会議事録データから主要な政策トピックを抽出し、可視化する Python スクリプトです。抽出したトピックは、マークダウン形式で保存され、トピックの出現頻度を視覚化したグラフも表示されます。

## 機能

- **国会会議録 API** を利用して指定年の国会議事録を取得
- 各発言の内容に基づいて **OpenAI API** を使用して主要な政策トピックを抽出
- 抽出したトピックをマークダウンファイル (`diet_topics_summary.md`) に保存
- トピックの出現頻度をグラフで表示

## セットアップ

### 必要条件

- Python 3.x
- 以下の Python ライブラリをインストール
  ```bash
  pip install requests matplotlib openai
  ```

### 環境変数の設定

OpenAI API キーを環境変数 `OPENAI_API_KEY` に設定してください。

#### 例 (Linux/Mac)

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

#### 例 (Windows)

```bash
set OPENAI_API_KEY='your_openai_api_key'
```

## 使い方

1. リポジトリをクローンまたはスクリプトをダウンロードします。

2. ターミナルまたはコマンドプロンプトで次のコマンドを実行して、指定年の国会議事録トピックを抽出し、可視化します。

   ```bash
   python diet_trend_visualizer.py
   ```

3. 実行例として `main(2024)` がデフォルトで設定されているため、2024 年のトピック抽出が行われます。別の年を指定したい場合は、`main(year)` 内の引数を変更してください。

## 出力結果

### マークダウンファイル (`diet_topics_summary.md`)

実行後、`diet_topics_summary.md` ファイルが生成され、抽出されたトピックと発言内容が以下のように記録されます。

```markdown
# 2024 年の国会議事録 トピック要約

### 発言内容

...（発言内容のテキスト）...

**抽出されたトピック**: 教育、経済、環境

### 発言内容

...（発言内容のテキスト）...

**抽出されたトピック**: 福祉、医療改革、インフラ
```

### トレンドグラフ

スクリプト実行時、主要トピックの出現頻度を示すグラフが表示されます。これは`matplotlib`を使用して生成され、政策トピックの重要度や関心度を視覚的に把握できます。

## 注意点

- 国会会議録 API のリクエスト制限に留意し、リクエスト間に待機を設けていますが、大量データの取得には時間がかかる場合があります。
- OpenAI API の利用には API キーが必要で、リクエスト回数に応じた料金が発生します。

## ライセンス

DietTrendVisualizer は MIT ライセンスのもとで提供されています。