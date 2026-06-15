# 学校Webサイト Chatbot システム (完全版)

近畿大学工業高等専門学校のWebサイトをスクレイピングし、Ollamaを使用したローカルLLMで質問に回答するchatbotシステムです。

## ✨ 主な機能

### 🔥 高度なクローラー（NEW!）
- ✅ **URL正規化** - 重複URLを自動検出・排除
- ✅ **コンテンツハッシュ管理** - 変更検知による増分更新
- ✅ **優先度付きクロール** - 重要なページを優先的に収集
- ✅ **インテリジェントなノイズ除去** - メインコンテンツのみ抽出
- ✅ **詳細な統計** - 新規/更新/未変更の分類

### 🧠 洗練されたベクトルDB（NEW!）
- ✅ **スマートチャンク分割** - 段落・見出し構造を保持
- ✅ **重複チャンク排除** - ハッシュベースの重複検出
- ✅ **リッチなメタデータ** - タイトル・説明・キーワード保存
- ✅ **増分更新** - 既存データに追加のみ
- ✅ **高度な検索** - フィルター・関連度スコア付き

### コア機能
- ✅ **自動Webスクレイピング** - 学校サイトから情報を自動収集
- ✅ **手動情報追加** - スクレイピングできない情報を手動で追加可能
- ✅ **PDF処理** - PDFファイルからテキストを抽出
- ✅ **ローカルLLM** - Ollamaで完全ローカル環境で動作
- ✅ **ベクトル検索** - ChromaDBによる効率的な情報検索

### インターフェース
- ✅ **Streamlit Chatbot** - ユーザーフレンドリーなチャット画面
- ✅ **REST API** - 他のサイトから利用可能なAPI
- ✅ **管理ダッシュボード** - クローラーとDBの状況を監視

### 自動化
- ✅ **定期実行スケジューラー** - 自動的に定期実行

## 🚀 クイックスタート

### 1. Ollamaのインストール

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
https://ollama.com/download からインストーラーをダウンロード

### 2. LLMモデルのダウンロード

```bash
ollama pull llama3.2
```

### 3. パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. ディレクトリ作成

```bash
python config.py
```

### 5. Ollamaの起動

新しいターミナルで：
```bash
ollama serve
```

### 6. 高度なクローラーを実行

```bash
# 初回実行（全ページ収集）
python advanced_scraper.py

# 2回目以降（増分更新のみ）
python advanced_scraper.py
```

### 7. 洗練されたベクトルDBを構築

```bash
# 初回構築
python enhanced_vectordb.py

# 2回目以降（増分追加）
python enhanced_vectordb.py
```

### 8. アプリケーション起動

**オプション1: Streamlit Chatbot**
```bash
streamlit run app.py
```
→ http://localhost:8501

**オプション2: REST API**
```bash
python api.py
```
→ http://localhost:8000
→ ドキュメント: http://localhost:8000/docs

**オプション3: 管理ダッシュボード**
```bash
streamlit run dashboard.py
```
→ http://localhost:8501

## 📁 ファイル構成

```
school_chatbot_v2/
├── README.md                    # このファイル
├── requirements.txt            # 依存パッケージ
├── config.py                   # 設定ファイル
│
├── scraper.py                  # シンプルなスクレイパー
├── advanced_scraper.py         # 🔥 高度なスクレイパー（推奨）
├── scheduler.py                # 定期実行スケジューラー
│
├── manual_add.py               # 手動情報追加ツール
├── pdf_processor.py            # PDF処理
│
├── vectordb.py                 # 基本ベクトルDB管理
├── enhanced_vectordb.py        # 🧠 洗練されたベクトルDB（推奨）
├── llm_handler.py              # Ollama連携
│
├── app.py                      # Streamlit Chatbot
├── api.py                      # REST API
├── dashboard.py                # 管理ダッシュボード
├── api_example.html            # API使用例
│
├── data/                       # データ保存ディレクトリ
│   ├── scraped/               # スクレイピングデータ
│   │   ├── scraped_data.json  # 全ページデータ
│   │   ├── content_hashes.json # コンテンツハッシュ
│   │   ├── scrape_stats.json  # 統計情報
│   │   ├── skipped_urls.json  # スキップされたURL
│   │   └── failed_urls.json   # 失敗したURL
│   ├── manual/                # 手動追加データ
│   └── pdfs/                  # PDFファイル
└── chroma_db/                  # ChromaDBデータベース
```

