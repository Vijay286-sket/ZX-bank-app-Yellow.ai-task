import Link from 'next/link';
import { useRouter } from 'next/router';

const navItems = [
  { href: '/', icon: '◉', label: 'Dashboard' },
  { href: '/transactions', icon: '↕', label: 'Transactions' },
  { href: '/chat', icon: '💬', label: 'AI Assistant' },
];

export default function Layout({ children, title = 'Dashboard' }) {
  const router = useRouter();
  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">ZX</div>
          <div>
            <div className="logo-text">ZX Bank</div>
            <div className="logo-sub">Personal Banking</div>
          </div>
        </div>

        <nav className="nav">
          <div className="nav-section-label">Main</div>
          {navItems.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item${router.pathname === item.href ? ' active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </Link>
          ))}
          <div className="nav-section-label">Settings</div>
          <a href="#" className="nav-item">
            <span className="nav-icon">⚙</span> Settings
          </a>
          <a href="#" className="nav-item">
            <span className="nav-icon">?</span> Help & Support
          </a>
        </nav>

        <div className="sidebar-footer">
          <div className="avatar-row">
            <div className="avatar">JD</div>
            <div className="avatar-info">
              <div className="name">Jane Doe</div>
              <div className="role">Premium Member</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="main">
        <header className="header">
          <div className="page-title">{title}</div>
          <div className="header-right">
            <div className="icon-btn">🔔<span className="badge" style={{position:'absolute',top:6,right:6,lineHeight:1}}>3</span></div>
            <div className="icon-btn">👤</div>
          </div>
        </header>
        <div className="content">{children}</div>
      </div>
    </div>
  );
}
