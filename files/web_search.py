"""
Web検索モジュール
DuckDuckGoを使用したWeb検索機能を提供
"""

import requests
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import re


class WebSearcher:
    """DuckDuckGoを使用したWeb検索クラス"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Web検索を実行

        Args:
            query: 検索クエリ
            max_results: 最大結果数

        Returns:
            検索結果のリスト
        """
        try:
            # DuckDuckGo HTML検索を使用
            results = self._search_duckduckgo(query, max_results)
            return results
        except Exception as e:
            print(f"[WARN] Web検索エラー: {e}")
            return []

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """DuckDuckGo HTML版で検索"""
        url = "https://html.duckduckgo.com/html/"

        try:
            response = self.session.post(
                url,
                data={'q': query, 'b': ''},
                timeout=10
            )
            response.raise_for_status()

            # HTMLをパース
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for result in soup.select('.result'):
                if len(results) >= max_results:
                    break

                # タイトルとURL
                title_elem = result.select_one('.result__title a')
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')

                # DuckDuckGoのリダイレクトURLから実際のURLを抽出
                url = self._extract_url(href)
                if not url:
                    continue

                # スニペット
                snippet_elem = result.select_one('.result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''

                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet,
                    'source': 'web_search'
                })

            return results

        except Exception as e:
            print(f"[WARN] DuckDuckGo検索エラー: {e}")
            return []

    def _extract_url(self, href: str) -> Optional[str]:
        """DuckDuckGoのリダイレクトURLから実際のURLを抽出"""
        if not href:
            return None

        # uddg=パラメータから実際のURLを抽出
        import urllib.parse
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)

        if 'uddg' in params:
            return params['uddg'][0]

        # 直接URLの場合
        if href.startswith('http'):
            return href

        return None

    def fetch_page_content(self, url: str, max_length: int = 2000) -> Optional[str]:
        """
        指定URLのページ内容を取得

        Args:
            url: 取得するURL
            max_length: 最大文字数

        Returns:
            ページのテキスト内容
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # スクリプトとスタイルを除去
            for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                tag.decompose()

            # テキストを抽出
            text = soup.get_text(separator='\n', strip=True)

            # 空行を削除して整形
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)

            # 長さ制限
            if len(text) > max_length:
                text = text[:max_length] + '...'

            return text

        except Exception as e:
            print(f"[WARN] ページ取得エラー ({url}): {e}")
            return None


def test_web_search():
    """Web検索テスト"""
    print("=" * 80)
    print("Web検索テスト")
    print("=" * 80)

    searcher = WebSearcher()

    query = "近畿大学工業高等専門学校"
    print(f"\n検索クエリ: {query}")

    results = searcher.search(query, max_results=3)

    if results:
        print(f"\n検索結果: {len(results)}件")
        for i, result in enumerate(results, 1):
            print(f"\n--- 結果 {i} ---")
            print(f"タイトル: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"スニペット: {result['snippet'][:100]}...")
    else:
        print("\n検索結果がありません")


if __name__ == "__main__":
    test_web_search()
