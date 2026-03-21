import React, { useEffect, useMemo, useState } from 'react';
import Editor from '@monaco-editor/react';
import API from '../config/api';

function formatTime(totalSeconds) {
  const safe = Math.max(0, totalSeconds || 0);
  const hours = Math.floor(safe / 3600);
  const minutes = Math.floor((safe % 3600) / 60);
  const seconds = safe % 60;
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function ChoiceButton({ active, label, leading, onClick }) {
  return <button className={`choice-option ${active ? 'active' : ''}`} onClick={onClick}><div className="choice-option-row"><span className="choice-option-mark">{leading}</span><div className="choice-option-body">{label}</div></div></button>;
}

export default function MockExamPage({ profile }) {
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
    } catch (error) { console.error(error); } finally { setLoading(false); }
  };

  useEffect(() => { loadStatus(); }, []);
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
  const remainingSeconds = useMemo(() => !activeExam ? 0 : Math.max(0, activeExam.duration_minutes * 60 - elapsedSeconds), [activeExam, elapsedSeconds]);

  const saveAnswer = async (taskNumber, answer, code) => {
    if (!activeExam) return;
    try {
      await fetch(`${API}/api/mock-exam/${activeExam.exam_id}/answer`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_number: taskNumber, answer, code }),
      });
    } catch (error) { console.error(error); }
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
    } catch (error) { console.error(error); setLoading(false); }
  };

  const togglePause = async () => {
    if (!activeExam) return;
    try {
      await fetch(`${API}/api/mock-exam/${activeExam.exam_id}/${activeExam.status === 'paused' ? 'resume' : 'pause'}`, { method: 'POST' });
      await loadStatus();
    } catch (error) { console.error(error); }
  };

  const toggleFlag = async (taskNumber) => {
    if (!activeExam) return;
    try {
      await fetch(`${API}/api/mock-exam/${activeExam.exam_id}/flag/${taskNumber}`, { method: 'PUT' });
      await loadStatus();
    } catch (error) { console.error(error); }
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
    } catch (error) { console.error(error); } finally { setSubmitting(false); }
  };

  const latestCompleted = useMemo(() => status?.recent_exams?.[0] || null, [status]);
  const editorFontSize = profile?.font_size || 14;

  if (loading) return <div className="page-shell fade-in"><div className="state-card loading-shimmer"><div className="state-title">Загрузка пробника</div><div className="state-description">Подтягиваем режимы, статус активного экзамена и последние локально завершённые попытки.</div></div></div>;

  if (!activeExam) {
    return <div className="page-shell page-shell-wide fade-in">
      <div className="hero-card dashboard-hero">
        <div className="eyebrow">Экзаменационный режим</div>
        <div className="hero-title">Пробный экзамен</div>
        <div className="hero-description">Два сценария: полноценный экзаменационный режим и укороченный тренировочный пробник. Оба поддерживают таймер, паузу и локальное сохранение.</div>
        <div style={{ marginTop: 18 }} className="segment-control">
          {(status?.modes || []).map((mode) => <button key={mode.mode} className={`segment-btn ${selectedMode === mode.mode ? 'active' : ''}`} onClick={() => setSelectedMode(mode.mode)}>{mode.label}</button>)}
        </div>
        <div className="analytics-grid" style={{ marginTop: 18 }}>
          {(status?.modes || []).map((mode) => <div key={mode.mode} className="metric-card"><div className="metric-value" style={{ color: mode.mode === 'exam' ? 'var(--accent-strong)' : 'var(--warning)' }}>{mode.tasks_count}</div><div className="metric-label">{mode.label}</div><div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>{mode.description}</div><div className="task-chip-row" style={{ marginTop: 12 }}><span className="badge badge-muted">{mode.duration_minutes} мин.</span></div></div>)}
        </div>
        <div className="row-actions" style={{ marginTop: 20 }}><button className="btn btn-primary btn-lg" onClick={startExam}>Начать {selectedMode === 'exam' ? 'экзаменационный' : 'тренировочный'} режим</button></div>
      </div>

      {latestCompleted ? <div className="card"><div className="section-title">Последний завершённый пробник</div><div className="info-grid" style={{ marginTop: 18 }}><div className="info-card"><div className="info-label">Режим</div><div className="info-value">{latestCompleted.mode === 'training' ? 'Тренировочный' : 'Экзаменационный'}</div></div><div className="info-card"><div className="info-label">Результат</div><div className="info-value">{latestCompleted.score?.toFixed?.(0) || 0}%</div></div><div className="info-card"><div className="info-label">Дата</div><div className="info-value">{latestCompleted.completed_at?.slice?.(0, 10) || '—'}</div></div></div></div> : null}
    </div>;
  }

  if (submittedResult) {
    return <div className="page-shell fade-in">
      <div className="hero-card dashboard-hero">
        <div className="eyebrow">Результат сохранён</div>
        <div className="hero-title">Пробник завершён</div>
        <div className="hero-description">Результат уже сохранён локально и будет учитываться в аналитике и истории.</div>
        <div className="row-actions" style={{ marginTop: 16 }}><div className="timer-chip">{formatTime(submittedResult.elapsed_seconds || 0)}</div><span className="badge badge-accent">{submittedResult.mode === 'training' ? 'Тренировочный' : 'Экзаменационный'}</span></div>
        <div className="analytics-grid" style={{ marginTop: 18 }}>
          <div className="metric-card"><div className="metric-value" style={{ color: 'var(--accent-strong)' }}>{submittedResult.score?.toFixed?.(0) || 0}%</div><div className="metric-label">Итоговый результат</div></div>
          <div className="metric-card"><div className="metric-value" style={{ color: 'var(--success)' }}>{submittedResult.correct || 0}</div><div className="metric-label">Верных задач</div></div>
          <div className="metric-card"><div className="metric-value" style={{ color: 'var(--warning)' }}>{submittedResult.total || 0}</div><div className="metric-label">Всего задач</div></div>
        </div>
      </div>
      <div className="card">
        <div className="section-title">Разбор по заданиям</div>
        <div className="table-like-list" style={{ marginTop: 16 }}>
          {(submittedResult.results || []).map((result) => <div key={result.task_number} className="table-like-row"><div className={`badge ${result.correct ? 'badge-success' : 'badge-danger'}`}>№{result.task_number}</div><div><div style={{ fontSize: 14, fontWeight: 740 }}>{result.correct ? 'Верно' : 'Нужно разобрать'}</div><div style={{ marginTop: 6, fontSize: 12, lineHeight: 1.65, color: 'var(--text-secondary)' }}>{result.explanation || result.details || 'Без дополнительного комментария.'}</div></div><div /><div /></div>)}
        </div>
        <div className="row-actions" style={{ marginTop: 18 }}><button className="btn btn-primary btn-md" onClick={() => { setSubmittedResult(null); loadStatus(); }}>К списку пробников</button></div>
      </div>
    </div>;
  }

  return <div className="page-shell page-shell-wide fade-in"><div className="mock-layout">
    <aside className="left-rail-card">
      <div className="card">
        <div className="eyebrow">Статус экзамена</div>
        <div className="section-title">{activeExam.mode === 'training' ? 'Тренировочный пробник' : 'Экзаменационный пробник'}</div>
        <div className="info-grid" style={{ marginTop: 16 }}>
          <div className="info-card"><div className="info-label">Прошло</div><div className="info-value">{formatTime(elapsedSeconds)}</div></div>
          <div className="info-card"><div className="info-label">Осталось</div><div className="info-value">{formatTime(remainingSeconds)}</div></div>
          <div className="info-card"><div className="info-label">Лимит</div><div className="info-value">{activeExam.duration_minutes} мин.</div></div>
          <div className="info-card"><div className="info-label">Решено</div><div className="info-value">{tasks.filter((task) => task.status === 'answered').length}/{tasks.length}</div></div>
        </div>
        <div className="row-actions" style={{ marginTop: 16 }}>
          <button className="btn btn-secondary btn-sm" onClick={togglePause}>{activeExam.status === 'paused' ? 'Продолжить' : 'Пауза'}</button>
          <button className="btn btn-danger btn-sm" onClick={submitExam} disabled={submitting}>{submitting ? 'Завершение…' : 'Завершить'}</button>
        </div>
      </div>
      <div className="card"><div className="section-title" style={{ fontSize: 18 }}>Навигация по задачам</div><div className="mock-nav-grid" style={{ marginTop: 14 }}>
        {tasks.map((task, index) => {
          const classes = ['mock-nav-btn', index === currentTaskIndex ? 'active' : '', task.status === 'answered' ? 'answered' : '', task.flagged ? 'flagged' : ''].filter(Boolean).join(' ');
          return <button key={task.task_number} className={classes} onClick={() => setCurrentTaskIndex(index)}>{task.task_number}</button>;
        })}
      </div></div>
    </aside>

    <section className="page-stack">
      {activeExam.status === 'paused' ? <div className="status-banner warning"><div style={{ fontWeight: 780, fontSize: 15 }}>Пробник поставлен на паузу</div><div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)' }}>Таймер остановлен. Нажмите «Продолжить», чтобы вернуться к решению.</div></div> : null}
      {currentTask ? <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div className="task-chip-row"><span className="badge badge-accent">Задание {currentTask.task_number}</span>{currentTask.is_code_task ? <span className="badge badge-accent">Python</span> : null}</div>
            <div className="section-title" style={{ marginTop: 14 }}>{currentTask.exercise?.title || currentTask.title}</div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => toggleFlag(currentTask.task_number)}>{currentTask.flagged ? 'Снять флаг' : 'Пометить'}</button>
        </div>
        <div style={{ marginTop: 12, fontSize: 14, lineHeight: 1.78, whiteSpace: 'pre-wrap', color: 'var(--text-secondary)' }}>{currentTask.exercise?.text || 'Для этой задачи не найдено локальное упражнение.'}</div>

        {currentTask.exercise?.exercise_type === 'code' ? <div style={{ marginTop: 20 }}><div style={{ border: '1px solid var(--border)', borderRadius: 18, overflow: 'hidden' }}>
          <Editor height="340px" language="python" theme="vs-dark" value={codes[currentTask.task_number] ?? currentTask.code ?? currentTask.exercise?.code_template ?? ''} onChange={(value) => { const nextCode = value || ''; setCodes((prev) => ({ ...prev, [currentTask.task_number]: nextCode })); saveAnswer(currentTask.task_number, 'code_submitted', nextCode); }} options={{ fontSize: editorFontSize, minimap: { enabled: false }, wordWrap: 'on', automaticLayout: true, scrollBeyondLastLine: false, padding: { top: 14 } }} />
        </div></div> : currentTask.exercise?.answer_type === 'single_choice' && currentTask.exercise?.options ? <div className="choice-list" style={{ marginTop: 20 }}>
          {currentTask.exercise.options.map((option, index) => { const value = option.charAt(0); const active = answers[currentTask.task_number] === value; return <ChoiceButton key={index} active={active} leading={value} label={option} onClick={() => { setAnswers((prev) => ({ ...prev, [currentTask.task_number]: value })); saveAnswer(currentTask.task_number, value, null); }} />; })}
        </div> : currentTask.exercise?.answer_type === 'multiple_choice' && currentTask.exercise?.options ? <div className="choice-list" style={{ marginTop: 20 }}>
          {currentTask.exercise.options.map((option, index) => {
            const value = option.charAt(0);
            const currentValue = Array.isArray(answers[currentTask.task_number]) ? answers[currentTask.task_number] : [];
            const active = currentValue.includes(value);
            return <ChoiceButton key={index} active={active} leading={active ? '✓' : '+'} label={option} onClick={() => { const nextValue = active ? currentValue.filter((item) => item !== value) : [...currentValue, value]; setAnswers((prev) => ({ ...prev, [currentTask.task_number]: nextValue })); saveAnswer(currentTask.task_number, nextValue, null); }} />;
          })}
        </div> : <div style={{ marginTop: 20, maxWidth: 280 }}><input className="input" type="number" value={answers[currentTask.task_number] || ''} onChange={(event) => { const nextValue = event.target.value; setAnswers((prev) => ({ ...prev, [currentTask.task_number]: nextValue })); saveAnswer(currentTask.task_number, nextValue, null); }} placeholder="Введите числовой ответ" /></div>}

        <div className="exercise-toolbar" style={{ marginTop: 20 }}>
          <button className="btn btn-secondary btn-sm" onClick={() => setCurrentTaskIndex((prev) => Math.max(0, prev - 1))} disabled={currentTaskIndex === 0}>Назад</button>
          <button className="btn btn-primary btn-sm" onClick={() => setCurrentTaskIndex((prev) => Math.min(tasks.length - 1, prev + 1))} disabled={currentTaskIndex >= tasks.length - 1}>Далее</button>
        </div>
      </div> : null}
    </section>
  </div></div>;
}
