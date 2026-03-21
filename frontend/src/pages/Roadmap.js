import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../config/api';

function kindMeta(kind) {
  switch (kind) {
    case 'learn':
      return { label: 'Новый блок', badge: 'badge-accent' };
    case 'revisit':
      return { label: 'Возврат и закрепление', badge: 'badge-warning' };
    case 'review':
      return { label: 'Обязательный checkpoint', badge: 'badge-danger' };
    case 'mock':
      return { label: 'Пробники', badge: 'badge-success' };
    default:
      return { label: 'Этап', badge: 'badge-muted' };
  }
}

function scoreLabel(estimatedScore) {
  if (!estimatedScore) return '—';
  if (typeof estimatedScore.center === 'number' && estimatedScore.center > 0) {
    return `${estimatedScore.min}-${estimatedScore.max}`;
  }
  return `${estimatedScore.min || 0}-${estimatedScore.max || 0}`;
}

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      try {
        const response = await fetch(`${API}/api/roadmap`);
        const data = await response.json();
        if (!cancelled) setRoadmap(data);
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDashboard();
    return () => {
      cancelled = true;
    };
  }, []);

  const stages = roadmap?.stages || [];
  const summary = roadmap?.summary || {};
  const todayPlan = roadmap?.today_plan || { items: [] };
  const weakTaskDetails = roadmap?.weak_task_details || [];
  const mistakeTasks = roadmap?.mistake_tasks || [];
  const quickActions = roadmap?.quick_actions || [];
  const currentFocusTasks = roadmap?.current_focus_tasks || [];
  const progressData = roadmap?.progress_data || {};

  const currentStage = useMemo(
    () => stages.find((stage) => stage.stage_number === roadmap?.current_stage) || null,
    [roadmap?.current_stage, stages]
  );

  const getTaskData = (taskNumber) => progressData[String(taskNumber)] || progressData[taskNumber] || {};
  const goToHref = (href) => href && navigate(href);
  const goToTaskPractice = (taskNumber, mode = 'free') => navigate(`/practice?task=${taskNumber}&mode=${mode}`);
  const goToTaskTheory = (taskNumber) => navigate(`/theory?task=${taskNumber}`);

  const primaryAction = (() => {
    if (roadmap?.review_due) {
      return { label: 'Открыть Weekly Review', onClick: () => navigate('/weekly-review') };
    }
    if (todayPlan.items?.length) {
      return {
        label: todayPlan.items[0].action_label || 'Продолжить',
        onClick: () => goToHref(todayPlan.items[0].href),
      };
    }
    if (currentFocusTasks.length) {
      return {
        label: 'Открыть текущий этап',
        onClick: () => goToTaskPractice(currentFocusTasks[0], roadmap?.profile_learning_mode === 'free' ? 'free' : 'guided'),
      };
    }
    return { label: 'Открыть практику', onClick: () => navigate('/practice') };
  })();

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка дашборда...</div>;
  }

  return (
    <div className="fade-in" style={{ maxWidth: 1180, margin: '0 auto', display: 'grid', gap: 20 }}>
      <div className="card" data-testid="dashboard-hero">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 20, flexWrap: 'wrap', alignItems: 'flex-start' }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
              <span className="badge badge-accent">{roadmap?.profile_learning_mode === 'free' ? 'Свободный режим' : 'Guided path'}</span>
              {roadmap?.review_due ? <span className="badge badge-danger">Checkpoint обязателен</span> : null}
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>{roadmap?.dashboard_title || 'Дашборд подготовки'}</h1>
            <div style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: 14, maxWidth: 760 }}>
              {roadmap?.review_due
                ? `Сейчас продвижение по guided path остановлено: сначала нужно пройти ${roadmap.review_gate_label || 'Weekly Review'}.`
                : currentStage
                  ? `Текущий этап: ${currentStage.title}. Дашборд показывает, что делать сейчас, что делать сегодня и где именно вы на дорожке.`
                  : 'Главная точка входа в обучение: текущий этап, слабые места, ошибки и полезные действия на сегодня.'}
            </div>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 18 }}>
              <button className="btn btn-primary btn-md" onClick={primaryAction.onClick}>{primaryAction.label}</button>
              <button className="btn btn-secondary btn-md" onClick={() => navigate('/progress')}>Открыть аналитику</button>
            </div>
          </div>
          <div style={{ minWidth: 220, flexShrink: 0 }}>
            <div className="card-elevated" style={{ padding: 16 }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Что сейчас</div>
              <div style={{ marginTop: 8, fontSize: 18, fontWeight: 700 }}>{currentStage?.title || 'Начать обучение'}</div>
              <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{currentStage?.description || 'Выберите следующий осмысленный шаг.'}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--accent)' }}>{summary.coverage?.toFixed?.(0) || 0}%</div><div className="metric-label">Покрытие</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--success)' }}>{summary.accuracy?.toFixed?.(0) || 0}%</div><div className="metric-label">Средняя точность</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--warning)' }}>{scoreLabel(summary.estimated_score)}</div><div className="metric-label">Прогноз баллов</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--accent)' }}>{summary.weekly_reviews_completed || 0}</div><div className="metric-label">Пройдено Weekly Review</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--accent)' }}>{summary.mock_exams_completed || 0}</div><div className="metric-label">Завершено пробников</div></div>
      </div>

      {todayPlan.items?.length > 0 ? (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
            <div>
              <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>Что делать сегодня</div>
              <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 14 }}>{todayPlan.summary}</div>
            </div>
            <div className="badge badge-muted">План: {todayPlan.planned_minutes || 0} из {todayPlan.daily_budget_minutes || 0} мин.</div>
          </div>
          <div className="analytics-grid" style={{ marginTop: 18 }}>
            {todayPlan.items.map((item, index) => (
              <div key={`${item.type}-${index}`} className="card-elevated" style={{ padding: 16 }}>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 10 }}>
                  <span className="badge badge-accent">{item.type}</span>
                  <span className="badge badge-muted">{item.minutes} мин.</span>
                </div>
                <div style={{ fontSize: 16, fontWeight: 700 }}>{item.title}</div>
                <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.description}</div>
                <div style={{ marginTop: 14 }}><button className="btn btn-primary btn-sm" onClick={() => goToHref(item.href)}>{item.action_label || 'Открыть'}</button></div>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {quickActions.length > 0 ? (
        <div className="card">
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Быстрые действия</div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {quickActions.map((action) => (
              <button key={`${action.label}-${action.href}`} className="btn btn-secondary btn-sm" onClick={() => goToHref(action.href)}>{action.label}</button>
            ))}
          </div>
        </div>
      ) : null}

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', alignItems: 'flex-start', marginBottom: 16 }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>Real guided path</div>
            <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 14 }}>Дорожка идёт не по прямой: новый блок → возврат назад → усложнённое закрепление → обязательный review → движение дальше.</div>
          </div>
          {currentStage ? <span className="badge badge-accent">Текущий этап: {currentStage.stage_number}</span> : null}
        </div>
        <div style={{ display: 'grid', gap: 12 }}>
          {stages.map((stage) => {
            const meta = kindMeta(stage.kind);
            const stageTasks = stage.tasks || stage.review_tasks || [];
            const isCurrent = stage.is_current;
            const isCompleted = stage.is_completed;
            return (
              <div key={stage.stage_number} className="card-elevated" style={{ padding: 16, border: '1px solid', borderColor: isCurrent ? 'var(--accent)' : isCompleted ? 'rgba(92,184,122,0.30)' : 'var(--border)', opacity: !isCurrent && !isCompleted && stage.blocked_by_review ? 0.75 : 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1, minWidth: 280 }}>
                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 10 }}>
                      <span className={`badge ${meta.badge}`}>{meta.label}</span>
                      <span className="badge badge-muted">Этап {stage.stage_number}</span>
                      {isCurrent ? <span className="badge badge-accent">Текущий</span> : null}
                      {isCompleted ? <span className="badge badge-success">Пройден</span> : null}
                    </div>
                    <div style={{ fontSize: 17, fontWeight: 700 }}>{stage.title}</div>
                    <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{stage.description}</div>
                    {stage.blocked_by_review ? <div className="status-banner warning" style={{ marginTop: 12 }}>Этот и последующие этапы пока заблокированы обязательным Weekly Review.</div> : null}
                    {stageTasks.length > 0 ? (
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 14 }}>
                        {stageTasks.map((taskNumber) => {
                          const task = getTaskData(taskNumber);
                          const accuracy = task.accuracy || 0;
                          return (
                            <button key={`${stage.stage_number}-${taskNumber}`} className={`badge ${accuracy >= 80 ? 'badge-success' : accuracy >= 60 ? 'badge-accent' : task.total_attempts > 0 ? 'badge-warning' : 'badge-muted'}`} style={{ border: 'none', cursor: 'pointer' }} onClick={() => {
                              if (stage.kind === 'review') return navigate('/weekly-review');
                              if (stage.kind === 'mock') return navigate('/mock-exam');
                              goToTaskPractice(taskNumber, roadmap?.profile_learning_mode === 'free' ? 'free' : 'guided');
                            }} title={task.title || `Задание ${taskNumber}`}>
                              №{taskNumber} {task.is_code_task ? '(PY)' : ''}
                            </button>
                          );
                        })}
                      </div>
                    ) : null}
                  </div>
                  <div style={{ minWidth: 180 }}>
                    <div className="card-elevated" style={{ padding: 12 }}>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Прогресс этапа</div>
                      <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700 }}>{stage.progress_pct?.toFixed?.(0) || 0}%</div>
                      <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-secondary)' }}>Средняя точность: {stage.avg_accuracy?.toFixed?.(0) || 0}%</div>
                      {stage.estimated_minutes ? <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-secondary)' }}>~ {stage.estimated_minutes} мин.</div> : null}
                    </div>
                    <div style={{ marginTop: 10 }}>
                      {stage.kind === 'review' ? <button className="btn btn-secondary btn-sm" onClick={() => navigate('/weekly-review')}>Открыть review</button> : stage.kind === 'mock' ? <button className="btn btn-secondary btn-sm" onClick={() => navigate('/mock-exam')}>Открыть пробник</button> : stageTasks.length > 0 ? <button className="btn btn-secondary btn-sm" onClick={() => goToTaskTheory(stageTasks[0])}>Теория блока</button> : null}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {(currentFocusTasks.length > 0 || weakTaskDetails.length > 0 || mistakeTasks.length > 0) ? (
        <div className="analytics-grid">
          <div className="card">
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Фокус текущего этапа</div>
            {currentFocusTasks.length > 0 ? (
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {currentFocusTasks.map((taskNumber) => {
                  const task = getTaskData(taskNumber);
                  return <button key={`focus-${taskNumber}`} className="badge badge-accent" style={{ border: 'none', cursor: 'pointer' }} onClick={() => goToTaskPractice(taskNumber, roadmap?.profile_learning_mode === 'free' ? 'free' : 'guided')}>№{taskNumber} {task.title || ''}</button>;
                })}
              </div>
            ) : <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Сейчас нет выделенного фокуса по этапу.</div>}
          </div>
          <div className="card">
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Слабые темы</div>
            {weakTaskDetails.length > 0 ? (
              <div style={{ display: 'grid', gap: 10 }}>
                {weakTaskDetails.slice(0, 4).map((item) => {
                  const task = getTaskData(item.task_number);
                  return (
                    <div key={`weak-${item.task_number}`} className="card-elevated" style={{ padding: 12 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
                        <div>
                          <div style={{ fontSize: 14, fontWeight: 700 }}>№{item.task_number} {task.title || ''}</div>
                          <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{item.reason}</div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="badge badge-warning">{item.accuracy?.toFixed?.(0) || 0}%</div>
                          <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-muted)' }}>Попыток: {item.attempts || 0}</div>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 12 }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => goToTaskTheory(item.task_number)}>Теория</button>
                        <button className="btn btn-secondary btn-sm" onClick={() => goToTaskPractice(item.task_number, 'weak')}>Слабые темы</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Явных слабых тем по текущим данным пока нет.</div>}
          </div>
          <div className="card">
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Работа над ошибками</div>
            {mistakeTasks.length > 0 ? (
              <div style={{ display: 'grid', gap: 10 }}>
                {mistakeTasks.slice(0, 5).map((taskNumber) => {
                  const task = getTaskData(taskNumber);
                  return (
                    <div key={`mistake-${taskNumber}`} className="card-elevated" style={{ padding: 12 }}>
                      <div style={{ fontSize: 14, fontWeight: 700 }}>№{taskNumber} {task.title || ''}</div>
                      <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>Недавние ошибки по этому заданию. Его стоит разобрать до следующего продвижения вперёд.</div>
                      <div style={{ marginTop: 12 }}><button className="btn btn-secondary btn-sm" onClick={() => goToTaskPractice(taskNumber, 'mistakes')}>Открыть ошибки</button></div>
                    </div>
                  );
                })}
              </div>
            ) : <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>Недавних ошибок, требующих отдельного режима, сейчас нет.</div>}
          </div>
        </div>
      ) : null}
    </div>
  );
}
