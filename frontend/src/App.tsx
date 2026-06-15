import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Flex,
  Spinner,
  useColorMode,
  useDisclosure,
  useToast,
} from '@chakra-ui/react';
import { useAuth } from './hooks/useAuth';
import { useChat } from './hooks/useChat';
import { useSearchHistory } from './hooks/useSearchHistory';
import { useScheduleAlerts } from './hooks/useScheduleAlerts';
import { checkApiHealth } from './services/api';
import { ApiStatus } from './types';

import { LoginScreen } from './components/LoginScreen';
import { Header } from './components/Header';
import { AlertBanner } from './components/AlertBanner';
import { ChatContainer } from './components/ChatContainer';
import { SideLinks } from './components/SideLinks';
import { SearchHistoryPanel } from './components/SearchHistoryPanel';

function App() {
  const { user, loading: authLoading, signInWithGoogle, signOut } = useAuth();
  const { colorMode } = useColorMode();
  const isDarkMode = colorMode === 'dark';

  const { messages, isLoading: chatLoading, sendMessage, clearMessages } = useChat(user, isDarkMode);
  const { searchHistory, saveSearchQuery, clearSearchHistory } = useSearchHistory(user);
  const { alerts, dismissAlert } = useScheduleAlerts();

  const [apiStatus, setApiStatus] = useState<ApiStatus>('connecting');
  const [loginLoading, setLoginLoading] = useState(false);

  const { isOpen: isHistoryOpen, onOpen: openHistory, onClose: closeHistory } = useDisclosure();
  const toast = useToast();

  // API状態チェック
  useEffect(() => {
    const checkStatus = async () => {
      const status = await checkApiHealth();
      setApiStatus(status);
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // メッセージ送信ハンドラ
  const handleSendMessage = useCallback(
    async (message: string, webSearchEnabled: boolean) => {
      await saveSearchQuery(message);
      await sendMessage(message, webSearchEnabled);
    },
    [saveSearchQuery, sendMessage]
  );

  // ログインハンドラ
  const handleLogin = async () => {
    setLoginLoading(true);
    try {
      await signInWithGoogle();
    } catch (error) {
      toast({
        title: 'ログインに失敗しました',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoginLoading(false);
    }
  };

  // ログアウトハンドラ
  const handleLogout = async () => {
    if (window.confirm('ログアウトしますか？')) {
      await signOut();
    }
  };

  // 会話クリアハンドラ
  const handleClearChat = async () => {
    if (window.confirm('会話履歴をクリアしますか？')) {
      await clearMessages();
    }
  };

  // 検索履歴クリアハンドラ
  const handleClearHistory = async () => {
    if (window.confirm('検索履歴をすべて削除しますか？')) {
      await clearSearchHistory();
    }
  };

  // クイック質問ハンドラ
  const handleQuickQuestion = (question: string) => {
    handleSendMessage(question, false);
  };

  // 検索履歴選択ハンドラ
  const handleSelectHistory = (query: string) => {
    handleSendMessage(query, false);
  };

  // ローディング表示
  if (authLoading) {
    return (
      <Flex minH="100vh" align="center" justify="center">
        <Spinner size="xl" color="blue.400" thickness="4px" />
      </Flex>
    );
  }

  // ログイン画面
  if (!user) {
    return <LoginScreen onLogin={handleLogin} isLoading={loginLoading} />;
  }

  // メイン画面
  return (
    <Box minH="100vh" display="flex" flexDirection="column">
        <AlertBanner alerts={alerts} onDismiss={dismissAlert} />

        <Header
          user={user}
          apiStatus={apiStatus}
          onToggleHistory={openHistory}
          onClearChat={handleClearChat}
          onLogout={handleLogout}
        />

        <Flex
          as="main"
          flex={1}
          justify="center"
          align="flex-start"
          p={{ base: 3, md: 6 }}
          gap={6}
        >
          <ChatContainer
            messages={messages}
            isLoading={chatLoading}
            onSendMessage={handleSendMessage}
            onQuickQuestion={handleQuickQuestion}
            userPhotoURL={user.photoURL}
          />
          <SideLinks />
        </Flex>

        <SearchHistoryPanel
          isOpen={isHistoryOpen}
          onClose={closeHistory}
          history={searchHistory}
          onSelectQuery={handleSelectHistory}
          onClear={handleClearHistory}
        />
    </Box>
  );
}

export default App;
