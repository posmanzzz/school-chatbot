// === DOM要素の取得 ===
const loginScreen = document.getElementById('login-screen');
const mainApp = document.getElementById('main-app');
const googleLoginBtn = document.getElementById('google-login-btn');
const logoutBtn = document.getElementById('logout-btn');
const userAvatar = document.getElementById('user-avatar');
const userName = document.getElementById('user-name');

const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatBox = document.getElementById('chat-box');
const submitButton = document.getElementById('submit-btn');
const typingIndicator = document.getElementById('typing-indicator');
const toggleBtn = document.getElementById('toggle-btn');
const clearBtn = document.getElementById('clear-btn');
const apiStatus = document.getElementById('api-status');
const copyToast = document.getElementById('copy-toast');

// 検索履歴
const historyBtn = document.getElementById('history-btn');
const historyPanel = document.getElementById('history-panel');
const historyOverlay = document.getElementById('history-overlay');
const historyCloseBtn = document.getElementById('history-close-btn');
const historyList = document.getElementById('history-list');
const historyClearBtn = document.getElementById('history-clear-btn');

// アラートバナー
const alertBanner = document.getElementById('alert-banner');

// Web検索チェックボックス
const webSearchCheckbox = document.getElementById('web-search-checkbox');

// === グローバル変数 ===
let currentUser = null;
let conversationId = null;
let searchHistory = [];

// === API設定 ===
const API_BASE_URL = '/api';

// === Marked.js設定 ===
marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    mangle: false
});

// ==========================================
// Firebase認証
// ==========================================

auth.onAuthStateChanged(async (user) => {
    if (user) {
        currentUser = user;
        showMainApp(user);
        await loadConversation();
        await loadSearchHistory();
        showScheduleAlerts();
    } else {
        currentUser = null;
        showLoginScreen();
    }
});

googleLoginBtn.addEventListener('click', async () => {
    try {
        googleLoginBtn.disabled = true;
        googleLoginBtn.textContent = 'ログイン中...';
        await auth.signInWithPopup(googleProvider);
    } catch (error) {
        console.error('ログインエラー:', error);
        alert('ログインに失敗しました: ' + error.message);
    } finally {
        googleLoginBtn.disabled = false;
        googleLoginBtn.innerHTML = '<img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google"> Googleでログイン';
    }
});

logoutBtn.addEventListener('click', async () => {
    if (!confirm('ログアウトしますか？')) return;
    try {
        await auth.signOut();
    } catch (error) {
        console.error('ログアウトエラー:', error);
    }
});

function showLoginScreen() {
    loginScreen.classList.remove('hidden');
    mainApp.classList.add('hidden');
}

function showMainApp(user) {
    loginScreen.classList.add('hidden');
    mainApp.classList.remove('hidden');
    userAvatar.src = user.photoURL || 'https://via.placeholder.com/32';
    userName.textContent = user.displayName || 'ユーザー';
    checkApiHealth();
}

// ==========================================
// 予定アラート
// ==========================================

function showScheduleAlerts() {
    const alerts = checkScheduleAlerts();

    if (alerts.length === 0) {
        alertBanner.classList.add('hidden');
        return;
    }

    alertBanner.innerHTML = '';
    alertBanner.classList.remove('hidden');

    alerts.forEach((alert, index) => {
        const alertItem = document.createElement('div');
        alertItem.className = `alert-item ${alert.type}`;
        alertItem.innerHTML = `
            <div class="alert-icon">
                <i class="fas ${alert.icon}"></i>
            </div>
            <div class="alert-content">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-message">${alert.message}</div>
            </div>
            <button class="alert-close" data-index="${index}">
                <i class="fas fa-times"></i>
            </button>
        `;
        alertBanner.appendChild(alertItem);
    });

    // 閉じるボタン
    alertBanner.querySelectorAll('.alert-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const item = e.target.closest('.alert-item');
            item.style.opacity = '0';
            item.style.transform = 'translateX(20px)';
            setTimeout(() => {
                item.remove();
                if (alertBanner.children.length === 0) {
                    alertBanner.classList.add('hidden');
                }
            }, 200);
        });
    });
}

