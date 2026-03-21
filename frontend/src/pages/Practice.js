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
  if (currentMode === 'mistakes') return 'Работа над ошибками';
  return 'Свободный режим';
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

function ExerciseCard({ exercise, currentMode, onNext, theoryLink, onRefreshProgress, editorFontSize = 14, exerciseIndex = 0, totalExercises = 1 }) {
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
      setSelectedAnswer(null); setMultiAnswers([]); setNumberAnswer(''); setCode(exercise.code_template || '');
      setResult(null); setOutput(null); setHintIdx(-1); setDraftReady(false); isFirstAutosave.current = true;
      try {
        const response = await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`);
        if (!response.ok) { setDraftReady(true); return; }
        const draft = await response.json();
        if (cancelled) return;
        const payload = draft?.payload || {};
        setSelectedAnswer(payload.selectedAnswer ?? null);
        setMultiAnswers(Array.isArray(payload.multiAnswers) ? payload.multiAnswers : []);
        setNumberAnswer(payload.numberAnswer ?? '');
        setCode(payload.code ?? (exercise.code_template || ''));
      } catch (error) { console.error(error); } finally { if (!cancelled) setDraftReady(true); }
    }
    loadDraft();
    return () => { cancelled = true; };
  }, [draftScope, exercise.code_template]);

  useEffect(() => {
    if (!draftReady) return undefined;
    if (isFirstAutosave.current) { isFirstAutosave.current = false; return undefined; }
    const timer = setTimeout(async () => {
      try {
        await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            draft_type: 'practice',
            task_number: exercise.task_number,
            exercise_id: exercise.exercise_id,
            payload: { selectedAnswer, multiAnswers, numberAnswer, code },
          }),
        });
      } catch (error) { console.error(error); }
    }, 350);
    return () => clearTimeout(timer);
  }, [code, draftReady, draftScope, exercise.exercise_id, exercise.task_number, multiAnswers, numberAnswer, selectedAnswer]);

  const toggleMulti = (value) => {
    setMultiAnswers((prev) => (prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value]));
  };

  const handleCheck = async () => {
    setChecking(true);
    try {
      if (isCode) {
        const response = await fetch(`${API}/api/code/check`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, code }),
        });
        setResult(await response.json());
      } else {
        let answer = selectedAnswer;
        if (answerType === 'multiple_choice') answer = multiAnswers;
        if (answerType === 'number') answer = numberAnswer;
        const response = await fetch(`${API}/api/exercises/check`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, answer }),
        });
        setResult(await response.json());
      }
      await onRefreshProgress?.();
    } catch (error) { console.error(error); } finally { setChecking(false); }
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      const response = await fetch(`${API}/api/code/run`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, stdin: '' }),
      });
      setOutput(await response.json());
    } catch (error) { console.error(error); } finally { setRunning(false); }
  };

  const handleReset = async () => {
    setSelectedAnswer(null); setMultiAnswers([]); setNumberAnswer(''); setCode(exercise.code_template || '');
    setResult(null); setOutput(null); setHintIdx(-1); isFirstAutosave.current = true;
    try { await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`, { method: 'DELETE' }); } catch (error) { console.error(error); } finally { setDraftReady(true); }
  };

  const selectedSummary = useMemo(() => {
    if (isCode) return code.trim() ? 'Код введён' : 'Черновик пока пуст';
    if (answerType === 'multiple_choice') return multiAnswers.length > 0 ? multiAnswers.join(', ') : 'Не выбрано';
    if (answerType === 'number') return numberAnswer || 'Не введено';
    return selectedAnswer || 'Не выбрано';
  }, [answerType, code, isCode, multiAnswers, numberAnswer, selectedAnswer]);

  return (
    <div className="card fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 14, alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 280 }}>
          <div className="task-chip-row">
            <span className="badge badge-accent">№{exercise.task_number}</span>
            <span className={`badge ${exercise.difficulty === 'hard' ? 'badge-danger' : exercise.difficulty === 'medium' ? 'badge-warning' : 'badge-success'}`}>{exercise.difficulty === 'hard' ? 'Сложное' : exercise.difficulty === 'medium' ? 'Среднее' : 'Базовое'}</span>
            {isCode ? <span className="badge badge-accent">Python</span> : null}
            <span className="badge badge-muted">{modeLabel(currentMode)}</span>
          </div>
          <div style={{ marginTop: 14 }} className="section-title">{exercise.title}</div>
          <div style={{ marginTop: 10, fontSize: 14, lineHeight: 1.8, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>{exercise.text}</div>
        </div>
        <div style={{ width: 220, maxWidth: '100%' }}>
          <div className="card-elevated">
            <div className="info-label">Позиция в наборе</div>
            <div className="info-value">{exerciseIndex + 1} / {totalExercises}</div>
            <div style={{ marginTop: 8, fontSize: 12, lineHeight: 1.6, color: 'var(--text-secondary)' }}>Черновик сохраняется локально автоматически.</div>
          </div>
        </div>
      </div>

      {isCode ? (
        <div style={{ marginTop: 20 }}>
          <div style={{ border: '1px solid var(--border)', borderRadius: 18, overflow: 'hidden' }}>
            <Editor
              height="320px"
              language="python"
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{ fontSize: editorFontSize, minimap: { enabled: false }, wordWrap: 'on', lineNumbers: 'on', scrollBeyondLastLine: false, automaticLayout: true, padding: { top: 14 } }}
            />
          </div>
          <div className="exercise-toolbar" style={{ marginTop: 14 }}>
            <button className="btn btn-secondary btn-sm" onClick={handleRun} disabled={running}>{running ? 'Выполняется…' : 'Запустить код'}</button>
            <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking || !code.trim()}>{checking ? 'Проверка…' : 'Проверить решение'}</button>
          </div>
          {output ? <div className="code-block" style={{ marginTop: 14 }}>{output.stdout ? <div>stdout: {output.stdout}</div> : null}{output.stderr ? <div style={{ color: 'var(--danger)', marginTop: output.stdout ? 10 : 0 }}>stderr: {output.stderr}</div> : null}</div> : null}
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
        <div className="status-banner danger" style={{ marginTop: 20 }}>Теоретические ручные ответы отключены продуктовой логикой. Для этого упражнения нужен объективный формат.</div>
      )}

      <div className="info-grid" style={{ marginTop: 18 }}>
        <div className="info-card"><div className="info-label">Текущее состояние ответа</div><div className="info-value" style={{ fontSize: 16 }}>{selectedSummary}</div></div>
        <div className="info-card"><div className="info-label">Подсказки</div><div className="info-value" style={{ fontSize: 16 }}>{exercise.hints?.length ? `${Math.max(hintIdx + 1, 0)} / ${exercise.hints.length}` : 'Нет'}</div></div>
      </div>

      {result ? <div className={`status-banner ${result.correct ? 'success' : 'danger'}`} style={{ marginTop: 18 }}>
        <div style={{ fontWeight: 780, fontSize: 15 }}>{result.correct ? 'Ответ принят' : 'Нужно доработать'}</div>
        {result.explanation ? <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}>{result.explanation}</div> : null}
        {result.details ? <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap', color: 'var(--text-secondary)' }}>{result.details}</div> : null}
        {result.expected !== undefined && !isCode ? <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Ожидаемый ответ: <strong>{Array.isArray(result.expected) ? result.expected.join(', ') : String(result.expected)}</strong></div> : null}
      </div> : null}

      <div className="exercise-toolbar" style={{ marginTop: 20 }}>
        {!isCode && answerType !== 'text' ? <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking || (answerType === 'single_choice' && !selectedAnswer) || (answerType === 'multiple_choice' && multiAnswers.length === 0) || (answerType === 'number' && numberAnswer === '')}>{checking ? 'Проверка…' : 'Проверить'}</button> : null}
        <button className="btn btn-ghost btn-sm" onClick={() => setHintIdx(Math.min(hintIdx + 1, (exercise.hints || []).length - 1))} disabled={!exercise.hints || exercise.hints.length === 0 || hintIdx >= exercise.hints.length - 1}>Подсказка {hintIdx >= 0 ? `(${hintIdx + 1}/${exercise.hints?.length || 0})` : ''}</button>
        <button className="btn btn-ghost btn-sm" onClick={handleReset}>Сбросить</button>
        <button className="btn btn-secondary btn-sm" onClick={onNext}>Следующее</button>
        <Link to={theoryLink} className="btn btn-ghost btn-sm">К теории</Link>
      </div>

      {hintIdx >= 0 && exercise.hints ? <div className="card-elevated surface-accent" style={{ marginTop: 16 }}>
        <div className="info-label">Подсказки</div>
        {exercise.hints.slice(0, hintIdx + 1).map((hint, index) => <div key={index} style={{ marginTop: index === 0 ? 10 : 8, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}>Подсказка {index + 1}: {hint}</div>)}
      </div> : null}
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
      const [theoryRes, progressRes, roadmapRes] = await Promise.all([fetch(`${API}/api/theory`), fetch(`${API}/api/progress`), fetch(`${API}/api/roadmap`)]);
      const [theoryData, progressData, roadmapData] = await Promise.all([theoryRes.json(), progressRes.json(), roadmapRes.json()]);
      setTasks(theoryData); setProgress(progressData); setRoadmap(roadmapData);
    } catch (error) { console.error(error); }
  };

  const refreshExercises = async () => {
    if (modeFromRoute === 'guided' && roadmap?.review_due) { setExercises([]); setLoading(false); return; }
    if (allowedTasks.length === 0 && modeFromRoute !== 'free') { setExercises([]); setLoading(false); return; }
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/exercises/${currentTask}?mode=${modeFromRoute}`);
      const data = await response.json();
      setExercises(data); setCurrentIdx(0);
    } catch (error) { console.error(error); setExercises([]); } finally { setLoading(false); }
  };

  useEffect(() => { refreshAll(); }, []);
  useEffect(() => {
    if (!roadmap && !tasks.length) return;
    if (taskFromRoute !== currentTask || normalizeMode(searchParams.get('mode'), modeFromRoute) !== modeFromRoute) {
      setSearchParams({ task: String(currentTask), mode: modeFromRoute });
      return;
    }
    refreshExercises();
  }, [currentTask, modeFromRoute, roadmap, searchParams, setSearchParams, taskFromRoute, tasks.length]);

  const modeDescription = {
    free: 'Свободный режим: можно брать любой номер задания и тренироваться без ограничений.',
    guided: roadmap?.review_due ? 'Guided path временно заблокирован: сначала нужен Weekly Review.' : 'Guided path: доступны только задания текущего этапа, без бессмысленных перескоков.',
    weak: 'Слабые темы: фокус на заданиях с просевшей точностью и нестабильными попытками.',
    mistakes: 'Работа над ошибками: режим для тем, где были последние неверные решения.',
  };

  const handleModeChange = (nextMode) => {
    const fallbackTask = nextMode === 'guided' ? roadmap?.current_focus_tasks?.[0] || 1 : nextMode === 'weak' ? roadmap?.weak_tasks?.[0] || 1 : nextMode === 'mistakes' ? roadmap?.mistake_tasks?.[0] || 1 : currentTask;
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

  const currentExercise = exercises[currentIdx];
  const editorFontSize = profile?.font_size || 14;

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
                    {taskProgress.total_attempts > 0 ? <span className={`badge ${taskProgress.accuracy >= 80 ? 'badge-success' : taskProgress.accuracy >= 60 ? 'badge-accent' : 'badge-warning'}`}>{taskProgress.accuracy?.toFixed?.(0) || 0}%</span> : null}
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
              {modeFromRoute === 'guided' && roadmap?.current_focus_tasks?.length > 0 ? <span className="badge badge-accent">Фокус этапа: {roadmap.current_focus_tasks.map((task) => `№${task}`).join(', ')}</span> : null}
              {modeFromRoute === 'weak' && (roadmap?.weak_tasks?.length || 0) === 0 ? <span className="badge badge-success">Слабых тем по текущим данным нет</span> : null}
              {modeFromRoute === 'mistakes' && (roadmap?.mistake_tasks?.length || 0) === 0 ? <span className="badge badge-success">Недавних ошибок нет</span> : null}
              {exercises.length > 0 ? <span className="badge badge-muted">Упражнение {currentIdx + 1} из {exercises.length}</span> : null}
            </div>
          </div>

          {modeFromRoute === 'guided' && roadmap?.review_due ? (
            <div className="state-card">
              <div className="state-title">Guided path временно закрыт checkpoint’ом</div>
              <div className="state-description">Сначала завершите Weekly Review. После этого guided practice снова откроет задания текущего этапа.</div>
              <div className="state-actions"><Link className="btn btn-primary btn-sm" to="/weekly-review">Перейти в Weekly Review</Link></div>
            </div>
          ) : loading ? (
            <div className="state-card loading-shimmer"><div className="state-title">Загрузка упражнений</div><div className="state-description">Подбираем локальный набор практики по выбранному заданию и режиму.</div></div>
          ) : exercises.length === 0 ? (
            <div className="state-card">
              <div className="state-title">Пока нет подходящих упражнений</div>
              <div className="state-description">{modeFromRoute === 'weak' ? 'Для режима слабых тем пока недостаточно провальных задач.' : modeFromRoute === 'mistakes' ? 'В режиме ошибок пока нет недавних неверных попыток.' : 'Для этого задания пока нет объективных упражнений в локальной базе.'}</div>
              <div className="state-actions">
                <Link className="btn btn-secondary btn-sm" to={`/theory?task=${currentTask}`}>Открыть теорию</Link>
                <Link className="btn btn-ghost btn-sm" to="/progress">Посмотреть аналитику</Link>
              </div>
            </div>
          ) : (
            <ExerciseCard key={currentExercise.exercise_id} exercise={currentExercise} currentMode={modeFromRoute} theoryLink={`/theory?task=${currentTask}`} onNext={() => setCurrentIdx((prev) => (prev + 1) % exercises.length)} onRefreshProgress={refreshAll} editorFontSize={editorFontSize} exerciseIndex={currentIdx} totalExercises={exercises.length} />
          )}
        </section>
      </div>
    </div>
  );
}
