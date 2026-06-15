"""
Streamlitチャットボットアプリケーション
学校情報に関する質問に回答
"""

import streamlit as st
from datetime import datetime
import config
from vectordb import VectorDatabase
from llm_handler import OllamaHandler


# ページ設定
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide"
)


@st.cache_resource
def initialize_system():
    """システムを初期化（キャッシュされる）"""
    with st.spinner("システムを初期化しています..."):
        db = VectorDatabase()
        llm = OllamaHandler()
    return db, llm


def format_sources(search_results):
    """検索結果をフォーマット"""
    if not search_results:
        return "参照情報なし"
    
    sources_text = "**参照した情報源:**\n\n"
    
    for idx, result in enumerate(search_results, 1):
        metadata = result.get('metadata', {})
        
        sources_text += f"**[{idx}] {metadata.get('title', '情報源')}**\n"
        
        if metadata.get('url'):
            sources_text += f"- URL: {metadata['url']}\n"
        
        if metadata.get('category'):
            sources_text += f"- カテゴリ: {metadata['category']}\n"
        
        sources_text += f"- 関連度: {1 - result.get('distance', 0):.2%}\n"
        sources_text += "\n"
    
    return sources_text


def main():
    """メインアプリケーション"""
    
    # タイトル
    st.title(f"{config.PAGE_ICON} {config.PAGE_TITLE}")
    
    # サイドバー
    with st.sidebar:
        st.header("⚙️ 設定")
        
        # 検索結果数
        top_k = st.slider(
            "検索する関連情報数",
            min_value=1,
            max_value=10,
            value=config.TOP_K_RESULTS,
            help="質問に関連する情報をいくつ取得するか"
        )
        
        # 温度設定
        temperature = st.slider(
            "回答の創造性",
            min_value=0.0,
            max_value=1.0,
            value=config.TEMPERATURE,
            step=0.1,
            help="低いほど確定的、高いほど創造的な回答"
        )
        
        st.divider()
        
        # システム情報
        st.header("📊 システム情報")
        
        try:
            db, llm = initialize_system()
            stats = db.get_stats()
            
            st.metric("総ドキュメント数", stats['total_chunks'])
            
            if stats['by_source']:
                st.write("**ソース別:**")
                for source, count in stats['by_source'].items():
                    st.write(f"- {source}: {count}件")
            
            st.write(f"**使用モデル:** {llm.model}")
            
        except Exception as e:
            st.error(f"エラー: {e}")
        
        st.divider()
        
        # 履歴クリアボタン
        if st.button("🗑️ チャット履歴をクリア"):
            st.session_state.messages = []
            if 'llm' in st.session_state:
                st.session_state.llm.clear_history()
            st.rerun()
        
        st.divider()
        
        # 使い方
        with st.expander("📖 使い方"):
            st.markdown("""
            **質問例:**
            - 入試の日程を教えて
            - 学生寮について知りたい
            - 図書館の開館時間は?
            - 各コースの特徴を比較して
            - 就職実績について
            
            **ヒント:**
            - 具体的な質問をすると、より正確な回答が得られます
            - 複数の観点から質問できます
            - 不明な点があれば、遠慮なく質問してください
            """)
    
    # システム初期化
    try:
        if 'db' not in st.session_state:
            st.session_state.db, st.session_state.llm = initialize_system()
        
        db = st.session_state.db
        llm = st.session_state.llm
        
    except Exception as e:
        st.error(f"""
        システムの初期化に失敗しました: {e}
        
        **確認事項:**
        1. データベースが構築されているか確認してください
           → `python vectordb.py` を実行
        2. Ollamaが起動しているか確認してください
           → `ollama serve` を実行
        3. モデルがダウンロードされているか確認してください
           → `ollama pull {config.OLLAMA_MODEL}` を実行
        """)
        st.stop()
    
    # チャット履歴初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # 初期メッセージ
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"こんにちは!{config.PAGE_TITLE.replace('Chatbot', '')}についてお気軽に質問してください。",
            "sources": None
        })
    
    # チャット履歴を表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 情報源を表示
            if message.get("sources"):
                with st.expander("📚 参照情報を表示"):
                    st.markdown(message["sources"])
    
    # ユーザー入力
    if prompt := st.chat_input("質問を入力してください..."):
        
        # ユーザーメッセージを追加
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "sources": None
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # アシスタント応答
        with st.chat_message("assistant"):
            
            # 関連情報を検索
            with st.spinner("関連情報を検索中..."):
                search_results = db.search(prompt, n_results=top_k)
            
            # 検索結果を表示（オプション）
            if search_results:
                st.caption(f"✓ {len(search_results)}件の関連情報を見つけました")
            
            # LLMで応答生成
            response_placeholder = st.empty()
            full_response = ""
            
            # 温度パラメータを更新
            llm.model = config.OLLAMA_MODEL  # モデル確認
            config.TEMPERATURE = temperature  # 一時的に更新
            
            try:
                for chunk in llm.generate_response(prompt, search_results, stream=True):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
            except Exception as e:
                error_msg = f"エラーが発生しました: {e}\n\nOllamaが起動しているか確認してください。"
                response_placeholder.error(error_msg)
                full_response = error_msg
            
            # 情報源を表示
            sources_text = format_sources(search_results)
            with st.expander("📚 参照情報を表示"):
                st.markdown(sources_text)
            
            # メッセージ履歴に追加
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": sources_text
            })
    
    # フッター
    st.divider()
    st.caption(f"Powered by Ollama ({config.OLLAMA_MODEL}) | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


if __name__ == "__main__":
    main()
