import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import API from '../config/api';

function MetricCard({ label, value, sublabel, tone = 'var(--accent)' }) {
  return <div className="metric-card"><div className="metric-value" style={{ color: tone }}>{value}</div><div className="metric-label">{label}</div>{sublabel ? <div style={{ marginTop: 10, fontSize: 12, lineHeight: 1.65, color: 'var(--text-secondary)' }}>{sublabel}</div> : null}</div>;
}
function readinessText(center) { if (center >= 82) return 'Сильная готовность'; if (center >= 68) return 'Хорошая динамика'; if (center >= 45) return 'Нужна стабилизация'; return 'Ранняя стадия'; }

export default function ProgressPage() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { (async () => {
    setLoading(true);
    try { const response = await fetch(`${API}/api/progress`); setProgress(await response.json()); }
    catch (error) { console.error(error); }
    finally { setLoading(false); }
  })(); }, []);

  const weakTasks = useMemo(() => (progress?.tasks || []).filter((task) => task.status === 'weak' || task.mistake_burden >= 2).slice(0, 8), [progress]);
  const strongTasks = useMemo(() => (progress?.tasks || []).filter((task) => task.status === 'mastered').slice(0, 8), [progress]);

  if (loading) return <div className="page-shell fade-in"><div className="state-card loading-shimmer"><div className="state-title">Загрузка аналитики</div><div className="state-description">Считаем покрытие, среднюю точность, историю и прогноз баллов.</div></div></div>;
  if (!progress) return <div className="page-shell fade-in"><div className="state-card"><div className="state-title">Не удалось загрузить аналитику</div></div></div>;

  const estimated = progress.estimated_score || {};
  const readiness = readinessText(estimated.center || 0);

  return <div className="page-shell page-shell-wide fade-in">
    <div className="hero-card dashboard-hero">
      <div className="eyebrow">Учебная аналитика</div>
      <div className="hero-title">Прогноз и фактический прогресс</div>
      <div className="hero-description">Это не декоративная цифра: прогноз строится по покрытию тем, средней точности и завершённым пробникам.</div>
      <div className="task-chip-row" style={{ marginTop: 16 }}><span className="badge badge-accent">{estimated.level || '—'}</span><span className="badge badge-muted">{readiness}</span></div>
      <div className="analytics-grid" style={{ marginTop: 18 }}>
        <MetricCard label="Покрытие" value={`${progress.coverage?.toFixed?.(0) || 0}%`} tone="var(--accent-strong)" sublabel="Сколько заданий уже хотя бы начаты." />
        <MetricCard label="Средняя точность" value={`${progress.avg_accuracy?.toFixed?.(0) || 0}%`} tone="var(--success)" sublabel="Средняя результативность по уже начатым заданиям." />
        <MetricCard label="Диапазон баллов" value={estimated.min !== undefined ? `${estimated.min}–${estimated.max}` : '—'} tone="var(--warning)" sublabel="Оценка по текущим попыткам и пробникам." />
        <MetricCard label="Всего попыток" value={progress.total_attempts || 0} tone="var(--accent)" sublabel="Все проверки в практике, review и пробниках." />
      </div>
    </div>

    <div className="page-grid-2">
      <div className="card"><div className="section-title">Сильные стороны</div>{strongTasks.length === 0 ? <div style={{ marginTop: 16, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>Пока нет заданий, дошедших до статуса mastered.</div> : <div className="task-chip-row" style={{ marginTop: 16 }}>{strongTasks.map((task) => <Link key={task.task_number} to={`/practice?task=${task.task_number}&mode=free`} className="badge badge-success">№{task.task_number} · {task.accuracy?.toFixed?.(0) || 0}%</Link>)}</div>}</div>
      <div className="card"><div className="section-title">Что тянет результат вниз</div>{weakTasks.length === 0 ? <div style={{ marginTop: 16, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>Явных слабых мест сейчас нет.</div> : <div className="task-chip-row" style={{ marginTop: 16 }}>{weakTasks.map((task) => <Link key={task.task_number} to={`/practice?task=${task.task_number}&mode=weak`} className="badge badge-danger">№{task.task_number} · {task.accuracy?.toFixed?.(0) || 0}%</Link>)}</div>}</div>
    </div>

    <div className="card">
      <div className="section-title">История за последние дни</div>
      {(progress.history || []).length === 0 ? <div style={{ marginTop: 16, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>История появится после первых попыток.</div> : <div className="history-list" style={{ marginTop: 16 }}>{progress.history.map((point) => <div key={point.date} className="history-row"><div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{point.date}</div><div><div className="progress-bar"><div className={`progress-fill ${point.accuracy >= 80 ? 'success' : point.accuracy >= 60 ? '' : 'warning'}`} style={{ width: `${point.accuracy || 0}%` }} /></div></div><div style={{ textAlign: 'right' }}><div style={{ fontSize: 14, fontWeight: 740 }}>{point.attempts} попыток</div><div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{point.accuracy?.toFixed?.(0) || 0}% точность</div></div></div>)}</div>}
    </div>

    <div className="card">
      <div className="section-title">Разбивка по заданиям</div>
      <div className="table-like-list" style={{ marginTop: 16 }}>
        {(progress.tasks || []).map((task) => <div key={task.task_number} className="table-like-row">
          <div className={`badge ${task.status === 'mastered' ? 'badge-success' : task.status === 'weak' ? 'badge-danger' : task.status === 'stable' ? 'badge-accent' : 'badge-muted'}`}>№{task.task_number}</div>
          <div><div style={{ fontSize: 14, fontWeight: 720 }}>{task.title}</div><div style={{ marginTop: 8 }} className="progress-bar"><div className={`progress-fill ${task.accuracy >= 80 ? 'success' : task.accuracy >= 60 ? '' : task.total_attempts > 0 ? 'warning' : ''}`} style={{ width: `${task.accuracy || 0}%` }} /></div></div>
          <div style={{ textAlign: 'right' }}><div style={{ fontSize: 14, fontWeight: 740 }}>{task.accuracy?.toFixed?.(0) || 0}%</div><div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{task.total_attempts || 0} попыток</div></div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 6, flexWrap: 'wrap' }}><Link className="btn btn-ghost btn-sm" to={`/theory?task=${task.task_number}`}>Теория</Link><Link className="btn btn-ghost btn-sm" to={`/practice?task=${task.task_number}&mode=${task.status === 'weak' ? 'weak' : 'free'}`}>Практика</Link></div>
        </div>)}
      </div>
    </div>
  </div>;
}
