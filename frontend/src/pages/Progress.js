import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

function MetricCard({ label, value, sublabel, tone = 'var(--accent)' }) {
  return (
    <div className="metric-card">
      <div className="metric-value" style={{ color: tone }}>{value}</div>
      <div className="metric-label">{label}</div>
      {sublabel ? <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{sublabel}</div> : null}
    </div>
  );
}

export default function ProgressPage() {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const response = await fetch(`${API}/api/progress`);
        setProgress(await response.json());
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const weakTasks = useMemo(() => {
    return (progress?.tasks || []).filter((task) => task.status === 'weak' || task.mistake_burden >= 2).slice(0, 8);
  }, [progress]);

  const strongTasks = useMemo(() => {
    return (progress?.tasks || []).filter((task) => task.status === 'mastered').slice(0, 8);
  }, [progress]);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка аналитики…</div>;
  }

  if (!progress) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Не удалось загрузить аналитику.</div>;
  }

  const estimated = progress.estimated_score || {};

  return (
    <div className="fade-in" style={{ maxWidth: 1200, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="analytics-grid">
        <MetricCard label="Покрытие" value={`${progress.coverage?.toFixed?.(0) || 0}%`} tone="var(--accent)" sublabel="Сколько заданий уже хотя бы начаты." />
        <MetricCard label="Средняя точность" value={`${progress.avg_accuracy?.toFixed?.(0) || 0}%`} tone="var(--success)" sublabel="Средняя результативность по уже начатым заданиям." />
        <MetricCard label="Всего попыток" value={progress.total_attempts || 0} tone="var(--warning)" sublabel="Все проверки в практике, review и пробниках." />
        <MetricCard label="Правильных решений" value={progress.total_correct || 0} tone="var(--accent)" sublabel="Суммарное количество верных ответов." />
      </div>

      <div className="card" data-testid="score-forecast-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>Прогноз баллов</div>
            <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 14 }}>
              Это не декоративная цифра: прогноз строится по покрытию тем, средней точности и завершённым пробникам.
            </div>
          </div>
          <div className="badge badge-accent">{estimated.level || '—'}</div>
        </div>

        <div className="analytics-grid" style={{ marginTop: 18 }}>
          <MetricCard label="Диапазон" value={estimated.min !== undefined ? `${estimated.min}–${estimated.max}` : '—'} tone="var(--accent)" />
          <MetricCard label="Пробники завершены" value={progress.mock_exams_completed || 0} tone="var(--warning)" />
          <MetricCard label="Weekly review пройдено" value={progress.weekly_reviews_completed || 0} tone="var(--accent)" />
          <MetricCard label="Слабых тем" value={weakTasks.length} tone="var(--danger)" />
        </div>

        {estimated.description && (
          <div className="status-banner warning" style={{ marginTop: 18 }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>Как читать прогноз</div>
            <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {estimated.description}
            </div>
          </div>
        )}
      </div>

      <div className="analytics-grid">
        <div className="card">
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Сильные стороны</div>
          {strongTasks.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 13 }}>
              Пока нет заданий, дошедших до статуса mastered.
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {strongTasks.map((task) => (
                <Link key={task.task_number} to={`/practice?task=${task.task_number}&mode=free`} className="badge badge-success">
                  №{task.task_number} · {task.accuracy?.toFixed?.(0) || 0}%
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="card">
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Что тянет результат вниз</div>
          {weakTasks.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 13 }}>
              Явных слабых мест сейчас нет.
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {weakTasks.map((task) => (
                <Link key={task.task_number} to={`/practice?task=${task.task_number}&mode=weak`} className="badge badge-danger">
                  №{task.task_number} · {task.accuracy?.toFixed?.(0) || 0}%
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', marginBottom: 16 }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>История за последние дни</div>
            <div style={{ marginTop: 6, color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 13 }}>
              Здесь видно не только общий итог, но и ритм работы: как часто вы занимались и с какой точностью.
            </div>
          </div>
        </div>

        {(progress.history || []).length === 0 ? (
          <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 13 }}>История появится после первых попыток.</div>
        ) : (
          <div className="history-list">
            {progress.history.map((point) => (
              <div key={point.date} className="history-row">
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{point.date}</div>
                <div>
                  <div className="progress-bar">
                    <div
                      className={`progress-fill ${point.accuracy >= 80 ? 'success' : point.accuracy >= 60 ? '' : 'warning'}`}
                      style={{ width: `${point.accuracy || 0}%` }}
                    />
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 14, fontWeight: 700 }}>{point.attempts} попыток</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{point.accuracy?.toFixed?.(0) || 0}% точность</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card" data-testid="task-breakdown-card">
        <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 12 }}>Разбивка по заданиям</div>
        <div className="table-like-list">
          {(progress.tasks || []).map((task) => (
            <div key={task.task_number} className="table-like-row">
              <div className={`badge ${task.status === 'mastered' ? 'badge-success' : task.status === 'weak' ? 'badge-danger' : task.status === 'stable' ? 'badge-accent' : 'badge-muted'}`}>
                №{task.task_number}
              </div>

              <div>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{task.title}</div>
                <div style={{ marginTop: 4 }} className="progress-bar">
                  <div
                    className={`progress-fill ${task.accuracy >= 80 ? 'success' : task.accuracy >= 60 ? '' : task.total_attempts > 0 ? 'warning' : ''}`}
                    style={{ width: `${task.accuracy || 0}%` }}
                  />
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: 14, fontWeight: 700 }}>{task.accuracy?.toFixed?.(0) || 0}%</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{task.total_attempts || 0} попыток</div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 6, flexWrap: 'wrap' }}>
                <Link className="btn btn-ghost btn-sm" to={`/theory?task=${task.task_number}`}>Теория</Link>
                <Link className="btn btn-ghost btn-sm" to={`/practice?task=${task.task_number}&mode=${task.status === 'weak' ? 'weak' : 'free'}`}>
                  Практика
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