// ==========================================
// 検索履歴
// ==========================================

async function loadSearchHistory() {
    if (!currentUser) return;

    try {
        const historyRef = db.collection('users').doc(currentUser.uid).collection('searchHistory');
        const snapshot = await historyRef.orderBy('timestamp', 'desc').limit(50).get();

        searchHistory = [];
        snapshot.forEach(doc => {
            searchHistory.push({ id: doc.id, ...doc.data() });
        });

        renderSearchHistory();
    } catch (error) {
        console.error('検索履歴の読み込みエラー:', error);
    }
}

async function saveSearchQuery(query) {
    if (!currentUser || !query.trim()) return;

    try {
        const historyRef = db.collection('users').doc(currentUser.uid).collection('searchHistory');

        // 重複チェック（同じクエリが直近にあれば追加しない）
        const existing = searchHistory.find(h => h.query === query);
        if (existing) {
            // 既存のものを削除して新しく追加（最新に更新）
            await historyRef.doc(existing.id).delete();
        }

        const docRef = await historyRef.add({
            query: query,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });

        // ローカルの履歴を更新
        searchHistory = searchHistory.filter(h => h.query !== query);
        searchHistory.unshift({
            id: docRef.id,
            query: query,
            timestamp: new Date()
        });

        // 50件を超えたら古いものを削除
        if (searchHistory.length > 50) {
            const oldItems = searchHistory.slice(50);
            for (const item of oldItems) {
                await historyRef.doc(item.id).delete();
            }
            searchHistory = searchHistory.slice(0, 50);
        }

        renderSearchHistory();
    } catch (error) {
        console.error('検索履歴の保存エラー:', error);
    }
}

async function clearSearchHistory() {
    if (!currentUser) return;

    try {
        const historyRef = db.collection('users').doc(currentUser.uid).collection('searchHistory');
        const snapshot = await historyRef.get();

        const batch = db.batch();
        snapshot.docs.forEach(doc => {
            batch.delete(doc.ref);
        });
        await batch.commit();

        searchHistory = [];
        renderSearchHistory();
    } catch (error) {
        console.error('検索履歴のクリアエラー:', error);
    }
}

function renderSearchHistory() {
    if (searchHistory.length === 0) {
        historyList.innerHTML = '<p class="history-empty">検索履歴がありません</p>';
        return;
    }

    historyList.innerHTML = '';
    searchHistory.forEach(item => {
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item';

        const timeAgo = getTimeAgo(item.timestamp);

        historyItem.innerHTML = `
            <i class="fas fa-search"></i>
            <div class="history-item-content">
                <div class="history-item-query">${escapeHtml(item.query)}</div>
                <div class="history-item-time">${timeAgo}</div>
            </div>
        `;

        historyItem.addEventListener('click', () => {
            userInput.value = item.query;
            closeHistoryPanel();
            userInput.focus();
        });

        historyList.appendChild(historyItem);
    });
}

function getTimeAgo(timestamp) {
    if (!timestamp) return '';

    const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'たった今';
    if (diff < 3600) return `${Math.floor(diff / 60)}分前`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}時間前`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}日前`;

    return date.toLocaleDateString('ja-JP');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 履歴パネル開閉
