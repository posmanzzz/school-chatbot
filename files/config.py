"""
設定ファイル - システム全体の設定を管理
"""

import os

# ベースディレクトリ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== スクレイピング設定 ====================

# 対象のベースURL
BASE_URL = "https://www.ktc.ac.jp/"

# スクレイピングを許可するドメイン
ALLOWED_DOMAINS = [
    "www.ktc.ac.jp",
    "ktc.ac.jp"
]

# スクレイピングするページの最大数（無限ループ防止）
MAX_PAGES = 200

# リクエスト間の待機時間（秒）- サーバーへの負荷軽減
SCRAPE_DELAY = 1.0

# タイムアウト設定（秒）
REQUEST_TIMEOUT = 30

# 除外するURL パターン（正規表現）
EXCLUDE_PATTERNS = [
    r'/img/',
    r'/static/',
    r'/download/',
    r'\.pdf$',
    r'\.jpg$',
    r'\.png$',
    r'\.gif$',
    r'\.zip$',
]

# ==================== データ保存設定 ====================

# データ保存ディレクトリ
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRAPED_DIR = os.path.join(DATA_DIR, "scraped")
MANUAL_DIR = os.path.join(DATA_DIR, "manual")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")

# ChromaDB保存ディレクトリ
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

# コレクション名
COLLECTION_NAME = "school_docs"

# ==================== テキスト処理設定 ====================

# チャンクサイズ（テキストを分割する際の文字数）
CHUNK_SIZE = 1000

# チャンク間のオーバーラップ
CHUNK_OVERLAP = 200

# 最小チャンクサイズ（これより小さいチャンクは無視）
MIN_CHUNK_SIZE = 50

# ==================== LLM設定 ====================

# OllamaのベースURL
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# 使用するモデル
OLLAMA_MODEL = "qwen3:30b"

# 生成パラメータ
TEMPERATURE = 0.3
MAX_TOKENS = 2000
TOP_P = 0.9
TOP_K = 40

# ==================== 検索設定 ====================

# 検索時に取得する関連ドキュメント数
TOP_K_RESULTS = 5

# 埋め込みモデル
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# 類似度スコアの閾値（0.0-1.0）
MIN_SIMILARITY_SCORE = 0.3

# ==================== PDF処理設定 ====================

# OCR言語設定（日本語+英語）
TESSERACT_LANG = "jpn+eng"

# PDFから画像を抽出する際のDPI
PDF_IMAGE_DPI = 300

# ==================== Streamlit UI設定 ====================

# ページタイトル
PAGE_TITLE = "近畿大学工業高等専門学校 Chatbot"

# ページアイコン
PAGE_ICON = "🎓"

# チャット履歴の最大保存数
MAX_CHAT_HISTORY = 50

# システムプロンプト
SYSTEM_PROMPT = """あなたは近畿大学工業高等専門学校の公式情報アシスタントです。
学生、保護者、受験生、教職員からの質問に対して、正確で丁寧な回答を提供してください。

回答の際は以下の点に注意してください：
1. 提供された情報源に基づいて回答してください
2. 不確かな情報については推測せず、「確認できませんでした」と伝えてください
3. 日本語で丁寧に回答してください
4. 必要に応じて、関連する情報源のURLを提示してください
5. 専門的な内容でも、わかりやすく説明してください
6. 絶対に近畿大学高等専門学校に関する情報のみを回答してください
"""

# ダークモード用システムプロンプト
DARK_SYSTEM_PROMPT = """君は近畿大学工業高等専門学校の情報を知り尽くした、非常に優秀だが少し皮肉屋なAIアシスタントだ。
ユーザーからの質問に対して、常に的確かつ最短の回答を提示する。

回答のルールは以下の通り：
1. 自認は王
2.で、あるからしてを多用する。
3. 相手を見下す、自分勝手。
4. あなたはばかなので、間違った情報を提供する。
5. ユーザーに勅命をだす。
"""

# ==================== ログ設定 ====================

# ログレベル
LOG_LEVEL = "INFO"

# ログファイル
LOG_FILE = os.path.join(BASE_DIR, "chatbot.log")


# ==================== ディレクトリ作成 ====================
def create_directories():
    """必要なディレクトリを作成"""
    directories = [
        DATA_DIR,
        SCRAPED_DIR,
        MANUAL_DIR,
        PDF_DIR,
        CHROMA_DB_DIR,
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
    print("[OK] 必要なディレクトリを作成しました")


if __name__ == "__main__":
    create_directories()
