# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なライブラリをインストール
COPY files/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクトファイルをコピー
COPY files/ /app/files/
COPY PBL/ /app/PBL/

# 作業ディレクトリをfilesに変更（インポートパスのため）
WORKDIR /app/files

# ポートを公開
EXPOSE 8000

# コンテナ起動時に実行するコマンド
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
