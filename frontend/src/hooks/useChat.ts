import { useState, useCallback, useEffect } from 'react';
import { User } from 'firebase/auth';
import {
  collection,
  doc,
  addDoc,
  updateDoc,
  query,
  orderBy,
  limit,
  getDocs,
  arrayUnion,
  serverTimestamp,
} from 'firebase/firestore';
import { db } from '../services/firebase';
import { sendChatMessage } from '../services/api';
import { ChatMessage, Source } from '../types';

export function useChat(user: User | null, isDarkMode: boolean) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // 会話を読み込む
  const loadConversation = useCallback(async () => {
    if (!user) return;

    try {
      const conversationsRef = collection(db, 'users', user.uid, 'conversations');
      const q = query(conversationsRef, orderBy('updatedAt', 'desc'), limit(1));
      const snapshot = await getDocs(q);

      if (!snapshot.empty) {
        const docSnapshot = snapshot.docs[0];
        setConversationId(docSnapshot.id);
        const data = docSnapshot.data();

        if (data.messages && data.messages.length > 0) {
          setMessages(
            data.messages.map((msg: ChatMessage) => ({
              content: msg.content,
              sender: msg.sender,
              sources: msg.sources || [],
            }))
          );
        }
      } else {
        await createNewConversation();
      }
    } catch (error) {
      console.error('会話の読み込みエラー:', error);
    }
  }, [user]);

  // 新しい会話を作成
  const createNewConversation = useCallback(async () => {
    if (!user) return;

    try {
      const conversationsRef = collection(db, 'users', user.uid, 'conversations');
      const docRef = await addDoc(conversationsRef, {
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        messages: [],
      });
      setConversationId(docRef.id);
    } catch (error) {
      console.error('会話の作成エラー:', error);
    }
  }, [user]);

  // メッセージを保存
  const saveMessage = useCallback(
    async (content: string, sender: 'user' | 'ai', sources: Source[] = []) => {
      if (!user || !conversationId) return;

      try {
        const conversationRef = doc(
          db,
          'users',
          user.uid,
          'conversations',
          conversationId
        );

        await updateDoc(conversationRef, {
          updatedAt: serverTimestamp(),
          messages: arrayUnion({
            content,
            sender,
            sources,
            timestamp: new Date().toISOString(),
          }),
        });
      } catch (error) {
        console.error('メッセージの保存エラー:', error);
      }
    },
    [user, conversationId]
  );

  // メッセージを送信
  const sendMessage = useCallback(
    async (message: string, webSearchEnabled: boolean) => {
      if (!message.trim() || isLoading) return;

      const userMessage: ChatMessage = {
        content: message,
        sender: 'user',
        sources: [],
      };

      setMessages((prev) => [...prev, userMessage]);
      await saveMessage(message, 'user');

      setIsLoading(true);

      try {
        const result = await sendChatMessage(message, webSearchEnabled, isDarkMode);

        const aiMessage: ChatMessage = {
          content: result.response,
          sender: 'ai',
          sources: result.sources,
        };

        setMessages((prev) => [...prev, aiMessage]);
        await saveMessage(result.response, 'ai', result.sources);
      } catch (error) {
        console.error('メッセージ送信エラー:', error);
        const errorMessage: ChatMessage = {
          content: 'エラーが発生しました。もう一度お試しください。',
          sender: 'ai',
          sources: [],
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, isDarkMode, saveMessage]
  );

  // 会話をクリア
  const clearMessages = useCallback(async () => {
    setMessages([]);
    await createNewConversation();
  }, [createNewConversation]);

  // 初期読み込み
  useEffect(() => {
    if (user) {
      loadConversation();
    } else {
      setMessages([]);
      setConversationId(null);
    }
  }, [user, loadConversation]);

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
  };
}
