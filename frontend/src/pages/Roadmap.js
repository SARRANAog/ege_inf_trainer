import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

function StageCard({ stage }) {
  const cardClass = [
    'stage-card',
    stage.is_current ? 'current' : '',
    stage.is_completed ? 'completed' : '',
    stage.blocked_by_review ? 'blocked' : '',
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClass} data-testid={`guided-stage-${stage.stage_number}`}>
      <div className="stage-header">
        <div className="stage-index">
          {stage.is_completed ? '✓' : stage.stage_number}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
            <div className="stage-title">{stage.title}</div>
            {stage.is_current && <span className="badge badge-accent">Текущий этап</span>}
            {stage.is_completed && <span className="badge badge-success">Пройден</span>}
            {stage.kind === 'review' && <span className="badge badge-warning">Checkpoint</span>}
            {stage.kind === 'revisit' && <span className="badge badge-muted">Возврат назад</span>}
          </div>
          <div className="stage-description">{stage.description}</div>
        </div>
        <div style={{ minWidth: 88, textAlign: 'right' }}>
          <div style={{ fontSize: 13, fontWeight: 600 }}>{stage.progress_pct?.toFixed?.(0) || 0}%</div>
          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{stage.estimated_minutes} мин.</div>
        </div>
      </div>

      {(stage.tasks || []).length > 0 && (
        <div className="stage-task-row">
          {stage.tasks.map((taskNumber) => (
            <span key={taskNumber} className="badge badge-muted">
              №{taskNumber}
            </span>
          ))}
        </div>
      )}

      <div style={{ marginTop: 12 }}>
        <div className="progress-bar">
          <div className={`progress-fill ${stage.is_completed ? 'success' : stage.kind === 'review' ? 'warning' : ''}`} style={{ width: `${stage.progress_pct || 0}%` }} />
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, tone = 'var(--accent)', sublabel }) {
  return (
    <div className="metric-card">
      <div className="metric-value" style={{ color: tone }}>{value}</div>
      <div className="metric-label">{label}</div>
      {sublabel ? <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{sublabel}</div> : null}
    </div>
  );
}

