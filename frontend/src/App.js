import React, { useCallback, useEffect, useState } from 'react';
import { BrowserRouter as Router, NavLink, Route, Routes, useLocation } from 'react-router-dom';
import './App.css';

import DashboardPage from './pages/Roadmap';
import TheoryPage from './pages/Theory';
import PracticePage from './pages/Practice';
import TaskBankPage from './pages/TaskBank';
import WeeklyReviewPage from './pages/WeeklyReview';
import MockExamPage from './pages/MockExam';
import ProgressPage from './pages/Progress';
import ProfilePage from './pages/Profile';

import API from './config/api';

const pageTitles = {
  '/': {
    title: 'Roadmap',
    subtitle: 'Текущий этап, слабые темы и следующий осмысленный шаг.',
  },
  '/theory': {
    title: 'Theory',
    subtitle: 'Краткая и полная теория по каждому номеру + общая стратегия ЕГЭ.',
  },
  '/practice': {
    title: 'Practice',
    subtitle: 'Последовательная практика: подсказки после ошибок и добивка слабых мест.',
  },
  '/task-bank': {
    title: 'Task Bank',
    subtitle: 'Отдельный банк случайных заданий с независимой статистикой.',
  },
  '/weekly-review': {
    title: 'Weekly Review',
    subtitle: 'Контрольный блок между этапами дорожки.',
  },
  '/mock-exam': {
    title: 'Mock Exam',
    subtitle: 'Пробник в формате экзамена: свободная навигация, проверка после завершения.',
  },
  '/progress': {
    title: 'Progress',
    subtitle: 'Покрытие тем, точность, история и прогноз.',
  },
  '/profile': {
    title: 'Profile',
    subtitle: 'Локальные настройки и цель подготовки.',
  },
};

