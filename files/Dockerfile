# ベースイメージとして公式のPythonイメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なファイルをコンテナにコピー
# まず requirements.txt をコピーしてライブラリインストールをキャッシュ
COPY files/requirements.txt .

# 依存ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクトのファイル（filesディレクトリ）をコピー
COPY files/ /app

# フロントエンドのファイル（PBLディレクトリ）をコピー
COPY PBL/ /app/PBL

# アプリケーションがリッスンするポートを公開
EXPOSE 8000

# コンテナ起動時に実行するコマンド
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
