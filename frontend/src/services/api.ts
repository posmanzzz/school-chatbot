import { ApiResponse, ApiStatus } from '../types';

// 開発時はプロキシ経由、本番時は直接アクセス
const API_BASE_URL = '/api';

// デバッグ用ログ
const DEBUG = true;
function log(...args: unknown[]) {
  if (DEBUG) console.log('[API]', ...args);
}

export async function sendChatMessage(
  query: string,
  webSearchEnabled: boolean,
  isDarkMode: boolean
): Promise<ApiResponse> {
  const data = {
    query,
    max_results: 5,
    temperature: 0.3,
    web_search: webSearchEnabled,
    mode: isDarkMode ? 'dark' : 'light',
  };

  try {
    log('Sending chat request:', data);
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    log('Response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      log('Error response:', errorData);
      throw new Error(errorData.detail || `APIエラー: ${response.status}`);
    }

    const result = await response.json();
    log('Success response:', result);
    return {
      response: result.response,
      sources: result.sources || [],
    };
  } catch (error) {
    log('Fetch error:', error);
    const errorMessage = error instanceof Error ? error.message : '不明なエラー';
    return {
      response: `エラーが発生しました: ${errorMessage}\n\nAPIサーバー (localhost:8000) が起動しているか確認してください。\n\n起動コマンド: cd files && python api.py`,
      sources: [],
    };
  }
}

export async function checkApiHealth(): Promise<ApiStatus> {
  try {
    log('Checking API health...');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(`${API_BASE_URL}/health`, {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      log('API is online');
      return 'online';
    }
    log('API returned non-ok status:', response.status);
  } catch (error) {
    log('Health check failed:', error);
  }
  return 'offline';
}
