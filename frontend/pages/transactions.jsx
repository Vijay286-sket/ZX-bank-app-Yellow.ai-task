import { useState } from 'react';
import Layout from '../components/Layout';

const ALL_TX = [
    { id: 1, name: 'Salary Credit', cat: 'Income', date: '2026-03-01', amount: 4200.00, positive: true, icon: '💼', status: 'Completed', acc: 'Checking' },
    { id: 2, name: 'Netflix', cat: 'Entertainment', date: '2026-03-03', amount: -15.99, icon: '🎬', status: 'Completed', acc: 'Checking' },
    { id: 3, name: 'Starbucks', cat: 'Food & Drink', date: '2026-02-28', amount: -6.40, icon: '☕', status: 'Completed', acc: 'Checking' },
    { id: 4, name: 'Wire Transfer – Jane Smith', cat: 'Transfer', date: '2026-02-27', amount: -500.00, icon: '⇄', status: 'Completed', acc: 'Savings' },
    { id: 5, name: 'Amazon', cat: 'Shopping', date: '2026-02-26', amount: -82.45, icon: '📦', status: 'Pending', acc: 'Checking' },
    { id: 6, name: 'ATM Withdrawal', cat: 'Cash', date: '2026-02-25', amount: -200.00, icon: '🏧', status: 'Completed', acc: 'Checking' },
    { id: 7, name: 'Electricity Bill', cat: 'Utilities', date: '2026-02-24', amount: -134.20, icon: '⚡', status: 'Completed', acc: 'Checking' },
    { id: 8, name: 'Dividend Credit', cat: 'Income', date: '2026-02-23', amount: 320.00, positive: true, icon: '📈', status: 'Completed', acc: 'Investment' },
    { id: 9, name: 'Uber Eats', cat: 'Food & Drink', date: '2026-02-22', amount: -38.90, icon: '🍕', status: 'Completed', acc: 'Checking' },
    { id: 10, name: 'Gym Membership', cat: 'Health', date: '2026-02-21', amount: -49.99, icon: '🏋', status: 'Completed', acc: 'Checking' },
    { id: 11, name: 'Interest Earned', cat: 'Income', date: '2026-02-20', amount: 58.32, positive: true, icon: '💰', status: 'Completed', acc: 'Savings' },
    { id: 12, name: 'Zara', cat: 'Shopping', date: '2026-02-19', amount: -145.00, icon: '👗', status: 'Completed', acc: 'Checking' },
];

const CATS = ['All', 'Income', 'Food & Drink', 'Shopping', 'Transfer', 'Utilities', 'Entertainment', 'Cash', 'Health'];

function statusChip(s) {
    if (s === 'Completed') return 'chip-green';
    if (s === 'Pending') return 'chip-yellow';
    return 'chip-blue';
}

export default function Transactions() {
    const [cat, setCat] = useState('All');
    const [search, setSearch] = useState('');

    const filtered = ALL_TX.filter(tx => {
        const matchCat = cat === 'All' || tx.cat === cat;
        const matchSearch = tx.name.toLowerCase().includes(search.toLowerCase()) || tx.cat.toLowerCase().includes(search.toLowerCase());
        return matchCat && matchSearch;
    });

    const totalIncome = filtered.filter(t => t.positive).reduce((a, b) => a + b.amount, 0);
    const totalExpenses = filtered.filter(t => !t.positive).reduce((a, b) => a + Math.abs(b.amount), 0);

    return (
        <Layout title="Transactions">
            {/* Summary */}
            <div className="grid-3 spacer">
                <div className="card card-sm">
                    <div className="stat-label">Filtered Income</div>
                    <div className="stat-value" style={{ color: 'var(--green)' }}>+${totalIncome.toFixed(2)}</div>
                </div>
                <div className="card card-sm">
                    <div className="stat-label">Filtered Expenses</div>
                    <div className="stat-value">-${totalExpenses.toFixed(2)}</div>
                </div>
                <div className="card card-sm">
                    <div className="stat-label">Net</div>
                    <div className="stat-value" style={{ color: (totalIncome - totalExpenses) >= 0 ? 'var(--green)' : 'var(--red)' }}>
                        {(totalIncome - totalExpenses) >= 0 ? '+' : ''}{(totalIncome - totalExpenses).toFixed(2)}
                    </div>
                </div>
            </div>

            <div className="card">
                {/* Filters */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
                    <div className="filter-row" style={{ margin: 0 }}>
                        {CATS.map(c => (
                            <button key={c} className={`filter-btn${cat === c ? ' active' : ''}`} onClick={() => setCat(c)}>{c}</button>
                        ))}
                    </div>
                    <input
                        className="search-box"
                        placeholder="🔍  Search transactions..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </div>

                {/* Table */}
                <table className="tx-table">
                    <thead>
                        <tr>
                            <th>Transaction</th>
                            <th>Account</th>
                            <th>Date</th>
                            <th>Status</th>
                            <th style={{ textAlign: 'right' }}>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filtered.map(tx => (
                            <tr key={tx.id}>
                                <td>
                                    <div className="tx-row">
                                        <div className="tx-icon" style={{ background: 'rgba(255,255,255,0.06)' }}>{tx.icon}</div>
                                        <div>
                                            <div className="tx-name">{tx.name}</div>
                                            <div className="tx-sub">{tx.cat}</div>
                                        </div>
                                    </div>
                                </td>
                                <td style={{ color: 'var(--text-muted)' }}>{tx.acc}</td>
                                <td style={{ color: 'var(--text-muted)' }}>{tx.date}</td>
                                <td><span className={`chip ${statusChip(tx.status)}`}>{tx.status}</span></td>
                                <td style={{ textAlign: 'right' }}>
                                    <span className={tx.positive ? 'amount-positive' : 'amount-negative'}>
                                        {tx.positive ? '+' : ''}{tx.amount < 0 ? '-' : ''}${Math.abs(tx.amount).toFixed(2)}
                                    </span>
                                </td>
                            </tr>
                        ))}
                        {filtered.length === 0 && (
                            <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No transactions found.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>
        </Layout>
    );
}
