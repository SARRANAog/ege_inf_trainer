import React, { useEffect, useMemo, useState } from 'react';
import API from '../config/api';

export default function ProfilePage({ profile: initialProfile, onProfileSaved }) {
  const [profile, setProfile] = useState(initialProfile || {});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showReset, setShowReset] = useState(false);

  useEffect(() => { fetch(`${API}/api/profile`).then((r) => r.json()).then((data) => { if (data.exists) setProfile(data); }).catch(() => {}); }, []);
  const update = (key, val) => setProfile((prev) => ({ ...prev, [key]: val }));
  const firstStart = useMemo(() => (profile.total_exercises_done || 0) === 0, [profile.total_exercises_done]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`${API}/api/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: profile.name, target_score: profile.target_score, exam_date: profile.exam_date,
          confidence_level: profile.confidence_level, daily_hours: profile.daily_hours, weekly_hours: profile.weekly_hours,
          font_size: profile.font_size, learning_mode: profile.learning_mode,
        }),
      });
      setSaved(true);
      await onProfileSaved?.();
      setTimeout(() => setSaved(false), 2000);
    } catch (error) { console.error(error); }
    setSaving(false);
  };

  return <div className="page-shell fade-in">
    <div className="hero-card dashboard-hero">
      <div className="eyebrow">Локальные настройки</div>
      <div className="hero-title">Профиль ученика</div>
      <div className="hero-description">Все параметры сохраняются локально: цель, дата экзамена, режим обучения и интерфейсные настройки.</div>
      <div className="task-chip-row" style={{ marginTop: 16 }}>
        <span className="badge badge-accent">{profile.learning_mode === 'free' ? 'Свободный режим' : 'Guided path'}</span>
        <span className="badge badge-muted">Цель: {profile.target_score || 80}</span>
        {saved ? <span className="badge badge-success">Сохранено</span> : null}
      </div>
    </div>

    {firstStart ? <div className="card"><div className="section-title">Первый запуск</div><div className="section-description">Здесь можно спокойно зафиксировать цель и ритм подготовки до начала активной практики.</div></div> : null}

    <div className="page-grid-2">
      <div className="card">
        <div className="section-title">Профиль и цель</div>
        <div className="form-grid" style={{ marginTop: 18 }}>
          <div className="field-group"><label className="field-label">Имя / ник</label><input className="input" value={profile.name || ''} onChange={(e) => update('name', e.target.value)} /></div>
          <div className="field-grid-2">
            <div className="field-group"><label className="field-label">Целевой балл</label><input className="input" type="number" min={0} max={100} value={profile.target_score || 80} onChange={(e) => update('target_score', +e.target.value)} /></div>
            <div className="field-group"><label className="field-label">Дата экзамена</label><input className="input" type="date" value={profile.exam_date || ''} onChange={(e) => update('exam_date', e.target.value)} /></div>
          </div>
          <div className="field-group">
            <label className="field-label">Уровень уверенности</label>
            <div className="segment-control" style={{ width: '100%' }}>
              {[{ v: 'low', l: 'Начальный' }, { v: 'medium', l: 'Средний' }, { v: 'high', l: 'Уверенный' }].map((option) => <button key={option.v} className={`segment-btn ${profile.confidence_level === option.v ? 'active' : ''}`} onClick={() => update('confidence_level', option.v)} style={{ flex: 1 }}>{option.l}</button>)}
            </div>
          </div>
          <div className="field-group">
            <label className="field-label">Режим обучения</label>
            <div className="segment-control" style={{ width: '100%' }}>
              {[{ v: 'guided', l: 'Guided path' }, { v: 'free', l: 'Свободный режим' }].map((option) => <button key={option.v} className={`segment-btn ${profile.learning_mode === option.v ? 'active' : ''}`} onClick={() => update('learning_mode', option.v)} style={{ flex: 1 }}>{option.l}</button>)}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="section-title">Ритм и интерфейс</div>
        <div className="form-grid" style={{ marginTop: 18 }}>
          <div className="field-grid-2">
            <div className="field-group"><label className="field-label">Часов в день</label><input className="input" type="number" min={0} max={12} step="0.5" value={profile.daily_hours ?? 2} onChange={(e) => update('daily_hours', Number(e.target.value))} /></div>
            <div className="field-group"><label className="field-label">Часов в неделю</label><input className="input" type="number" min={0} max={60} step="0.5" value={profile.weekly_hours ?? 10} onChange={(e) => update('weekly_hours', Number(e.target.value))} /></div>
          </div>
          <div className="field-group"><label className="field-label">Размер шрифта редактора</label><input className="input" type="number" min={10} max={24} value={profile.font_size || 14} onChange={(e) => update('font_size', +e.target.value)} /><div className="field-help">Используется в кодовом редакторе практики и пробника.</div></div>
          <div className="row-actions" style={{ marginTop: 8 }}><button className="btn btn-primary btn-md" onClick={handleSave} disabled={saving}>{saving ? 'Сохранение…' : 'Сохранить'}</button></div>
        </div>
      </div>
    </div>

    <div className="page-grid-2">
      <div className="card"><div className="section-title">Локальная статистика</div><div className="info-grid" style={{ marginTop: 18 }}><div className="info-card"><div className="info-label">Решено заданий</div><div className="info-value" style={{ color: 'var(--accent-strong)' }}>{profile.total_exercises_done || 0}</div></div><div className="info-card"><div className="info-label">Правильных решений</div><div className="info-value" style={{ color: 'var(--success)' }}>{profile.total_correct || 0}</div></div></div></div>
      <div className="card" style={{ borderColor: 'rgba(225,123,135,0.22)' }}><div className="section-title" style={{ color: 'var(--danger)' }}>Опасная зона</div><div className="section-description">Это действие удалит все локальные данные о прогрессе, попытках, пробниках и Weekly Review.</div><div className="row-actions" style={{ marginTop: 18 }}><button className="btn btn-danger btn-sm" onClick={() => setShowReset(true)}>Сбросить весь прогресс</button></div></div>
    </div>

    {showReset ? <div className="modal-overlay"><div className="modal" style={{ textAlign: 'center' }}><div className="section-title" style={{ color: 'var(--danger)' }}>Сбросить прогресс?</div><div style={{ marginTop: 12, fontSize: 14, lineHeight: 1.75, color: 'var(--text-secondary)' }}>Все данные будут безвозвратно удалены: прогресс, попытки, пробники и Weekly Review.</div><div className="row-actions" style={{ justifyContent: 'center', marginTop: 22 }}><button className="btn btn-danger btn-md" onClick={async () => { await fetch(`${API}/api/profile/reset`, { method: 'POST', headers: { 'Content-Type': 'application/json' } }); setShowReset(false); window.location.reload(); }}>Да, сбросить</button><button className="btn btn-secondary btn-md" onClick={() => setShowReset(false)}>Отмена</button></div></div></div> : null}
  </div>;
}
