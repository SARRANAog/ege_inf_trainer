import React, { useEffect, useMemo, useState } from 'react';

import API from '../config/api';

function formatMinutes(value) {
  return `${value || 0} мин.`;
}

export default function WeeklyReviewPage() {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});

  const loadReview = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/weekly-review`);
      setReview(await response.json());
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReview();
  }, []);

  const startReview = async () => {
    try {
      const response = await fetch(`${API}/api/weekly-review/start`, { method: 'POST' });
      setReview(await response.json());
      setCurrentIdx(0);
    } catch (error) {
      console.error(error);
    }
  };

  const submitAnswer = async (exercise) => {
    const value = answers[exercise.exercise_id];
    if (value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) return;

    try {
      const response = await fetch(`${API}/api/weekly-review/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exercise_id: exercise.exercise_id, answer: value }),
      });
      const result = await response.json();
      setReview((prev) => ({
        ...prev,
        results: {
          ...(prev?.results || {}),
          [exercise.exercise_id]: result,
        },
        answers_count: Object.keys({
          ...(prev?.results || {}),
          [exercise.exercise_id]: result,
        }).length,
        correct_count: Object.values({
          ...(prev?.results || {}),
          [exercise.exercise_id]: result,
        }).filter((item) => item.correct).length,
      }));
    } catch (error) {
      console.error(error);
    }
  };

  const completeReview = async () => {
    try {
      const response = await fetch(`${API}/api/weekly-review/complete`, { method: 'POST' });
      setReview(await response.json());
    } catch (error) {
      console.error(error);
      alert('Нужно ответить почти на все задания review перед завершением.');
    }
  };

  const updateSingleChoice = (exerciseId, value) => {
    setAnswers((prev) => ({ ...prev, [exerciseId]: value }));
  };

  const updateMultiChoice = (exerciseId, value) => {
    setAnswers((prev) => {
      const current = Array.isArray(prev[exerciseId]) ? prev[exerciseId] : [];
      return {
        ...prev,
        [exerciseId]: current.includes(value)
          ? current.filter((item) => item !== value)
          : [...current, value],
      };
    });
  };

  const activeExercises = review?.exercises || [];
  const currentExercise = activeExercises[currentIdx];
  const currentResult = currentExercise ? review?.results?.[currentExercise.exercise_id] : null;
  const isActiveReview = review?.status === 'active';
  const completionRatio = useMemo(() => {
    if (!activeExercises.length) return 0;
    return ((review?.answers_count || 0) / activeExercises.length) * 100;
  }, [activeExercises.length, review]);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка weekly review…</div>;
  }

  if (!review) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Не удалось загрузить weekly review.</div>;
  }

  if (!isActiveReview) {
    return (
      <div className="fade-in" style={{ maxWidth: 820, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: 280 }}>
              <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 10 }}>Weekly Review</h1>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: 14 }}>
                Это обязательный контрольный блок между группами заданий. Он собирается из текущего этапа guided path,
                слабых тем и недавних ошибок. Пока review не выполнен, дорожка может не пустить дальше.
              </p>
            </div>
            <div className="badge badge-warning">
              {review.required_checkpoint ? 'Обязательный checkpoint' : 'Повторение'}
            </div>
          </div>

          <div className="analytics-grid" style={{ marginTop: 18 }}>
            <div className="card-elevated" style={{ padding: 14 }}>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Упражнений</div>
              <div style={{ marginTop: 6, fontSize: 24, fontWeight: 700 }}>{activeExercises.length}</div>
            </div>
            <div className="card-elevated" style={{ padding: 14 }}>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Оценка времени</div>
              <div style={{ marginTop: 6, fontSize: 24, fontWeight: 700 }}>{formatMinutes(review.estimated_time)}</div>
            </div>
            <div className="card-elevated" style={{ padding: 14 }}>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Слабые темы внутри review</div>
              <div style={{ marginTop: 6, fontSize: 24, fontWeight: 700 }}>{review.weak_tasks?.length || 0}</div>
            </div>
            <div className="card-elevated" style={{ padding: 14 }}>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Review уже пройдено</div>
              <div style={{ marginTop: 6, fontSize: 24, fontWeight: 700 }}>{review.completed_reviews || 0}</div>
            </div>
          </div>

          {(review.review_tasks || []).length > 0 && (
            <div style={{ marginTop: 18 }}>
              <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>Темы блока</div>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {review.review_tasks.map((taskNumber) => (
                  <span key={taskNumber} className="badge badge-muted">№{taskNumber}</span>
                ))}
              </div>
            </div>
          )}

          {review.checkpoint_label && (
            <div className="status-banner warning" style={{ marginTop: 18 }}>
              <div style={{ fontWeight: 700, fontSize: 14 }}>{review.checkpoint_label}</div>
              <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)' }}>
                Этот review встроен в guided path как обязательный checkpoint.
              </div>
            </div>
          )}

          <div style={{ marginTop: 20 }}>
            <button className="btn btn-primary btn-lg" onClick={startReview} data-testid="start-review-btn">
              Начать Weekly Review
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!currentExercise) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>В review нет упражнений.</div>;
  }

  const answerValue = answers[currentExercise.exercise_id];
  const canSubmit = answerValue !== undefined && answerValue !== '' && (!Array.isArray(answerValue) || answerValue.length > 0);

  return (
    <div className="fade-in" style={{ maxWidth: 960, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>Weekly Review в процессе</div>
            <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Ответьте почти на все задания блока, чтобы checkpoint считался пройденным.
            </div>
          </div>
          <div className="badge badge-accent">
            {review.answers_count || 0}/{activeExercises.length}
          </div>
        </div>

        <div style={{ marginTop: 14 }}>
          <div className="progress-bar">
            <div className="progress-fill warning" style={{ width: `${completionRatio}%` }} />
          </div>
        </div>

        <div style={{ marginTop: 14 }} className="review-grid">
          {activeExercises.map((exercise, index) => {
            const result = review?.results?.[exercise.exercise_id];
            const classes = [
              'review-nav-btn',
              index === currentIdx ? 'active' : '',
              result?.correct ? 'correct' : '',
              result && !result.correct ? 'wrong' : '',
            ].filter(Boolean).join(' ');

            return (
              <button key={exercise.exercise_id} className={classes} onClick={() => setCurrentIdx(index)}>
                {index + 1}
              </button>
            );
          })}
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 16 }}>
          <span className="badge badge-accent">№{currentExercise.task_number}</span>
          <span className={`badge ${currentExercise.difficulty === 'hard' ? 'badge-danger' : currentExercise.difficulty === 'medium' ? 'badge-warning' : 'badge-success'}`}>
            {currentExercise.difficulty || 'objective'}
          </span>
        </div>

        <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{currentExercise.title}</h2>
        <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-wrap', marginBottom: 18 }}>
          {currentExercise.text}
        </p>

        {currentExercise.answer_type === 'single_choice' && currentExercise.options ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentExercise.options.map((option, index) => {
              const value = option.charAt(0);
              const active = answerValue === value;
              return (
                <button
                  key={index}
                  onClick={() => updateSingleChoice(currentExercise.exercise_id, value)}
                  style={{
                    padding: '12px 16px',
                    borderRadius: 12,
                    border: '1px solid',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: 14,
                    borderColor: active ? 'var(--accent)' : 'var(--border)',
                    background: active ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                    color: 'var(--text-primary)',
                  }}
                >
                  {option}
                </button>
              );
            })}
          </div>
        ) : currentExercise.answer_type === 'multiple_choice' && currentExercise.options ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentExercise.options.map((option, index) => {
              const value = option.charAt(0);
              const active = Array.isArray(answerValue) && answerValue.includes(value);
              return (
                <button
                  key={index}
                  onClick={() => updateMultiChoice(currentExercise.exercise_id, value)}
                  style={{
                    padding: '12px 16px',
                    borderRadius: 12,
                    border: '1px solid',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: 14,
                    borderColor: active ? 'var(--accent)' : 'var(--border)',
                    background: active ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                    color: 'var(--text-primary)',
                  }}
                >
                  <span style={{ marginRight: 8 }}>{active ? '☑' : '☐'}</span>
                  {option}
                </button>
              );
            })}
          </div>
        ) : (
          <input
            className="input"
            type="number"
            value={answerValue || ''}
            onChange={(event) => setAnswers((prev) => ({ ...prev, [currentExercise.exercise_id]: event.target.value }))}
            placeholder="Введите числовой ответ"
            style={{ maxWidth: 260 }}
          />
        )}

        {currentResult && (
          <div className={`status-banner ${currentResult.correct ? 'success' : 'danger'}`} style={{ marginTop: 18 }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>{currentResult.correct ? 'Верно' : 'Неверно'}</div>
            {currentResult.explanation ? (
              <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {currentResult.explanation}
              </div>
            ) : null}
          </div>
        )}

        <div className="exercise-toolbar" style={{ marginTop: 20 }}>
          <button className="btn btn-primary btn-sm" onClick={() => submitAnswer(currentExercise)} disabled={!canSubmit || Boolean(currentResult)}>
            {currentResult ? 'Ответ сохранён' : 'Проверить'}
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => setCurrentIdx((prev) => Math.max(0, prev - 1))} disabled={currentIdx === 0}>
            Назад
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => setCurrentIdx((prev) => Math.min(activeExercises.length - 1, prev + 1))} disabled={currentIdx >= activeExercises.length - 1}>
            Далее
          </button>
          <button
            className="btn btn-ghost btn-sm"
            onClick={completeReview}
            disabled={(review.answers_count || 0) < Math.max(3, activeExercises.length - 1)}
          >
            Завершить Review
          </button>
        </div>
      </div>
    </div>
  );
}
