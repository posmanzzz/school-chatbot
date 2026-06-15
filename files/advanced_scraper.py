"""
高度なWebスクレイピングエンジン
- URL正規化による重複排除
- コンテンツハッシュによる変更検知
- 増分更新（変更されたページのみ更新）
- インテリジェントな優先度付けクロール
- 詳細な統計とログ
"""

import os
import re
import json
import time
import hashlib
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
from typing import Set, List, Dict, Optional, Tuple
from collections import deque, defaultdict
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import config


class URLNormalizer:
    """URL正規化クラス - 重複URLを検出"""
    
    @staticmethod
    def normalize(url: str) -> str:
        """URLを正規化して一意にする"""
        parsed = urlparse(url)
        
        # クエリパラメータをソート
        query_params = parse_qs(parsed.query)
        # 不要なパラメータを削除
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'fbclid', 'gclid']
        for param in tracking_params:
            query_params.pop(param, None)
        
        # クエリを再構築
        sorted_query = urlencode(sorted(query_params.items()), doseq=True)
        
        # 末尾のスラッシュを統一
        path = parsed.path.rstrip('/') or '/'
        
        # 正規化されたURLを再構築
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            '',  # params
            sorted_query,
            ''   # fragment
        ))
        
        return normalized


class ContentHashManager:
    """コンテンツハッシュ管理 - 変更検知"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.url_hashes: Dict[str, Dict] = {}
        self.load()
    
    def load(self):
        """既存のハッシュデータベースを読み込み"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.url_hashes = data.get('url_hashes', {})
                print(f"✓ ハッシュDB読み込み: {len(self.url_hashes)}件のURL")
            except Exception as e:
                print(f"⚠️ ハッシュDB読み込みエラー: {e}")
                self.url_hashes = {}
    
    def save(self):
        """ハッシュデータベースを保存"""
        data = {
            'url_hashes': self.url_hashes,
            'last_updated': datetime.now().isoformat(),
            'total_urls': len(self.url_hashes)
        }
        
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_hash(self, content: str) -> str:
        """コンテンツのハッシュを計算"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def has_changed(self, url: str, content: str) -> bool:
        """コンテンツが変更されたかチェック"""
        content_hash = self.get_hash(content)
        
        if url not in self.url_hashes:
            # 新規URL
            self.url_hashes[url] = {
                'hash': content_hash,
                'first_seen': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'update_count': 1
            }
            return True
        
        # 既存URLのハッシュと比較
        if self.url_hashes[url]['hash'] != content_hash:
            # 変更あり
            self.url_hashes[url].update({
                'hash': content_hash,
                'last_updated': datetime.now().isoformat(),
                'update_count': self.url_hashes[url].get('update_count', 0) + 1
            })
            return True
        
        # 変更なし
        return False


class AdvancedScraper:
    """高度なWebスクレイパー"""
    
    def __init__(self):
        self.normalizer = URLNormalizer()
        self.hash_manager = ContentHashManager(
            os.path.join(config.SCRAPED_DIR, 'content_hashes.json')
        )
        
        # URL管理
        self.visited_urls: Set[str] = set()
        self.url_queue: deque = deque()
        self.url_priority: Dict[str, int] = defaultdict(int)  # 優先度スコア
        
        # データ管理
        self.scraped_data: List[Dict] = []
        self.skipped_urls: List[Dict] = []
        self.failed_urls: List[Dict] = []
        
        # 統計
        self.stats = {
            'total_visited': 0,
            'new_pages': 0,
            'updated_pages': 0,
            'unchanged_pages': 0,
            'failed_pages': 0,
            'duplicate_urls': 0
        }
        
        # セッション
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 初期URLを追加
        normalized_base = self.normalizer.normalize(config.BASE_URL)
        self.url_queue.append(normalized_base)
        self.url_priority[normalized_base] = 100  # 最高優先度
    
    def calculate_priority(self, url: str, depth: int) -> int:
        """URLの優先度を計算"""
        priority = 50  # ベース優先度
        
        # 深度が浅いほど優先度高
        priority += (10 - depth) * 5
        
        # 重要なキーワードを含むURLは優先度高
        important_keywords = [
            'nyushi', 'admission', '入試',
            'about', 'course', 'コース',
            'student', '学生',
            'news', 'お知らせ'
        ]
        
        for keyword in important_keywords:
            if keyword in url.lower():
                priority += 20
                break
        
        # 画像やダウンロードは優先度低
        if any(ext in url.lower() for ext in ['.jpg', '.png', '.pdf', '.zip']):
            priority -= 30
        
        return max(0, min(100, priority))
    
    def is_valid_url(self, url: str) -> bool:
        """URLが有効かチェック"""
        parsed = urlparse(url)
        
        # ドメインチェック
        if parsed.netloc and parsed.netloc not in config.ALLOWED_DOMAINS:
            return False
        
        # 除外パターンチェック
        for pattern in config.EXCLUDE_PATTERNS:
            if re.search(pattern, url):
                return False
        
        # ファイル拡張子チェック
        excluded_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',  # 画像
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',  # ドキュメント
            '.zip', '.tar', '.gz',  # アーカイブ
            '.mp4', '.avi', '.mov',  # 動画
            '.mp3', '.wav',  # 音声
        ]
        
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
        
        return True
    
    def extract_links(self, soup: BeautifulSoup, base_url: str, depth: int) -> List[Tuple[str, int, int]]:
        """ページから全てのリンクを抽出（URL, 深度, 優先度）"""
        links = []
        seen_in_this_page = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # JavaScriptリンクをスキップ
            if href.startswith('javascript:') or href.startswith('#'):
                continue
            
            # 相対URLを絶対URLに変換
            absolute_url = urljoin(base_url, href)
            
            # 正規化
            normalized_url = self.normalizer.normalize(absolute_url)
            
            # 有効性チェック
            if not self.is_valid_url(normalized_url):
                continue
            
            # このページで既に見たURLはスキップ
            if normalized_url in seen_in_this_page:
                continue
            
            seen_in_this_page.add(normalized_url)
            
            # 既に訪問済みまたはキューにあるURLはスキップ
            if normalized_url in self.visited_urls:
                self.stats['duplicate_urls'] += 1
                continue
            
            # キューにも入っていないかチェック
            if normalized_url in [u for u in self.url_queue]:
                continue
            
            # 優先度計算
            priority = self.calculate_priority(normalized_url, depth + 1)
            
            links.append((normalized_url, depth + 1, priority))
        
        return links
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """ページからメタデータを抽出"""
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'author': '',
            'published_date': ''
        }
        
        # タイトル
        if soup.title and soup.title.string:
            metadata['title'] = soup.title.string.strip()
        elif soup.h1:
            metadata['title'] = soup.h1.get_text(strip=True)
        
        # メタタグ
        meta_tags = {
            'description': ['name', 'description'],
            'keywords': ['name', 'keywords'],
            'author': ['name', 'author'],
            'published_date': ['property', 'article:published_time']
        }
        
        for key, (attr_name, attr_value) in meta_tags.items():
            meta = soup.find('meta', attrs={attr_name: attr_value})
            if meta and meta.get('content'):
                metadata[key] = meta['content'].strip()
        
        return metadata
    
    def extract_content(self, soup: BeautifulSoup) -> str:
        """メインコンテンツを抽出（ノイズ除去）"""
        # 不要なタグを削除
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            tag.decompose()
        
        # メインコンテンツを優先的に抽出
        content_candidates = [
            soup.find('main'),
            soup.find('article'),
            soup.find('div', class_=re.compile(r'content|main', re.I)),
            soup.find('div', id=re.compile(r'content|main', re.I)),
        ]
        
        main_content = None
        for candidate in content_candidates:
            if candidate:
                main_content = candidate
                break
        
        if not main_content:
            main_content = soup.find('body') or soup
        
        # テキスト抽出
        text = main_content.get_text(separator='\n', strip=True)
        
        # 過度な改行を整理
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 短すぎる行を削除（ノイズ除去）
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if len(line.strip()) > 2]
        
        return '\n'.join(cleaned_lines)
    
    def scrape_page(self, url: str, depth: int) -> Optional[Dict]:
        """単一ページをスクレイピング"""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # リンクを先に抽出（nav/footer/header削除前に）
            new_links = self.extract_links(soup, url, depth)

            # リンクをキューに追加
            for link_url, link_depth, link_priority in new_links:
                self.url_queue.append(link_url)
                self.url_priority[link_url] = link_priority

            # メタデータとコンテンツを抽出（ここでnav/footer/headerが削除される）
            metadata = self.extract_metadata(soup)
            content = self.extract_content(soup)

            # 最小サイズチェック
            if len(content) < config.MIN_CHUNK_SIZE:
                self.skipped_urls.append({
                    'url': url,
                    'reason': 'content_too_short',
                    'length': len(content)
                })
                return None
            
            # コンテンツ変更チェック
            has_changed = self.hash_manager.has_changed(url, content)
            
            if not has_changed:
                self.stats['unchanged_pages'] += 1
                self.skipped_urls.append({
                    'url': url,
                    'reason': 'no_changes',
                    'last_updated': self.hash_manager.url_hashes[url]['last_updated']
                })
                return None
            
            # 新規または更新されたページ
            is_new = url not in self.hash_manager.url_hashes or \
                     self.hash_manager.url_hashes[url].get('update_count', 1) == 1
            
            if is_new:
                self.stats['new_pages'] += 1
            else:
                self.stats['updated_pages'] += 1
            
            # データを整形
            result = {
                'url': url,
                'title': metadata['title'],
                'content': content,
                'metadata': metadata,
                'depth': depth,
                'scraped_at': datetime.now().isoformat(),
                'is_new': is_new,
                'content_length': len(content)
            }

            return result
            
        except requests.exceptions.Timeout:
            self.stats['failed_pages'] += 1
            self.failed_urls.append({'url': url, 'error': 'Timeout', 'depth': depth})
            return None
        except requests.exceptions.RequestException as e:
            self.stats['failed_pages'] += 1
            self.failed_urls.append({'url': url, 'error': str(e), 'depth': depth})
            return None
        except Exception as e:
            self.stats['failed_pages'] += 1
            self.failed_urls.append({'url': url, 'error': f'Unexpected: {str(e)}', 'depth': depth})
            return None
    
    def run(self):
        """スクレイピングを実行"""
        print(f"🚀 高度スクレイピング開始: {config.BASE_URL}")
        print(f"📊 最大ページ数: {config.MAX_PAGES}")
        print(f"🔄 増分更新モード: 有効")
        print(f"📋 初期キューサイズ: {len(self.url_queue)}")
        
        start_time = time.time()
        
        with tqdm(total=config.MAX_PAGES, desc="スクレイピング進行中") as pbar:
            while self.url_queue and self.stats['total_visited'] < config.MAX_PAGES:
                # 優先度でソート（高い順）
                self.url_queue = deque(sorted(
                    self.url_queue,
                    key=lambda u: self.url_priority.get(u, 0),
                    reverse=True
                ))
                
                url = self.url_queue.popleft()
                
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                self.stats['total_visited'] += 1
                
                # 深度を推定
                depth = url.count('/') - 2
                
                # デバッグ情報
                if self.stats['total_visited'] <= 3:
                    print(f"\n処理中: {url}")
                    print(f"  深度: {depth}")
                    print(f"  キューサイズ: {len(self.url_queue)}")
                
                result = self.scrape_page(url, depth)
                
                if result:
                    self.scraped_data.append(result)
                
                # プログレスバー更新
                pbar.set_postfix({
                    '新規': self.stats['new_pages'],
                    '更新': self.stats['updated_pages'],
                    '未変更': self.stats['unchanged_pages'],
                    'キュー': len(self.url_queue),
                    'URL': url[:30]
                })
                pbar.update(1)
                
                # 負荷軽減
                time.sleep(config.SCRAPE_DELAY)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ スクレイピング完了 ({elapsed_time:.1f}秒)")
        print(f"\n📊 統計:")
        print(f"  - 訪問URL数: {self.stats['total_visited']}")
        print(f"  - 新規ページ: {self.stats['new_pages']}")
        print(f"  - 更新ページ: {self.stats['updated_pages']}")
        print(f"  - 未変更ページ: {self.stats['unchanged_pages']}")
        print(f"  - 失敗ページ: {self.stats['failed_pages']}")
        print(f"  - 重複URL検出: {self.stats['duplicate_urls']}")
        print(f"  - 最終キューサイズ: {len(self.url_queue)}")
    
    def save_data(self):
        """データを保存"""
        if not self.scraped_data:
            print("✗ 保存する新規/更新データがありません")
            self.hash_manager.save()
            return
        
        # JSONファイルとして保存
        output_file = os.path.join(config.SCRAPED_DIR, 'scraped_data.json')
        
        # 既存データを読み込み
        existing_data = {}
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
                    existing_data = {item['url']: item for item in data_list}
            except:
                existing_data = {}
        
        # 新規/更新データをマージ
        for item in self.scraped_data:
            existing_data[item['url']] = item
        
        merged_data = list(existing_data.values())
        
        # 保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        # 個別ファイルとして保存（新規/更新のみ）
        for item in self.scraped_data:
            url_hash = hashlib.md5(item['url'].encode()).hexdigest()[:8]
            filename = f"page_{url_hash}.txt"
            filepath = os.path.join(config.SCRAPED_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"URL: {item['url']}\n")
                f.write(f"Title: {item['title']}\n")
                f.write(f"Depth: {item['depth']}\n")
                f.write(f"Status: {'新規' if item['is_new'] else '更新'}\n")
                f.write(f"Scraped at: {item['scraped_at']}\n")
                if item['metadata']['description']:
                    f.write(f"Description: {item['metadata']['description']}\n")
                f.write("-" * 80 + "\n\n")
                f.write(item['content'])
        
        # ハッシュデータベースを保存
        self.hash_manager.save()
        
        # 統計を保存
        stats_file = os.path.join(config.SCRAPED_DIR, 'scrape_stats.json')
        stats_data = {
            'stats': self.stats,
            'timestamp': datetime.now().isoformat(),
            'total_pages': len(merged_data)
        }
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        
        # スキップされたURLを保存
        if self.skipped_urls:
            skipped_file = os.path.join(config.SCRAPED_DIR, 'skipped_urls.json')
            with open(skipped_file, 'w', encoding='utf-8') as f:
                json.dump(self.skipped_urls, f, ensure_ascii=False, indent=2)
        
        # 失敗したURLを保存
        if self.failed_urls:
            failed_file = os.path.join(config.SCRAPED_DIR, 'failed_urls.json')
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(self.failed_urls, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ データを保存しました:")
        print(f"  - メインデータ: {output_file}")
        print(f"  - 総ページ数: {len(merged_data)}")
        print(f"  - 今回追加/更新: {len(self.scraped_data)}")
        print(f"  - スキップ: {len(self.skipped_urls)}")
        print(f"  - 失敗: {len(self.failed_urls)}")


def main():
    """メイン処理"""
    # ディレクトリ作成
    config.create_directories()
    
    # スクレイパー実行
    scraper = AdvancedScraper()
    scraper.run()
    scraper.save_data()
    
    print("\n" + "=" * 80)
    print("次のステップ:")
    print("1. python enhanced_vectordb.py でベクトルデータベースを構築/更新")
    print("2. streamlit run app.py でChatbotを起動")
    print("=" * 80)


if __name__ == "__main__":
    main()
