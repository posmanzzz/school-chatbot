"""
手動情報追加ツール
スクレイピングできない情報を手動で追加
"""

import os
import json
import time
from typing import Optional
import config


class ManualDataAdder:
    """手動でデータを追加するクラス"""
    
    def __init__(self):
        self.data_file = os.path.join(config.MANUAL_DIR, 'manual_data.json')
        self.load_existing_data()
    
    def load_existing_data(self):
        """既存の手動追加データを読み込み"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.manual_data = json.load(f)
        else:
            self.manual_data = []
        
        print(f"既存の手動追加データ: {len(self.manual_data)}件")
    
    def add_entry(self, title: str, content: str, source: str = "手動追加", 
                  category: str = "その他", url: Optional[str] = None):
        """新しいエントリーを追加"""
        entry = {
            'id': f"manual_{len(self.manual_data):04d}",
            'title': title,
            'content': content,
            'source': source,
            'category': category,
            'url': url or "",
            'added_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.manual_data.append(entry)
        print(f"✓ エントリーを追加しました: {title}")
        
        return entry
    
    def save_data(self):
        """データをファイルに保存"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.manual_data, f, ensure_ascii=False, indent=2)
        
        # 個別テキストファイルとしても保存
        for idx, entry in enumerate(self.manual_data):
            filename = f"manual_{idx:04d}.txt"
            filepath = os.path.join(config.MANUAL_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"ID: {entry['id']}\n")
                f.write(f"Title: {entry['title']}\n")
                f.write(f"Category: {entry['category']}\n")
                f.write(f"Source: {entry['source']}\n")
                if entry['url']:
                    f.write(f"URL: {entry['url']}\n")
                f.write(f"Added at: {entry['added_at']}\n")
                f.write("-" * 80 + "\n\n")
                f.write(entry['content'])
        
        print(f"✓ データを保存しました: {self.data_file}")
        print(f"  - 総エントリー数: {len(self.manual_data)}")
    
    def list_entries(self):
        """全エントリーのリストを表示"""
        if not self.manual_data:
            print("手動追加されたデータはありません")
            return
        
        print("\n" + "=" * 80)
        print(f"手動追加データ一覧 ({len(self.manual_data)}件)")
        print("=" * 80)
        
        for idx, entry in enumerate(self.manual_data):
            print(f"\n[{idx + 1}] ID: {entry['id']}")
            print(f"    Title: {entry['title']}")
            print(f"    Category: {entry['category']}")
            print(f"    Added: {entry['added_at']}")
            print(f"    Content: {entry['content'][:100]}...")
    
    def delete_entry(self, entry_id: str):
        """エントリーを削除"""
        original_count = len(self.manual_data)
        self.manual_data = [e for e in self.manual_data if e['id'] != entry_id]
        
        if len(self.manual_data) < original_count:
            print(f"✓ エントリーを削除しました: {entry_id}")
            return True
        else:
            print(f"✗ エントリーが見つかりません: {entry_id}")
            return False


def interactive_mode():
    """対話モードでデータを追加"""
    adder = ManualDataAdder()
    
    print("\n" + "=" * 80)
    print("手動情報追加ツール - 対話モード")
    print("=" * 80)
    print("\nコマンド:")
    print("  add    - 新しい情報を追加")
    print("  list   - 既存の情報を一覧表示")
    print("  delete - 情報を削除")
    print("  quit   - 終了")
    print("=" * 80)
    
    while True:
        command = input("\nコマンドを入力してください: ").strip().lower()
        
        if command == 'quit':
            print("終了します")
            break
        
        elif command == 'add':
            print("\n--- 新しい情報を追加 ---")
            title = input("タイトル: ").strip()
            if not title:
                print("✗ タイトルは必須です")
                continue
            
            category = input("カテゴリ (入試/学生生活/施設/その他): ").strip() or "その他"
            url = input("参照URL (オプション): ").strip()
            
            print("\n内容を入力してください (複数行可、終了は空行を2回入力):")
            content_lines = []
            empty_count = 0
            
            while True:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                    content_lines.append(line)
            
            content = "\n".join(content_lines).strip()
            
            if not content:
                print("✗ 内容は必須です")
                continue
            
            adder.add_entry(
                title=title,
                content=content,
                category=category,
                url=url if url else None
            )
            adder.save_data()
        
        elif command == 'list':
            adder.list_entries()
        
        elif command == 'delete':
            adder.list_entries()
            entry_id = input("\n削除するエントリーのIDを入力: ").strip()
            if adder.delete_entry(entry_id):
                adder.save_data()
        
        else:
            print("✗ 不明なコマンドです")


def add_sample_data():
    """サンプルデータを追加（初回セットアップ用）"""
    adder = ManualDataAdder()
    
    # サンプルデータ
    samples = [
        {
            'title': '学生寮の門限について',
            'content': '''学生寮の門限は以下の通りです：

平日（月〜金）: 22:00
休日前（金・土）: 23:00
日曜日・祝日: 21:00

門限を過ぎる場合は、事前に寮監に連絡が必要です。
無断での門限破りは、警告の対象となります。''',
            'category': '学生生活',
            'source': '学生寮規則より'
        },
        {
            'title': '図書館の開館時間',
            'content': '''図書館の開館時間：

平日: 9:00 - 20:00
土曜日: 9:00 - 17:00
日曜日・祝日: 休館

定期試験期間中は延長開館を実施します（21:00まで）。
詳細は図書館掲示板でお知らせします。''',
            'category': '施設',
            'source': '図書館案内'
        },
        {
            'title': '編入学試験の出願期間',
            'content': '''令和7年度 編入学試験の出願期間：

出願期間: 2025年6月1日(日) ～ 6月15日(日)
試験日: 2025年7月5日(土)
合格発表: 2025年7月12日(土)

出願書類は本校ホームページからダウンロード可能です。
郵送の場合は、出願期間内必着となります。''',
            'category': '入試',
            'source': '令和7年度入試要項'
        }
    ]
    
    for sample in samples:
        adder.add_entry(**sample)
    
    adder.save_data()
    print(f"\n✓ サンプルデータを{len(samples)}件追加しました")


def main():
    """メイン処理"""
    import sys
    
    config.create_directories()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--sample':
        # サンプルデータ追加モード
        add_sample_data()
    else:
        # 対話モード
        interactive_mode()


if __name__ == "__main__":
    main()
