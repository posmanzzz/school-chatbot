import { useState, useCallback, useEffect } from 'react';
import { User } from 'firebase/auth';
import {
  collection,
  doc,
  addDoc,
  deleteDoc,
  query,
  orderBy,
  limit,
  getDocs,
  writeBatch,
  serverTimestamp,
} from 'firebase/firestore';
import { db } from '../services/firebase';
import { SearchHistoryItem } from '../types';

export function useSearchHistory(user: User | null) {
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);

  // 検索履歴を読み込む
  const loadSearchHistory = useCallback(async () => {
    if (!user) return;

    try {
      const historyRef = collection(db, 'users', user.uid, 'searchHistory');
      const q = query(historyRef, orderBy('timestamp', 'desc'), limit(50));
      const snapshot = await getDocs(q);

      const history: SearchHistoryItem[] = [];
      snapshot.forEach((doc) => {
        const data = doc.data();
        history.push({
          id: doc.id,
          query: data.query,
          timestamp: data.timestamp?.toDate() || new Date(),
        });
      });

      setSearchHistory(history);
    } catch (error) {
      console.error('検索履歴の読み込みエラー:', error);
    }
  }, [user]);

  // 検索クエリを保存
  const saveSearchQuery = useCallback(
    async (queryText: string) => {
      if (!user || !queryText.trim()) return;

      try {
        const historyRef = collection(db, 'users', user.uid, 'searchHistory');

        // 重複チェック
        const existing = searchHistory.find((h) => h.query === queryText);
        if (existing) {
          await deleteDoc(doc(db, 'users', user.uid, 'searchHistory', existing.id));
        }

        const docRef = await addDoc(historyRef, {
          query: queryText,
          timestamp: serverTimestamp(),
        });

        // ローカルの履歴を更新
        const newItem: SearchHistoryItem = {
          id: docRef.id,
          query: queryText,
          timestamp: new Date(),
        };

        setSearchHistory((prev) => {
          const filtered = prev.filter((h) => h.query !== queryText);
          const updated = [newItem, ...filtered];
          return updated.slice(0, 50);
        });

        // 50件を超えたら古いものを削除
        if (searchHistory.length >= 50) {
          const oldItems = searchHistory.slice(49);
          for (const item of oldItems) {
            await deleteDoc(doc(db, 'users', user.uid, 'searchHistory', item.id));
          }
        }
      } catch (error) {
        console.error('検索履歴の保存エラー:', error);
      }
    },
    [user, searchHistory]
  );

  // 検索履歴をクリア
  const clearSearchHistory = useCallback(async () => {
    if (!user) return;

    try {
      const historyRef = collection(db, 'users', user.uid, 'searchHistory');
      const snapshot = await getDocs(historyRef);

      const batch = writeBatch(db);
      snapshot.docs.forEach((docSnapshot) => {
        batch.delete(docSnapshot.ref);
      });
      await batch.commit();

      setSearchHistory([]);
    } catch (error) {
      console.error('検索履歴のクリアエラー:', error);
    }
  }, [user]);

  // 初期読み込み
  useEffect(() => {
    if (user) {
      loadSearchHistory();
    } else {
      setSearchHistory([]);
    }
  }, [user, loadSearchHistory]);

  return {
    searchHistory,
    saveSearchQuery,
    clearSearchHistory,
  };
}