function openHistoryPanel() {
    historyPanel.classList.remove('hidden');
    historyOverlay.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeHistoryPanel() {
    historyPanel.classList.add('hidden');
    historyOverlay.classList.add('hidden');
    document.body.style.overflow = '';
}

historyBtn.addEventListener('click', openHistoryPanel);
historyCloseBtn.addEventListener('click', closeHistoryPanel);
historyOverlay.addEventListener('click', closeHistoryPanel);

historyClearBtn.addEventListener('click', async () => {
    if (!confirm('検索履歴をすべて削除しますか？')) return;
    await clearSearchHistory();
});

// ==========================================
// Firestore - 会話履歴
// ==========================================

async function loadConversation() {
    if (!currentUser) return;

    try {
        const conversationsRef = db.collection('users').doc(currentUser.uid).collection('conversations');
        const snapshot = await conversationsRef.orderBy('updatedAt', 'desc').limit(1).get();

        if (!snapshot.empty) {
            const doc = snapshot.docs[0];
            conversationId = doc.id;
            const data = doc.data();

            if (data.messages && data.messages.length > 0) {
                hideWelcomeSection();
                data.messages.forEach(msg => {
                    addMessageToUI(msg.content, msg.sender, msg.sources || [], false);
                });
            }
        } else {
            await createNewConversation();
        }
    } catch (error) {
        console.error('会話の読み込みエラー:', error);
    }
}

async function createNewConversation() {
    if (!currentUser) return;

    try {
        const conversationsRef = db.collection('users').doc(currentUser.uid).collection('conversations');
        const docRef = await conversationsRef.add({
            createdAt: firebase.firestore.FieldValue.serverTimestamp(),
            updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
            messages: []
        });
        conversationId = docRef.id;
    } catch (error) {
        console.error('会話の作成エラー:', error);
    }
}

async function saveMessage(content, sender, sources = []) {
    if (!currentUser || !conversationId) return;

    try {
        const conversationRef = db.collection('users').doc(currentUser.uid)
            .collection('conversations').doc(conversationId);

        await conversationRef.update({
            updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
            messages: firebase.firestore.FieldValue.arrayUnion({
                content,
                sender,
                sources,
                timestamp: new Date().toISOString()
            })
        });
    } catch (error) {
        console.error('メッセージの保存エラー:', error);
    }
}

async function clearConversation() {
    if (!currentUser) return;
    try {
        await createNewConversation();
    } catch (error) {
        console.error('会話のクリアエラー:', error);
    }
}

// ==========================================
// API接続ステータス
// ==========================================

function updateApiStatus(status) {
    const statusText = apiStatus.querySelector('.status-text');
    apiStatus.classList.remove('online', 'offline', 'connecting');
    apiStatus.classList.add(status);

    switch (status) {
        case 'online': statusText.textContent = 'オンライン'; break;
        case 'offline': statusText.textContent = 'オフライン'; break;
        case 'connecting': statusText.textContent = '接続中...'; break;
    }
}

async function checkApiHealth() {
    updateApiStatus('connecting');
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            signal: AbortSignal.timeout(5000)
        });
        if (response.ok) {
            updateApiStatus('online');
            return true;
        }
    } catch (error) {
        console.warn('[API] サーバーに接続できません');
    }
    updateApiStatus('offline');
    return false;
}

setInterval(checkApiHealth, 30000);

// ==========================================
// API通信
// ==========================================

async function getAiResponse(message) {
    const url = `${API_BASE_URL}/chat`;
    const webSearchEnabled = webSearchCheckbox ? webSearchCheckbox.checked : false;
    const isDarkMode = document.body.classList.contains('dark-mode');
    const data = {
        query: message,
        max_results: 5,
        temperature: 0.3,
        web_search: webSearchEnabled,
        mode: isDarkMode ? 'dark' : 'light'
    };

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `APIエラー: ${response.status}`);
        }

        const result = await response.json();
        updateApiStatus('online');
        return {
            response: result.response,
            sources: result.sources || []
        };
    } catch (error) {
        console.error("通信に失敗しました:", error);
        updateApiStatus('offline');
        return {
            response: `エラーが発生しました: ${error.message}\n\nAPIサーバーが起動しているか確認してください。`,
            sources: []
        };
    }
}

// ==========================================
// UI関連
// ==========================================

function hideWelcomeSection() {
    const welcomeMsg = chatBox.querySelector('.welcome-message');
    const quickQuestions = chatBox.querySelector('.quick-questions');

    if (welcomeMsg) {
        welcomeMsg.style.opacity = '0';
        welcomeMsg.style.transform = 'translateY(-10px)';
        welcomeMsg.style.transition = 'all 0.3s ease';
        setTimeout(() => welcomeMsg.remove(), 300);
    }

    if (quickQuestions) {
        quickQuestions.style.opacity = '0';
        quickQuestions.style.transform = 'translateY(-10px)';
        quickQuestions.style.transition = 'all 0.3s ease';
        setTimeout(() => quickQuestions.remove(), 300);
    }
}

