import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useNavigate, useLocation } from 'react-router-dom';
import './App.css';
import RoadmapPage from './pages/Roadmap';
import TheoryPage from './pages/Theory';
import PracticePage from './pages/Practice';
import WeeklyReviewPage from './pages/WeeklyReview';
import MockExamPage from './pages/MockExam';
import ProgressPage from './pages/Progress';
import ProfilePage from './pages/Profile';

const API = process.env.REACT_APP_BACKEND_URL;

function Sidebar({ profile }) {
  const location = useLocation();
  const navItems = [
    { path: '/', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', label: 'Дорожка' },
    { path: '/theory', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253', label: 'Теория' },
    { path: '/practice', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4', label: 'Практика' },
    { path: '/weekly-review', icon: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15', label: 'Weekly Review' },
    { path: '/mock-exam', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z', label: 'Пробник' },
    { path: '/progress', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', label: 'Прогресс' },
    { path: '/profile', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z', label: 'Профиль' },
  ];

  return (
    <div className="sidebar" data-testid="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">ЕГЭ</div>
          <div>
            <div className="sidebar-logo-text">Информатика</div>
            <div className="sidebar-logo-sub">Тренажёр</div>
          </div>
        </div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g,'-')}`}
            end={item.path === '/'}
          >
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
            </svg>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="saving-indicator">
          <div className="saving-dot"></div>
          Сохранено
        </div>
        <div style={{marginTop: 4}}>v1.0.0</div>
      </div>
    </div>
  );
}

function Topbar({ title, subtitle }) {
  return (
    <div className="topbar" data-testid="topbar">
      <div style={{display:'flex',alignItems:'baseline'}}>
        <span className="topbar-title">{title}</span>
        {subtitle && <span className="topbar-subtitle">{subtitle}</span>}
      </div>
      <div className="topbar-actions">
        <div className="saving-indicator">
          <div className="saving-dot"></div>
          Автосохранение
        </div>
      </div>
    </div>
  );
}

function OnboardingModal({ onComplete }) {
  const [name, setName] = useState('');
  const [targetScore, setTargetScore] = useState(80);
  const [examDate, setExamDate] = useState('2026-06-01');
  const [confidence, setConfidence] = useState('medium');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name || 'Ученик',
          target_score: targetScore,
          exam_date: examDate,
          confidence_level: confidence,
          daily_hours: 2,
          weekly_hours: 10,
          font_size: 14,
        }),
      });
      onComplete();
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="modal-overlay" data-testid="onboarding-modal">
      <div className="modal" style={{maxWidth: 480}}>
        <h2 className="modal-title" style={{fontSize: 22, marginBottom: 4}}>Добро пожаловать!</h2>
        <p style={{color: 'var(--text-secondary)', marginBottom: 24, fontSize: 14}}>
          Создайте локальный профиль для отслеживания прогресса
        </p>

        <div style={{display:'flex',flexDirection:'column',gap:16}}>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Имя или ник</label>
            <input className="input" value={name} onChange={e => setName(e.target.value)} placeholder="Как вас называть?" data-testid="onboard-name" />
          </div>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Целевой балл ЕГЭ</label>
            <input className="input" type="number" min={0} max={100} value={targetScore} onChange={e => setTargetScore(+e.target.value)} data-testid="onboard-score" />
          </div>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Дата экзамена</label>
            <input className="input" type="date" value={examDate} onChange={e => setExamDate(e.target.value)} data-testid="onboard-date" />
          </div>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Уровень уверенности</label>
            <div className="segment-control" style={{width:'100%'}}>
              {[{v:'low',l:'Начальный'},{v:'medium',l:'Средний'},{v:'high',l:'Уверенный'}].map(o => (
                <button key={o.v} className={`segment-btn ${confidence===o.v?'active':''}`} onClick={() => setConfidence(o.v)} style={{flex:1}} data-testid={`confidence-${o.v}`}>{o.l}</button>
              ))}
            </div>
          </div>
        </div>

        <div style={{display:'flex',gap:12,marginTop:24}}>
          <button className="btn btn-primary btn-md" style={{flex:1}} onClick={handleSubmit} disabled={loading} data-testid="create-profile-btn">
            {loading ? 'Создание...' : 'Создать профиль'}
          </button>
          <button className="btn btn-secondary btn-md" onClick={() => { setName('Ученик'); handleSubmit(); }} data-testid="default-profile-btn">
            По умолчанию
          </button>
        </div>
      </div>
    </div>
  );
}

const pageTitles = {
  '/': ['Дорожка', 'Ваш путь к успешной сдаче ЕГЭ'],
  '/theory': ['Теория', 'Задания 1–27'],
  '/practice': ['Практика', 'Решайте задания'],
  '/weekly-review': ['Weekly Review', 'Еженедельное повторение'],
  '/mock-exam': ['Пробник', 'Полноценный экзамен'],
  '/progress': ['Прогресс', 'Аналитика и статистика'],
  '/profile': ['Профиль', 'Настройки'],
};

function AppLayout({ profile }) {
  const location = useLocation();
  const [title, subtitle] = pageTitles[location.pathname] || ['', ''];

  return (
    <div className="app-layout">
      <Sidebar profile={profile} />
      <div className="main-content">
        <Topbar title={title} subtitle={subtitle} />
        <div className="page-content">
          <Routes>
            <Route path="/" element={<RoadmapPage profile={profile} />} />
            <Route path="/theory" element={<TheoryPage />} />
            <Route path="/practice" element={<PracticePage />} />
            <Route path="/weekly-review" element={<WeeklyReviewPage />} />
            <Route path="/mock-exam" element={<MockExamPage />} />
            <Route path="/progress" element={<ProgressPage />} />
            <Route path="/profile" element={<ProfilePage profile={profile} />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  const loadProfile = useCallback(async () => {
    try {
      const res = await fetch(`${API}/api/profile`);
      const data = await res.json();
      if (data.exists) {
        setProfile(data);
        setShowOnboarding(false);
      } else {
        setShowOnboarding(true);
      }
    } catch (e) {
      console.error('Profile load error:', e);
      setShowOnboarding(true);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadProfile(); }, [loadProfile]);

  if (loading) {
    return (
      <div style={{height:'100vh',display:'flex',alignItems:'center',justifyContent:'center',background:'var(--bg-app)',flexDirection:'column',gap:16}}>
        <div className="sidebar-logo-icon" style={{width:56,height:56,fontSize:20,borderRadius:14}}>ЕГЭ</div>
        <div style={{color:'var(--text-primary)',fontSize:16,fontWeight:600}}>Информатика Тренажёр</div>
        <div style={{color:'var(--text-muted)',fontSize:13}}>Загрузка...</div>
      </div>
    );
  }

  return (
    <Router>
      {showOnboarding && <OnboardingModal onComplete={loadProfile} />}
      <AppLayout profile={profile} />
    </Router>
  );
}
