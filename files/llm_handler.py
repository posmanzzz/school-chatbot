"""
LLMハンドラー
Ollamaとの連携を管理
"""

import json
import requests
from typing import List, Dict, Optional, Generator
import config


class OllamaHandler:
    """Ollamaとの連携を管理するクラス"""
    
    def __init__(self, model: str = None):
        """初期化"""
        self.model = model or config.OLLAMA_MODEL
        self.conversation_history = []
        self.base_url = config.OLLAMA_BASE_URL
        
        # モデルが利用可能か確認
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = response.json()
                model_names = [m['name'] for m in available_models.get('models', [])]
                
                if not any(self.model in name for name in model_names):
                    print(f"[WARN] 警告: モデル '{self.model}' が見つかりません")
                    print(f"   利用可能なモデル: {', '.join(model_names)}")
                    print(f"   'ollama pull {self.model}' を実行してください")
                else:
                    print(f"[OK] Ollamaモデル準備完了: {self.model}")
            else:
                print(f"[WARN] 警告: Ollama APIレスポンスエラー (Status: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"[WARN] Ollamaへの接続エラー: {self.base_url} に接続できません")
            print("   Ollamaが起動しているか確認してください: ollama serve")
        except Exception as e:
            print(f"[WARN] 予期しないエラー: {e}")
    
    def create_prompt(self, query: str, context_docs: List[Dict], system_prompt: str) -> str:
        """クエリとコンテキストからプロンプトを生成"""
        # コンテキスト情報を整形
        context_text = ""
        
        if context_docs:
            context_text = "以下の情報を参考にしてください:\n\n"
            
            for idx, doc in enumerate(context_docs, 1):
                metadata = doc.get('metadata', {})
                content = doc.get('content', '')
                
                context_text += f"【情報源 {idx}】\n"
                if metadata.get('title'):
                    context_text += f"タイトル: {metadata['title']}\n"
                if metadata.get('url'):
                    context_text += f"URL: {metadata['url']}\n"
                if metadata.get('category'):
                    context_text += f"カテゴリ: {metadata['category']}\n"
                context_text += f"内容:\n{content}\n\n"
                context_text += "-" * 60 + "\n\n"
        
        # 最終プロンプト
        prompt = f"""{system_prompt}

{context_text}

質問: {query}

回答:"""
        
        return prompt
    
    def generate_response(self, 
                         query: str, 
                         context_docs: List[Dict] = None,
                         stream: bool = True,
                         system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        """応答を生成"""
        
        # 使用するシステムプロンプトを決定
        final_system_prompt = system_prompt or config.SYSTEM_PROMPT
        
        # プロンプト作成
        prompt = self.create_prompt(query, context_docs or [], final_system_prompt)
        
        try:
            if stream:
                # ストリーミングモードで生成
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        'model': self.model,
                        'prompt': prompt,
                        'stream': True,
                        'options': {
                            'temperature': config.TEMPERATURE,
                            'top_p': config.TOP_P,
                            'top_k': config.TOP_K,
                            'num_predict': config.MAX_TOKENS,
                        }
                    },
                    stream=True,
                    timeout=60
                )
                
                response_text = ""
                
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if 'response' in chunk:
                                response_text += chunk['response']
                                yield chunk['response']
                        except json.JSONDecodeError:
                            continue
                
                # 会話履歴に追加
                self.conversation_history.append({
                    'query': query,
                    'response': response_text
                })
                
            else:
                # 非ストリーミングモード
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        'model': self.model,
                        'prompt': prompt,
                        'stream': False,
                        'options': {
                            'temperature': config.TEMPERATURE,
                            'top_p': config.TOP_P,
                            'top_k': config.TOP_K,
                            'num_predict': config.MAX_TOKENS,
                        }
                    },
                    timeout=60
                )
                
                result = response.json()
                response_text = result.get('response', '')
                
                # 会話履歴に追加
                self.conversation_history.append({
                    'query': query,
                    'response': response_text
                })
                
                yield response_text
                
        except requests.exceptions.ConnectionError:
            error_msg = f"エラー: Ollamaに接続できません ({self.base_url})\n\nOllamaが起動しているか確認してください: ollama serve"
            yield error_msg
        except requests.exceptions.Timeout:
            error_msg = "エラー: Ollamaからの応答がタイムアウトしました。モデルが大きすぎる可能性があります。"
            yield error_msg
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            yield error_msg
    
    def clear_history(self):
        """会話履歴をクリア"""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict]:
        """会話履歴を取得"""
        return self.conversation_history


def test_ollama_connection():
    """Ollama接続テスト"""
    print("=" * 80)
    print("Ollama接続テスト")
    print("=" * 80)
    
    try:
        # 利用可能なモデルを確認
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print("\n利用可能なモデル:")
            for model in models.get('models', []):
                print(f"  - {model['name']} (Size: {model.get('size', 'N/A')})")
            
            # テスト生成
            print(f"\n'{config.OLLAMA_MODEL}'でテスト生成中...")
            
            handler = OllamaHandler()
            response_text = ""
            for chunk in handler.generate_response(
                query="こんにちは",
                stream=True
            ):
                response_text += chunk
            
            print(f"\n応答:\n{response_text}")
            print("\n[OK] Ollama接続テスト成功!")
        else:
            print(f"\n[ERROR] エラー: HTTPステータス {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] 接続エラー: {config.OLLAMA_BASE_URL} に接続できません")
        print("\nトラブルシューティング:")
        print("1. Ollamaが起動しているか確認")
        print("   → ターミナルで 'ollama serve' を実行")
        print("2. ポートが正しいか確認")
        print(f"   → 現在の設定: {config.OLLAMA_BASE_URL}")
        print("3. ファイアウォールの設定を確認")
    except Exception as e:
        print(f"\n[ERROR] エラー: {e}")
        print("\nトラブルシューティング:")
        print("1. Ollamaがインストールされているか確認")
        print("   → https://ollama.com/download")
        print("2. Ollamaサービスが起動しているか確認")
        print("   → ターミナルで 'ollama serve' を実行")
        print(f"3. モデルがダウンロードされているか確認")
        print(f"   → 'ollama pull {config.OLLAMA_MODEL}' を実行")


def main():
    """メイン処理 - テスト実行"""
    import sys
    
    if '--test' in sys.argv:
        test_ollama_connection()
    else:
        print("使用方法: python llm_handler.py --test")
        print("Ollama接続テストを実行します")


if __name__ == "__main__":
    main()