function showToast(message = 'コピーしました') {
    copyToast.classList.remove('hidden');
    copyToast.offsetHeight;
    copyToast.classList.add('show');
    setTimeout(() => {
        copyToast.classList.remove('show');
        setTimeout(() => copyToast.classList.add('hidden'), 300);
    }, 2000);
}

async function copyToClipboard(text, button) {
    try {
        await navigator.clipboard.writeText(text);
        button.classList.add('copied');
        button.innerHTML = '<i class="fas fa-check"></i>';
        showToast();
        setTimeout(() => {
            button.classList.remove('copied');
            button.innerHTML = '<i class="fas fa-copy"></i>';
        }, 2000);
    } catch (error) {
        console.error('コピーに失敗しました:', error);
    }
}

function parseMarkdown(text) {
    const rawHtml = marked.parse(text);
    return DOMPurify.sanitize(rawHtml, {
        ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                       'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'hr', 'table', 'thead',
                       'tbody', 'tr', 'th', 'td', 'del', 'sup', 'sub', 'span'],
        ALLOWED_ATTR: ['href', 'target', 'rel', 'class']
    });
}

function addMessageToUI(content, sender, sources = [], animate = true) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    if (!animate) messageElement.style.animation = 'none';

    const avatar = document.createElement('div');
    avatar.classList.add('message-avatar');
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<img src="ai-icon.png" alt="AI Avatar">';

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');

    if (sender === 'ai') {
        messageContent.classList.add('markdown-body');
        messageContent.innerHTML = parseMarkdown(content);
        messageContent.querySelectorAll('a').forEach(link => {
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
        });

        const copyBtn = document.createElement('button');
        copyBtn.classList.add('copy-btn');
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'コピー';
        copyBtn.addEventListener('click', () => copyToClipboard(content, copyBtn));
        messageElement.appendChild(copyBtn);
    } else {
        messageContent.textContent = content;
    }

    if (sender === 'ai' && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.classList.add('message-sources');
        const sourcesHeader = document.createElement('div');
        sourcesHeader.classList.add('sources-header');
        sourcesHeader.innerHTML = '<i class="fas fa-book"></i> 参照元';
        sourcesDiv.appendChild(sourcesHeader);

        const sourcesList = document.createElement('ul');
        sources.forEach(source => {
            if (source.url) {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = source.url;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                link.textContent = source.title || source.url;
                li.appendChild(link);
                sourcesList.appendChild(li);
            }
        });

        if (sourcesList.children.length > 0) {
            sourcesDiv.appendChild(sourcesList);
            messageContent.appendChild(sourcesDiv);
        }
    }

    messageElement.appendChild(avatar);
    messageElement.appendChild(messageContent);
    chatBox.appendChild(messageElement);
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

async function addMessage(content, sender, sources = []) {
    hideWelcomeSection();
    addMessageToUI(content, sender, sources, true);
    await saveMessage(content, sender, sources);
}

function showTypingIndicator() {
    typingIndicator.classList.remove('hidden');
    chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

function hideTypingIndicator() {
    typingIndicator.classList.add('hidden');
}

function setSubmitLoading(loading) {
    submitButton.disabled = loading;
    submitButton.innerHTML = loading ? '<i class="fas fa-spinner fa-spin"></i>' : '<i class="fas fa-paper-plane"></i>';
}

// ==========================================
// メッセージ送信
// ==========================================

async function sendMessage(message) {
    if (!message.trim()) return;

    // 検索履歴に保存
    await saveSearchQuery(message);

    await addMessage(message, 'user');
    userInput.value = '';
    userInput.style.height = 'auto';

    setSubmitLoading(true);
    showTypingIndicator();

    const result = await getAiResponse(message);

    hideTypingIndicator();

    // タイピングエフェクト付きでAI応答を表示
    if (typeof addMessageWithTyping === 'function') {
        addMessageWithTyping(result.response, 'ai', result.sources, true);
        await saveMessage(result.response, 'ai', result.sources);
    } else {
        await addMessage(result.response, 'ai', result.sources);
    }

    setSubmitLoading(false);
}

chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    await sendMessage(userInput.value.trim());
});

