import Layout from '../components/Layout';
import Link from 'next/link';

const accounts = [
    { type: 'Savings Account', balance: '$24,580.00', num: '**** 4821', color: 'blue' },
    { type: 'Checking Account', balance: '$8,340.50', num: '**** 9034', color: 'teal' },
    { type: 'Investment Portfolio', balance: '$142,700.00', num: '**** 1156', color: 'purple' },
];

const stats = [
    { icon: '↑', label: 'Total Income', value: '$12,400', change: '+8.2% this month', dir: 'up', color: 'green' },
    { icon: '↓', label: 'Total Expenses', value: '$4,230', change: '+2.1% this month', dir: 'down', color: 'red' },
    { icon: '⬡', label: 'Savings Rate', value: '65.8%', change: 'vs 60.2% last month', dir: 'up', color: 'blue' },
    { icon: '★', label: 'Credit Score', value: '782', change: '+12 pts this month', dir: 'up', color: 'yellow' },
];

const recentTx = [
    { name: 'Netflix', cat: 'Entertainment', date: 'Mar 03', amount: '-$15.99', icon: '🎬', status: 'Completed', statusColor: 'chip-green' },
    { name: 'Salary Credit', cat: 'Income', date: 'Mar 01', amount: '+$4,200.00', icon: '💼', status: 'Completed', statusColor: 'chip-green', positive: true },
    { name: 'Starbucks', cat: 'Food & Drink', date: 'Feb 28', amount: '-$6.40', icon: '☕', status: 'Completed', statusColor: 'chip-green' },
    { name: 'Wire Transfer', cat: 'Transfer', date: 'Feb 27', amount: '-$500.00', icon: '⇄', status: 'Completed', statusColor: 'chip-green' },
    { name: 'Amazon', cat: 'Shopping', date: 'Feb 26', amount: '-$82.45', icon: '📦', status: 'Pending', statusColor: 'chip-yellow' },
];

export default function Dashboard() {
    return (
        <Layout title="Dashboard">
            {/* Account Cards */}
            <div className="section-header">
                <h2 className="section-title">My Accounts</h2>
                <a href="#" className="link-btn">+ Add Account</a>
            </div>
            <div className="grid-3 spacer">
                {accounts.map(a => (
                    <div key={a.type} className={`account-card ${a.color}`}>
                        <div className="account-card-type">{a.type}</div>
                        <div className="account-card-balance">{a.balance}</div>
                        <div className="account-card-bottom">
                            <div>
                                <div className="account-card-label">Account Number</div>
                                <div className="account-card-num">{a.num}</div>
                            </div>
                            <span style={{ fontSize: 22, opacity: 0.6 }}>›</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Stats */}
            <div className="grid-4 spacer">
                {stats.map(s => (
                    <div key={s.label} className="card card-sm">
                        <div className="stat-card">
                            <div className={`stat-icon ${s.color}`}>{s.icon}</div>
                            <div>
                                <div className="stat-label">{s.label}</div>
                                <div className="stat-value">{s.value}</div>
                                <div className={`stat-change ${s.dir}`}>{s.change}</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <div className="grid-2">
                {/* Recent Transactions */}
                <div className="card">
                    <div className="section-header">
                        <span className="section-title">Recent Transactions</span>
                        <Link href="/transactions" className="link-btn">View all</Link>
                    </div>
                    <table className="tx-table">
                        <tbody>
                            {recentTx.map(tx => (
                                <tr key={tx.name + tx.date}>
                                    <td>
                                        <div className="tx-row">
                                            <div className="tx-icon" style={{ background: 'rgba(255,255,255,0.06)' }}>{tx.icon}</div>
                                            <div>
                                                <div className="tx-name">{tx.name}</div>
                                                <div className="tx-sub">{tx.cat} · {tx.date}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td style={{ textAlign: 'right' }}>
                                        <div className={tx.positive ? 'amount-positive' : 'amount-negative'}>{tx.amount}</div>
                                        <span className={`chip ${tx.statusColor}`}>{tx.status}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Quick Actions + Spending */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div className="card">
                        <div className="section-title spacer-sm">Quick Actions</div>
                        <div className="quick-actions">
                            {[['⇄', 'Transfer'], ['⬆', 'Send'], ['⬇', 'Receive'], ['💳', 'Pay Bill'], ['💬', 'AI Chat'], ['📋', 'Statement']].map(([icon, label]) => (
                                <button key={label} className="quick-action-btn" onClick={label === 'AI Chat' ? () => window.location.href = '/chat' : undefined}>
                                    <span className="quick-action-icon">{icon}</span>
                                    {label}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="card">
                        <div className="section-title spacer-sm">Monthly Budget</div>
                        {[
                            { label: 'Housing', used: 1800, total: 2000, pct: 90, color: 'blue' },
                            { label: 'Food & Dining', used: 320, total: 500, pct: 64, color: 'green' },
                            { label: 'Entertainment', used: 85, total: 150, pct: 57, color: 'blue' },
                        ].map(b => (
                            <div key={b.label} style={{ marginBottom: 14 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                                    <span>{b.label}</span>
                                    <span style={{ color: 'var(--text-muted)' }}>${b.used} / ${b.total}</span>
                                </div>
                                <div className="progress-bar-wrap">
                                    <div className={`progress-bar ${b.color}`} style={{ width: `${b.pct}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </Layout>
    );
}
