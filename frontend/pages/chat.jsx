import { useState, useRef, useEffect } from 'react';
import Layout from '../components/Layout';

const BACKEND_URL = 'http://127.0.0.1:8000';

const SUGGESTED = [
    "What are ZX Bank's ATM withdrawal fees?",
    "How do I enable two-factor authentication?",
    "What are the fixed deposit interest rates?",
    "How do I report a fraudulent transaction?",
    "What rewards does the ZX credit card offer?",
];

function formatTime(d) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export default function Chat() {
    const [messages, setMessages] = useState([
        {
            id: 0,
            role: 'bot',
            content: "Hello! I'm the ZX Bank AI Assistant. I can help you with account inquiries, transfers, loan information, and more. What can I help you with today?",
            time: new Date(),
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [error, setError] = useState(null);
    const bottomRef = useRef(null);

    // Load persisted session on component mount
    useEffect(() => {
        const savedSessionId = sessionStorage.getItem('zxbank_session_id');
        if (savedSessionId) {
            setSessionId(savedSessionId);
        }
    }, []);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    async function sendMessage(text) {
        const msg = text || input.trim();
        if (!msg || loading) return;
        setInput('');
        setError(null);

        const userMsg = { id: Date.now(), role: 'user', content: msg, time: new Date() };
        setMessages(prev => [...prev, userMsg]);
        setLoading(true);

        try {
            const res = await fetch(`${BACKEND_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, session_id: sessionId }),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `HTTP ${res.status}`);
            }

            const data = await res.json();

            // Sync session ID with whatever backend returns, in case it expired or was recreated
            if (data.session_id !== sessionId) {
                setSessionId(data.session_id);
                sessionStorage.setItem('zxbank_session_id', data.session_id);
            }

            const botMsg = {
                id: Date.now() + 1,
                role: 'bot',
                content: data.response,
                time: new Date(),
                intent: data.intent,
                confidence: data.confidence,
                citations: data.citations || [],
                retrieval_triggered: data.retrieval_triggered,
                escalation_triggered: data.escalation_triggered,
            };
            setMessages(prev => [...prev, botMsg]);
        } catch (e) {
            setError('Could not connect to ZX Bank backend. Make sure the server is running on port 8000.');
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                role: 'bot',
                content: '⚠️ Connection error. Please ensure the backend server is running.',
                time: new Date(),
                isError: true,
            }]);
        } finally {
            setLoading(false);
        }
    }

    function handleKey(e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    }

    return (
        <Layout title="AI Banking Assistant">
            {/* Session Badge */}
            {sessionId && (
                <div style={{ marginBottom: 12, fontSize: 11, color: 'var(--text-muted)' }}>
                    <span style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: 4, padding: '2px 8px' }}>
                        Session: {sessionId.slice(0, 8)}…
                    </span>
                </div>
            )}

            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                {/* Chat Window */}
                <div className="chat-wrap">
                    <div className="chat-messages">
                        {messages.map(m => (
                            <div key={m.id} className={`msg ${m.role}`}>
                                <div className={`msg-avatar ${m.role}`}>
                                    {m.role === 'bot' ? 'ZX' : 'JD'}
                                </div>
                                <div>
                                    {m.role === 'bot' && m.intent && (
                                        <div className={`intent-tag intent-${m.intent}`}>{m.intent.replace('_', ' ')}</div>
                                    )}
                                    <div className="msg-bubble">{m.content}</div>
                                    {m.citations && m.citations.length > 0 && (
                                        <div className="chat-citations">
                                            {m.citations.map(c => (
                                                <span key={c} className="chat-citation-tag">📄 {c}</span>
                                            ))}
                                        </div>
                                    )}
                                    <div className="msg-meta">{formatTime(m.time)}</div>
                                </div>
                            </div>
                        ))}

                        {loading && (
                            <div className="msg bot">
                                <div className="msg-avatar bot">ZX</div>
                                <div className="msg-bubble" style={{ color: 'var(--text-muted)' }}>
                                    <span className="typing-dot">●</span>{' '}
                                    <span className="typing-dot" style={{ animationDelay: '0.2s' }}>●</span>{' '}
                                    <span className="typing-dot" style={{ animationDelay: '0.4s' }}>●</span>
                                    <style>{`
                    .typing-dot { animation: pulse 1s ease-in-out infinite; display:inline-block; }
                    @keyframes pulse { 0%,100%{opacity:0.3} 50%{opacity:1} }
                  `}</style>
                                </div>
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    {/* Input */}
                    <div className="chat-input-row">
                        <input
                            className="chat-input"
                            placeholder="Ask about accounts, transfers, loans, security…"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKey}
                            disabled={loading}
                        />
                        <button className="btn btn-primary" onClick={() => sendMessage()} disabled={loading || !input.trim()}>
                            Send ↑
                        </button>
                    </div>
                </div>
            </div>

            {/* Suggested questions */}
            <div style={{ marginTop: 16 }}>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 10 }}>Suggested questions:</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {SUGGESTED.map(q => (
                        <button
                            key={q}
                            onClick={() => sendMessage(q)}
                            disabled={loading}
                            style={{
                                background: 'rgba(255,255,255,0.04)',
                                border: '1px solid var(--border)',
                                borderRadius: 20,
                                padding: '5px 13px',
                                fontSize: 12,
                                color: 'var(--text-dim)',
                                cursor: 'pointer',
                                fontFamily: 'Inter, sans-serif',
                                transition: 'all 0.15s',
                            }}
                            onMouseEnter={e => e.target.style.borderColor = 'var(--accent)'}
                            onMouseLeave={e => e.target.style.borderColor = 'var(--border)'}
                        >
                            {q}
                        </button>
                    ))}
                </div>
            </div>
        </Layout>
    );
}
