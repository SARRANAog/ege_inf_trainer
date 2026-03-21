import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_BACKEND_URL;

export default function RoadmapPage({ profile }) {
  const [roadmap, setRoadmap] = useState(null);
  const [progress, setProgress] = useState(null);
  const [theory, setTheory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/roadmap`).then(r => r.json()),
      fetch(`${API}/api/progress`).then(r => r.json()),
      fetch(`${API}/api/theory`).then(r => r.json()),
    ])
      .then(([rm, pr, th]) => {
        setRoadmap(rm);
        setProgress(pr);
        setTheory(th);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка дорожки...</div>;

  const name = profile?.name || 'Ученик';
  const coveragePct = progress?.coverage || 0;
  const avgAcc = progress?.avg_accuracy || 0;
  const est = progress?.estimated_score || {};
  const weakTasks = roadmap?.weak_tasks || [];
  const currentStage = roadmap?.current_stage || 1;
  const stages = roadmap?.stages || [];
  const reviewDue = roadmap?.weekly_review_due;
  const totalAttempts = progress?.total_attempts || 0;

  const theoryMap = {};
  theory.forEach(item => {
    theoryMap[item.task_number] = item;
  });

  const toTheory = (taskNumber) => navigate(`/theory?task=${taskNumber}`);
  const toPractice = (taskNumber, mode = 'training') => navigate(`/practice?task=${taskNumber}&mode=${mode}`);

  const getRecommendation = () => {
    if (reviewDue) return { text: 'Пройдите Weekly Review для продвижения по дорожке', action: () => navigate('/weekly-review'), btn: 'Пройти Review' };
    if (totalAttempts === 0) return { text: 'Начните с теории по первому заданию', action: () => toTheory(1), btn: 'Начать обучение' };
    if (weakTasks.length > 0) return { text: `Рекомендуем повторить задание №${weakTasks[0]}`, action: () => toPractice(weakTasks[0], 'weak'), btn: 'Решать слабые темы' };
    if (coveragePct < 50) return { text: 'Продолжайте изучение новых тем', action: () => toTheory(currentStage), btn: 'Продолжить' };
    if (coveragePct >= 70) return { text: 'Отличный прогресс! Попробуйте пробный экзамен', action: () => navigate('/mock-exam'), btn: 'Начать пробник' };
    return { text: 'Продолжайте решать задания для повышения точности', action: () => toPractice(currentStage), btn: 'К практике' };
  };

  const rec = getRecommendation();
  const examDate = profile?.exam_date;
  const daysLeft = examDate ? Math.max(0, Math.floor((new Date(examDate) - new Date()) / 86400000)) : null;

  return (
    <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto' }}>
      <div className="card" style={{ marginBottom: 20, padding: 0, overflow: 'hidden' }} data-testid="roadmap-hero">
        <div style={{ background: 'linear-gradient(135deg, rgba(108,127,216,0.1) 0%, rgba(74,90,158,0.05) 100%)', padding: 28 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 20 }}>
            <div style={{ flex: 1, minWidth: 280 }}>
              <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 6 }}>Привет, {name}!</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.6, marginBottom: 16, maxWidth: 480 }}>
                {totalAttempts === 0
                  ? 'Добро пожаловать! Следуйте дорожке обучения — она проведёт вас через все 27 заданий ЕГЭ.'
                  : rec.text}
              </p>

              <div style={{ display: 'flex', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>{coveragePct.toFixed(0)}%</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>покрытие</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--success)' }}>{avgAcc.toFixed(0)}%</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>точность</div>
                </div>
                {est.min > 0 && (
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--accent)' }}>{est.min}–{est.max}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>балл</div>
                  </div>
                )}
                {daysLeft !== null && (
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 22, fontWeight: 700, color: daysLeft < 30 ? 'var(--danger)' : daysLeft < 90 ? 'var(--warning)' : 'var(--text-primary)' }}>{daysLeft}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>дней</div>
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                <button className="btn btn-primary btn-md" onClick={rec.action} data-testid="hero-action-btn">{rec.btn}</button>
                {!reviewDue && <button className="btn btn-secondary btn-md" onClick={() => navigate('/mock-exam')} data-testid="hero-mock-btn">Пробник</button>}
              </div>
            </div>

            <div style={{ width: 140, textAlign: 'center' }}>
              <div style={{ position: 'relative', width: 120, height: 120, margin: '0 auto' }}>
                <svg viewBox="0 0 36 36" style={{ width: 120, height: 120, transform: 'rotate(-90deg)' }}>
                  <path d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--bg-app)" strokeWidth="2.5" />
                  <path d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--accent)" strokeWidth="2.5" strokeDasharray={`${coveragePct}, 100`} strokeLinecap="round" />
                </svg>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                  <span style={{ fontSize: 26, fontWeight: 700 }}>{coveragePct.toFixed(0)}%</span>
                  <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>прогресс</span>
                </div>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>Этап {currentStage} из {stages.length}</div>
            </div>
          </div>
        </div>
      </div>

      {reviewDue && (
        <div className="card" style={{ marginBottom: 16, borderColor: 'var(--warning)', padding: '14px 20px', display: 'flex', alignItems: 'center', gap: 12 }} data-testid="review-warning">
          <div style={{ width: 32, height: 32, borderRadius: 10, background: 'rgba(224,160,80,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--warning)', fontSize: 16, fontWeight: 700, flexShrink: 0 }}>!</div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, fontSize: 14 }}>Weekly Review ожидает выполнения</div>
            <div style={{ color: 'var(--text-secondary)', fontSize: 12 }}>Продвижение приостановлено. Теория и обычная практика доступны.</div>
          </div>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/weekly-review')}>Начать Review</button>
        </div>
      )}

      <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 14 }}>Этапы обучения</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 24 }}>
        {stages.map(stage => {
          const isCurrent = stage.stage_number === currentStage;
          const isCompleted = stage.stage_number < currentStage;
          const isMock = stage.is_mock_stage;
          const progressData = roadmap?.progress_data || {};
          const tasksDone = (stage.tasks || []).filter(task => (progressData[task]?.accuracy || 0) >= 60).length;
          const totalTasks = (stage.tasks || []).length;
          const pct = totalTasks > 0 ? (tasksDone / totalTasks) * 100 : 0;

          return (
            <div
              key={stage.stage_number}
              className="card"
              style={{
                padding: '16px 20px',
                borderColor: isCurrent ? 'var(--accent)' : isCompleted ? 'rgba(92,184,122,0.3)' : 'var(--border)',
                opacity: !isCurrent && !isCompleted ? 0.65 : 1,
                transition: 'all 0.2s',
              }}
              data-testid={`stage-${stage.stage_number}`}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, fontWeight: 700, flexShrink: 0,
                  background: isCompleted ? 'var(--success)' : isCurrent ? 'var(--accent)' : 'var(--bg-elevated)',
                  color: isCompleted || isCurrent ? 'white' : 'var(--text-muted)',
                }}>
                  {isCompleted ? <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><path d="M5 13l4 4L19 7" /></svg> : isMock ? 'E' : stage.stage_number}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontWeight: 600, fontSize: 14 }}>{stage.title}</span>
                    {isCurrent && <span className="badge badge-accent" style={{ fontSize: 11 }}>Текущий</span>}
                    {isCompleted && <span className="badge badge-success" style={{ fontSize: 11 }}>Пройден</span>}
                  </div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: 12, marginTop: 2 }}>{stage.description}</div>
                </div>
                {!isMock && totalTasks > 0 && (
                  <div style={{ textAlign: 'right', flexShrink: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600 }}>{tasksDone}/{totalTasks}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>~{stage.estimated_hours}ч</div>
                  </div>
                )}
              </div>

              {stage.tasks && stage.tasks.length > 0 && (
                <div style={{ marginTop: 12, display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {stage.tasks.map(taskNumber => {
                    const taskProgress = progressData[taskNumber];
                    const accuracy = taskProgress?.accuracy || 0;
                    const theoryItem = theoryMap[taskNumber];
                    return (
                      <button
                        key={taskNumber}
                        onClick={() => toPractice(taskNumber)}
                        className={`badge ${accuracy >= 60 ? 'badge-success' : accuracy > 0 ? 'badge-warning' : 'badge-muted'}`}
                        style={{ cursor: 'pointer', border: 'none', fontSize: 12, padding: '3px 10px' }}
                        title={theoryItem ? `${theoryItem.title} — ${accuracy > 0 ? `${accuracy.toFixed(0)}%` : 'не начато'}` : `Задание ${taskNumber}`}
                      >
                        №{taskNumber} {theoryItem?.is_code_task ? '(PY)' : ''}
                      </button>
                    );
                  })}
                </div>
              )}

              {totalTasks > 0 && (
                <div style={{ marginTop: 10 }}>
                  <div className="progress-bar" style={{ height: 4 }}>
                    <div className="progress-fill success" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              )}

              {stage.checkpoint && (
                <div style={{ marginTop: 10, padding: '8px 12px', background: 'rgba(224,160,80,0.06)', borderRadius: 8, border: '1px solid rgba(224,160,80,0.15)', fontSize: 12, color: 'var(--warning)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                  {stage.checkpoint_name}
                </div>
              )}

              {isMock && (
                <div style={{ marginTop: 12 }}>
                  <button className="btn btn-primary btn-sm" onClick={() => navigate('/mock-exam')} data-testid="stage-mock-btn">Начать пробный экзамен</button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {weakTasks.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 12 }}>Слабые места</h2>
          <div className="card" style={{ padding: 16 }}>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              {weakTasks.map(taskNumber => {
                const theoryItem = theoryMap[taskNumber];
                return (
                  <div key={taskNumber} className="card-elevated" style={{ padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span className="badge badge-danger" style={{ fontSize: 12 }}>№{taskNumber}</span>
                    <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{theoryItem?.title || ''}</span>
                    <div style={{ display: 'flex', gap: 4, marginLeft: 4 }}>
                      <button className="btn btn-ghost btn-sm" style={{ fontSize: 11, height: 26, padding: '0 8px' }} onClick={() => toTheory(taskNumber)}>Теория</button>
                      <button className="btn btn-ghost btn-sm" style={{ fontSize: 11, height: 26, padding: '0 8px' }} onClick={() => toPractice(taskNumber, 'weak')}>Практика</button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      <div style={{ display: 'flex', gap: 10, justifyContent: 'center', paddingBottom: 20 }}>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/theory')}>Вся теория</button>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/practice')}>Вся практика</button>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate('/progress')}>Аналитика</button>
      </div>
    </div>
  );
}
