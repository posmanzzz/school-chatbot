# school-chatbot

近畿大学工業高等専門学校のWebサイトをスクレイピングし、
ローカルLLM（Ollama）で質問に回答するRAGチャットボット。

## 技術スタック
- **Backend**: Python / FastAPI
- **LLM**: Ollama（ローカル推論）
- **Vector DB**: ChromaDB
- **Frontend**: TypeScript
- **Infra**: Docker / nginx / SSL

## 機能
- 学校サイトの自動スクレイピング（PDF・画像対応）
- ChromaDBによるベクトル検索（RAG）
- 手動でのナレッジ追加機能
- Docker Composeで本番デプロイ対応

## セットアップ
\`\`\`bash
cp .env.example .env
docker compose up -d
\`\`\`
