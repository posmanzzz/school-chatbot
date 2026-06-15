"""
ベクトルデータベース管理
ChromaDBを使用してドキュメントの保存と検索を行う
"""

import os
import json
import re
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import config


class VectorDatabase:
    """ベクトルデータベースの管理クラス"""
    
    def __init__(self):
        """データベースを初期化"""
        # ChromaDBクライアントを作成
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_DB_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 埋め込みモデルを読み込み
        print("[INFO] 埋め込みモデルを読み込んでいます...")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        print(f"[OK] モデル読み込み完了: {config.EMBEDDING_MODEL}")
        
        # コレクションを取得または作成
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"description": "School website documents"}
        )
        
        print(f"[OK] コレクション準備完了: {config.COLLECTION_NAME}")
        print(f"  - 既存ドキュメント数: {self.collection.count()}")
    
    def split_text(self, text: str) -> List[str]:
        """テキストをチャンクに分割"""
        chunks = []
        
        # 段落で分割
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # チャンクサイズチェック
            if len(current_chunk) + len(para) < config.CHUNK_SIZE:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        # 最後のチャンクを追加
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 最小サイズフィルター
        chunks = [c for c in chunks if len(c) >= config.MIN_CHUNK_SIZE]
        
        return chunks
    
    def add_documents(self, documents: List[Dict], source_type: str = "scraped"):
        """ドキュメントをデータベースに追加"""
        print(f"\n[INFO] ドキュメントを追加中 (ソース: {source_type})...")
        
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for doc_idx, doc in enumerate(tqdm(documents, desc="処理中")):
            # テキストをチャンクに分割
            content = doc.get('content', '')
            title = doc.get('title', f"Document {doc_idx}")
            url = doc.get('url', '')
            
            chunks = self.split_text(content)
            
            # 各チャンクにメタデータを付与
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"{source_type}_{doc_idx:04d}_{chunk_idx:04d}"
                
                metadata = {
                    'source_type': source_type,
                    'title': title,
                    'url': url,
                    'doc_index': doc_idx,
                    'chunk_index': chunk_idx,
                    'category': doc.get('category', 'general')
                }
                
                all_chunks.append(chunk)
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)
        
        if not all_chunks:
            print("[WARN] 追加するチャンクがありません")
            return
        
        # 埋め込みを生成
        print(f"[INFO] 埋め込みを生成中 ({len(all_chunks)}チャンク)...")
        embeddings = self.embedding_model.encode(
            all_chunks,
            show_progress_bar=True,
            batch_size=32
        ).tolist()
        
        # データベースに追加
        print("[INFO] データベースに保存中...")
        self.collection.add(
            ids=all_ids,
            embeddings=embeddings,
            documents=all_chunks,
            metadatas=all_metadatas
        )
        
        print(f"[OK] {len(all_chunks)}個のチャンクを追加しました")
        print(f"  - 総ドキュメント数: {self.collection.count()}")
    
    def search(self, query: str, n_results: int = None) -> List[Dict]:
        """クエリに基づいてドキュメントを検索"""
        if n_results is None:
            n_results = config.TOP_K_RESULTS
        
        # クエリの埋め込みを生成
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # 検索実行
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # 結果を整形
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for idx in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][idx],
                    'metadata': results['metadatas'][0][idx],
                    'distance': results['distances'][0][idx] if 'distances' in results else None
                })
        
        return formatted_results
    
    def reset_database(self):
        """データベースをリセット"""
        print("[WARN] データベースをリセットしています...")
        self.client.delete_collection(config.COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=config.COLLECTION_NAME,
            metadata={"description": "School website documents"}
        )
        print("[OK] データベースをリセットしました")
    
    def get_stats(self) -> Dict:
        """データベースの統計情報を取得"""
        total_count = self.collection.count()
        
        # ソースタイプ別の集計
        if total_count > 0:
            # 全データを取得してカウント（小規模DBの場合）
            all_data = self.collection.get()
            source_counts = {}
            category_counts = {}
            
            for metadata in all_data['metadatas']:
                source = metadata.get('source_type', 'unknown')
                category = metadata.get('category', 'unknown')
                
                source_counts[source] = source_counts.get(source, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1
        else:
            source_counts = {}
            category_counts = {}
        
        return {
            'total_chunks': total_count,
            'by_source': source_counts,
            'by_category': category_counts
        }


def load_scraped_data() -> List[Dict]:
    """スクレイピングしたデータを読み込み"""
    scraped_file = os.path.join(config.SCRAPED_DIR, 'scraped_data.json')
    
    if not os.path.exists(scraped_file):
        print(f"[WARN] スクレイピングデータが見つかりません: {scraped_file}")
        return []
    
    with open(scraped_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[OK] スクレイピングデータを読み込みました: {len(data)}件")
    return data


def load_manual_data() -> List[Dict]:
    """手動追加データを読み込み"""
    manual_file = os.path.join(config.MANUAL_DIR, 'manual_data.json')
    
    if not os.path.exists(manual_file):
        print(f"[INFO] 手動追加データがありません: {manual_file}")
        return []
    
    with open(manual_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[OK] 手動追加データを読み込みました: {len(data)}件")
    return data


def main():
    """メイン処理 - データベース構築"""
    import sys
    
    print("=" * 80)
    print("ベクトルデータベース構築ツール")
    print("=" * 80)
    
    # データベース初期化
    db = VectorDatabase()
    
    # リセットオプション
    if '--reset' in sys.argv:
        db.reset_database()
    
    # スクレイピングデータを追加
    scraped_data = load_scraped_data()
    if scraped_data:
        db.add_documents(scraped_data, source_type="scraped")
    
    # 手動追加データを追加
    manual_data = load_manual_data()
    if manual_data:
        db.add_documents(manual_data, source_type="manual")
    
    # 統計情報表示
    print("\n" + "=" * 80)
    print("データベース統計")
    print("=" * 80)
    stats = db.get_stats()
    print(f"総チャンク数: {stats['total_chunks']}")
    
    if stats['by_source']:
        print("\nソース別:")
        for source, count in stats['by_source'].items():
            print(f"  - {source}: {count}チャンク")
    
    if stats['by_category']:
        print("\nカテゴリ別:")
        for category, count in stats['by_category'].items():
            print(f"  - {category}: {count}チャンク")
    
    print("\n" + "=" * 80)
    print("データベース構築完了!")
    print("次のステップ: streamlit run app.py")
    print("=" * 80)
    
    # テスト検索（オプション）
    if '--test' in sys.argv:
        print("\n" + "=" * 80)
        print("テスト検索")
        print("=" * 80)
        
        test_queries = [
            "入試について教えて",
            "学生寮の情報",
            "図書館の利用方法"
        ]
        
        for query in test_queries:
            print(f"\nクエリ: {query}")
            results = db.search(query, n_results=3)
            
            for i, result in enumerate(results, 1):
                print(f"\n  [{i}] {result['metadata']['title']}")
                print(f"      カテゴリ: {result['metadata'].get('category', 'N/A')}")
                print(f"      内容: {result['content'][:100]}...")


if __name__ == "__main__":
    main()