export default function DashboardPage({ profile, reloadProfile }) {
  const [roadmap, setRoadmap] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [savingMode, setSavingMode] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [roadmapRes, progressRes] = await Promise.all([
        fetch(`${API}/api/roadmap`),
        fetch(`${API}/api/progress`),
      ]);
      const [roadmapData, progressData] = await Promise.all([roadmapRes.json(), progressRes.json()]);
      setRoadmap(roadmapData);
      setProgress(progressData);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleModeChange = async (learningMode) => {
    setSavingMode(true);
    try {
      await fetch(`${API}/api/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ learning_mode: learningMode }),
      });
      await Promise.all([loadData(), reloadProfile?.()]);
    } catch (error) {
      console.error(error);
    } finally {
      setSavingMode(false);
    }
  };

  const focusTasksLabel = useMemo(() => {
    if (!roadmap?.current_focus_tasks?.length) return 'Нет фокуса';
    return roadmap.current_focus_tasks.map((taskNumber) => `№${taskNumber}`).join(', ');
  }, [roadmap]);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка дашборда…</div>;
  }

  if (!roadmap || !progress) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Не удалось загрузить дашборд.</div>;
  }

  const estimated = progress.estimated_score || {};
  const weakDetails = roadmap.weak_task_details || [];
  const todayPlan = roadmap.today_plan || { items: [] };
  const mode = roadmap.profile_learning_mode || profile?.learning_mode || 'guided';

  return (
    <div className="fade-in" style={{ maxWidth: 1320, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="dashboard-grid">
        <div className="dashboard-stack">
          <div className="card dashboard-hero" data-testid="dashboard-hero">
            <div style={{ display: 'flex', gap: 16, justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: 280 }}>
                <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 10 }}>
                  {profile?.name || 'Ученик'}, это ваш рабочий дашборд
                </h1>
                <p style={{ maxWidth: 760 }}>
                  Здесь видны текущий этап guided path, обязательные checkpoint-блоки, слабые темы, ошибки и конкретный план на сегодня.
                  Главный экран больше не декоративный — он управляет тем, что делать дальше.
                </p>

                <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 18 }}>
                  <Link className="btn btn-primary btn-md" to={roadmap.review_due ? '/weekly-review' : '/practice?mode=guided'}>
                    {roadmap.review_due ? 'Открыть Weekly Review' : 'Продолжить guided path'}
                  </Link>
                  <Link className="btn btn-secondary btn-md" to="/practice?mode=free">
                    Свободная практика
                  </Link>
                  <Link className="btn btn-ghost btn-md" to="/mock-exam">
                    Пробник
                  </Link>
                </div>
              </div>

              <div style={{ minWidth: 280 }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8 }}>Режим обучения</div>
                <div className="segment-control" style={{ width: '100%' }}>
                  <button
                    className={`segment-btn ${mode === 'guided' ? 'active' : ''}`}
                    onClick={() => handleModeChange('guided')}
                    disabled={savingMode}
                    style={{ flex: 1 }}
                  >
                    Guided path
                  </button>
                  <button
                    className={`segment-btn ${mode === 'free' ? 'active' : ''}`}
                    onClick={() => handleModeChange('free')}
                    disabled={savingMode}
                    style={{ flex: 1 }}
                  >
                    Свободный режим
                  </button>
                </div>

                <div style={{ marginTop: 16, display: 'grid', gap: 10 }}>
                  <div className={`status-banner ${roadmap.review_due ? 'warning' : 'success'}`}>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>
                      {roadmap.review_due ? 'Переход заблокирован checkpoint-блоком' : 'Следующий этап открыт'}
                    </div>
                    <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                      {roadmap.review_due
                        ? `Сейчас нужно пройти ${roadmap.review_gate_label}. Без этого guided path дальше не откроется.`
                        : `Текущий фокус: ${focusTasksLabel}.`}
                    </div>
                  </div>

                  <div className="card-elevated" style={{ padding: 14 }}>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Текущий этап</div>
                    <div style={{ marginTop: 4, fontSize: 16, fontWeight: 600 }}>{roadmap.current_stage_title}</div>
                    <div style={{ marginTop: 8 }} className="progress-bar">
                      <div className="progress-fill" style={{ width: `${(roadmap.current_stage / roadmap.stages.length) * 100}%` }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {roadmap.review_due && (
            <div className="status-banner warning" data-testid="weekly-review-gate">
              <div style={{ fontWeight: 700, fontSize: 15 }}>Weekly Review обязателен</div>
              <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Дорожка специально не даёт перескочить дальше. Сначала контрольный блок по пройденному, затем новый материал.
              </div>
            </div>
          )}

          <div className="analytics-grid">
            <MetricCard label="Покрытие программы" value={`${progress.coverage?.toFixed?.(0) || 0}%`} tone="var(--accent)" />
            <MetricCard label="Средняя точность" value={`${progress.avg_accuracy?.toFixed?.(0) || 0}%`} tone="var(--success)" />
            <MetricCard
              label="Примерный прогноз баллов"
              value={estimated.min !== undefined ? `${estimated.min}–${estimated.max}` : '—'}
              tone="var(--warning)"
              sublabel={estimated.description}
            />
            <MetricCard label="Фокус текущего этапа" value={`${roadmap.current_focus_tasks?.length || 0} тем`} tone="var(--accent)" sublabel={focusTasksLabel} />
          </div>

          <div className="card" data-testid="today-plan-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>Что делать сейчас / сегодня</div>
                <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {todayPlan.summary}
                </div>
              </div>
              <div className="badge badge-muted">
                {todayPlan.planned_minutes || 0} из {todayPlan.daily_budget_minutes || 0} мин.
              </div>
            </div>

            <div className="today-plan-list">
              {todayPlan.items?.map((item, index) => (
                <div className="today-plan-item" key={`${item.type}-${index}`}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', flexWrap: 'wrap' }}>
                    <div>
                      <div className="today-plan-title">{item.title}</div>
                      <div className="today-plan-description">{item.description}</div>
                    </div>
                    <div className="badge badge-muted">{item.minutes} мин.</div>
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <Link className="btn btn-secondary btn-sm" to={item.href}>{item.action_label}</Link>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card" data-testid="guided-path-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 16 }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>Real guided path</div>
                <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  Осмысленная жёсткая дорожка с возвратами назад, усложнённым повторением и обязательными review-checkpoint’ами.
                </div>
              </div>
              <div className="badge badge-accent">Этап {roadmap.current_stage} из {roadmap.stages.length}</div>
            </div>

            <div className="stage-list">
              {roadmap.stages.map((stage) => (
                <StageCard key={stage.stage_number} stage={stage} />
              ))}
            </div>
          </div>
        </div>

        <div className="dashboard-stack">
          <div className="card">
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 14 }}>Быстрые действия</div>
            <div className="quick-actions-grid">
              {roadmap.quick_actions?.map((action) => (
                <Link key={action.href} className="card-elevated" to={action.href} style={{ textDecoration: 'none' }}>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>{action.label}</div>
                  <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-secondary)' }}>{action.href}</div>
                </Link>
              ))}
            </div>
          </div>

          <div className="card" data-testid="weak-topics-card">
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 14 }}>Слабые темы и ошибки</div>

            {weakDetails.length === 0 ? (
              <div className="status-banner success">
                <div style={{ fontWeight: 600, fontSize: 14 }}>Явно провальных тем сейчас нет</div>
                <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)' }}>
                  Продолжайте guided path или переходите в пробник.
                </div>
              </div>
            ) : (
              <div className="table-like-list">
                {weakDetails.map((item) => (
                  <div className="table-like-row" key={item.task_number}>
                    <div className="badge badge-danger">№{item.task_number}</div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 600 }}>Задание {item.task_number}</div>
                      <div style={{ marginTop: 4, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.reason}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--warning)' }}>{item.accuracy?.toFixed?.(0) || 0}%</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>точность</div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 6, flexWrap: 'wrap' }}>
                      <Link className="btn btn-ghost btn-sm" to={`/practice?task=${item.task_number}&mode=weak`}>Практика</Link>
                      <Link className="btn btn-ghost btn-sm" to={`/theory?task=${item.task_number}`}>Теория</Link>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {roadmap.mistake_tasks?.length > 0 && (
              <div style={{ marginTop: 16 }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Недавние ошибки</div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {roadmap.mistake_tasks.map((taskNumber) => (
                    <Link key={taskNumber} className="badge badge-warning" to={`/practice?task=${taskNumber}&mode=mistakes`}>
                      №{taskNumber}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Weekly review / mock / analytics</div>
            <div style={{ display: 'grid', gap: 10 }}>
              <div className="card-elevated" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Weekly review пройдено</div>
                <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700 }}>{progress.weekly_reviews_completed || 0}</div>
              </div>
              <div className="card-elevated" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Пробники завершены</div>
                <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700 }}>{progress.mock_exams_completed || 0}</div>
              </div>
              <div className="card-elevated" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Последняя средняя точность</div>
                <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700 }}>{progress.avg_accuracy?.toFixed?.(0) || 0}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
