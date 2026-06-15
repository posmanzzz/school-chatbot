"""
Webスクレイピングスクリプト
学校のWebサイトから情報を収集し、データベースに保存
"""

import os
import re
import json
import time
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import config


class SchoolWebScraper:
    """学校Webサイトのスクレイパー"""
    
    def __init__(self):
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = [config.BASE_URL]
        self.scraped_data: List[Dict] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def is_valid_url(self, url: str) -> bool:
        """URLが有効かチェック"""
        parsed = urlparse(url)
        
        # ドメインチェック
        if parsed.netloc not in config.ALLOWED_DOMAINS:
            return False
            
        # 除外パターンチェック
        for pattern in config.EXCLUDE_PATTERNS:
            if re.search(pattern, url):
                return False
                
        return True
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """ページから全てのリンクを抽出"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # 相対URLを絶対URLに変換
            absolute_url = urljoin(base_url, href)
            # フラグメント(#)を削除
            absolute_url = absolute_url.split('#')[0]
            
            if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                links.append(absolute_url)
                
        return links
    
    def extract_text_content(self, soup: BeautifulSoup) -> Dict[str, str]:
        """ページからテキストコンテンツを抽出"""
        # 不要なタグを削除
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # タイトル取得
        title = ""
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else ""
        elif soup.h1:
            title = soup.h1.get_text(strip=True)
        
        # メインコンテンツを取得
        content = soup.get_text(separator='\n', strip=True)
        
        # 複数の改行を1つにまとめる
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        return {
            'title': title,
            'content': content
        }
    
    def scrape_page(self, url: str) -> bool:
        """単一ページをスクレイピング"""
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            # リンクを先に抽出（nav/footer/header削除前に）
            new_links = self.extract_links(soup, url)
            self.to_visit.extend(new_links)

            # テキストコンテンツを抽出（ここでnav/footer/headerが削除される）
            content_data = self.extract_text_content(soup)

            # 最小サイズチェック
            if len(content_data['content']) < config.MIN_CHUNK_SIZE:
                return False

            # データを保存
            self.scraped_data.append({
                'url': url,
                'title': content_data['title'],
                'content': content_data['content'],
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            return True
            
        except Exception as e:
            print(f"[ERROR] エラー ({url}): {str(e)}")
            return False
    
    def run(self):
        """スクレイピングを実行"""
        print(f"[START] スクレイピング開始: {config.BASE_URL}")
        print(f"[INFO] 最大ページ数: {config.MAX_PAGES}")
        
        with tqdm(total=config.MAX_PAGES, desc="スクレイピング進行中") as pbar:
            while self.to_visit and len(self.visited_urls) < config.MAX_PAGES:
                url = self.to_visit.pop(0)
                
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                
                if self.scrape_page(url):
                    pbar.set_postfix({'成功': len(self.scraped_data), 'URL': url[:50]})
                
                pbar.update(1)
                
                # 負荷軽減のため待機
                time.sleep(config.SCRAPE_DELAY)
        
        print(f"\n[OK] スクレイピング完了")
        print(f"  - 訪問したURL数: {len(self.visited_urls)}")
        print(f"  - 収集したページ数: {len(self.scraped_data)}")
        
    def save_data(self):
        """スクレイピングしたデータを保存"""
        if not self.scraped_data:
            print("[WARN] 保存するデータがありません")
            return
        
        # JSONファイルとして保存
        output_file = os.path.join(config.SCRAPED_DIR, 'scraped_data.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, ensure_ascii=False, indent=2)
        
        # 各ページを個別のテキストファイルとして保存
        for idx, data in enumerate(self.scraped_data):
            filename = f"page_{idx:04d}.txt"
            filepath = os.path.join(config.SCRAPED_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"URL: {data['url']}\n")
                f.write(f"Title: {data['title']}\n")
                f.write(f"Scraped at: {data['scraped_at']}\n")
                f.write("-" * 80 + "\n\n")
                f.write(data['content'])
        
        print(f"[OK] データを保存しました: {output_file}")
        print(f"  - 個別ファイル数: {len(self.scraped_data)}")


def main():
    """メイン処理"""
    # ディレクトリ作成
    config.create_directories()
    
    # スクレイパー実行
    scraper = SchoolWebScraper()
    scraper.run()
    scraper.save_data()
    
    print("\n" + "=" * 80)
    print("次のステップ:")
    print("1. python vectordb.py でベクトルデータベースを構築")
    print("2. streamlit run app.py でChatbotを起動")
    print("   または python api.py でAPIサーバーを起動")
    print("=" * 80)


if __name__ == "__main__":
    main()
