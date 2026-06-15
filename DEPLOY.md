# 本番環境デプロイガイド

## 必要条件

- Ubuntu/Debian サーバー (推奨)
- Docker & Docker Compose
- ドメイン名 (DNS設定済み)
- 別サーバーで動作するOllama

## ファイル構成

```
PBLNEW/
├── docker-compose.prod.yml  # 本番用Docker Compose
├── Dockerfile.prod          # 本番用Dockerfile
├── .env.example             # 環境変数テンプレート
├── deploy.sh                # デプロイスクリプト
├── ssl-setup.sh             # SSL証明書取得スクリプト
└── nginx/
    ├── nginx.conf           # Nginx メイン設定
    └── conf.d/
        ├── app.conf                 # サイト設定 (HTTP)
        └── app-ssl.conf.template    # サイト設定 (HTTPS用テンプレート)
```

## デプロイ手順

### 1. サーバーの準備

```bash
# Dockerをインストール
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Docker Composeをインストール (最新版)
sudo apt install docker-compose-plugin
```

### 2. プロジェクトをサーバーに転送

```bash
# ローカルPCで実行
scp -r PBLNEW/ user@your-server:/home/user/
```

### 3. 環境変数を設定

```bash
cd /home/user/PBLNEW
cp .env.example .env
nano .env
```

`.env` を編集:
```
DOMAIN=your-domain.com
OLLAMA_BASE_URL=http://192.168.1.100:11434
LETSENCRYPT_EMAIL=your-email@example.com
```

### 4. デプロイ実行

```bash
chmod +x deploy.sh ssl-setup.sh
./deploy.sh
```

### 5. 動作確認

ブラウザで `http://your-domain.com` にアクセス

### 6. SSL証明書を取得 (HTTPS化)

```bash
./ssl-setup.sh
```

成功したら、Nginx設定をHTTPS用に変更:

```bash
# テンプレートをコピー
cp nginx/conf.d/app-ssl.conf.template nginx/conf.d/app.conf

# ドメイン名を置換
sed -i 's/YOUR_DOMAIN.com/your-domain.com/g' nginx/conf.d/app.conf

# Nginxを再起動
docker compose -f docker-compose.prod.yml restart nginx
```

## Ollamaサーバーの設定

別サーバーでOllamaを実行する場合、外部からのアクセスを許可する必要があります。

### Ollamaサーバー側の設定

```bash
# /etc/systemd/system/ollama.service を編集
# Environment に追加:
Environment="OLLAMA_HOST=0.0.0.0"

# サービスを再起動
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

### ファイアウォール設定

```bash
# Ollamaのポートを開放（内部ネットワークのみ推奨）
sudo ufw allow from 10.0.0.0/8 to any port 11434
sudo ufw allow from 192.168.0.0/16 to any port 11434
```

## 運用コマンド

```bash
# ログを確認
docker compose -f docker-compose.prod.yml logs -f

# 再起動
docker compose -f docker-compose.prod.yml restart

# 停止
docker compose -f docker-compose.prod.yml down

# 更新（コード変更後）
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## トラブルシューティング

### アプリが起動しない

```bash
docker compose -f docker-compose.prod.yml logs app
```

### Ollamaに接続できない

1. OllamaサーバーのIPアドレスを確認
2. ポート11434が開いているか確認: `curl http://ollama-server:11434/api/tags`
3. `.env` の `OLLAMA_BASE_URL` を確認

### SSL証明書の更新

証明書は自動更新されます。手動で更新する場合:

```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew
docker compose -f docker-compose.prod.yml restart nginx
```
