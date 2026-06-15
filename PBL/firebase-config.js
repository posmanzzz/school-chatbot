// Firebase設定
// Firebaseコンソールから取得した設定をここに貼り付けてください
// https://console.firebase.google.com/ → プロジェクト設定 → マイアプリ → SDK設定

// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "YOUR_FIREBASE_API_KEY",
  authDomain: "YOUR_FIREBASE_AUTH_DOMAIN",
  projectId: "YOUR_FIREBASE_PROJECT_ID",
  storageBucket: "YOUR_FIREBASE_STORAGE_BUCKET",
  messagingSenderId: "YOUR_FIREBASE_MESSAGING_SENDER_ID",
  appId: "YOUR_FIREBASE_APP_ID",
  measurementId: "YOUR_FIREBASE_MEASUREMENT_ID"
};

// Firebase初期化
firebase.initializeApp(firebaseConfig);

// Firebase サービスのインスタンス
const auth = firebase.auth();
const db = firebase.firestore();

// Google認証プロバイダー
const googleProvider = new firebase.auth.GoogleAuthProvider();
