#!/bin/bash
# ==============================================
# 本番環境デプロイスクリプト
# ==============================================

set -e

echo "=========================================="
echo "  Chatbot 本番環境デプロイ"
echo "=========================================="

# .envファイルの確認
if [ ! -f .env ]; then
    echo "[ERROR] .env ファイルが見つかりません"
    echo "cp .env.example .env を実行して設定してください"
    exit 1
fi

# 環境変数を読み込み
source .env

# 必須変数のチェック
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-domain.com" ]; then
    echo "[ERROR] .env の DOMAIN を設定してください"
    exit 1
fi

if [ -z "$OLLAMA_BASE_URL" ] || [ "$OLLAMA_BASE_URL" = "http://your-ollama-server:11434" ]; then
    echo "[ERROR] .env の OLLAMA_BASE_URL を設定してください"
    exit 1
fi

echo "[INFO] ドメイン: $DOMAIN"
echo "[INFO] Ollama URL: $OLLAMA_BASE_URL"

# Nginx設定のドメイン名を置換
echo "[INFO] Nginx設定を更新中..."
sed -i "s/YOUR_DOMAIN.com/$DOMAIN/g" nginx/conf.d/app.conf

# certbot用ディレクトリを作成
mkdir -p certbot/www certbot/conf

# Dockerイメージをビルド
echo "[INFO] Dockerイメージをビルド中..."
docker compose -f docker-compose.prod.yml build

# コンテナを起動
echo "[INFO] コンテナを起動中..."
docker compose -f docker-compose.prod.yml up -d nginx app

# 起動待機
echo "[INFO] サービス起動を待機中..."
sleep 10

# ヘルスチェック
echo "[INFO] ヘルスチェック中..."
if curl -sf http://localhost/api/health > /dev/null; then
    echo "[OK] アプリケーションが正常に起動しました"
else
    echo "[WARN] ヘルスチェックに失敗しました。ログを確認してください:"
    docker compose -f docker-compose.prod.yml logs app
fi

echo ""
echo "=========================================="
echo "  デプロイ完了"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "1. http://$DOMAIN でアクセスできることを確認"
echo "2. SSL証明書を取得: ./ssl-setup.sh"
echo ""
