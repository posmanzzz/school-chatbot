"""
洗練されたベクトルデータベース管理
- スマートなチャンク分割
- 段落構造の保持
- メタデータの充実
- 増分更新
- クエリ最適化
"""

import os
import json
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import config


class SmartChunker:
    """スマートなテキストチャンク分割"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split_by_structure(self, text: str, metadata: Dict) -> List[Dict]:
        """構造を考慮してテキストを分割"""
        chunks = []
        
        # 見出しで分割を試みる
        heading_pattern = r'\n([A-Z][^\n]{10,100})\n'
        sections = re.split(heading_pattern, text)
        
        if len(sections) > 3:  # 見出しが見つかった場合
            current_heading = metadata.get('title', '')
            current_text = ""
            
            for i, section in enumerate(sections):
                if i % 2 == 1:  # 見出し
                    if current_text:
                        # 前のセクションを保存
                        chunks.extend(self._split_text(
                            current_text,
                            {'heading': current_heading, **metadata}
                        ))
                    current_heading = section.strip()
                    current_text = ""
                else:  # 内容
                    current_text = section.strip()
            
            # 最後のセクション
            if current_text:
                chunks.extend(self._split_text(
                    current_text,
                    {'heading': current_heading, **metadata}
                ))
        else:
            # 見出しがない場合は段落で分割
            chunks = self._split_by_paragraphs(text, metadata)
        
        return chunks
    
    def _split_by_paragraphs(self, text: str, metadata: Dict) -> List[Dict]:
        """段落を考慮して分割"""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'metadata': metadata.copy()
                    })
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata.copy()
            })
        
        return chunks
    
    def _split_text(self, text: str, metadata: Dict) -> List[Dict]:
        """テキストを固定サイズで分割（オーバーラップ付き）"""
        chunks = []
        
        # 文で分割
        sentences = re.split(r'([。．！？\n])', text)
        sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences), 2)]
        
        current_chunk = ""
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # チャンクを保存
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': metadata.copy()
                })
                
                # オーバーラップ分を保持
                overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                current_chunk = overlap_text + sentence
                current_length = len(current_chunk)
            else:
                current_chunk += sentence
                current_length += sentence_length
        
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata.copy()
            })
        
        return chunks


class EnhancedVectorDatabase:
    """洗練されたベクトルデータベース"""
    
    def __init__(self):
        """データベースを初期化"""
        # ChromaDBクライアント
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_DB_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 埋め込みモデル
        print("📚 埋め込みモデルを読み込んでいます...")
        self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        print(f"✓ モデル読み込み完了: {config.EMBEDDING_MODEL}")
        
        # コレクション
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"description": "Enhanced school website documents"}
        )
        
        # チャンカー
        self.chunker = SmartChunker(
            chunk_size=config.CHUNK_SIZE,
            overlap=config.CHUNK_OVERLAP
        )
        
        # チャンクハッシュ管理（重複防止）
        self.chunk_hashes: set = self._load_existing_hashes()
        
        print(f"✓ コレクション準備完了: {config.COLLECTION_NAME}")
        print(f"  - 既存チャンク数: {self.collection.count()}")
    
    def _load_existing_hashes(self) -> set:
        """既存のチャンクハッシュを読み込み"""
        hashes = set()
        
        try:
            if self.collection.count() > 0:
                # 既存データからハッシュを取得
                all_data = self.collection.get()
                for metadata in all_data['metadatas']:
                    if 'chunk_hash' in metadata:
                        hashes.add(metadata['chunk_hash'])
        except:
            pass
        
        return hashes
    
    def _get_chunk_hash(self, text: str, url: str) -> str:
        """チャンクの一意なハッシュを生成"""
        content = f"{url}::{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def process_documents(self, documents: List[Dict], source_type: str = "scraped") -> Tuple[int, int]:
        """ドキュメントを処理してチャンクに分割"""
        print(f"\n📝 ドキュメント処理中 (ソース: {source_type})...")
        
        all_chunks = []
        new_chunks = 0
        duplicate_chunks = 0
        
        for doc in tqdm(documents, desc="処理中"):
            content = doc.get('content', '')
            if not content or len(content) < config.MIN_CHUNK_SIZE:
                continue
            
            # メタデータ準備
            base_metadata = {
                'source_type': source_type,
                'title': doc.get('title', ''),
                'url': doc.get('url', ''),
                'category': doc.get('category', 'general'),
                'scraped_at': doc.get('scraped_at', ''),
            }
            
            # ドキュメントのメタデータがある場合は追加
            if 'metadata' in doc:
                doc_metadata = doc['metadata']
                if doc_metadata.get('description'):
                    base_metadata['description'] = doc_metadata['description']
                if doc_metadata.get('keywords'):
                    base_metadata['keywords'] = doc_metadata['keywords']
            
            # スマートチャンク分割
            chunks = self.chunker.split_by_structure(content, base_metadata)
            
            # 重複チェック
            for i, chunk_data in enumerate(chunks):
                chunk_text = chunk_data['text']
                chunk_hash = self._get_chunk_hash(chunk_text, base_metadata['url'])
                
                if chunk_hash in self.chunk_hashes:
                    duplicate_chunks += 1
                    continue
                
                # メタデータに追加情報
                chunk_metadata = chunk_data['metadata'].copy()
                chunk_metadata.update({
                    'chunk_index': i,
                    'chunk_hash': chunk_hash,
                    'chunk_length': len(chunk_text),
                    'processed_at': datetime.now().isoformat()
                })
                
                all_chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata,
                    'hash': chunk_hash
                })
                
                self.chunk_hashes.add(chunk_hash)
                new_chunks += 1
        
        print(f"  - 新規チャンク: {new_chunks}")
        print(f"  - 重複スキップ: {duplicate_chunks}")
        
        return all_chunks, new_chunks
    
    def add_chunks(self, chunks: List[Dict]):
        """チャンクをデータベースに追加"""
        if not chunks:
            print("✗ 追加するチャンクがありません")
            return
        
        print(f"\n🔄 埋め込み生成中 ({len(chunks)}チャンク)...")
        
        # バッチ処理
        batch_size = 100
        total_added = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # テキストとメタデータを抽出
            texts = [chunk['text'] for chunk in batch]
            metadatas = [chunk['metadata'] for chunk in batch]
            ids = [chunk['hash'] for chunk in batch]
            
            # 埋め込み生成
            embeddings = self.embedding_model.encode(
                texts,
                show_progress_bar=False,
                batch_size=32
            ).tolist()
            
            # データベースに追加
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            total_added += len(batch)
            print(f"  進捗: {total_added}/{len(chunks)}")
        
        print(f"✓ {total_added}個のチャンクを追加しました")
        print(f"  - 総チャンク数: {self.collection.count()}")
    
    def search(self, query: str, n_results: int = None, filters: Dict = None) -> List[Dict]:
        """高度な検索"""
        if n_results is None:
            n_results = config.TOP_K_RESULTS
        
        # クエリの埋め込み生成
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # 検索実行
        search_params = {
            'query_embeddings': query_embedding,
            'n_results': n_results
        }
        
        # フィルター適用
        if filters:
            search_params['where'] = filters
        
        results = self.collection.query(**search_params)
        
        # 結果を整形
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for idx in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][idx],
                    'metadata': results['metadatas'][0][idx],
                    'distance': results['distances'][0][idx] if 'distances' in results else None,
                    'relevance': 1 - results['distances'][0][idx] if 'distances' in results else None
                })
        
        return formatted_results
    
    def update_from_scraper(self):
        """スクレイパーからデータを読み込んで更新"""
        scraped_file = os.path.join(config.SCRAPED_DIR, 'scraped_data.json')
        
        if not os.path.exists(scraped_file):
            print(f"⚠️ スクレイピングデータが見つかりません: {scraped_file}")
            return
        
        with open(scraped_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
        
        print(f"✓ スクレイピングデータ読み込み: {len(scraped_data)}件")
        
        # 処理
        chunks, new_count = self.process_documents(scraped_data, source_type="scraped")
        
        # 追加
        if chunks:
            self.add_chunks(chunks)
        else:
            print("ℹ️ 追加する新しいチャンクはありません（全て既存）")
    
    def reset_database(self):
        """データベースをリセット"""
        print("⚠️ データベースをリセットしています...")
        self.client.delete_collection(config.COLLECTION_NAME)
        self.collection = self.client.create_collection(
            name=config.COLLECTION_NAME,
            metadata={"description": "Enhanced school website documents"}
        )
        self.chunk_hashes.clear()
        print("✓ データベースをリセットしました")
    
    def get_stats(self) -> Dict:
        """詳細な統計情報"""
        total_count = self.collection.count()
        
        if total_count == 0:
            return {
                'total_chunks': 0,
                'by_source': {},
                'by_category': {},
                'by_url': {}
            }
        
        # 全データを取得
        all_data = self.collection.get()
        
        # 統計集計
        source_counts = {}
        category_counts = {}
        url_counts = {}
        
        for metadata in all_data['metadatas']:
            source = metadata.get('source_type', 'unknown')
            category = metadata.get('category', 'unknown')
            url = metadata.get('url', 'unknown')
            
            source_counts[source] = source_counts.get(source, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
            url_counts[url] = url_counts.get(url, 0) + 1
        
        # URL数（ユニーク）
        unique_urls = len(url_counts)
        
        return {
            'total_chunks': total_count,
            'unique_urls': unique_urls,
            'by_source': source_counts,
            'by_category': category_counts,
            'top_urls': dict(sorted(url_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }


def main():
    """メイン処理"""
    import sys
    
    print("=" * 80)
    print("洗練されたベクトルデータベース構築ツール")
    print("=" * 80)
    
    # データベース初期化
    db = EnhancedVectorDatabase()
    
    # リセットオプション
    if '--reset' in sys.argv:
        db.reset_database()
    
    # スクレイパーデータから更新
    db.update_from_scraper()
    
    # 手動追加データ
    manual_file = os.path.join(config.MANUAL_DIR, 'manual_data.json')
    if os.path.exists(manual_file):
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_data = json.load(f)
        
        if manual_data:
            print(f"\n✓ 手動追加データ読み込み: {len(manual_data)}件")
            chunks, new_count = db.process_documents(manual_data, source_type="manual")
            if chunks:
                db.add_chunks(chunks)
    
    # 統計表示
    print("\n" + "=" * 80)
    print("データベース統計")
    print("=" * 80)
    
    stats = db.get_stats()
    print(f"総チャンク数: {stats['total_chunks']}")
    print(f"ユニークURL数: {stats['unique_urls']}")
    
    if stats['by_source']:
        print("\nソース別:")
        for source, count in stats['by_source'].items():
            print(f"  - {source}: {count}チャンク")
    
    if stats['top_urls']:
        print("\nチャンク数トップ10 URL:")
        for url, count in list(stats['top_urls'].items())[:10]:
            print(f"  - {count}チャンク: {url[:60]}")
    
    print("\n" + "=" * 80)
    print("データベース構築完了!")
    print("次のステップ: streamlit run app.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
