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

function modeLabel(currentMode) {
  if (currentMode === 'guided') return 'Guided path';
  if (currentMode === 'weak') return 'Слабые темы';
  if (currentMode === 'mistakes') return 'Разбор ошибок';
  return 'Свободный режим';
}

function sourceLabel(source) {
  const normalized = String(source || 'mixed').toLowerCase();
  if (normalized === 'fipi') return 'ФИПИ';
  if (normalized === 'reshu') return 'Решу ЕГЭ';
  if (normalized === 'author') return 'Авторское';
  return 'Смешанный';
}

function isImagePath(path) {
  return /\.(png|jpe?g|gif|webp|svg)$/i.test(String(path || ''));
}

function ChoiceButton({ active, label, leading, onClick }) {
  return (
    <button className={`choice-option ${active ? 'active' : ''}`} onClick={onClick}>
      <div className="choice-option-row">
        <span className="choice-option-mark">{leading}</span>
        <div className="choice-option-body">{label}</div>
      </div>
    </button>
  );
}

function TestsList({ testResults }) {
  if (!Array.isArray(testResults) || testResults.length === 0) return null;
  return (
    <div className="card-elevated" style={{ marginTop: 14 }}>
      <div className="info-label">Результаты тестов</div>
      <div className="table-like-list" style={{ marginTop: 10 }}>
        {testResults.map((test) => (
          <div key={`test-${test.test_number}`} className="table-like-row" style={{ gridTemplateColumns: '96px minmax(0, 1fr) 1fr 1fr' }}>
            <div className={`badge ${test.passed ? 'badge-success' : 'badge-danger'}`}>Тест {test.test_number}</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{test.passed ? 'верно' : 'неверно'}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Ожидалось: <code>{String(test.expected || '')}</code></div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Получено: <code>{String(test.actual || '')}</code></div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ExerciseCard({
  exercise,
  currentMode,
  onNext,
  theoryLink,
  onRefreshProgress,
  editorFontSize = 14,
  exerciseIndex = 0,
  totalExercises = 1,
  strictSequence = false,
}) {
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [multiAnswers, setMultiAnswers] = useState([]);
  const [numberAnswer, setNumberAnswer] = useState('');
  const [code, setCode] = useState(exercise.code_template || '');
  const [stdinPath, setStdinPath] = useState(Array.isArray(exercise.files) && exercise.files.length > 0 ? String(exercise.files[0]) : '');
  const [result, setResult] = useState(null);
  const [output, setOutput] = useState(null);
  const [checking, setChecking] = useState(false);
  const [running, setRunning] = useState(false);
  const [attemptCount, setAttemptCount] = useState(0);
  const [imageModal, setImageModal] = useState(null);
  const [loadingPrevious, setLoadingPrevious] = useState(false);

  const draftReady = useRef(false);
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
      setAttemptCount(0);
      setStdinPath(Array.isArray(exercise.files) && exercise.files.length > 0 ? String(exercise.files[0]) : '');
      draftReady.current = false;

      try {
        const response = await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`);
        if (!response.ok) {
          draftReady.current = true;
          return;
        }
        const draft = await response.json();
        if (cancelled) return;
        const payload = draft?.payload || {};
        setSelectedAnswer(payload.selectedAnswer ?? null);
        setMultiAnswers(Array.isArray(payload.multiAnswers) ? payload.multiAnswers : []);
        setNumberAnswer(payload.numberAnswer ?? '');
        setCode(payload.code ?? (exercise.code_template || ''));
        setStdinPath(payload.stdinPath ?? (Array.isArray(exercise.files) && exercise.files.length > 0 ? String(exercise.files[0]) : ''));
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) draftReady.current = true;
      }
    }
    loadDraft();
    return () => {
      cancelled = true;
    };
  }, [draftScope, exercise.code_template, exercise.files]);

  useEffect(() => {
    if (!draftReady.current) return undefined;
    const timer = setTimeout(async () => {
      try {
        await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            draft_type: 'practice',
            task_number: exercise.task_number,
            exercise_id: exercise.exercise_id,
            payload: { selectedAnswer, multiAnswers, numberAnswer, code, stdinPath },
          }),
        });
      } catch (error) {
        console.error(error);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [code, draftScope, exercise.exercise_id, exercise.task_number, multiAnswers, numberAnswer, selectedAnswer, stdinPath]);

  const canSubmit = useMemo(() => {
    if (isCode) return Boolean(code.trim());
    if (answerType === 'single_choice') return Boolean(selectedAnswer);
    if (answerType === 'multiple_choice') return multiAnswers.length > 0;
    if (answerType === 'number') return numberAnswer !== '';
    return false;
  }, [answerType, code, isCode, multiAnswers, numberAnswer, selectedAnswer]);

  const isResolved = Boolean(result?.correct || result?.reveal_solution);

  const toggleMulti = (value) => {
    setMultiAnswers((prev) => (prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value]));
  };

  const submitPayload = () => {
    if (isCode) {
      return {
        endpoint: `${API}/api/code/check`,
        body: {
          exercise_id: exercise.exercise_id,
          code,
          attempt_count: attemptCount + 1,
        },
      };
    }

    let answer = selectedAnswer;
    if (answerType === 'multiple_choice') answer = multiAnswers;
    if (answerType === 'number') answer = numberAnswer;

    return {
      endpoint: `${API}/api/exercises/check`,
      body: {
        exercise_id: exercise.exercise_id,
        answer,
        attempt_count: attemptCount + 1,
      },
    };
  };

  const handleCheck = async () => {
    if (!canSubmit) return;
    setChecking(true);
    try {
      const request = submitPayload();
      const response = await fetch(request.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request.body),
      });
      const data = await response.json();
      setResult(data);
      setAttemptCount((prev) => prev + 1);
      await onRefreshProgress?.();
    } catch (error) {
      console.error(error);
    } finally {
      setChecking(false);
    }
  };

  const handleRunCode = async () => {
    if (!isCode) return;
    setRunning(true);
    try {
      const payload = { code };
      if (stdinPath) payload.stdin_path = stdinPath;
      const response = await fetch(`${API}/api/code/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
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
    setAttemptCount(0);
    setStdinPath(Array.isArray(exercise.files) && exercise.files.length > 0 ? String(exercise.files[0]) : '');
    try {
      await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, { method: 'DELETE' });
    } catch (error) {
      console.error(error);
    }
  };

  const loadPreviousCode = async () => {
    if (!isCode) return;
    setLoadingPrevious(true);
    try {
      const response = await fetch(`${API}/api/attempts/exercise/${encodeURIComponent(exercise.exercise_id)}?limit=15`);
      const attempts = await response.json();
      const latestCodeAttempt = (Array.isArray(attempts) ? attempts : []).find((item) => typeof item?.submitted_code === 'string' && item.submitted_code.trim());
      if (latestCodeAttempt?.submitted_code) {
        setCode(latestCodeAttempt.submitted_code);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingPrevious(false);
    }
  };

  const nextLabel = strictSequence
    ? isResolved ? 'Следующее' : 'Решите текущий шаг'
    : 'Следующее';

  const nextDisabled = strictSequence ? !isResolved : false;

  return (
    <div className="card fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 14, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 280 }}>
          <div className="task-chip-row">
            <span className="badge badge-accent">№{exercise.task_number}</span>
            <span className={`badge ${exercise.exercise_mode === 'prototype' ? 'badge-warning' : 'badge-success'}`}>
              {exercise.exercise_mode === 'prototype' ? 'Прототип' : 'Обучающее'}
            </span>
            <span className="badge badge-muted">{sourceLabel(exercise.source)}</span>
            {isCode ? <span className="badge badge-accent">Python</span> : null}
            {isCode ? <span className="badge badge-muted">{exercise.code_step || 'full_code'}</span> : null}
            <span className="badge badge-muted">{modeLabel(currentMode)}</span>
          </div>
          <div style={{ marginTop: 14 }} className="section-title">{exercise.title}</div>
          <div style={{ marginTop: 10, fontSize: 14, lineHeight: 1.8, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>{exercise.text}</div>
        </div>

        <div style={{ width: 220, maxWidth: '100%' }}>
          <div className="card-elevated">
            <div className="info-label">Позиция в уроке</div>
            <div className="info-value">{exerciseIndex + 1} / {totalExercises}</div>
            <div style={{ marginTop: 8, fontSize: 12, lineHeight: 1.6, color: 'var(--text-secondary)' }}>Черновик сохраняется локально автоматически.</div>
          </div>
        </div>
      </div>

      {Array.isArray(exercise.media) && exercise.media.length > 0 ? (
        <div className="card-elevated" style={{ marginTop: 16 }}>
          <div className="info-label">Материалы задания</div>
          <div className="media-grid" style={{ marginTop: 10 }}>
            {exercise.media.map((mediaPath) => {
              const image = isImagePath(mediaPath);
              const href = `${API}/api/content/file?path=${encodeURIComponent(mediaPath)}`;
              return (
                <div key={`media-${mediaPath}`} className="media-item">
                  {image ? (
                    <img src={href} alt={mediaPath} className="media-thumb" onClick={() => setImageModal(href)} />
                  ) : (
                    <div className="media-placeholder">{String(mediaPath).split('/').pop()}</div>
                  )}
                  <div className="row-actions" style={{ marginTop: 8 }}>
                    {image ? <button className="btn btn-ghost btn-sm" onClick={() => setImageModal(href)}>Увеличить</button> : null}
                    <a className="btn btn-ghost btn-sm" href={`${href}&download=true`} target="_blank" rel="noreferrer">Скачать</a>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}

      {Array.isArray(exercise.files) && exercise.files.length > 0 ? (
        <div className="card-elevated" style={{ marginTop: 14 }}>
          <div className="info-label">Файлы задания</div>
          <div className="row-actions" style={{ marginTop: 10 }}>
            {exercise.files.map((filePath) => (
              <a key={`file-${filePath}`} className="btn btn-ghost btn-sm" href={`${API}/api/content/file?path=${encodeURIComponent(filePath)}&download=true`} target="_blank" rel="noreferrer">
                Скачать {String(filePath).split('/').pop()}
              </a>
            ))}
          </div>
        </div>
      ) : null}

      {isCode ? (
        <div style={{ marginTop: 20 }}>
          <div style={{ border: '1px solid var(--border)', borderRadius: 18, overflow: 'hidden' }}>
            <Editor
              height="320px"
              language="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                fontSize: editorFontSize,
                minimap: { enabled: false },
                wordWrap: 'on',
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                padding: { top: 14 },
              }}
            />
          </div>

          {Array.isArray(exercise.files) && exercise.files.length > 0 ? (
            <div style={{ marginTop: 12, maxWidth: 420 }}>
              <label className="info-label">Файл для stdin в раннере</label>
              <select className="input" value={stdinPath} onChange={(event) => setStdinPath(event.target.value)}>
                <option value="">Без файла</option>
                {exercise.files.map((filePath) => (
                  <option key={`stdin-${filePath}`} value={filePath}>{filePath}</option>
                ))}
              </select>
            </div>
          ) : null}

          <div className="exercise-toolbar" style={{ marginTop: 14 }}>
            <button className="btn btn-secondary btn-sm" onClick={handleRunCode} disabled={running}>{running ? 'Запуск...' : 'Запустить код'}</button>
            <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking || !canSubmit}>{checking ? 'Проверка...' : 'Проверить решение'}</button>
            <button className="btn btn-ghost btn-sm" onClick={loadPreviousCode} disabled={loadingPrevious}>{loadingPrevious ? 'Загрузка...' : 'Показать прошлое решение'}</button>
          </div>

          {output ? (
            <div className="code-block" style={{ marginTop: 14 }}>
              {output.stdout ? <div>stdout: {output.stdout}</div> : null}
              {output.stderr ? <div style={{ color: 'var(--danger)', marginTop: output.stdout ? 10 : 0 }}>stderr: {output.stderr}</div> : null}
            </div>
          ) : null}
        </div>
      ) : answerType === 'single_choice' && exercise.options ? (
        <div className="choice-list" style={{ marginTop: 20 }}>
          {exercise.options.map((option, index) => {
            const optionValue = option.charAt(0);
            return <ChoiceButton key={index} active={selectedAnswer === optionValue} leading={optionValue} label={option} onClick={() => setSelectedAnswer(optionValue)} />;
          })}
        </div>
      ) : answerType === 'multiple_choice' && exercise.options ? (
        <div className="choice-list" style={{ marginTop: 20 }}>
          {exercise.options.map((option, index) => {
            const optionValue = option.charAt(0);
            const active = multiAnswers.includes(optionValue);
            return <ChoiceButton key={index} active={active} leading={active ? '✓' : '+'} label={option} onClick={() => toggleMulti(optionValue)} />;
          })}
        </div>
      ) : answerType === 'number' ? (
        <div style={{ marginTop: 20, maxWidth: 280 }}>
          <input className="input" type="number" value={numberAnswer} onChange={(event) => setNumberAnswer(event.target.value)} placeholder="Введите числовой ответ" />
        </div>
      ) : (
        <div className="status-banner danger" style={{ marginTop: 20 }}>
          Теоретические вопросы в practice принимаются только в объективных форматах (single/multiple/number).
        </div>
      )}

      {result ? (
        <div className={`status-banner ${result.correct ? 'success' : 'danger'}`} style={{ marginTop: 18 }}>
          <div style={{ fontWeight: 780, fontSize: 15 }}>{result.correct ? 'Ответ принят' : (result.reveal_solution ? 'Показываем разбор после 3 ошибок' : 'Нужна доработка')}</div>
          {Array.isArray(result.hints_shown) && result.hints_shown.length > 0 ? (
            <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}>
              {result.hints_shown.map((hint, index) => <div key={`hint-${index}`}>Подсказка {index + 1}: {hint}</div>)}
            </div>
          ) : null}
          {result.hint && (!Array.isArray(result.hints_shown) || result.hints_shown.length === 0) ? (
            <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}><strong>Подсказка:</strong> {result.hint}</div>
          ) : null}
          {result.expected !== undefined && !isCode ? (
            <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Ожидаемый ответ: <strong>{Array.isArray(result.expected) ? result.expected.join(', ') : String(result.expected)}</strong></div>
          ) : null}
          {result.details ? <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap', color: 'var(--text-secondary)' }}>{result.details}</div> : null}
          {result.explanation ? <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}>{result.explanation}</div> : null}
        </div>
      ) : null}

      <TestsList testResults={result?.test_results} />

      <div className="exercise-toolbar" style={{ marginTop: 20 }}>
        {!isCode && answerType !== 'text' ? (
          <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking || !canSubmit}>{checking ? 'Проверка...' : 'Проверить'}</button>
        ) : null}
        <button className="btn btn-ghost btn-sm" onClick={handleReset}>Сбросить</button>
        <button className="btn btn-secondary btn-sm" onClick={() => onNext(result)} disabled={nextDisabled}>{nextLabel}</button>
        <Link to={theoryLink} className="btn btn-ghost btn-sm">К теории</Link>
      </div>

      {imageModal ? (
        <div className="modal-backdrop" onClick={() => setImageModal(null)}>
          <div className="media-modal" onClick={(event) => event.stopPropagation()}>
            <img src={imageModal} alt="media preview" className="media-modal-image" />
            <div className="row-actions" style={{ marginTop: 10 }}>
              <button className="btn btn-secondary btn-sm" onClick={() => setImageModal(null)}>Закрыть</button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default function PracticePage({ profile }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [roadmap, setRoadmap] = useState(null);
  const [progress, setProgress] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [lessonItems, setLessonItems] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [loading, setLoading] = useState(true);
  const [completed, setCompleted] = useState(false);

  const modeFromRoute = normalizeMode(searchParams.get('mode'), profile?.learning_mode === 'guided' ? 'guided' : 'free');
  const taskFromRoute = normalizeTaskNumber(searchParams.get('task'), 1);

  const allowedTasks = useMemo(() => {
    if (!roadmap) return [];
    if (modeFromRoute === 'guided') return roadmap.review_due ? [] : roadmap.current_focus_tasks || [];
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
      const [theoryData, progressData, roadmapData] = await Promise.all([
        theoryRes.json(),
        progressRes.json(),
        roadmapRes.json(),
      ]);
      setTasks(theoryData);
      setProgress(progressData);
      setRoadmap(roadmapData);
    } catch (error) {
      console.error(error);
    }
  };

  const refreshExercises = async () => {
    if (modeFromRoute === 'guided' && roadmap?.review_due) {
      setLessonItems([]);
      setCompleted(false);
      setLoading(false);
      return;
    }
    if (allowedTasks.length === 0 && modeFromRoute !== 'free') {
      setLessonItems([]);
      setCompleted(false);
      setLoading(false);
      return;
    }

    setLoading(true);
    setCompleted(false);
    try {
      const response = await fetch(`${API}/api/exercises/${currentTask}?mode=${modeFromRoute}`);
      const data = await response.json();
      const prepared = (Array.isArray(data) ? data : []).map((exercise, index) => ({
        ...exercise,
        _instance_key: `${exercise.exercise_id}::base::${index}`,
      }));
      setLessonItems(prepared);
      setCurrentIdx(0);
    } catch (error) {
      console.error(error);
      setLessonItems([]);
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentTask, modeFromRoute, roadmap, tasks.length, taskFromRoute, searchParams, setSearchParams]);

  const modeDescription = {
    free: 'Свободная практика: любой номер и независимый темп.',
    guided: roadmap?.review_due
      ? 'Guided path временно закрыт: сначала завершите Weekly Review.'
      : 'Guided path: задания идут последовательно, без ручных перескоков внутри урока.',
    weak: 'Слабые темы: акцент на заданиях с просевшей точностью.',
    mistakes: 'Режим ошибок: повтор по темам с недавними неверными попытками.',
  };

  const freeUnlocked = (roadmap?.summary?.coverage || 0) >= 35 || profile?.learning_mode === 'free';

  const handleModeChange = (nextMode) => {
    if (nextMode === 'free' && !freeUnlocked) {
      window.alert('Свободный режим откроется после прохождения базового сегмента дорожки (35%).');
      return;
    }
    const fallbackTask = nextMode === 'guided'
      ? roadmap?.current_focus_tasks?.[0] || 1
      : nextMode === 'weak'
        ? roadmap?.weak_tasks?.[0] || 1
        : nextMode === 'mistakes'
          ? roadmap?.mistake_tasks?.[0] || 1
          : currentTask;
    setSearchParams({ task: String(fallbackTask), mode: nextMode });
  };

  const taskMap = useMemo(() => {
    const map = {};
    tasks.forEach((task) => { map[task.task_number] = task; });
    return map;
  }, [tasks]);

  const progressMap = useMemo(() => {
    const map = {};
    (progress?.tasks || []).forEach((task) => { map[task.task_number] = task; });
    return map;
  }, [progress]);

  const currentExercise = lessonItems[currentIdx] || null;
  const strictSequence = modeFromRoute !== 'free';
  const editorFontSize = profile?.font_size || 14;

  const handleExerciseNext = (result) => {
    if (strictSequence && !(result?.correct || result?.reveal_solution)) {
      return;
    }

    if (result?.should_retry_in_lesson_end && currentExercise) {
      setLessonItems((prev) => {
        const alreadyQueued = prev.some((item) => item._retry_for === currentExercise.exercise_id);
        if (alreadyQueued) return prev;
        return [
          ...prev,
          {
            ...currentExercise,
            _instance_key: `${currentExercise.exercise_id}::retry`,
            _retry_for: currentExercise.exercise_id,
            title: `${currentExercise.title} (повтор в конце урока)`,
          },
        ];
      });
    }

    if (currentIdx + 1 < lessonItems.length) {
      setCurrentIdx((prev) => prev + 1);
      return;
    }

    setCompleted(true);
  };

  return (
    <div className="page-shell page-shell-wide fade-in">
      <div className="page-columns">
        <aside className="left-rail-card">
          <div className="card">
            <div className="eyebrow">Навигация по заданиям</div>
            <div className="section-title">Практика</div>
            <div className="section-description">{modeDescription[modeFromRoute]}</div>
            <div className="info-grid" style={{ marginTop: 16 }}>
              <div className="info-card"><div className="info-label">Режим</div><div className="info-value" style={{ fontSize: 16 }}>{modeLabel(modeFromRoute)}</div></div>
              <div className="info-card"><div className="info-label">Доступно задач</div><div className="info-value">{allowedTasks.length || 27}</div></div>
            </div>
          </div>

          <div className="card">
            <div className="task-nav-list">
              {(allowedTasks.length > 0 ? allowedTasks : Array.from({ length: 27 }, (_, index) => index + 1)).map((taskNumber) => {
                const taskInfo = taskMap[taskNumber];
                const taskProgress = progressMap[taskNumber] || {};
                const active = taskNumber === currentTask;
                return (
                  <button key={taskNumber} onClick={() => setSearchParams({ task: String(taskNumber), mode: modeFromRoute })} className={`task-nav-button ${active ? 'active' : ''}`}>
                    <span className="task-nav-index">{taskNumber}</span>
                    <span className="task-nav-title">{taskInfo?.title || `Задание ${taskNumber}`}</span>
                    {taskProgress.total_attempts > 0 ? (
                      <span className={`badge ${taskProgress.accuracy >= 80 ? 'badge-success' : taskProgress.accuracy >= 60 ? 'badge-accent' : 'badge-warning'}`}>
                        {taskProgress.accuracy?.toFixed?.(0) || 0}%
                      </span>
                    ) : null}
                  </button>
                );
              })}
            </div>
          </div>
        </aside>

        <section className="page-stack">
          <div className="hero-card dashboard-hero">
            <div className="eyebrow">Режим работы</div>
            <div className="hero-title">Практика по заданиям</div>
            <div className="hero-description">{modeDescription[modeFromRoute]}</div>
            <div className="row-actions" style={{ marginTop: 18 }}>
              <div className="segment-control">
                <button className={`segment-btn ${modeFromRoute === 'free' ? 'active' : ''}`} onClick={() => handleModeChange('free')}>Свободный</button>
                <button className={`segment-btn ${modeFromRoute === 'guided' ? 'active' : ''}`} onClick={() => handleModeChange('guided')}>Guided</button>
                <button className={`segment-btn ${modeFromRoute === 'weak' ? 'active' : ''}`} onClick={() => handleModeChange('weak')}>Слабые темы</button>
                <button className={`segment-btn ${modeFromRoute === 'mistakes' ? 'active' : ''}`} onClick={() => handleModeChange('mistakes')}>Ошибки</button>
              </div>
            </div>
            <div className="task-chip-row" style={{ marginTop: 16 }}>
              {!freeUnlocked ? <span className="badge badge-warning">Свободный режим откроется после 35% дорожки</span> : null}
              {modeFromRoute === 'guided' && roadmap?.current_focus_tasks?.length > 0 ? <span className="badge badge-accent">Фокус этапа: {roadmap.current_focus_tasks.map((task) => `№${task}`).join(', ')}</span> : null}
              {lessonItems.length > 0 ? <span className="badge badge-muted">Упражнение {Math.min(currentIdx + 1, lessonItems.length)} из {lessonItems.length}</span> : null}
              {completed ? <span className="badge badge-success">Урок завершён</span> : null}
            </div>
          </div>

          {modeFromRoute === 'guided' && roadmap?.review_due ? (
            <div className="state-card">
              <div className="state-title">Guided path временно закрыт checkpoint-блоком</div>
              <div className="state-description">Сначала завершите Weekly Review. После этого guided practice снова откроется.</div>
              <div className="state-actions"><Link className="btn btn-primary btn-sm" to="/weekly-review">Перейти в Weekly Review</Link></div>
            </div>
          ) : loading ? (
            <div className="state-card loading-shimmer">
              <div className="state-title">Загрузка упражнений</div>
              <div className="state-description">Подбираем локальный набор практики по выбранному номеру.</div>
            </div>
          ) : lessonItems.length === 0 ? (
            <div className="state-card">
              <div className="state-title">Пока нет подходящих упражнений</div>
              <div className="state-description">Для выбранного режима пока не найдено упражнений в локальном банке.</div>
              <div className="state-actions">
                <Link className="btn btn-secondary btn-sm" to={`/theory?task=${currentTask}`}>Открыть теорию</Link>
                <Link className="btn btn-ghost btn-sm" to="/task-bank">Перейти в банк задач</Link>
              </div>
            </div>
          ) : completed ? (
            <div className="state-card">
              <div className="state-title">Урок завершён</div>
              <div className="state-description">Можно перейти к следующему номеру или повторить этот урок ещё раз.</div>
              <div className="state-actions">
                <button className="btn btn-primary btn-sm" onClick={() => refreshExercises()}>Пройти снова</button>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => {
                    const taskPool = allowedTasks.length > 0 ? allowedTasks : Array.from({ length: 27 }, (_, index) => index + 1);
                    const nextTask = taskPool[(taskPool.indexOf(currentTask) + 1) % taskPool.length] || 1;
                    setSearchParams({ task: String(nextTask), mode: modeFromRoute });
                  }}
                >
                  Следующее задание
                </button>
              </div>
            </div>
          ) : (
            <ExerciseCard
              key={currentExercise._instance_key || `${currentExercise.exercise_id}-${currentIdx}`}
              exercise={currentExercise}
              currentMode={modeFromRoute}
              theoryLink={`/theory?task=${currentTask}`}
              onNext={handleExerciseNext}
              onRefreshProgress={refreshAll}
              editorFontSize={editorFontSize}
              exerciseIndex={currentIdx}
              totalExercises={lessonItems.length}
              strictSequence={strictSequence}
            />
          )}
        </section>
      </div>
    </div>
  );
}
