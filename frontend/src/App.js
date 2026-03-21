import React, { useCallback, useEffect, useState } from 'react';
import { BrowserRouter as Router, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import './App.css';
import DashboardPage from './pages/Roadmap';
import TheoryPage from './pages/Theory';
import PracticePage from './pages/Practice';
import WeeklyReviewPage from './pages/WeeklyReview';
import MockExamPage from './pages/MockExam';
import ProgressPage from './pages/Progress';
import ProfilePage from './pages/Profile';

const API = process.env.REACT_APP_BACKEND_URL;

const pageTitles = {
  '/': ['Дашборд', 'Главная точка входа: что делать сейчас, где вы на пути и что блокирует прогресс'],
  '/theory': ['Теория', 'Краткая и полная теория по каждому заданию'],
  '/practice': ['Практика', 'Свободный режим, guided path, слабые темы и работа над ошибками'],
  '/weekly-review': ['Weekly Review', 'Обязательный контрольный блок между этапами дорожки'],
  '/mock-exam': ['Пробник', 'Экзаменационный и тренировочный режимы с таймером и паузой'],
  '/progress': ['Аналитика', 'Покрытие, прогноз баллов, история и проблемные зоны'],
  '/profile': ['Профиль', 'Локальные настройки ученика'],
};

function Sidebar({ profile }) {
  const navItems = [
    { path: '/', label: 'Дашборд', icon: 'M4 10.5L12 4l8 6.5V20a1 1 0 01-1 1h-4v-6H9v6H5a1 1 0 01-1-1v-9.5z' },
    { path: '/theory', label: 'Теория', icon: 'M5 5h6a4 4 0 014 4v10H9a4 4 0 00-4 4V5zm14 0h-6a4 4 0 00-4 4v10h6a4 4 0 014 4V5z' },
    { path: '/practice', label: 'Практика', icon: 'M7 7h10M7 12h10M7 17h6M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z' },
    { path: '/weekly-review', label: 'Weekly Review', icon: 'M4 7h16M7 3v4m10-4v4M5 11h14v8H5z' },
    { path: '/mock-exam', label: 'Пробник', icon: 'M7 4h10l3 3v13a1 1 0 01-1 1H7a1 1 0 01-1-1V5a1 1 0 011-1zm9 0v4h4' },
    { path: '/progress', label: 'Аналитика', icon: 'M5 19V9m7 10V5m7 14v-8M3 21h18' },
    { path: '/profile', label: 'Профиль', icon: 'M12 13a4 4 0 100-8 4 4 0 000 8zm0 2c-4.418 0-8 2.015-8 4.5V21h16v-1.5C20 17.015 16.418 15 12 15z' },
  ];

  return (
    <aside className="sidebar" data-testid="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">ЕГЭ</div>
          <div>
            <div className="sidebar-logo-text">Informatics Trainer</div>
            <div className="sidebar-logo-sub">локально · офлайн · без лишней геймификации</div>
          </div>
        </div>

        <div className="sidebar-profile-chip">
          <div className="sidebar-profile-name">{profile?.name || 'Ученик'}</div>
          <div className="sidebar-profile-meta">
            <span className="badge badge-muted">{profile?.learning_mode === 'free' ? 'Свободный режим' : 'Guided path'}</span>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end={item.path === '/'}
          >
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
              <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
            </svg>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="saving-indicator">
          <div className="saving-dot" />
          Локальные данные сохранены
        </div>
        <div style={{ marginTop: 6 }}>UTF-8 · SQLite · Offline first</div>
      </div>
    </aside>
  );
}

function Topbar() {
  const location = useLocation();
  const [title, subtitle] = pageTitles[location.pathname] || ['Тренажёр', ''];

  return (
    <header className="topbar" data-testid="topbar">
      <div>
        <div className="topbar-title">{title}</div>
        <div className="topbar-subtitle">{subtitle}</div>
      </div>
      <div className="topbar-actions">
        <div className="saving-indicator">
          <div className="saving-dot" />
          Автосохранение
        </div>
      </div>
    </header>
  );
}

function AppLayout({ profile, reloadProfile }) {
  return (
    <div className="app-layout">
      <Sidebar profile={profile} />
      <main className="main-content">
        <Topbar />
        <div className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage profile={profile} reloadProfile={reloadProfile} />} />
            <Route path="/theory" element={<TheoryPage />} />
            <Route path="/practice" element={<PracticePage profile={profile} />} />
            <Route path="/weekly-review" element={<WeeklyReviewPage />} />
            <Route path="/mock-exam" element={<MockExamPage />} />
            <Route path="/progress" element={<ProgressPage />} />
            <Route path="/profile" element={<ProfilePage profile={profile} onProfileSaved={reloadProfile} />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/profile`);
      const data = await response.json();
      setProfile(data);
    } catch (error) {
      console.error('Profile load error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  if (loading) {
    return (
      <div className="app-loading-screen">
        <div className="sidebar-logo-icon app-loading-logo">ЕГЭ</div>
        <div className="app-loading-title">Загрузка локального тренажёра</div>
        <div className="app-loading-subtitle">Поднимаем дашборд, аналитику и дорожку обучения…</div>
      </div>
    );
  }

  return (
    <Router>
      <AppLayout profile={profile} reloadProfile={loadProfile} />
    </Router>
  );
}
