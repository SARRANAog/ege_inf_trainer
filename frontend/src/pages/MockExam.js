import React, { useEffect, useMemo, useState } from 'react';
import Editor from '@monaco-editor/react';

const API = process.env.REACT_APP_BACKEND_URL;

function formatTime(totalSeconds) {
  const safe = Math.max(0, totalSeconds || 0);
  const hours = Math.floor(safe / 3600);
  const minutes = Math.floor((safe % 3600) / 60);
  const seconds = safe % 60;
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

export default function MockExamPage() {
  const [status, setStatus] = useState(null);
  const [selectedMode, setSelectedMode] = useState('exam');
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [codes, setCodes] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timerTick, setTimerTick] = useState(0);
  const [submittedResult, setSubmittedResult] = useState(null);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/mock-exam`);
      const data = await response.json();
      setStatus(data);
      setTimerTick(0);

      if (data.exam) {
        const nextAnswers = {};
        const nextCodes = {};
        (data.exam.tasks || []).forEach((task) => {
          if (task.answer !== null && task.answer !== undefined) nextAnswers[task.task_number] = task.answer;
          if (task.code) nextCodes[task.task_number] = task.code;
        });
        setAnswers(nextAnswers);
        setCodes(nextCodes);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  useEffect(() => {
    if (!status?.exam || status.exam.status !== 'active') return undefined;
    const timer = setInterval(() => setTimerTick((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, [status?.exam?.exam_id, status?.exam?.status]);

  const activeExam = status?.exam || null;
  const tasks = activeExam?.tasks || [];
  const currentTask = tasks[currentTaskIndex];
  const elapsedSeconds = useMemo(() => {
    if (!activeExam) return 0;
    const base = activeExam.elapsed_seconds || 0;
    if (activeExam.status === 'paused') return base;
    return base + timerTick;
  }, [activeExam, timerTick]);

  const saveAnswer = async (taskNumber, answer, code) => {
    if (!activeExam) return;
    try {
      await fetch(`${API}/api/mock-exam/${activeExam.exam_id}/answer`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_number: taskNumber, answer, code }),
      });
    } catch (error) {
      console.error(error);
    }
  };

  const startExam = async () => {
    setLoading(true);
    try {
      await fetch(`${API}/api/mock-exam/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: selectedMode }),
      });
      setCurrentTaskIndex(0);
      setTimerTick(0);
      await loadStatus();
    } catch (error) {
      console.error(error);
      setLoading(false);
    }
  };

  const togglePause = async () => {
    if (!activeExam) return;
    try {
      await fetch(`${API}/api/mock-exam/${activeExam.exam_id}/${activeExam.status === 'paused' ? 'resume' : 'pause'}`, {
        method: 'POST',
      });
      await loadStatus();
    } catch (error) {
      console.error(error);
    }
  };

  const toggleFlag = async (taskNumber) => {
    if (!activeExam) return;
    try {
      await fetch(`${API}/api/mock-exam/${activeExam.exam_id}/flag/${taskNumber}`, { method: 'PUT' });
      await loadStatus();
    } catch (error) {
      console.error(error);
    }
  };

  const submitExam = async () => {
    if (!activeExam) return;
    if (!window.confirm('Завершить пробник и посчитать результат?')) return;

    setSubmitting(true);
    try {
      const response = await fetch(`${API}/api/mock-exam/${activeExam.exam_id}/submit`, { method: 'POST' });
      const data = await response.json();
      setSubmittedResult(data);
      setStatus((prev) => ({ ...prev, exam: null }));
    } catch (error) {
      console.error(error);
    } finally {
      setSubmitting(false);
    }
  };

  const latestCompleted = useMemo(() => {
    return status?.recent_exams?.[0] || null;
  }, [status]);

  if (loading) {
    return <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка пробника…</div>;
  }

  if (!activeExam) {
    return (
      <div className="fade-in" style={{ maxWidth: 980, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
            <div style={{ flex: 1, minWidth: 280 }}>
              <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 10 }}>Пробный экзамен</h1>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: 14 }}>
                Здесь два полноценных сценария: максимально близкий к ЕГЭ экзаменационный режим и укороченный тренировочный пробник.
                Оба поддерживают таймер, паузу и продолжение без потери данных.
              </p>
            </div>
            <div className="badge badge-accent">mock + timer + pause/resume</div>
          </div>

          <div style={{ marginTop: 18 }} className="segment-control">
            {(status?.modes || []).map((mode) => (
              <button
                key={mode.mode}
                className={`segment-btn ${selectedMode === mode.mode ? 'active' : ''}`}
                onClick={() => setSelectedMode(mode.mode)}
              >
                {mode.label}
              </button>
            ))}
          </div>

          <div className="analytics-grid" style={{ marginTop: 18 }}>
            {(status?.modes || []).map((mode) => (
              <div key={mode.mode} className="card-elevated" style={{ padding: 16 }}>
                <div style={{ fontSize: 15, fontWeight: 700 }}>{mode.label}</div>
                <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{mode.description}</div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 12 }}>
                  <span className="badge badge-muted">{mode.tasks_count} заданий</span>
                  <span className="badge badge-muted">{mode.duration_minutes} мин.</span>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 20 }}>
            <button className="btn btn-primary btn-lg" onClick={startExam} data-testid="start-mock-btn">
              Начать {selectedMode === 'exam' ? 'экзаменационный' : 'тренировочный'} режим
            </button>
          </div>
        </div>

        {latestCompleted && (
          <div className="card">
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 12 }}>Последний завершённый пробник</div>
            <div className="analytics-grid">
              <div className="card-elevated" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Режим</div>
                <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700 }}>{latestCompleted.mode === 'training' ? 'Тренировочный' : 'Экзаменационный'}</div>
              </div>
              <div className="card-elevated" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Результат</div>
                <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700 }}>{latestCompleted.score?.toFixed?.(0) || 0}%</div>
              </div>
              <div className="card-elevated" style={{ padding: 14 }}>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Дата</div>
                <div style={{ marginTop: 6, fontSize: 22, fontWeight: 700 }}>{latestCompleted.completed_at?.slice?.(0, 10) || '—'}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (submittedResult) {
    return (
      <div className="fade-in" style={{ maxWidth: 920, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
            <div>
              <div style={{ fontSize: 26, fontWeight: 700, marginBottom: 8 }}>Результаты пробника</div>
              <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                Результат уже сохранён локально и участвует в аналитике и прогнозе баллов.
              </div>
            </div>
            <div className="timer-chip">{formatTime(submittedResult.elapsed_seconds || 0)}</div>
          </div>

          <div className="analytics-grid" style={{ marginTop: 18 }}>
            <div className="metric-card">
              <div className="metric-value" style={{ color: 'var(--accent)' }}>{submittedResult.score?.toFixed?.(0) || 0}%</div>
              <div className="metric-label">Итоговый результат</div>
            </div>
            <div className="metric-card">
              <div className="metric-value" style={{ color: 'var(--success)' }}>{submittedResult.correct || 0}</div>
              <div className="metric-label">Верных задач</div>
            </div>
            <div className="metric-card">
              <div className="metric-value" style={{ color: 'var(--warning)' }}>{submittedResult.total || 0}</div>
              <div className="metric-label">Всего задач</div>
            </div>
            <div className="metric-card">
              <div className="metric-value" style={{ color: 'var(--accent)' }}>{submittedResult.mode === 'training' ? 'Трен.' : 'Экзамен'}</div>
              <div className="metric-label">Режим</div>
            </div>
          </div>

          <div style={{ marginTop: 18 }} className="table-like-list">
            {(submittedResult.results || []).map((result) => (
              <div key={result.task_number} className="table-like-row">
                <div className={`badge ${result.correct ? 'badge-success' : 'badge-danger'}`}>№{result.task_number}</div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>{result.correct ? 'Верно' : 'Нужно разобрать'}</div>
                  <div style={{ marginTop: 4, fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                    {result.explanation || result.details || 'Без дополнительного комментария.'}
                  </div>
                </div>
                <div />
                <div />
              </div>
            ))}
          </div>

          <div style={{ marginTop: 18 }}>
            <button className="btn btn-primary btn-md" onClick={() => { setSubmittedResult(null); loadStatus(); }}>К списку пробников</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in mock-layout" style={{ maxWidth: 1320, margin: '0 auto' }}>
      <div className="dashboard-stack">
        <div className="card">
          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 10 }}>
            {activeExam.mode === 'training' ? 'Тренировочный пробник' : 'Экзаменационный пробник'}
          </div>
          <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: 13 }}>
            Все ответы сохраняются локально. Можно поставить паузу и продолжить позже.
          </div>

          <div style={{ display: 'grid', gap: 10, marginTop: 16 }}>
            <div className="timer-chip">{formatTime(elapsedSeconds)}</div>
            <div className="card-elevated" style={{ padding: 12 }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Лимит времени</div>
              <div style={{ marginTop: 6, fontSize: 18, fontWeight: 700 }}>{activeExam.duration_minutes} мин.</div>
            </div>
            <div className="card-elevated" style={{ padding: 12 }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Решено задач</div>
              <div style={{ marginTop: 6, fontSize: 18, fontWeight: 700 }}>
                {tasks.filter((task) => task.status === 'answered').length}/{tasks.length}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 16 }}>
            <button className="btn btn-secondary btn-sm" onClick={togglePause}>
              {activeExam.status === 'paused' ? 'Продолжить' : 'Пауза'}
            </button>
            <button className="btn btn-danger btn-sm" onClick={submitExam} disabled={submitting}>
              {submitting ? 'Завершение…' : 'Завершить'}
            </button>
          </div>
        </div>

        <div className="card">
          <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Навигация по задачам</div>
          <div className="mock-nav-grid">
            {tasks.map((task, index) => {
              const classes = [
                'mock-nav-btn',
                index === currentTaskIndex ? 'active' : '',
                task.status === 'answered' ? 'answered' : '',
                task.flagged ? 'flagged' : '',
              ].filter(Boolean).join(' ');

              return (
                <button key={task.task_number} className={classes} onClick={() => setCurrentTaskIndex(index)}>
                  {task.task_number}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="dashboard-stack">
        {activeExam.status === 'paused' && (
          <div className="status-banner warning">
            <div style={{ fontWeight: 700, fontSize: 14 }}>Пробник поставлен на паузу</div>
            <div style={{ marginTop: 6, fontSize: 13, color: 'var(--text-secondary)' }}>
              Таймер остановлен. Нажмите «Продолжить», чтобы вернуться к решению.
            </div>
          </div>
        )}

        {currentTask && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'flex-start', flexWrap: 'wrap', marginBottom: 16 }}>
              <div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                  <span className="badge badge-accent">Задание {currentTask.task_number}</span>
                  {currentTask.is_code_task ? <span className="badge badge-accent">Python</span> : null}
                </div>
                <h2 style={{ marginTop: 10, fontSize: 20, fontWeight: 700 }}>{currentTask.exercise?.title || currentTask.title}</h2>
              </div>

              <button className="btn btn-ghost btn-sm" onClick={() => toggleFlag(currentTask.task_number)}>
                {currentTask.flagged ? 'Снять флаг' : 'Пометить'}
              </button>
            </div>

            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-wrap', marginBottom: 18 }}>
              {currentTask.exercise?.text || 'Для этой задачи нет локального упражнения.'}
            </p>

            {currentTask.exercise?.exercise_type === 'code' ? (
              <div style={{ marginBottom: 16 }}>
                <div style={{ border: '1px solid var(--border)', borderRadius: 14, overflow: 'hidden' }}>
                  <Editor
                    height="320px"
                    language="python"
                    theme="vs-dark"
                    value={codes[currentTask.task_number] ?? currentTask.code ?? currentTask.exercise?.code_template ?? ''}
                    onChange={(value) => {
                      const nextCode = value || '';
                      setCodes((prev) => ({ ...prev, [currentTask.task_number]: nextCode }));
                      saveAnswer(currentTask.task_number, 'code_submitted', nextCode);
                    }}
                    options={{
                      fontSize: 14,
                      minimap: { enabled: false },
                      wordWrap: 'on',
                      automaticLayout: true,
                      scrollBeyondLastLine: false,
                    }}
                  />
                </div>
              </div>
            ) : currentTask.exercise?.answer_type === 'single_choice' && currentTask.exercise?.options ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 18 }}>
                {currentTask.exercise.options.map((option, index) => {
                  const value = option.charAt(0);
                  const active = answers[currentTask.task_number] === value;
                  return (
                    <button
                      key={index}
                      onClick={() => {
                        setAnswers((prev) => ({ ...prev, [currentTask.task_number]: value }));
                        saveAnswer(currentTask.task_number, value, null);
                      }}
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
            ) : currentTask.exercise?.answer_type === 'multiple_choice' && currentTask.exercise?.options ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 18 }}>
                {currentTask.exercise.options.map((option, index) => {
                  const value = option.charAt(0);
                  const currentValue = Array.isArray(answers[currentTask.task_number]) ? answers[currentTask.task_number] : [];
                  const active = currentValue.includes(value);
                  return (
                    <button
                      key={index}
                      onClick={() => {
                        const nextValue = active ? currentValue.filter((item) => item !== value) : [...currentValue, value];
                        setAnswers((prev) => ({ ...prev, [currentTask.task_number]: nextValue }));
                        saveAnswer(currentTask.task_number, nextValue, null);
                      }}
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
                value={answers[currentTask.task_number] || ''}
                onChange={(event) => {
                  const nextValue = event.target.value;
                  setAnswers((prev) => ({ ...prev, [currentTask.task_number]: nextValue }));
                  saveAnswer(currentTask.task_number, nextValue, null);
                }}
                placeholder="Введите числовой ответ"
                style={{ maxWidth: 260, marginBottom: 18 }}
              />
            )}

            <div className="exercise-toolbar">
              <button className="btn btn-secondary btn-sm" onClick={() => setCurrentTaskIndex((prev) => Math.max(0, prev - 1))} disabled={currentTaskIndex === 0}>
                Назад
              </button>
              <button className="btn btn-primary btn-sm" onClick={() => setCurrentTaskIndex((prev) => Math.min(tasks.length - 1, prev + 1))} disabled={currentTaskIndex >= tasks.length - 1}>
                Далее
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
