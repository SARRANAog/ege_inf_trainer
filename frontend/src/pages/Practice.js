import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';

import API from '../config/api';

function normalizeTaskNumber(value, fallback = 1) {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed >= 1 && parsed <= 27 ? parsed : fallback;
}

function normalizeMode(value, fallback = 'free') {
  return ['free', 'guided', 'weak', 'mistakes'].includes(value) ? value : fallback;
}

function ExerciseCard({ exercise, currentMode, onNext, theoryLink, onRefreshProgress }) {
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [multiAnswers, setMultiAnswers] = useState([]);
  const [numberAnswer, setNumberAnswer] = useState('');
  const [code, setCode] = useState(exercise.code_template || '');
  const [result, setResult] = useState(null);
  const [output, setOutput] = useState(null);
  const [checking, setChecking] = useState(false);
  const [running, setRunning] = useState(false);
  const [hintIdx, setHintIdx] = useState(-1);
  const [draftReady, setDraftReady] = useState(false);
  const isFirstAutosave = useRef(true);

  const isCode = exercise.exercise_type === 'code';
  const answerType = exercise.answer_type;
  const draftScope = `practice:${exercise.exercise_id}`;

  useEffect(() => {
    let cancelled = false;

    async function loadDraft() {
      setSelectedAnswer(null);
      setMultiAnswers([]);
      setNumberAnswer('');
      setCode(exercise.code_template || '');
      setResult(null);
      setOutput(null);
      setHintIdx(-1);
      setDraftReady(false);
      isFirstAutosave.current = true;

      try {
        const response = await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`);
        if (!response.ok) {
          setDraftReady(true);
          return;
        }
        const draft = await response.json();
        if (cancelled) return;

        const payload = draft?.payload || {};
        setSelectedAnswer(payload.selectedAnswer ?? null);
        setMultiAnswers(Array.isArray(payload.multiAnswers) ? payload.multiAnswers : []);
        setNumberAnswer(payload.numberAnswer ?? '');
        setCode(payload.code ?? (exercise.code_template || ''));
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) setDraftReady(true);
      }
    }

    loadDraft();
    return () => {
      cancelled = true;
    };
  }, [draftScope, exercise.code_template]);

  useEffect(() => {
    if (!draftReady) return undefined;
    if (isFirstAutosave.current) {
      isFirstAutosave.current = false;
      return undefined;
    }

    const timer = setTimeout(async () => {
      try {
        await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            draft_type: 'practice',
            task_number: exercise.task_number,
            exercise_id: exercise.exercise_id,
            payload: {
              selectedAnswer,
              multiAnswers,
              numberAnswer,
              code,
            },
          }),
        });
      } catch (error) {
        console.error(error);
      }
    }, 350);

    return () => clearTimeout(timer);
  }, [code, draftReady, draftScope, exercise.exercise_id, exercise.task_number, multiAnswers, numberAnswer, selectedAnswer]);

  const toggleMulti = (value) => {
    setMultiAnswers((prev) => (
      prev.includes(value)
        ? prev.filter((item) => item !== value)
        : [...prev, value]
    ));
  };

  const handleCheck = async () => {
    setChecking(true);
    try {
      if (isCode) {
        const response = await fetch(`${API}/api/code/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, code }),
        });
        setResult(await response.json());
      } else {
        let answer = selectedAnswer;
        if (answerType === 'multiple_choice') answer = multiAnswers;
        if (answerType === 'number') answer = numberAnswer;

        const response = await fetch(`${API}/api/exercises/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, answer }),
        });
        setResult(await response.json());
      }
      await onRefreshProgress?.();
    } catch (error) {
      console.error(error);
    } finally {
      setChecking(false);
    }
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      const response = await fetch(`${API}/api/code/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, stdin: '' }),
      });
      setOutput(await response.json());
    } catch (error) {
      console.error(error);
    } finally {
      setRunning(false);
    }
  };

  const handleReset = async () => {
    setSelectedAnswer(null);
    setMultiAnswers([]);
    setNumberAnswer('');
    setCode(exercise.code_template || '');
    setResult(null);
    setOutput(null);
    setHintIdx(-1);
    isFirstAutosave.current = true;
    try {
      await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, { method: 'DELETE' });
    } catch (error) {
      console.error(error);
    } finally {
      setDraftReady(true);
    }
  };

  const selectedSummary = useMemo(() => {
    if (isCode) return 'Кодовое решение';
    if (answerType === 'multiple_choice') return multiAnswers.length > 0 ? multiAnswers.join(', ') : 'Не выбрано';
    if (answerType === 'number') return numberAnswer || 'Не введено';
    return selectedAnswer || 'Не выбрано';
  }, [answerType, isCode, multiAnswers, numberAnswer, selectedAnswer]);

  return (
    <div className="card fade-in" style={{ padding: 24 }} data-testid={`exercise-${exercise.exercise_id}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 16 }}>
        <span className="badge badge-accent">№{exercise.task_number}</span>
        <span className={`badge ${exercise.difficulty === 'hard' ? 'badge-danger' : exercise.difficulty === 'medium' ? 'badge-warning' : 'badge-success'}`}>
          {exercise.difficulty === 'hard' ? 'Сложное' : exercise.difficulty === 'medium' ? 'Среднее' : 'Базовое'}
        </span>
        {isCode && <span className="badge badge-accent">Python</span>}
        <span className="badge badge-muted">{currentMode === 'guided' ? 'Guided path' : currentMode === 'weak' ? 'Слабые темы' : currentMode === 'mistakes' ? 'Работа над ошибками' : 'Свободный режим'}</span>
        <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: 12 }}>Черновик сохраняется локально</span>
      </div>

      <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{exercise.title}</h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7, marginBottom: 20, whiteSpace: 'pre-wrap' }}>
        {exercise.text}
      </p>

      {isCode ? (
        <div style={{ marginBottom: 16 }}>
          <div style={{ border: '1px solid var(--border)', borderRadius: 14, overflow: 'hidden' }}>
            <Editor
              height="280px"
              language="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                fontSize: 14,
                minimap: { enabled: false },
                wordWrap: 'on',
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                padding: { top: 12 },
              }}
            />
          </div>
          <div className="exercise-toolbar" style={{ marginTop: 12 }}>
            <button className="btn btn-secondary btn-sm" onClick={handleRun} disabled={running}>
              {running ? 'Выполняется…' : 'Запустить код'}
            </button>
            <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking || !code.trim()}>
              {checking ? 'Проверка…' : 'Проверить решение'}
            </button>
          </div>
          {output && (
            <div className="code-block" style={{ marginTop: 12 }}>
              {output.stdout ? <div>stdout: {output.stdout}</div> : null}
              {output.stderr ? <div style={{ color: 'var(--danger)' }}>stderr: {output.stderr}</div> : null}
            </div>
          )}
        </div>
      ) : answerType === 'single_choice' && exercise.options ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 18 }}>
          {exercise.options.map((option, index) => {
            const optionValue = option.charAt(0);
            const active = selectedAnswer === optionValue;
            return (
              <button
                key={index}
                onClick={() => setSelectedAnswer(optionValue)}
                style={{
                  padding: '12px 16px',
                  borderRadius: 12,
                  border: '1px solid',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: 14,
                  borderColor: active ? 'var(--accent)' : 'var(--border)',
                  background: active ? 'rgba(108,127,216,0.10)' : 'var(--bg-elevated)',
                  color: 'var(--text-primary)',
                }}
              >
                {option}
              </button>
            );
          })}
        </div>
      ) : answerType === 'multiple_choice' && exercise.options ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 18 }}>
          {exercise.options.map((option, index) => {
            const optionValue = option.charAt(0);
            const active = multiAnswers.includes(optionValue);
            return (
              <button
                key={index}
                onClick={() => toggleMulti(optionValue)}
                style={{
                  padding: '12px 16px',
                  borderRadius: 12,
                  border: '1px solid',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: 14,
                  borderColor: active ? 'var(--accent)' : 'var(--border)',
                  background: active ? 'rgba(108,127,216,0.10)' : 'var(--bg-elevated)',
                  color: 'var(--text-primary)',
                }}
              >
                <span style={{ marginRight: 8 }}>{active ? '☑' : '☐'}</span>
                {option}
              </button>
            );
          })}
        </div>
      ) : answerType === 'number' ? (
        <div style={{ marginBottom: 18 }}>
          <input
            className="input"
            type="number"
            value={numberAnswer}
            onChange={(event) => setNumberAnswer(event.target.value)}
            placeholder="Введите числовой ответ"
            style={{ maxWidth: 260 }}
          />
        </div>
      ) : (
        <div className="status-banner danger" style={{ marginBottom: 18 }}>
          Теоретические ручные ответы отключены продуктовой логикой. Для этого упражнения нужен объективный формат.
        </div>
      )}

      <div className="card-elevated" style={{ marginBottom: 16, padding: 14 }}>
        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Текущее состояние ответа</div>
        <div style={{ marginTop: 6, fontSize: 14, fontWeight: 600 }}>{selectedSummary}</div>
      </div>

      {result && (
        <div
          className={`status-banner ${result.correct ? 'success' : 'danger'}`}
          style={{ marginBottom: 16 }}
          data-testid="exercise-result"
        >
          <div style={{ fontWeight: 700, fontSize: 14 }}>
            {result.correct ? 'Правильно' : 'Нужно доработать'}
          </div>
          {result.explanation ? (
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {result.explanation}
            </div>
          ) : null}
          {result.details ? (
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
              {result.details}
            </div>
          ) : null}
          {result.expected !== undefined && !isCode ? (
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>
              Ожидаемый ответ: <strong>{Array.isArray(result.expected) ? result.expected.join(', ') : String(result.expected)}</strong>
            </div>
          ) : null}
        </div>
      )}

      <div className="exercise-toolbar">
        {!isCode && answerType !== 'text' && (
          <button
            className="btn btn-primary btn-sm"
            onClick={handleCheck}
            disabled={checking || (answerType === 'single_choice' && !selectedAnswer) || (answerType === 'multiple_choice' && multiAnswers.length === 0) || (answerType === 'number' && numberAnswer === '')}
          >
            {checking ? 'Проверка…' : 'Проверить'}
          </button>
        )}
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => setHintIdx(Math.min(hintIdx + 1, (exercise.hints || []).length - 1))}
          disabled={!exercise.hints || exercise.hints.length === 0 || hintIdx >= exercise.hints.length - 1}
        >
          Подсказка {hintIdx >= 0 ? `(${hintIdx + 1}/${exercise.hints?.length || 0})` : ''}
        </button>
        <button className="btn btn-ghost btn-sm" onClick={handleReset}>Сбросить</button>
        <button className="btn btn-secondary btn-sm" onClick={onNext}>Следующее</button>
        <Link to={theoryLink} className="btn btn-ghost btn-sm">К теории</Link>
      </div>

      {hintIdx >= 0 && exercise.hints && (
        <div style={{ marginTop: 14, padding: 14, background: 'rgba(108,127,216,0.06)', borderRadius: 12, border: '1px solid rgba(108,127,216,0.18)' }}>
          {exercise.hints.slice(0, hintIdx + 1).map((hint, index) => (
            <div key={index} style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, marginTop: index === 0 ? 0 : 6 }}>
              Подсказка {index + 1}: {hint}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PracticePage({ profile }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [roadmap, setRoadmap] = useState(null);
  const [progress, setProgress] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [exercises, setExercises] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [loading, setLoading] = useState(true);

  const modeFromRoute = normalizeMode(searchParams.get('mode'), profile?.learning_mode === 'guided' ? 'guided' : 'free');
  const taskFromRoute = normalizeTaskNumber(searchParams.get('task'), 1);

  const allowedTasks = useMemo(() => {
    if (!roadmap) return [];
    if (modeFromRoute === 'guided') return roadmap.review_due ? [] : (roadmap.current_focus_tasks || []);
    if (modeFromRoute === 'weak') return roadmap.weak_tasks || [];
    if (modeFromRoute === 'mistakes') return roadmap.mistake_tasks || [];
    return tasks.map((task) => task.task_number);
  }, [modeFromRoute, roadmap, tasks]);

  const currentTask = useMemo(() => {
    if (allowedTasks.length === 0) return taskFromRoute;
    return allowedTasks.includes(taskFromRoute) ? taskFromRoute : allowedTasks[0];
  }, [allowedTasks, taskFromRoute]);

  const refreshAll = async () => {
    try {
      const [theoryRes, progressRes, roadmapRes] = await Promise.all([
        fetch(`${API}/api/theory`),
        fetch(`${API}/api/progress`),
        fetch(`${API}/api/roadmap`),
      ]);
      const [theoryData, progressData, roadmapData] = await Promise.all([theoryRes.json(), progressRes.json(), roadmapRes.json()]);
      setTasks(theoryData);
      setProgress(progressData);
      setRoadmap(roadmapData);
    } catch (error) {
      console.error(error);
    }
  };

  const refreshExercises = async () => {
    if (modeFromRoute === 'guided' && roadmap?.review_due) {
      setExercises([]);
      setLoading(false);
      return;
    }

    if (allowedTasks.length === 0 && modeFromRoute !== 'free') {
      setExercises([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API}/api/exercises/${currentTask}?mode=${modeFromRoute}`);
      const data = await response.json();
      setExercises(data);
      setCurrentIdx(0);
    } catch (error) {
      console.error(error);
      setExercises([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAll();
  }, []);

  useEffect(() => {
    if (!roadmap && !tasks.length) return;
    if (taskFromRoute !== currentTask || normalizeMode(searchParams.get('mode'), modeFromRoute) !== modeFromRoute) {
      setSearchParams({ task: String(currentTask), mode: modeFromRoute });
      return;
    }
    refreshExercises();
  }, [currentTask, modeFromRoute, roadmap, taskFromRoute, tasks.length]);

  const modeDescription = {
    free: 'Свободный режим: можно брать любой номер задания и тренироваться без ограничений.',
    guided: roadmap?.review_due
      ? 'Guided path сейчас заблокирован обязательным Weekly Review.'
      : 'Guided path: доступны только задания текущего этапа, без произвольных перескоков.',
    weak: 'Слабые темы: фокус на заданиях с просевшей точностью.',
    mistakes: 'Работа над ошибками: берём темы, где были последние неверные попытки.',
  };

  const handleModeChange = (nextMode) => {
    const fallbackTask = nextMode === 'guided'
      ? (roadmap?.current_focus_tasks?.[0] || 1)
      : nextMode === 'weak'
        ? (roadmap?.weak_tasks?.[0] || 1)
        : nextMode === 'mistakes'
          ? (roadmap?.mistake_tasks?.[0] || 1)
          : currentTask;
    setSearchParams({ task: String(fallbackTask), mode: nextMode });
  };

  const taskMap = useMemo(() => {
    const map = {};
    tasks.forEach((task) => {
      map[task.task_number] = task;
    });
    return map;
  }, [tasks]);

  const progressMap = useMemo(() => {
    const map = {};
    (progress?.tasks || []).forEach((task) => {
      map[task.task_number] = task;
    });
    return map;
  }, [progress]);

  const currentExercise = exercises[currentIdx];

  return (
    <div className="fade-in" style={{ display: 'grid', gridTemplateColumns: '240px minmax(0, 1fr)', gap: 20, height: 'calc(100vh - 132px)' }}>
      <div style={{ overflowY: 'auto' }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-secondary)', marginBottom: 12 }}>Навигация по заданиям</div>

        {(allowedTasks.length > 0 ? allowedTasks : Array.from({ length: 27 }, (_, index) => index + 1)).map((taskNumber) => {
          const taskInfo = taskMap[taskNumber];
          const taskProgress = progressMap[taskNumber] || {};
          const active = taskNumber === currentTask;

          return (
            <button
              key={taskNumber}
              onClick={() => setSearchParams({ task: String(taskNumber), mode: modeFromRoute })}
              className={`nav-item ${active ? 'active' : ''}`}
              style={{ width: '100%', textAlign: 'left', border: 'none' }}
              data-testid={`practice-task-${taskNumber}`}
            >
              <span style={{
                width: 26,
                height: 26,
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 12,
                fontWeight: 700,
                background: active ? 'var(--accent)' : 'var(--bg-elevated)',
                color: active ? 'white' : 'var(--text-secondary)',
                flexShrink: 0,
              }}>
                {taskNumber}
              </span>
              <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {taskInfo?.title || `Задание ${taskNumber}`}
              </span>
              {taskProgress.total_attempts > 0 ? (
                <span className={`badge ${taskProgress.accuracy >= 80 ? 'badge-success' : taskProgress.accuracy >= 60 ? 'badge-accent' : 'badge-warning'}`} style={{ marginLeft: 'auto' }}>
                  {taskProgress.accuracy?.toFixed?.(0) || 0}%
                </span>
              ) : null}
            </button>
          );
        })}
      </div>

      <div style={{ overflowY: 'auto', minWidth: 0 }}>
        <div className="card" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Практика</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{modeDescription[modeFromRoute]}</div>
            </div>
            <div className="segment-control" data-testid="practice-mode">
              <button className={`segment-btn ${modeFromRoute === 'free' ? 'active' : ''}`} onClick={() => handleModeChange('free')}>Свободный</button>
              <button className={`segment-btn ${modeFromRoute === 'guided' ? 'active' : ''}`} onClick={() => handleModeChange('guided')}>Guided</button>
              <button className={`segment-btn ${modeFromRoute === 'weak' ? 'active' : ''}`} onClick={() => handleModeChange('weak')}>Слабые темы</button>
              <button className={`segment-btn ${modeFromRoute === 'mistakes' ? 'active' : ''}`} onClick={() => handleModeChange('mistakes')}>Ошибки</button>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 14 }}>
            {modeFromRoute === 'guided' && roadmap?.current_focus_tasks?.length > 0 && (
              <span className="badge badge-accent">Фокус этапа: {roadmap.current_focus_tasks.map((task) => `№${task}`).join(', ')}</span>
            )}
            {modeFromRoute === 'weak' && (roadmap?.weak_tasks?.length || 0) === 0 && (
              <span className="badge badge-success">Слабых тем по текущим данным нет</span>
            )}
            {modeFromRoute === 'mistakes' && (roadmap?.mistake_tasks?.length || 0) === 0 && (
              <span className="badge badge-success">Недавних ошибок нет</span>
            )}
            {exercises.length > 0 && (
              <span className="badge badge-muted">Упражнение {currentIdx + 1} из {exercises.length}</span>
            )}
          </div>
        </div>

        {modeFromRoute === 'guided' && roadmap?.review_due ? (
          <div className="status-banner warning">
            <div style={{ fontWeight: 700, fontSize: 15 }}>Guided path временно закрыт checkpoint’ом</div>
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Сначала завершите Weekly Review, затем guided path снова откроет практику текущего этапа.
            </div>
            <div style={{ marginTop: 12 }}>
              <Link className="btn btn-primary btn-sm" to="/weekly-review">Перейти в Weekly Review</Link>
            </div>
          </div>
        ) : loading ? (
          <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка упражнений…</div>
        ) : exercises.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <div style={{ fontSize: 15, color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              {modeFromRoute === 'weak'
                ? 'Для режима слабых тем пока недостаточно провальных задач.'
                : modeFromRoute === 'mistakes'
                  ? 'В режиме ошибок пока нет недавних неверных попыток.'
                  : 'Для этого задания пока нет объективных упражнений в локальной базе.'}
            </div>
            <div style={{ marginTop: 16, display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link className="btn btn-secondary btn-sm" to={`/theory?task=${currentTask}`}>Открыть теорию</Link>
              <Link className="btn btn-ghost btn-sm" to="/progress">Посмотреть аналитику</Link>
            </div>
          </div>
        ) : (
          <ExerciseCard
            key={currentExercise.exercise_id}
            exercise={currentExercise}
            currentMode={modeFromRoute}
            theoryLink={`/theory?task=${currentTask}`}
            onNext={() => setCurrentIdx((prev) => (prev + 1) % exercises.length)}
            onRefreshProgress={refreshAll}
          />
        )}
      </div>
    </div>
  );
}
