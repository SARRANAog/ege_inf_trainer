import React, { useEffect, useMemo, useState } from 'react';
import API from '../config/api';

function formatMinutes(value) { return `${value || 0} мин.`; }
function ChoiceButton({ active, label, leading, onClick }) {
  return <button className={`choice-option ${active ? 'active' : ''}`} onClick={onClick}><div className="choice-option-row"><span className="choice-option-mark">{leading}</span><div className="choice-option-body">{label}</div></div></button>;
}

export default function WeeklyReviewPage() {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});

  const loadReview = async () => {
    setLoading(true);
    try { const response = await fetch(`${API}/api/weekly-review`); setReview(await response.json()); }
    catch (error) { console.error(error); }
    finally { setLoading(false); }
  };

  useEffect(() => { loadReview(); }, []);

  const startReview = async () => {
    try { const response = await fetch(`${API}/api/weekly-review/start`, { method: 'POST' }); setReview(await response.json()); setCurrentIdx(0); }
    catch (error) { console.error(error); }
  };

  const submitAnswer = async (exercise) => {
    const value = answers[exercise.exercise_id];
    if (value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) return;
    try {
      const response = await fetch(`${API}/api/weekly-review/answer`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ exercise_id: exercise.exercise_id, answer: value }) });
      const result = await response.json();
      setReview((prev) => ({
        ...prev,
        results: { ...(prev?.results || {}), [exercise.exercise_id]: result },
        answers_count: Object.keys({ ...(prev?.results || {}), [exercise.exercise_id]: result }).length,
        correct_count: Object.values({ ...(prev?.results || {}), [exercise.exercise_id]: result }).filter((item) => item.correct).length,
      }));
    } catch (error) { console.error(error); }
  };

  const completeReview = async () => {
    try { const response = await fetch(`${API}/api/weekly-review/complete`, { method: 'POST' }); setReview(await response.json()); }
    catch (error) { console.error(error); alert('Нужно ответить почти на все задания review перед завершением.'); }
  };

  const updateSingleChoice = (exerciseId, value) => setAnswers((prev) => ({ ...prev, [exerciseId]: value }));
  const updateMultiChoice = (exerciseId, value) => {
    setAnswers((prev) => {
      const current = Array.isArray(prev[exerciseId]) ? prev[exerciseId] : [];
      return { ...prev, [exerciseId]: current.includes(value) ? current.filter((item) => item !== value) : [...current, value] };
    });
  };

  const activeExercises = review?.exercises || [];
  const currentExercise = activeExercises[currentIdx];
  const currentResult = currentExercise ? review?.results?.[currentExercise.exercise_id] : null;
  const isActiveReview = review?.status === 'active';
  const completionRatio = useMemo(() => !activeExercises.length ? 0 : ((review?.answers_count || 0) / activeExercises.length) * 100, [activeExercises.length, review]);
  const requiredAnswers = Math.max(3, activeExercises.length - 1);

  if (loading) return <div className="page-shell fade-in"><div className="state-card loading-shimmer"><div className="state-title">Загрузка Weekly Review</div><div className="state-description">Подтягиваем контрольный блок по текущему этапу, слабым темам и последним ошибкам.</div></div></div>;
  if (!review) return <div className="page-shell fade-in"><div className="state-card"><div className="state-title">Не удалось загрузить Weekly Review</div><div className="state-description">Проверьте локальный backend и повторите запуск страницы.</div></div></div>;

  if (!isActiveReview) {
    return <div className="page-shell fade-in"><div className="hero-card dashboard-hero">
      <div className="eyebrow">Контрольный блок</div>
      <div className="hero-title">Weekly Review</div>
      <div className="hero-description">Это обязательный checkpoint между этапами дорожки. Он собирается из текущего блока, слабых тем и недавних ошибок.</div>
      <div className="task-chip-row" style={{ marginTop: 16 }}>
        <span className={`badge ${review.required_checkpoint ? 'badge-danger' : 'badge-warning'}`}>{review.required_checkpoint ? 'Обязательный checkpoint' : 'Повторение'}</span>
        {review.checkpoint_label ? <span className="badge badge-muted">{review.checkpoint_label}</span> : null}
      </div>
      <div className="analytics-grid" style={{ marginTop: 18 }}>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--accent)' }}>{activeExercises.length}</div><div className="metric-label">Упражнений</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--warning)' }}>{formatMinutes(review.estimated_time)}</div><div className="metric-label">Оценка времени</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--danger)' }}>{review.weak_tasks?.length || 0}</div><div className="metric-label">Слабых тем внутри</div></div>
        <div className="metric-card"><div className="metric-value" style={{ color: 'var(--success)' }}>{review.completed_reviews || 0}</div><div className="metric-label">Review уже пройдено</div></div>
      </div>
      <div className="row-actions" style={{ marginTop: 20 }}><button className="btn btn-primary btn-lg" onClick={startReview}>Начать Weekly Review</button></div>
    </div></div>;
  }

  if (!currentExercise) return <div className="page-shell fade-in"><div className="state-card"><div className="state-title">В review нет упражнений</div></div></div>;
  const answerValue = answers[currentExercise.exercise_id];
  const canSubmit = answerValue !== undefined && answerValue !== '' && (!Array.isArray(answerValue) || answerValue.length > 0);

  return <div className="page-shell page-shell-wide fade-in"><div className="mock-layout">
    <aside className="left-rail-card">
      <div className="card">
        <div className="eyebrow">Прогресс review</div>
        <div className="section-title">Weekly Review в процессе</div>
        <div style={{ marginTop: 16 }}><div className="progress-bar"><div className="progress-fill warning" style={{ width: `${completionRatio}%` }} /></div></div>
        <div className="info-grid" style={{ marginTop: 16 }}>
          <div className="info-card"><div className="info-label">Ответов</div><div className="info-value">{review.answers_count || 0}/{activeExercises.length}</div></div>
          <div className="info-card"><div className="info-label">Нужно минимум</div><div className="info-value">{requiredAnswers}</div></div>
        </div>
        <div className="row-actions" style={{ marginTop: 16 }}><button className="btn btn-ghost btn-sm" onClick={completeReview} disabled={(review.answers_count || 0) < requiredAnswers}>Завершить Review</button></div>
      </div>
      <div className="card"><div className="section-title" style={{ fontSize: 18 }}>Навигация по блоку</div><div className="review-grid" style={{ marginTop: 14 }}>
        {activeExercises.map((exercise, index) => {
          const result = review?.results?.[exercise.exercise_id];
          const classes = ['review-nav-btn', index === currentIdx ? 'active' : '', result?.correct ? 'correct' : '', result && !result.correct ? 'wrong' : ''].filter(Boolean).join(' ');
          return <button key={exercise.exercise_id} className={classes} onClick={() => setCurrentIdx(index)}>{index + 1}</button>;
        })}
      </div></div>
    </aside>

    <section className="page-stack">
      <div className="card">
        <div className="task-chip-row" style={{ marginBottom: 14 }}>
          <span className="badge badge-accent">№{currentExercise.task_number}</span>
          <span className={`badge ${currentExercise.difficulty === 'hard' ? 'badge-danger' : currentExercise.difficulty === 'medium' ? 'badge-warning' : 'badge-success'}`}>{currentExercise.difficulty || 'objective'}</span>
        </div>
        <div className="section-title">{currentExercise.title}</div>
        <div style={{ marginTop: 10, fontSize: 14, lineHeight: 1.75, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>{currentExercise.text}</div>

        {currentExercise.answer_type === 'single_choice' && currentExercise.options ? <div className="choice-list" style={{ marginTop: 20 }}>
          {currentExercise.options.map((option, index) => { const value = option.charAt(0); return <ChoiceButton key={index} active={answerValue === value} leading={value} label={option} onClick={() => updateSingleChoice(currentExercise.exercise_id, value)} />; })}
        </div> : currentExercise.answer_type === 'multiple_choice' && currentExercise.options ? <div className="choice-list" style={{ marginTop: 20 }}>
          {currentExercise.options.map((option, index) => { const value = option.charAt(0); const active = Array.isArray(answerValue) && answerValue.includes(value); return <ChoiceButton key={index} active={active} leading={active ? '✓' : '+'} label={option} onClick={() => updateMultiChoice(currentExercise.exercise_id, value)} />; })}
        </div> : <div style={{ marginTop: 20, maxWidth: 280 }}><input className="input" type="number" value={answerValue || ''} onChange={(event) => setAnswers((prev) => ({ ...prev, [currentExercise.exercise_id]: event.target.value }))} placeholder="Введите числовой ответ" /></div>}

        {currentResult ? <div className={`status-banner ${currentResult.correct ? 'success' : 'danger'}`} style={{ marginTop: 18 }}>
          <div style={{ fontWeight: 780, fontSize: 15 }}>{currentResult.correct ? 'Верно' : 'Неверно'}</div>
          {currentResult.explanation ? <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}>{currentResult.explanation}</div> : null}
        </div> : null}

        <div className="exercise-toolbar" style={{ marginTop: 20 }}>
          <button className="btn btn-primary btn-sm" onClick={() => submitAnswer(currentExercise)} disabled={!canSubmit || Boolean(currentResult)}>{currentResult ? 'Ответ сохранён' : 'Проверить'}</button>
          <button className="btn btn-secondary btn-sm" onClick={() => setCurrentIdx((prev) => Math.max(0, prev - 1))} disabled={currentIdx === 0}>Назад</button>
          <button className="btn btn-secondary btn-sm" onClick={() => setCurrentIdx((prev) => Math.min(activeExercises.length - 1, prev + 1))} disabled={currentIdx >= activeExercises.length - 1}>Далее</button>
        </div>
      </div>
    </section>
  </div></div>;
}