## 🎯 推奨ワークフロー

### 初回セットアップ
```bash
# 1. 高度なクローラーで全ページ収集
python advanced_scraper.py

# 2. 洗練されたベクトルDBを構築
python enhanced_vectordb.py

# 3. Chatbot起動
streamlit run app.py
```

### 定期更新（2回目以降）
```bash
# 1. 増分更新（変更されたページのみ）
python advanced_scraper.py

# 2. 新規チャンクのみDB追加
python enhanced_vectordb.py

# 自動化する場合
python scheduler.py --interval=24
```

## 🎯 使用方法

### 基本的な使い方

1. **Chatbotで質問する**
   ```bash
   streamlit run app.py
   ```
   ブラウザで質問を入力

2. **手動で情報を追加**
   ```bash
   python manual_add.py
   ```
   対話形式で情報を入力

3. **PDFを処理**
   - PDFファイルを `data/pdfs/` に配置
   ```bash
   python pdf_processor.py
   ```

### 定期実行

クローラーを24時間ごとに自動実行：

```bash
python scheduler.py
```

カスタム間隔（例: 12時間ごと）：
```bash
python scheduler.py --interval=12
```

バックグラウンド実行（Linux/macOS）：
```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

### API経由で使用

#### Python
```python
import requests

response = requests.post(
    'http://localhost:8000/chat',
    json={
        'query': '入試の日程を教えて',
        'max_results': 5
    }
)

data = response.json()
print(data['response'])
```

#### JavaScript
```javascript
fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        query: '入試の日程を教えて',
        max_results: 5
    })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

#### HTMLサンプル
`api_example.html` をブラウザで開いてください。

## ⚙️ 設定のカスタマイズ

### スクレイピング設定

`config.py` を編集：

```python
# 対象URL
BASE_URL = "https://www.ktc.ac.jp/"

# 最大ページ数
MAX_PAGES = 200

# 待機時間（秒）
SCRAPE_DELAY = 1.0
```

### LLMモデル変更

```python
# config.py
OLLAMA_MODEL = "llama3.2"  # または "mistral", "qwen2.5:7b" など
```

利用可能なモデル：
```bash
ollama list
```

新しいモデルをダウンロード：
```bash
ollama pull <model-name>
```

### 検索結果数の調整

```python
# config.py
TOP_K_RESULTS = 5  # 1-20
```

## 🔧 トラブルシューティング

### Ollamaに接続できない

```bash
# Ollamaが起動しているか確認
curl http://localhost:11434/api/tags

# または
python llm_handler.py --test
```

解決方法：
```bash
ollama serve
```

### スクレイピングが失敗する

- インターネット接続を確認
- `config.py` の `SCRAPE_DELAY` を増やす（例: 2.0秒）
- `MAX_PAGES` を減らす（例: 50ページ）

### メモリ不足

より小さいモデルを使用：
```bash
ollama pull llama3.2:1b
```

`config.py` を編集：
```python
OLLAMA_MODEL = "llama3.2:1b"
```

### データベースをリセット

```bash
python vectordb.py --reset
python scraper.py
python vectordb.py
```

## 📊 APIエンドポイント

| エンドポイント | メソッド | 説明 |
|------------|--------|------|
| `/` | GET | API情報 |
| `/health` | GET | ヘルスチェック |
| `/chat` | POST | チャット |
| `/chat/stream` | POST | ストリーミングチャット |
| `/search` | POST | ベクトル検索 |
| `/stats` | GET | データベース統計 |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |

## 🌟 高度な使い方

### Docker化

```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api.py"]
```

### systemdサービス化（Linux）

```bash
# /etc/systemd/system/chatbot-scheduler.service
[Unit]
Description=Chatbot Scheduler
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/school_chatbot_v2
ExecStart=/usr/bin/python3 scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

有効化：
```bash
sudo systemctl enable chatbot-scheduler
sudo systemctl start chatbot-scheduler
```

## 📝 ライセンス

MIT License

## 🙋 サポート

問題が発生した場合は、以下を確認してください：
1. Python 3.9以上がインストールされているか
2. Ollamaが起動しているか
3. 必要なパッケージがインストールされているか
4. ファイアウォールの設定

それでも解決しない場合は、エラーメッセージを確認してください。