function daysUntil(dateString) {
  if (!dateString) return null;
  const target = new Date(dateString);
  if (Number.isNaN(target.getTime())) return null;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  target.setHours(0, 0, 0, 0);

  return Math.round((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
}

function Sidebar({ profile }) {
  const navGroups = [
    {
      label: 'Учёба',
      items: [
        { path: '/', label: 'Дорожка', icon: 'M4 10.5L12 4l8 6.5V20a1 1 0 01-1 1h-4v-6H9v6H5a1 1 0 01-1-1v-9.5z' },
        { path: '/theory', label: 'Теория', icon: 'M5 5h6a4 4 0 014 4v10H9a4 4 0 00-4 4V5zm14 0h-6a4 4 0 00-4 4v10h6a4 4 0 014 4V5z' },
        { path: '/practice', label: 'Практика', icon: 'M7 7h10M7 12h10M7 17h6M5 3h14a2 2 0 012 2v14a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2z' },
        { path: '/task-bank', label: 'Банк задач', icon: 'M4 6h16M4 12h16M4 18h16' },
      ],
    },
    {
      label: 'Контроль',
      items: [
        { path: '/weekly-review', label: 'Weekly Review', icon: 'M4 7h16M7 3v4m10-4v4M5 11h14v8H5z' },
        { path: '/mock-exam', label: 'Пробник', icon: 'M7 4h10l3 3v13a1 1 0 01-1 1H7a1 1 0 01-1-1V5a1 1 0 011-1zm9 0v4h4' },
        { path: '/progress', label: 'Аналитика', icon: 'M5 19V9m7 10V5m7 14v-8M3 21h18' },
      ],
    },
    {
      label: 'Аккаунт',
      items: [{ path: '/profile', label: 'Профиль', icon: 'M12 13a4 4 0 100-8 4 4 0 000 8zm0 2c-4.418 0-8 2.015-8 4.5V21h16v-1.5C20 17.015 16.418 15 12 15z' }],
    },
  ];

  const examDays = daysUntil(profile?.exam_date);

  return (
    <aside className="sidebar" data-testid="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">ЕГЭ</div>
          <div>
            <div className="sidebar-logo-text">Informatics Trainer</div>
            <div className="sidebar-logo-sub">offline-first desktop · локальная база · без лишнего шума</div>
          </div>
        </div>

        <div className="sidebar-profile-chip">
          <div className="sidebar-profile-label">Локальный профиль</div>
          <div className="sidebar-profile-name">{profile?.name || 'Ученик'}</div>
          <div className="sidebar-profile-meta">
            <span className="badge badge-accent">{profile?.learning_mode === 'free' ? 'Свободный режим' : 'Guided path'}</span>
            <span className="badge badge-muted">Цель: {profile?.target_score || 80}</span>
            {typeof examDays === 'number' ? (
              <span className={`badge ${examDays <= 30 ? 'badge-warning' : 'badge-muted'}`}>
                {examDays >= 0 ? `Экзамен через ${examDays} дн.` : 'Дата экзамена прошла'}
              </span>
            ) : null}
          </div>
        </div>
      </div>

      <div className="sidebar-nav">
        {navGroups.map((group) => (
          <div key={group.label}>
            <div className="sidebar-section-label">{group.label}</div>
            {group.items.map((item) => (
              <NavLink key={item.path} to={item.path} end={item.path === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.6}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                </svg>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="saving-indicator">
          <div className="saving-dot" />
          Локальные данные сохранены
        </div>
        <div style={{ marginTop: 8 }}>UTF-8 · SQLite · Offline-compatible</div>
      </div>
    </aside>
  );
}

function Topbar({ profile }) {
  const location = useLocation();
  const meta = pageTitles[location.pathname] || { title: 'EGE Trainer', subtitle: '' };
  const examDays = daysUntil(profile?.exam_date);

  return (
    <header className="topbar" data-testid="topbar">
      <div>
        <div className="topbar-title">{meta.title}</div>
        <div className="topbar-subtitle">{meta.subtitle}</div>
      </div>

      <div className="topbar-actions">
        <div className="topbar-chip">
          <div className="saving-dot" />
          Автосохранение
        </div>
        <div className="topbar-chip">Локально</div>
        <div className="topbar-chip">Цель <strong>{profile?.target_score || 80}</strong></div>
        {typeof examDays === 'number' ? <div className="topbar-chip">Экзамен <strong>{examDays >= 0 ? `через ${examDays} дн.` : 'прошёл'}</strong></div> : null}
      </div>
    </header>
  );
}

function BaselineModal({ open, onSaved }) {
  const [pythonLevel, setPythonLevel] = useState('beginner');
  const [egeLevel, setEgeLevel] = useState('start');
  const [weeklyGoalHours, setWeeklyGoalHours] = useState(6);
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);

  if (!open) return null;

  const handleSubmit = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API}/api/onboarding/baseline`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          python_level: pythonLevel,
          ege_level: egeLevel,
          weekly_goal_hours: Number(weeklyGoalHours || 0),
          note,
        }),
      });
      const data = await response.json();
      onSaved?.(data?.baseline || null);
    } catch (error) {
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="section-title">Небольшой стартовый опрос</div>
        <div className="section-description" style={{ marginTop: 8 }}>
          Это нужно, чтобы подстроить дорожку и темп без перегруза.
        </div>

        <div className="info-grid" style={{ marginTop: 16 }}>
          <div className="info-card" style={{ gridColumn: '1 / -1' }}>
            <div className="info-label">Уровень Python</div>
            <div className="segment-control" style={{ marginTop: 10 }}>
              <button className={`segment-btn ${pythonLevel === 'beginner' ? 'active' : ''}`} onClick={() => setPythonLevel('beginner')}>Начинающий</button>
              <button className={`segment-btn ${pythonLevel === 'basic' ? 'active' : ''}`} onClick={() => setPythonLevel('basic')}>Базовый</button>
              <button className={`segment-btn ${pythonLevel === 'confident' ? 'active' : ''}`} onClick={() => setPythonLevel('confident')}>Уверенный</button>
            </div>
          </div>

          <div className="info-card" style={{ gridColumn: '1 / -1' }}>
            <div className="info-label">Текущий уровень ЕГЭ</div>
            <div className="segment-control" style={{ marginTop: 10 }}>
              <button className={`segment-btn ${egeLevel === 'start' ? 'active' : ''}`} onClick={() => setEgeLevel('start')}>С нуля</button>
              <button className={`segment-btn ${egeLevel === 'middle' ? 'active' : ''}`} onClick={() => setEgeLevel('middle')}>Средний</button>
              <button className={`segment-btn ${egeLevel === 'advanced' ? 'active' : ''}`} onClick={() => setEgeLevel('advanced')}>Продвинутый</button>
            </div>
          </div>

          <div className="info-card">
            <div className="info-label">Часов в неделю</div>
            <input
              className="input"
              type="number"
              min="1"
              max="40"
              value={weeklyGoalHours}
              onChange={(event) => setWeeklyGoalHours(event.target.value)}
              style={{ marginTop: 8 }}
            />
          </div>

          <div className="info-card">
            <div className="info-label">Комментарий (опционально)</div>
            <input
              className="input"
              value={note}
              onChange={(event) => setNote(event.target.value)}
              placeholder="Например: нужен мягкий старт"
              style={{ marginTop: 8 }}
            />
          </div>
        </div>

        <div className="row-actions" style={{ marginTop: 18 }}>
          <button className="btn btn-primary btn-md" onClick={handleSubmit} disabled={saving}>{saving ? 'Сохраняем...' : 'Сохранить и продолжить'}</button>
        </div>
      </div>
    </div>
  );
}

function AppLayout({ profile, reloadProfile }) {
  return (
    <div className="app-layout">
      <Sidebar profile={profile} />
      <main className="main-content">
        <Topbar profile={profile} />
        <div className="page-content">
          <Routes>
            <Route path="/" element={<DashboardPage profile={profile} reloadProfile={reloadProfile} />} />
            <Route path="/theory" element={<TheoryPage profile={profile} />} />
            <Route path="/practice" element={<PracticePage profile={profile} />} />
            <Route path="/task-bank" element={<TaskBankPage profile={profile} />} />
            <Route path="/weekly-review" element={<WeeklyReviewPage profile={profile} />} />
            <Route path="/mock-exam" element={<MockExamPage profile={profile} />} />
            <Route path="/progress" element={<ProgressPage profile={profile} />} />
            <Route path="/profile" element={<ProfilePage profile={profile} onProfileSaved={reloadProfile} />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  const [profile, setProfile] = useState(null);
  const [baseline, setBaseline] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadBootstrap = useCallback(async () => {
    setLoading(true);
    try {
      const [profileResponse, baselineResponse] = await Promise.all([
        fetch(`${API}/api/profile`),
        fetch(`${API}/api/onboarding/baseline`),
      ]);
      const [profileData, baselineData] = await Promise.all([
        profileResponse.json(),
        baselineResponse.json(),
      ]);
      setProfile(profileData);
      setBaseline(baselineData);
    } catch (error) {
      console.error('Bootstrap load error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBootstrap();
  }, [loadBootstrap]);

  if (loading) {
    return (
      <div className="app-loading-screen">
        <div className="app-loading-card loading-shimmer">
          <div className="sidebar-logo-icon app-loading-logo">ЕГЭ</div>
          <div className="app-loading-title">Загрузка локального тренажёра</div>
          <div className="app-loading-subtitle">Поднимаем профиль, статистику и дорожку обучения из локальной базы.</div>
        </div>
      </div>
    );
  }

  const baselineOpen = !baseline?.completed;

  return (
    <Router>
      <AppLayout profile={profile} reloadProfile={loadBootstrap} />
      <BaselineModal
        open={baselineOpen}
        onSaved={(savedBaseline) => {
          setBaseline((prev) => ({ ...(prev || {}), ...(savedBaseline || {}), completed: true }));
          loadBootstrap();
        }}
      />
    </Router>
  );
}