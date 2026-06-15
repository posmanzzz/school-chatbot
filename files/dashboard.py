"""
管理ダッシュボード
クローラーとデータベースの状況を監視
"""

import streamlit as st
import json
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import config
from vectordb import VectorDatabase


st.set_page_config(
    page_title="Chatbot管理ダッシュボード",
    page_icon="📊",
    layout="wide"
)


@st.cache_resource
def load_database():
    """データベースを読み込み"""
    return VectorDatabase()


def load_scrape_database():
    """スクレイピングデータベースを読み込み"""
    db_file = os.path.join(config.SCRAPED_DIR, 'scrape_database.json')
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_scraped_data():
    """スクレイピングデータを読み込み"""
    data_file = os.path.join(config.SCRAPED_DIR, 'scraped_data.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def load_failed_urls():
    """失敗したURLを読み込み"""
    failed_file = os.path.join(config.SCRAPED_DIR, 'failed_urls.json')
    if os.path.exists(failed_file):
        with open(failed_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def main():
    """メインダッシュボード"""
    
    st.title("📊 Chatbot管理ダッシュボード")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 操作")
        
        if st.button("🔄 データを再読み込み"):
            st.cache_resource.clear()
            st.rerun()
        
        st.divider()
        
        st.header("📋 クイックアクション")
        
        if st.button("🕷️ クローラーを実行"):
            with st.spinner("クローラーを実行中..."):
                import subprocess
                result = subprocess.run(
                    ['python', 'advanced_scraper.py'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    st.success("✓ クローラー完了")
                else:
                    st.error(f"✗ エラー: {result.stderr}")
        
        if st.button("💾 データベースを更新"):
            with st.spinner("データベースを更新中..."):
                import subprocess
                result = subprocess.run(
                    ['python', 'vectordb.py'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    st.success("✓ データベース更新完了")
                else:
                    st.error(f"✗ エラー: {result.stderr}")
    
    # メインコンテンツ
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 概要", 
        "🕷️ クローラー状況", 
        "💾 データベース", 
        "⚠️ エラー"
    ])
    
    # タブ1: 概要
    with tab1:
        st.header("システム概要")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # データベース統計
        try:
            db = load_database()
            stats = db.get_stats()
            
            with col1:
                st.metric(
                    "総チャンク数",
                    f"{stats['total_chunks']:,}",
                    delta=None
                )
            
            with col2:
                scraped_data = load_scraped_data()
                st.metric(
                    "スクレイピング済みページ",
                    f"{len(scraped_data):,}",
                    delta=None
                )
            
            with col3:
                failed_urls = load_failed_urls()
                st.metric(
                    "失敗したURL",
                    f"{len(failed_urls):,}",
                    delta=None,
                    delta_color="inverse"
                )
            
            with col4:
                scrape_db = load_scrape_database()
                if scrape_db and 'last_updated' in scrape_db:
                    last_updated = scrape_db['last_updated']
                    st.metric(
                        "最終更新",
                        datetime.fromisoformat(last_updated).strftime("%m/%d %H:%M")
                    )
                else:
                    st.metric("最終更新", "N/A")
            
            # ソース別グラフ
            st.subheader("ソース別データ分布")
            
            if stats['by_source']:
                source_df = pd.DataFrame([
                    {'ソース': source, 'チャンク数': count}
                    for source, count in stats['by_source'].items()
                ])
                
                fig = px.pie(
                    source_df,
                    values='チャンク数',
                    names='ソース',
                    title='ソース別データ分布'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # カテゴリ別グラフ
            if stats['by_category']:
                st.subheader("カテゴリ別データ分布")
                
                category_df = pd.DataFrame([
                    {'カテゴリ': category, 'チャンク数': count}
                    for category, count in stats['by_category'].items()
                ])
                
                fig = px.bar(
                    category_df,
                    x='カテゴリ',
                    y='チャンク数',
                    title='カテゴリ別データ分布'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"データベース読み込みエラー: {e}")
    
    # タブ2: クローラー状況
    with tab2:
        st.header("クローラー状況")
        
        scrape_db = load_scrape_database()
        
        if scrape_db:
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("総URL数", f"{scrape_db.get('total_urls', 0):,}")
            
            with col2:
                if 'last_updated' in scrape_db:
                    last_updated = datetime.fromisoformat(scrape_db['last_updated'])
                    st.metric(
                        "最終実行",
                        last_updated.strftime("%Y-%m-%d %H:%M:%S")
                    )
            
            # URL一覧
            st.subheader("スクレイピング済みURL一覧")
            
            url_metadata = scrape_db.get('url_metadata', {})
            
            if url_metadata:
                url_list = []
                for url, metadata in url_metadata.items():
                    url_list.append({
                        'URL': url,
                        'タイトル': metadata.get('title', 'N/A'),
                        '深度': metadata.get('depth', 0),
                        '最終取得': metadata.get('last_scraped', 'N/A')
                    })
                
                url_df = pd.DataFrame(url_list)
                
                # フィルター
                search_query = st.text_input("🔍 URLを検索")
                if search_query:
                    url_df = url_df[url_df['URL'].str.contains(search_query, case=False)]
                
                st.dataframe(url_df, use_container_width=True, height=400)
                
                # 深度別分布
                st.subheader("深度別URL分布")
                depth_counts = url_df['深度'].value_counts().sort_index()
                
                fig = px.bar(
                    x=depth_counts.index,
                    y=depth_counts.values,
                    labels={'x': '深度', 'y': 'URL数'},
                    title='深度別URL分布'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("スクレイピングデータベースが見つかりません")
    
    # タブ3: データベース
    with tab3:
        st.header("ベクトルデータベース詳細")
        
        try:
            db = load_database()
            stats = db.get_stats()
            
            st.metric("総チャンク数", f"{stats['total_chunks']:,}")
            
            # ソース別詳細
            st.subheader("ソース別詳細")
            
            if stats['by_source']:
                source_table = pd.DataFrame([
                    {'ソース': source, 'チャンク数': count, '割合': f"{count/stats['total_chunks']*100:.1f}%"}
                    for source, count in stats['by_source'].items()
                ])
                st.dataframe(source_table, use_container_width=True)
            
            # カテゴリ別詳細
            st.subheader("カテゴリ別詳細")
            
            if stats['by_category']:
                category_table = pd.DataFrame([
                    {'カテゴリ': category, 'チャンク数': count, '割合': f"{count/stats['total_chunks']*100:.1f}%"}
                    for category, count in stats['by_category'].items()
                ])
                st.dataframe(category_table, use_container_width=True)
            
            # テスト検索
            st.subheader("🔍 テスト検索")
            
            test_query = st.text_input("検索クエリを入力")
            test_k = st.slider("取得件数", 1, 10, 5)
            
            if st.button("検索実行") and test_query:
                with st.spinner("検索中..."):
                    results = db.search(test_query, n_results=test_k)
                    
                    st.write(f"**{len(results)}件の結果:**")
                    
                    for idx, result in enumerate(results, 1):
                        with st.expander(f"[{idx}] {result['metadata'].get('title', 'N/A')}"):
                            st.write(f"**URL:** {result['metadata'].get('url', 'N/A')}")
                            st.write(f"**カテゴリ:** {result['metadata'].get('category', 'N/A')}")
                            st.write(f"**関連度:** {1 - result.get('distance', 0):.2%}")
                            st.write(f"**内容:**")
                            st.text(result['content'][:500] + "...")
        
        except Exception as e:
            st.error(f"データベースエラー: {e}")
    
    # タブ4: エラー
    with tab4:
        st.header("エラーログ")
        
        failed_urls = load_failed_urls()
        
        if failed_urls:
            st.warning(f"⚠️ {len(failed_urls)}件の失敗したURLがあります")
            
            failed_df = pd.DataFrame(failed_urls)
            st.dataframe(failed_df, use_container_width=True)
            
            # エラー種類別集計
            if 'error' in failed_df.columns:
                st.subheader("エラー種類別集計")
                error_counts = failed_df['error'].value_counts()
                
                fig = px.bar(
                    x=error_counts.index,
                    y=error_counts.values,
                    labels={'x': 'エラー種類', 'y': '件数'},
                    title='エラー種類別件数'
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✓ エラーはありません")
        
        # スケジューラーログ
        st.subheader("📋 スケジューラーログ")
        
        log_file = "scheduler.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = f.readlines()
                
                # 最新100行を表示
                st.text_area(
                    "ログ（最新100行）",
                    "".join(logs[-100:]),
                    height=300
                )
        else:
            st.info("スケジューラーログがありません")


if __name__ == "__main__":
    main()
