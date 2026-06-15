"""
REST API and Frontend Server
FastAPIを使用してChatbot機能とフロントエンドを同時に提供
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uvicorn
import os
import json
from fastapi.responses import StreamingResponse, FileResponse, RedirectResponse

from vectordb import VectorDatabase
from llm_handler import OllamaHandler
from web_search import WebSearcher
import config

# --- アプリケーションの分割 ---
# メインアプリ: 静的ファイル(フロントエンド)を配信
app = FastAPI(
    title="学校Chatbot",
    description="フロントエンドとバックエンドAPIを提供",
    version="1.0.0"
)

# APIアプリ: チャットボットのAPI機能を提供
api_app = FastAPI(
    title="学校Chatbot API",
    description="Ollamaを使用したローカルLLM Chatbot API",
    version="1.0.0",
    docs_url="/docs", # ドキュメントのURLを変更
    redoc_url="/redoc"
)

# --- CORS設定 ---
# APIアプリにCORSミドルウェアを適用
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- リクエスト/レスポンスモデル ---
class ChatRequest(BaseModel):
    query: str = Field(..., description="ユーザーの質問", min_length=1, max_length=1000)
    max_results: Optional[int] = Field(5, description="検索する関連情報の数", ge=1, le=20)
    temperature: Optional[float] = Field(0.3, description="応答の創造性", ge=0.0, le=1.0)
    web_search: Optional[bool] = Field(False, description="Web検索を有効にする")
    mode: Optional[str] = Field("light", description="UIモード (light or dark)")

class ChatResponse(BaseModel):
    query: str
    response: str
    sources: List[Dict]
    timestamp: str
    model: str

class SearchRequest(BaseModel):
    query: str = Field(..., description="検索クエリ", min_length=1, max_length=500)
    max_results: Optional[int] = Field(5, description="最大結果数", ge=1, le=20)

class SearchResponse(BaseModel):
    query: str
    results: List[Dict]
    total: int
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    database_size: int
    model: str
    timestamp: str

# --- グローバル変数 ---
db: Optional[VectorDatabase] = None
llm: Optional[OllamaHandler] = None
web_searcher: Optional[WebSearcher] = None

# --- イベントハンドラ (メインアプリに適用) ---
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    global db, llm, web_searcher
    print("[START] システムを初期化中...")
    try:
        db = VectorDatabase()
        llm = OllamaHandler()
        web_searcher = WebSearcher()
        print("[OK] データベース、LLM、Web検索を初期化しました")
    except Exception as e:
        print(f"[ERROR] 初期化エラー: {e}")
        # 本番環境ではここで終了させるのが望ましい
        # raise

# --- APIエンドポイント (@api_appを使用) ---
@api_app.get("/", response_model=Dict, summary="APIルート")
async def api_root():
    return {
        "message": "学校Chatbot API",
        "version": "1.0.0",
    }

@api_app.get("/health", response_model=HealthResponse, summary="ヘルスチェック")
async def health_check():
    if db is None or llm is None:
        raise HTTPException(status_code=503, detail="サービスが初期化されていません")
    stats = db.get_stats()
    return HealthResponse(
        status="healthy",
        database_size=stats['total_chunks'],
        model=llm.model,
        timestamp=datetime.now().isoformat()
    )

@api_app.post("/search", response_model=SearchResponse, summary="ベクトル検索")
async def search(request: SearchRequest):
    if db is None:
        raise HTTPException(status_code=503, detail="データベースが初期化されていません")
    try:
        results = db.search(request.query, n_results=request.max_results)
        formatted_results = []
        for result in results:
            formatted_results.append({
                'content': result['content'],
                'title': result['metadata'].get('title', 'N/A'),
                'url': result['metadata'].get('url', ''),
                'category': result['metadata'].get('category', 'general'),
                'relevance': 1 - result.get('distance', 0)
            })
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total=len(formatted_results),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索エラー: {str(e)}")

@api_app.post("/chat", response_model=ChatResponse, summary="チャット応答（非ストリーミング）")
async def chat(request: ChatRequest):
    if db is None or llm is None:
        raise HTTPException(status_code=503, detail="サービスが初期化されていません")
    try:
        # ローカルデータベースから検索
        search_results = db.search(request.query, n_results=request.max_results)

        # Web検索が有効な場合
        web_results = []
        if request.web_search and web_searcher is not None:
            web_results = web_searcher.search(request.query, max_results=3)
            # Web検索結果をコンテキストに追加
            for web_result in web_results:
                search_results.append({
                    'content': f"{web_result['title']}\n{web_result['snippet']}",
                    'metadata': {
                        'title': web_result['title'],
                        'url': web_result['url'],
                        'category': 'web_search'
                    },
                    'distance': 0.5  # Web検索結果のデフォルト距離
                })

        # モードに応じてシステムプロンプトを選択
        if request.mode == "dark":
            system_prompt = config.DARK_SYSTEM_PROMPT
        else:
            system_prompt = config.SYSTEM_PROMPT

        config.TEMPERATURE = request.temperature
        response_text = ""
        # llm.generate_responseがジェネレータを返す想定
        for chunk in llm.generate_response(request.query, search_results, stream=False, system_prompt=system_prompt):
            response_text += chunk

        sources = []
        for result in search_results:
            sources.append({
                'title': result['metadata'].get('title', 'N/A'),
                'url': result['metadata'].get('url', ''),
                'category': result['metadata'].get('category', 'general'),
                'relevance': 1 - result.get('distance', 0)
            })

        return ChatResponse(
            query=request.query,
            response=response_text,
            sources=sources,
            timestamp=datetime.now().isoformat(),
            model=llm.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"チャットエラー: {str(e)}")

@api_app.post("/chat/stream", summary="チャット応答（ストリーミング）")
async def chat_stream(request: ChatRequest):
    if db is None or llm is None:
        raise HTTPException(status_code=503, detail="サービスが初期化されていません")
    
    async def generate():
        try:
            search_results = db.search(request.query, n_results=request.max_results)
            sources = []
            for result in search_results:
                sources.append({
                    'title': result['metadata'].get('title', 'N/A'),
                    'url': result['metadata'].get('url', ''),
                })
            yield f"data: {json.dumps({'type': 'sources', 'data': sources})}\n\n"
            
            # モードに応じてシステムプロンプトを選択
            if request.mode == "dark":
                system_prompt = config.DARK_SYSTEM_PROMPT
            else:
                system_prompt = config.SYSTEM_PROMPT

            config.TEMPERATURE = request.temperature
            for chunk in llm.generate_response(request.query, search_results, stream=True, system_prompt=system_prompt):
                yield f"data: {json.dumps({'type': 'token', 'data': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@api_app.post("/web-search", summary="Web検索のみ実行")
async def web_search_only(request: SearchRequest):
    if web_searcher is None:
        raise HTTPException(status_code=503, detail="Web検索が初期化されていません")
    try:
        results = web_searcher.search(request.query, max_results=request.max_results)
        return {
            "query": request.query,
            "results": results,
            "total": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web検索エラー: {str(e)}")

@api_app.get("/stats", response_model=Dict, summary="データベース統計情報")
async def get_stats():
    if db is None:
        raise HTTPException(status_code=503, detail="データベースが初期化されていません")
    stats = db.get_stats()
    return {
        "total_chunks": stats['total_chunks'],
        "by_source": stats['by_source'],
        "by_category": stats['by_category'],
        "timestamp": datetime.now().isoformat()
    }

# --- アプリケーションのマウント ---
# APIアプリをメインアプリの /api パスにマウント
app.mount("/api", api_app)

# 静的ファイル(フロントエンド)をマウント
# このファイルの場所からの相対パスでPBLディレクトリを指定
# pbl_path = os.path.join(os.path.dirname(__file__), '..', 'PBL')
# コンテナ内の絶対パスを指定
pbl_path = "/app/PBL"

# ルートアクセス時にpbl.htmlを返す
@app.get("/")
async def root():
    return FileResponse(os.path.join(pbl_path, 'pbl.html'))

# 静的ファイルをマウント（/以外のパス用）
app.mount("/", StaticFiles(directory=pbl_path), name="static")


# --- メイン処理 ---
def main():
    import sys
    port = 8000
    for arg in sys.argv:
        if arg.startswith('--port='):
            port = int(arg.split('=')[1])
    
    print("=" * 80)
    print("学校Chatbot サーバー")
    print("=" * 80)
    print(f"\n🌐 フロントエンド: http://localhost:{port}")
    print(f"📚 APIドキュメント: http://localhost:{port}/api/docs")
    print("\nCtrl+C で停止\n")
    print("=" * 80)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()