document.querySelectorAll('.quick-question-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
        const question = btn.dataset.question;
        if (question) await sendMessage(question);
    });
});

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.shiftKey) return;
    if (e.key === 'Enter') {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
});

// ==========================================
// ダークモード
// ==========================================

function updateDarkModeIcon() {
    const isDark = document.body.classList.contains('dark-mode');
    toggleBtn.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
}

if (localStorage.getItem('dark-mode') === 'true') {
    document.body.classList.add('dark-mode');
}
updateDarkModeIcon();

toggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('dark-mode', document.body.classList.contains('dark-mode'));
    updateDarkModeIcon();
});

// ==========================================
// 会話クリア
// ==========================================

clearBtn.addEventListener('click', async () => {
    if (!confirm('会話履歴をクリアしますか？')) return;

    chatBox.innerHTML = '';

    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-message';
    welcomeDiv.innerHTML = `
        <i class="fas fa-comment-dots"></i>
        <p>こんにちは！近大高専について何でも聞いてください。</p>
    `;
    chatBox.appendChild(welcomeDiv);

    const quickQuestionsDiv = document.createElement('div');
    quickQuestionsDiv.className = 'quick-questions';
    quickQuestionsDiv.innerHTML = `
        <p class="quick-questions-label">よくある質問:</p>
        <div class="quick-questions-list">
            <button class="quick-question-btn" data-question="入学試験について教えてください">
                <i class="fas fa-graduation-cap"></i> 入学試験
            </button>
            <button class="quick-question-btn" data-question="学科の特徴を教えてください">
                <i class="fas fa-flask"></i> 学科紹介
            </button>
            <button class="quick-question-btn" data-question="年間行事予定を教えてください">
                <i class="fas fa-calendar"></i> 行事予定
            </button>
            <button class="quick-question-btn" data-question="取得できる資格について教えてください">
                <i class="fas fa-certificate"></i> 資格取得
            </button>
            <button class="quick-question-btn" data-question="部活動について教えてください">
                <i class="fas fa-futbol"></i> 部活動
            </button>
            <button class="quick-question-btn" data-question="寮について教えてください">
                <i class="fas fa-building"></i> 学生寮
            </button>
        </div>
    `;
    chatBox.appendChild(quickQuestionsDiv);

    quickQuestionsDiv.querySelectorAll('.quick-question-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const question = btn.dataset.question;
            if (question) await sendMessage(question);
        });
    });

    await clearConversation();
});

// ==========================================
// 動的UIエフェクト
// ==========================================

// パーティクル背景
function createParticles() {
    const container = document.getElementById('particles-container');
    if (!container) return;

    const particleCount = 20;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (15 + Math.random() * 10) + 's';
        particle.style.width = (4 + Math.random() * 6) + 'px';
        particle.style.height = particle.style.width;
        particle.style.opacity = 0.2 + Math.random() * 0.3;
        container.appendChild(particle);
    }
}

// リップルエフェクト
function createRipple(event, element) {
    const ripple = document.createElement('span');
    ripple.className = 'ripple';

    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';

    element.appendChild(ripple);

    ripple.addEventListener('animationend', () => {
        ripple.remove();
    });
}

// ボタンにリップルエフェクトを適用
function applyRippleEffect() {
    const buttons = document.querySelectorAll('.quick-question-btn, #submit-btn, .google-login-btn, .icon-btn');

    buttons.forEach(button => {
        button.classList.add('ripple-container');
        button.addEventListener('click', (e) => {
            createRipple(e, button);
        });
    });
}

// スムーズスクロール
function smoothScrollToBottom() {
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: 'smooth'
    });
}

// メッセージ表示時のアニメーション強化
const originalAddMessageToUI = addMessageToUI;

