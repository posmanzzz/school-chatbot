#!/bin/bash
# ==============================================
# SSL証明書取得スクリプト (Let's Encrypt)
# ==============================================

set -e

echo "=========================================="
echo "  SSL証明書取得 (Let's Encrypt)"
echo "=========================================="

# .envファイルの確認
if [ ! -f .env ]; then
    echo "[ERROR] .env ファイルが見つかりません"
    exit 1
fi

source .env

if [ -z "$DOMAIN" ] || [ -z "$LETSENCRYPT_EMAIL" ]; then
    echo "[ERROR] .env の DOMAIN と LETSENCRYPT_EMAIL を設定してください"
    exit 1
fi

echo "[INFO] ドメイン: $DOMAIN"
echo "[INFO] メール: $LETSENCRYPT_EMAIL"

# 証明書取得
echo "[INFO] SSL証明書を取得中..."
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $LETSENCRYPT_EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# 成功した場合、HTTPS設定を有効化
if [ $? -eq 0 ]; then
    echo "[OK] SSL証明書を取得しました"
    echo ""
    echo "[INFO] nginx/conf.d/app.conf を編集して HTTPS を有効化してください:"
    echo "  1. HTTP の location / ブロックをコメントアウト"
    echo "  2. HTTP の redirect 行のコメントを解除"
    echo "  3. HTTPS server ブロック全体のコメントを解除"
    echo "  4. YOUR_DOMAIN.com を $DOMAIN に置換（済みのはず）"
    echo ""
    echo "その後、Nginxを再起動:"
    echo "  docker compose -f docker-compose.prod.yml restart nginx"
else
    echo "[ERROR] SSL証明書の取得に失敗しました"
    exit 1
fi
