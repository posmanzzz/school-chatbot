# 近大高専チャット フロントエンド仕様書・教科書

## 目次
1. [プロジェクト概要](#1-プロジェクト概要)
2. [技術スタック](#2-技術スタック)
3. [ディレクトリ構造](#3-ディレクトリ構造)
4. [各ファイルの解説](#4-各ファイルの解説)
5. [データの流れ](#5-データの流れ)
6. [学習ポイント](#6-学習ポイント)

---

## 1. プロジェクト概要

このアプリは「近大高専チャット」という、学校の情報を質問できるAIチャットボットです。

### 主な機能
- Googleログイン認証
- AIとのチャット機能
- 検索履歴の保存
- ダークモード切り替え
- よくある質問のショートカット

---

## 2. 技術スタック

| 技術 | 用途 | 公式サイト |
|------|------|-----------|
| React | UIライブラリ | https://react.dev |
| TypeScript | 型付きJavaScript | https://www.typescriptlang.org |
| Vite | ビルドツール | https://vitejs.dev |
| Chakra UI | UIコンポーネント | https://chakra-ui.com |
| Firebase | 認証・データベース | https://firebase.google.com |

### なぜこれらを使うのか？

**React**: UIを「コンポーネント」という部品に分けて作れる。再利用しやすい。

**TypeScript**: JavaScriptに「型」を追加。エラーを事前に防げる。

**Chakra UI**: すぐ使えるボタンやカードなどの部品が揃っている。

**Firebase**: バックエンドを自分で作らなくても認証やデータ保存ができる。

---

## 3. ディレクトリ構造

```
src/
├── components/     # 画面の部品（コンポーネント）
├── hooks/          # カスタムフック（ロジックの再利用）
├── services/       # 外部サービスとの通信
├── types/          # 型定義
├── utils/          # 便利関数
├── theme/          # デザイン設定
├── App.tsx         # アプリのメイン
└── main.tsx        # エントリーポイント
```

---

## 4. 各ファイルの解説

### 4.1 エントリーポイント

#### `main.tsx` - アプリの起動点

```tsx
// これがアプリの一番最初に実行されるファイル
import { ChakraProvider } from '@chakra-ui/react';
import App from './App';
import theme from './theme';

// ChakraProviderでアプリ全体にテーマを適用
<ChakraProvider theme={theme}>
  <App />
</ChakraProvider>
```

**学習ポイント**: `Provider`パターン - アプリ全体で共有したいデータを提供する仕組み

---

### 4.2 メインコンポーネント

#### `App.tsx` - アプリの中心

```tsx
function App() {
  // カスタムフックで機能を取得
  const { user, loading, signInWithGoogle, signOut } = useAuth();
  const { messages, isLoading, sendMessage } = useChat(user);

  // ログイン前はログイン画面を表示
  if (!user) {
    return <LoginScreen onLogin={signInWithGoogle} />;
  }

  // ログイン後はメイン画面を表示
  return (
    <Box>
      <Header user={user} />
      <ChatContainer messages={messages} onSend={sendMessage} />
    </Box>
  );
}
```

**学習ポイント**:
- 条件分岐でログイン状態によって表示を切り替える
- カスタムフックで複雑なロジックを隠蔽

---

### 4.3 コンポーネント（components/）

#### `LoginScreen.tsx` - ログイン画面

**役割**: Googleログインボタンを表示

```tsx
interface LoginScreenProps {
  onLogin: () => Promise<void>;  // ログイン処理を親から受け取る
  isLoading: boolean;            // ローディング状態
}

export function LoginScreen({ onLogin, isLoading }: LoginScreenProps) {
  return (
    <Button onClick={onLogin} isLoading={isLoading}>
      Googleでログイン
    </Button>
  );
}
```

**学習ポイント**:
- `interface`で受け取る値の型を定義
- 親から関数を受け取って実行する（コールバック）

---

#### `Header.tsx` - ヘッダー

**役割**: ロゴ、ステータス表示、各種ボタン

```tsx
// useColorModeValue: ダークモードに対応した色を返す
const bgColor = useColorModeValue('white', 'gray.800');
// ライトモードでは'white'、ダークモードでは'gray.800'を使用
```

**学習ポイント**: Chakra UIのダークモード対応

---

#### `ChatContainer.tsx` - チャットエリア

**役割**: メッセージ一覧と入力欄を含むコンテナ

```tsx
<Box
  maxW="700px"           // 最大幅
  h="calc(100vh - 140px)" // 高さ計算
  display="flex"
  flexDirection="column"
>
  <ChatBox messages={messages} />
  <ChatInput onSend={onSendMessage} />
</Box>
```

**学習ポイント**: Flexboxレイアウト

---

#### `ChatMessage.tsx` - メッセージ表示

**役割**: 1つのメッセージを表示

```tsx
const isUser = message.sender === 'user';

// ユーザーとAIで配置を変える
<Box alignSelf={isUser ? 'flex-end' : 'flex-start'}>
  {/* ユーザー: 右寄せ、AI: 左寄せ */}
</Box>
```

**学習ポイント**: 三項演算子で条件分岐

---

#### `ChatInput.tsx` - 入力欄

**役割**: メッセージ入力と送信

```tsx
const [message, setMessage] = useState('');

const handleSubmit = async () => {
  if (!message.trim()) return;  // 空なら何もしない
  await onSend(message);        // 送信処理
  setMessage('');               // 入力欄をクリア
};

// Enterキーで送信
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSubmit();
  }
};
```

**学習ポイント**:
- `useState`で状態管理
- キーボードイベント処理

---

#### `QuickQuestions.tsx` - よくある質問

**役割**: ワンクリックで質問できるボタン

```tsx
const QUESTIONS = [
  { text: '入学試験', question: '入学試験について教えてください' },
  { text: '学科紹介', question: '学科の特徴を教えてください' },
  // ...
];

// 配列をmapでボタンに変換
{QUESTIONS.map((q, index) => (
  <Button key={index} onClick={() => onQuestionClick(q.question)}>
    {q.text}
  </Button>
))}
```

**学習ポイント**: 配列データからUIを生成する

---

### 4.4 カスタムフック（hooks/）

#### `useAuth.ts` - 認証管理

```tsx
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 認証状態の変化を監視
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    // クリーンアップ（監視を停止）
    return () => unsubscribe();
  }, []);

  return { user, loading, signInWithGoogle, signOut };
}
```

**学習ポイント**:
- `useEffect`の依存配列が空 = マウント時に1回だけ実行
- クリーンアップ関数でメモリリークを防ぐ

---

#### `useChat.ts` - チャット管理

```tsx
export function useChat(user: User | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (message: string) => {
    // 1. ユーザーメッセージを追加
    setMessages(prev => [...prev, { content: message, sender: 'user' }]);

    // 2. APIに送信
    setIsLoading(true);
    const result = await sendChatMessage(message);

    // 3. AIの返答を追加
    setMessages(prev => [...prev, { content: result.response, sender: 'ai' }]);
    setIsLoading(false);
  }, []);

  return { messages, isLoading, sendMessage };
}
```

**学習ポイント**:
- `useCallback`で関数をメモ化（不要な再生成を防ぐ）
- スプレッド演算子で配列に要素を追加

---

#### `useSearchHistory.ts` - 検索履歴

**役割**: 検索履歴のCRUD操作

```tsx
// Firestoreからデータを取得
const historyRef = collection(db, 'users', user.uid, 'searchHistory');
const q = query(historyRef, orderBy('timestamp', 'desc'), limit(50));
const snapshot = await getDocs(q);
```

**学習ポイント**: Firestoreのクエリ操作

---

### 4.5 サービス（services/）

#### `firebase.ts` - Firebase設定

```tsx
// Firebaseの初期化
const app = initializeApp(firebaseConfig);

// 各サービスをエクスポート
export const auth = getAuth(app);       // 認証
export const db = getFirestore(app);    // データベース
export const googleProvider = new GoogleAuthProvider();
```

---

#### `api.ts` - API通信

```tsx
export async function sendChatMessage(query: string): Promise<ApiResponse> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error(`APIエラー: ${response.status}`);
  }

  return response.json();
}
```

**学習ポイント**:
- `fetch`でHTTPリクエスト
- `async/await`で非同期処理

---

### 4.6 型定義（types/）

#### `index.ts` - 型定義

```tsx
// チャットメッセージの型
interface ChatMessage {
  content: string;           // メッセージ本文
  sender: 'user' | 'ai';     // 送信者（ユーザーかAI）
  sources?: Source[];        // 参照元（任意）
}

// APIのレスポンス型
interface ApiResponse {
  response: string;
  sources: Source[];
}
```

**学習ポイント**:
- `interface`でオブジェクトの形を定義
- `?`で任意のプロパティ
- ユニオン型（`'user' | 'ai'`）

---

### 4.7 ユーティリティ（utils/）

#### `markdown.ts` - 便利関数

```tsx
export function getTimeAgo(timestamp: Date): string {
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diff < 60) return 'たった今';
  if (diff < 3600) return `${Math.floor(diff / 60)}分前`;
  // ...
}
```

**学習ポイント**: 純粋関数（副作用のない関数）

---

## 5. データの流れ

```
[ユーザー操作]
      ↓
[コンポーネント] ← UIを表示
      ↓
[カスタムフック] ← ロジックを処理
      ↓
[サービス] ← 外部と通信
      ↓
[Firebase/API] ← データを保存・取得
```

### 例：メッセージ送信の流れ

1. ユーザーがChatInputでメッセージを入力、送信ボタンをクリック
2. ChatInputが`onSend`関数を呼び出し
3. App.tsxの`handleSendMessage`が実行
4. useChatの`sendMessage`が呼ばれる
5. api.tsの`sendChatMessage`がAPIにリクエスト
6. 返答を受け取り、messagesステートを更新
7. ChatMessageコンポーネントが新しいメッセージを表示

---

## 6. 学習ポイント

### 6.1 Reactの基本概念

| 概念 | 説明 | 使用例 |
|------|------|--------|
| コンポーネント | UIの部品 | `<Header />`, `<ChatMessage />` |
| Props | 親から子へのデータ渡し | `<Button onClick={handleClick}>` |
| State | コンポーネントの状態 | `useState` |
| Effect | 副作用の処理 | `useEffect` |

### 6.2 TypeScriptの基本

```tsx
// 型注釈
const name: string = 'hello';
const count: number = 42;

// インターフェース
interface User {
  id: string;
  name: string;
  email?: string;  // ?は任意
}

// ジェネリクス
const [items, setItems] = useState<string[]>([]);
```

### 6.3 よく使うパターン

**条件付きレンダリング**
```tsx
{isLoading ? <Spinner /> : <Content />}
{user && <UserProfile user={user} />}
```

**リストのレンダリング**
```tsx
{items.map((item) => (
  <Item key={item.id} data={item} />
))}
```

**イベントハンドリング**
```tsx
<Button onClick={() => handleClick(id)}>クリック</Button>
```

---

## 付録：コード規約

1. コンポーネントはPascalCase: `ChatMessage`, `LoginScreen`
2. 関数はcamelCase: `sendMessage`, `handleClick`
3. 定数はUPPER_SNAKE_CASE: `API_BASE_URL`, `QUESTIONS`
4. ファイル名はコンポーネント名と一致: `ChatMessage.tsx`
5. カスタムフックは`use`で始める: `useAuth`, `useChat`

---

## 次のステップ

1. このコードを実際に動かしてみる
2. 小さな変更を加えてみる（色を変える、文字を変える）
3. 新しいコンポーネントを追加してみる
4. TypeScriptの型エラーを意図的に起こして理解を深める

質問があれば、コードのコメントを参考にしたり、各ライブラリの公式ドキュメントを確認してください。