// タイピングエフェクト付きメッセージ表示
function addMessageWithTyping(content, sender, sources = [], animate = true) {
    hideWelcomeSection();

    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    if (!animate) messageElement.style.animation = 'none';

    const avatar = document.createElement('div');
    avatar.classList.add('message-avatar');
    avatar.innerHTML = sender === 'user' ? '<i class="fas fa-user"></i>' : '<img src="ai-icon.png" alt="AI Avatar">';

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');

    if (sender === 'ai' && animate) {
        messageContent.classList.add('markdown-body');
        // タイピングエフェクト用に空で開始
        messageElement.appendChild(avatar);
        messageElement.appendChild(messageContent);
        chatBox.appendChild(messageElement);
        smoothScrollToBottom();

        // タイピングエフェクト
        typeMessage(content, messageContent, sources);

        // コピーボタン追加
        const copyBtn = document.createElement('button');
        copyBtn.classList.add('copy-btn');
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.title = 'コピー';
        copyBtn.addEventListener('click', () => copyToClipboard(content, copyBtn));
        messageElement.appendChild(copyBtn);
    } else {
        if (sender === 'ai') {
            messageContent.classList.add('markdown-body');
            messageContent.innerHTML = parseMarkdown(content);
            messageContent.querySelectorAll('a').forEach(link => {
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
            });

            const copyBtn = document.createElement('button');
            copyBtn.classList.add('copy-btn');
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.title = 'コピー';
            copyBtn.addEventListener('click', () => copyToClipboard(content, copyBtn));
            messageElement.appendChild(copyBtn);
        } else {
            messageContent.textContent = content;
        }

        if (sender === 'ai' && sources.length > 0) {
            addSourcesToMessage(messageContent, sources);
        }

        messageElement.appendChild(avatar);
        messageElement.appendChild(messageContent);
        chatBox.appendChild(messageElement);
        smoothScrollToBottom();
    }
}

// タイピングエフェクト
async function typeMessage(content, container, sources) {
    const html = parseMarkdown(content);
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;

    // 段階的にコンテンツを表示
    const textContent = tempDiv.textContent;
    const words = textContent.split(' ');
    let currentText = '';

    for (let i = 0; i < words.length; i++) {
        currentText += (i === 0 ? '' : ' ') + words[i];
        container.innerHTML = parseMarkdown(currentText);
        smoothScrollToBottom();
        await new Promise(resolve => setTimeout(resolve, 30));
    }

    // 最終的なHTMLを設定
    container.innerHTML = html;
    container.querySelectorAll('a').forEach(link => {
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
    });

    // ソースを追加
    if (sources && sources.length > 0) {
        addSourcesToMessage(container, sources);
    }

    smoothScrollToBottom();
}

// ソース追加ヘルパー
function addSourcesToMessage(messageContent, sources) {
    const sourcesDiv = document.createElement('div');
    sourcesDiv.classList.add('message-sources');
    const sourcesHeader = document.createElement('div');
    sourcesHeader.classList.add('sources-header');
    sourcesHeader.innerHTML = '<i class="fas fa-book"></i> 参照元';
    sourcesDiv.appendChild(sourcesHeader);

    const sourcesList = document.createElement('ul');
    sources.forEach(source => {
        if (source.url) {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = source.url;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = source.title || source.url;
            li.appendChild(link);
            sourcesList.appendChild(li);
        }
    });

    if (sourcesList.children.length > 0) {
        sourcesDiv.appendChild(sourcesList);
        messageContent.appendChild(sourcesDiv);
    }
}

// ヘッダーにグロー効果
function addHeaderGlow() {
    const header = document.querySelector('.header');
    if (header) {
        header.style.position = 'relative';
        header.style.overflow = 'hidden';
    }
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    applyRippleEffect();
    addHeaderGlow();

    // 入力欄のフォーカスアニメーション
    if (userInput) {
        userInput.addEventListener('focus', () => {
            userInput.parentElement.style.transform = 'scale(1.01)';
        });
        userInput.addEventListener('blur', () => {
            userInput.parentElement.style.transform = 'scale(1)';
        });
    }
});
