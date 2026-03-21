import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../config/api';

function kindMeta(kind) {
  switch (kind) {
    case 'learn': return { label: 'Новый блок', badge: 'badge-accent' };
    case 'revisit': return { label: 'Возврат и закрепление', badge: 'badge-warning' };
    case 'review': return { label: 'Обязательный checkpoint', badge: 'badge-danger' };
    case 'mock': return { label: 'Пробники', badge: 'badge-success' };
    default: return { label: 'Этап', badge: 'badge-muted' };
  }
}

function scoreLabel(estimatedScore) {
  if (!estimatedScore) return '—';
  return `${estimatedScore.min || 0}-${estimatedScore.max || 0}`;
}

function accuracyTone(value) {
  if (value >= 80) return 'badge-success';
  if (value >= 60) return 'badge-accent';
  if (value > 0) return 'badge-warning';
  return 'badge-muted';
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
    return () => { cancelled = true; };
  }, []);

  const stages = roadmap?.stages || [];
  const summary = roadmap?.summary || {};
  const todayPlan = roadmap?.today_plan || { items: [] };
  const weakTaskDetails = roadmap?.weak_task_details || [];
  const mistakeTasks = roadmap?.mistake_tasks || [];
  const quickActions = roadmap?.quick_actions || [];
  const currentFocusTasks = roadmap?.current_focus_tasks || [];
  const progressData = roadmap?.progress_data || {};

  const currentStage = useMemo(() => stages.find((stage) => stage.stage_number === roadmap?.current_stage) || null, [roadmap?.current_stage, stages]);
  const isFirstStart = (summary.coverage || 0) === 0 && (summary.mock_exams_completed || 0) === 0 && (summary.weekly_reviews_completed || 0) === 0;
  const getTaskData = (taskNumber) => progressData[String(taskNumber)] || progressData[taskNumber] || {};
  const goToHref = (href) => href && navigate(href);
  const goToTaskPractice = (taskNumber, mode = 'free') => navigate(`/practice?task=${taskNumber}&mode=${mode}`);
  const goToTaskTheory = (taskNumber) => navigate(`/theory?task=${taskNumber}`);

  const primaryAction = (() => {
    if (roadmap?.review_due) return { label: 'Открыть Weekly Review', onClick: () => navigate('/weekly-review') };
    if (todayPlan.items?.length) return { label: todayPlan.items[0].action_label || 'Продолжить', onClick: () => goToHref(todayPlan.items[0].href) };
    if (currentFocusTasks.length) return { label: 'Открыть текущий этап', onClick: () => goToTaskPractice(currentFocusTasks[0], roadmap?.profile_learning_mode === 'free' ? 'free' : 'guided') };
    return { label: 'Открыть практику', onClick: () => navigate('/practice') };
  })();

  if (loading) {
    return <div className="page-shell fade-in"><div className="state-card loading-shimmer"><div className="state-title">Загрузка дашборда</div><div className="state-description">Подтягиваем дорожку обучения, текущий этап, weak-state и план на сегодня.</div></div></div>;
  }

  return (
    <div className="page-shell page-shell-wide fade-in">
      <section className="hero-card dashboard-hero">
        <div className="dashboard-grid">
          <div className="page-stack">
            <div>
              <div className="eyebrow">Главный экран подготовки</div>
              <div className="hero-title">{roadmap?.dashboard_title || 'Дашборд подготовки'}</div>
              <div className="hero-description">
                {roadmap?.review_due
                  ? `Сейчас движение по guided path остановлено: сначала нужно пройти ${roadmap.review_gate_label || 'Weekly Review'}.`
                  : currentStage
                    ? `Текущий этап: ${currentStage.title}. Здесь видно, что делать прямо сейчас, где вы на дорожке и что сильнее всего влияет на результат.`
                    : 'Это главная продуктовая точка входа в обучение: этап, фокус, ошибки, слабые темы и понятный следующий шаг.'}
              </div>
            </div>
            <div className="hero-actions">
              <button className="btn btn-primary btn-md" onClick={primaryAction.onClick}>{primaryAction.label}</button>
              <button className="btn btn-secondary btn-md" onClick={() => navigate('/progress')}>Открыть аналитику</button>
              <button className="btn btn-ghost btn-md" onClick={() => navigate('/practice?mode=free')}>Свободная практика</button>
            </div>
            <div className="hero-metrics">
              <div className="metric-card"><div className="metric-value" style={{ color: 'var(--accent-strong)' }}>{summary.coverage?.toFixed?.(0) || 0}%</div><div className="metric-label">Покрытие</div></div>
              <div className="metric-card"><div className="metric-value" style={{ color: 'var(--success)' }}>{summary.accuracy?.toFixed?.(0) || 0}%</div><div className="metric-label">Средняя точность</div></div>
              <div className="metric-card"><div className="metric-value" style={{ color: 'var(--warning)' }}>{scoreLabel(summary.estimated_score)}</div><div className="metric-label">Прогноз баллов</div></div>
              <div className="metric-card"><div className="metric-value" style={{ color: 'var(--accent)' }}>{summary.weekly_reviews_completed || 0}</div><div className="metric-label">Weekly Review пройдено</div></div>
            </div>
          </div>
          <div className="page-stack">
            <div className="card-elevated surface-accent">
              <div className="info-label">Что сейчас в фокусе</div>
              <div className="info-value">{currentStage?.title || 'Начать обучение'}</div>
              <div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>{currentStage?.description || 'Выберите следующий осмысленный шаг и начните с теории или практики.'}</div>
              <div className="task-chip-row" style={{ marginTop: 14 }}>
                <span className="badge badge-accent">{roadmap?.profile_learning_mode === 'free' ? 'Свободный режим' : 'Guided path'}</span>
                {roadmap?.review_due ? <span className="badge badge-danger">Checkpoint обязателен</span> : null}
                {currentStage ? <span className="badge badge-muted">Этап {currentStage.stage_number}</span> : null}
              </div>
            </div>
            {isFirstStart ? (
              <div className="card-elevated">
                <div className="info-label">Onboarding</div>
                <div className="info-value">Спокойный старт без визуального шума</div>
                <div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}>Сначала откройте теорию по первому блоку, затем переходите в guided practice.</div>
                <div className="row-actions" style={{ marginTop: 14 }}>
                  <button className="btn btn-primary btn-sm" onClick={() => navigate('/theory?task=1')}>Открыть первую теорию</button>
                  <button className="btn btn-secondary btn-sm" onClick={() => navigate('/practice?task=1&mode=guided')}>Перейти в guided practice</button>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </section>

      {todayPlan.items?.length > 0 ? (
        <section className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
            <div><div className="section-title">Что делать сегодня</div><div className="section-description">{todayPlan.summary}</div></div>
            <div className="badge badge-muted">План: {todayPlan.planned_minutes || 0} / {todayPlan.daily_budget_minutes || 0} мин.</div>
          </div>
          <div className="hero-metrics" style={{ marginTop: 18 }}>
            {todayPlan.items.map((item, index) => (
              <div key={`${item.type}-${index}`} className="today-plan-item">
                <div className="task-chip-row" style={{ marginBottom: 10 }}>
                  <span className="badge badge-accent">{item.type}</span>
                  <span className="badge badge-muted">{item.minutes} мин.</span>
                </div>
                <div className="today-plan-title">{item.title}</div>
                <div className="today-plan-description">{item.description}</div>
                <div className="row-actions" style={{ marginTop: 14 }}><button className="btn btn-primary btn-sm" onClick={() => goToHref(item.href)}>{item.action_label || 'Открыть'}</button></div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {quickActions.length > 0 ? (
        <section className="card">
          <div className="section-title">Быстрые действия</div>
          <div className="row-actions" style={{ marginTop: 16 }}>
            {quickActions.map((action) => (<button key={`${action.label}-${action.href}`} className="btn btn-secondary btn-sm" onClick={() => goToHref(action.href)}>{action.label}</button>))}
          </div>
        </section>
      ) : null}

      <section className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
          <div><div className="section-title">Guided roadmap</div><div className="section-description">Реальная дорожка без детской геймификации: новый материал, возврат, закрепление, контрольные точки и выход в пробники.</div></div>
          {currentStage ? <span className="badge badge-accent">Текущий этап: {currentStage.stage_number}</span> : null}
        </div>

        <div className="stage-list" style={{ marginTop: 18 }}>
          {stages.map((stage) => {
            const meta = kindMeta(stage.kind);
            const stageTasks = stage.tasks || stage.review_tasks || [];
            const stageClass = ['roadmap-stage-card', stage.is_current ? 'is-current' : '', stage.is_completed ? 'is-completed' : '', !stage.is_current && !stage.is_completed && stage.blocked_by_review ? 'is-blocked' : ''].filter(Boolean).join(' ');
            return (
              <div key={stage.stage_number} className={stageClass}>
                <div className="stage-header">
                  <div style={{ flex: 1, minWidth: 280 }}>
                    <div className="task-chip-row" style={{ marginBottom: 10 }}>
                      <span className={`badge ${meta.badge}`}>{meta.label}</span>
                      <span className="badge badge-muted">Этап {stage.stage_number}</span>
                      {stage.is_current ? <span className="badge badge-accent">Текущий</span> : null}
                      {stage.is_completed ? <span className="badge badge-success">Пройден</span> : null}
                    </div>
                    <div className="stage-title">{stage.title}</div>
                    <div className="stage-description">{stage.description}</div>
                    {stage.blocked_by_review ? <div className="status-banner warning" style={{ marginTop: 14 }}>Этот и последующие этапы пока заблокированы обязательным Weekly Review.</div> : null}
                    {stageTasks.length > 0 ? (
                      <div className="stage-task-row" style={{ marginTop: 14 }}>
                        {stageTasks.map((taskNumber) => {
                          const task = getTaskData(taskNumber);
                          const accuracy = task.accuracy || 0;
                          return (
                            <button key={`${stage.stage_number}-${taskNumber}`} className={`badge ${accuracyTone(accuracy)}`} style={{ border: 'none', cursor: 'pointer' }} onClick={() => {
                              if (stage.kind === 'review') return navigate('/weekly-review');
                              if (stage.kind === 'mock') return navigate('/mock-exam');
                              goToTaskPractice(taskNumber, roadmap?.profile_learning_mode === 'free' ? 'free' : 'guided');
                            }}>
                              №{taskNumber} {task.is_code_task ? '· PY' : ''}
                            </button>
                          );
                        })}
                      </div>
                    ) : null}
                  </div>
                  <div style={{ width: 220, maxWidth: '100%' }}>
                    <div className="card-elevated">
                      <div className="info-label">Прогресс этапа</div>
                      <div className="info-value">{stage.progress_pct?.toFixed?.(0) || 0}%</div>
                      <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Средняя точность: {stage.avg_accuracy?.toFixed?.(0) || 0}%</div>
                    </div>
                    <div className="row-actions" style={{ marginTop: 12 }}>
                      {stage.kind === 'review' ? <button className="btn btn-secondary btn-sm" onClick={() => navigate('/weekly-review')}>Открыть review</button> : stage.kind === 'mock' ? <button className="btn btn-secondary btn-sm" onClick={() => navigate('/mock-exam')}>Открыть пробник</button> : stageTasks.length > 0 ? <button className="btn btn-secondary btn-sm" onClick={() => goToTaskTheory(stageTasks[0])}>Теория блока</button> : null}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="page-grid-3">
        <div className="card">
          <div className="section-title">Фокус текущего этапа</div>
          {currentFocusTasks.length > 0 ? <div className="task-chip-row" style={{ marginTop: 16 }}>{currentFocusTasks.map((taskNumber) => {
            const task = getTaskData(taskNumber);
            return <button key={`focus-${taskNumber}`} className="badge badge-accent" style={{ border: 'none', cursor: 'pointer' }} onClick={() => goToTaskPractice(taskNumber, roadmap?.profile_learning_mode === 'free' ? 'free' : 'guided')}>№{taskNumber} {task.title || ''}</button>;
          })}</div> : <div style={{ marginTop: 16, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>Сейчас нет выделенного фокуса по этапу.</div>}
        </div>

        <div className="card">
          <div className="section-title">Слабые темы</div>
          {weakTaskDetails.length > 0 ? <div className="page-stack" style={{ marginTop: 16 }}>{weakTaskDetails.slice(0, 4).map((item) => {
            const task = getTaskData(item.task_number);
            return <div key={`weak-${item.task_number}`} className="card-elevated">
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
                <div><div style={{ fontSize: 14, fontWeight: 740 }}>№{item.task_number} {task.title || ''}</div><div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>{item.reason}</div></div>
                <div className="badge badge-warning">{item.accuracy?.toFixed?.(0) || 0}%</div>
              </div>
              <div className="row-actions" style={{ marginTop: 14 }}>
                <button className="btn btn-ghost btn-sm" onClick={() => goToTaskTheory(item.task_number)}>Теория</button>
                <button className="btn btn-secondary btn-sm" onClick={() => goToTaskPractice(item.task_number, 'weak')}>Слабые темы</button>
              </div>
            </div>;
          })}</div> : <div style={{ marginTop: 16, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>Явных слабых тем по текущим данным пока нет.</div>}
        </div>

        <div className="card">
          <div className="section-title">Работа над ошибками</div>
          {mistakeTasks.length > 0 ? <div className="page-stack" style={{ marginTop: 16 }}>{mistakeTasks.slice(0, 5).map((taskNumber) => {
            const task = getTaskData(taskNumber);
            return <div key={`mistake-${taskNumber}`} className="card-elevated">
              <div style={{ fontSize: 14, fontWeight: 740 }}>№{taskNumber} {task.title || ''}</div>
              <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>Недавние ошибки по этому заданию. Его стоит разобрать до следующего продвижения вперёд.</div>
              <div className="row-actions" style={{ marginTop: 14 }}>
                <button className="btn btn-secondary btn-sm" onClick={() => goToTaskPractice(taskNumber, 'mistakes')}>Открыть ошибки</button>
              </div>
            </div>;
          })}</div> : <div style={{ marginTop: 16, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>Недавних ошибок, требующих отдельного режима, сейчас нет.</div>}
        </div>
      </section>
    </div>
  );
}
