"""
定期実行スケジューラー
クローラーを自動的に定期実行
"""

import time
import schedule
import subprocess
import logging
from datetime import datetime
import config


# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class CrawlerScheduler:
    """クローラースケジューラー"""
    
    def __init__(self):
        self.is_running = False
    
    def run_crawler(self):
        """クローラーを実行"""
        if self.is_running:
            logger.warning("前回のクローラーがまだ実行中です。スキップします。")
            return
        
        try:
            self.is_running = True
            logger.info("=" * 80)
            logger.info(f"クローラー開始: {datetime.now()}")
            logger.info("=" * 80)
            
            # scraper.pyを実行
            result = subprocess.run(
                ['python', 'scraper.py'],
                capture_output=True,
                text=True,
                timeout=3600  # 1時間でタイムアウト
            )
            
            if result.returncode == 0:
                logger.info("[OK] クローラー完了")
                logger.info(result.stdout)
                
                # データベースを更新
                logger.info("データベースを更新中...")
                db_result = subprocess.run(
                    ['python', 'vectordb.py'],
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30分でタイムアウト
                )
                
                if db_result.returncode == 0:
                    logger.info("[OK] データベース更新完了")
                else:
                    logger.error(f"[ERROR] データベース更新エラー: {db_result.stderr}")
            else:
                logger.error(f"[ERROR] クローラーエラー: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            logger.error("[ERROR] クローラーがタイムアウトしました")
        except Exception as e:
            logger.error(f"[ERROR] 予期しないエラー: {e}")
        finally:
            self.is_running = False
            logger.info("=" * 80)
    
    def start(self, interval_hours: int = 24):
        """スケジューラーを開始"""
        logger.info(f"スケジューラー開始: {interval_hours}時間ごとに実行")
        
        # 初回実行
        self.run_crawler()
        
        # 定期実行をスケジュール
        schedule.every(interval_hours).hours.do(self.run_crawler)
        
        # ループ実行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック


def main():
    """メイン処理"""
    import sys
    
    # 実行間隔（デフォルト: 24時間）
    interval_hours = 24
    
    for arg in sys.argv:
        if arg.startswith('--interval='):
            interval_hours = int(arg.split('=')[1])
    
    scheduler = CrawlerScheduler()
    
    try:
        scheduler.start(interval_hours=interval_hours)
    except KeyboardInterrupt:
        logger.info("\nスケジューラーを停止しました")


if __name__ == "__main__":
    main()
