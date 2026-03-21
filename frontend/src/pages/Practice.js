import React, { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';

const API = process.env.REACT_APP_BACKEND_URL;

function normalizeTaskNumber(value, fallback = 1) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 27) return fallback;
  return parsed;
}

function normalizeMode(value) {
  return ['training', 'control', 'weak'].includes(value) ? value : 'training';
}

function ExerciseCard({ exercise, onNext, theoryLink }) {
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
  const atype = exercise.answer_type;
  const draftScope = `practice:${exercise.exercise_id}`;

  useEffect(() => {
    let cancelled = false;

    const loadDraft = async () => {
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
        const res = await fetch(`${API}/api/drafts/${encodeURIComponent(draftScope)}`);
        if (!res.ok) {
          if (res.status !== 404) {
            console.error('Failed to load draft', res.status);
          }
          return;
        }

        const draft = await res.json();
        const payload = draft?.payload || {};
        if (cancelled) return;

        setSelectedAnswer(payload.selectedAnswer ?? null);
        setMultiAnswers(Array.isArray(payload.multiAnswers) ? payload.multiAnswers : []);
        setNumberAnswer(payload.numberAnswer ?? '');
        setCode(payload.code ?? (exercise.code_template || ''));
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) {
          setDraftReady(true);
        }
      }
    };

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
    }, 400);

    return () => clearTimeout(timer);
  }, [code, draftReady, draftScope, exercise.exercise_id, exercise.task_number, multiAnswers, numberAnswer, selectedAnswer]);

  const handleCheck = async () => {
    setChecking(true);
    try {
      if (isCode) {
        const res = await fetch(`${API}/api/code/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, code }),
        });
        setResult(await res.json());
      } else {
        let answer = selectedAnswer;
        if (atype === 'multiple_choice') answer = multiAnswers;
        else if (atype === 'number') answer = numberAnswer;
        const res = await fetch(`${API}/api/exercises/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ exercise_id: exercise.exercise_id, answer }),
        });
        setResult(await res.json());
      }
    } catch (e) {
      console.error(e);
    }
    setChecking(false);
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      const res = await fetch(`${API}/api/code/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, stdin: '' }),
      });
      setOutput(await res.json());
    } catch (e) {
      console.error(e);
    }
    setRunning(false);
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

  const toggleMulti = (opt) => {
    setMultiAnswers(prev => prev.includes(opt) ? prev.filter(x => x !== opt) : [...prev, opt]);
  };

  return (
    <div className="card fade-in" style={{ padding: 24 }} data-testid={`exercise-${exercise.exercise_id}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span className="badge badge-accent">№{exercise.task_number}</span>
        <span className={`badge ${exercise.difficulty === 'easy' ? 'badge-success' : exercise.difficulty === 'hard' ? 'badge-danger' : 'badge-warning'}`}>
          {exercise.difficulty === 'easy' ? 'Лёгкое' : exercise.difficulty === 'hard' ? 'Сложное' : 'Среднее'}
        </span>
        {isCode && <span className="badge badge-accent">Python</span>}
        <span style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: 12 }}>Локальный автосейв</span>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>{exercise.title}</h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 1.7, marginBottom: 20, whiteSpace: 'pre-wrap' }}>{exercise.text}</p>

      {isCode ? (
        <div style={{ marginBottom: 16 }}>
          <div style={{ border: '1px solid var(--border)', borderRadius: 12, overflow: 'hidden' }}>
            <Editor
              height="260px"
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
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button className="btn btn-secondary btn-sm" onClick={handleRun} disabled={running} data-testid="run-code-btn">
              {running ? 'Выполняется...' : 'Запустить код'}
            </button>
            <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking} data-testid="check-code-btn">
              {checking ? 'Проверка...' : 'Проверить решение'}
            </button>
          </div>
          {output && (
            <div className="code-block" style={{ marginTop: 12, fontSize: 13 }}>
              {output.stdout && <div style={{ color: 'var(--text-primary)' }}>Вывод: {output.stdout}</div>}
              {output.stderr && <div style={{ color: 'var(--danger)' }}>Ошибка: {output.stderr}</div>}
              {output.timeout && <div style={{ color: 'var(--warning)' }}>Превышено время выполнения</div>}
            </div>
          )}
        </div>
      ) : atype === 'single_choice' && exercise.options ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
          {exercise.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => setSelectedAnswer(opt.charAt(0))}
              style={{
                padding: '10px 16px', borderRadius: 10, border: '1px solid', textAlign: 'left', cursor: 'pointer', fontSize: 14,
                borderColor: selectedAnswer === opt.charAt(0) ? 'var(--accent)' : 'var(--border)',
                background: selectedAnswer === opt.charAt(0) ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                color: 'var(--text-primary)',
              }}
              data-testid={`option-${i}`}
            >
              {opt}
            </button>
          ))}
        </div>
      ) : atype === 'multiple_choice' && exercise.options ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
          {exercise.options.map((opt, i) => (
            <button
              key={i}
              onClick={() => toggleMulti(opt.charAt(0))}
              style={{
                padding: '10px 16px', borderRadius: 10, border: '1px solid', textAlign: 'left', cursor: 'pointer', fontSize: 14,
                borderColor: multiAnswers.includes(opt.charAt(0)) ? 'var(--accent)' : 'var(--border)',
                background: multiAnswers.includes(opt.charAt(0)) ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                color: 'var(--text-primary)',
              }}
              data-testid={`option-multi-${i}`}
            >
              <span style={{ marginRight: 8 }}>{multiAnswers.includes(opt.charAt(0)) ? '☑' : '☐'}</span>
              {opt}
            </button>
          ))}
        </div>
      ) : (
        <div style={{ marginBottom: 16 }}>
          <input
            className="input"
            type={atype === 'number' ? 'number' : 'text'}
            value={numberAnswer}
            onChange={e => setNumberAnswer(e.target.value)}
            placeholder="Введите ответ"
            style={{ maxWidth: 300 }}
            data-testid="number-answer-input"
          />
        </div>
      )}

      {result && (
        <div
          style={{
            padding: 14,
            borderRadius: 12,
            marginBottom: 16,
            background: result.correct || result.passed ? 'rgba(92,184,122,0.08)' : 'rgba(224,96,112,0.08)',
            border: `1px solid ${result.correct || result.passed ? 'var(--success)' : 'var(--danger)'}`,
          }}
          data-testid="exercise-result"
        >
          <div style={{ fontWeight: 600, fontSize: 14, color: result.correct || result.passed ? 'var(--success)' : 'var(--danger)', marginBottom: 4 }}>
            {result.correct || result.passed ? 'Правильно!' : 'Неправильно'}
          </div>
          {result.feedback && <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>{result.feedback}</div>}
          {result.explanation && <div style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 6 }}>{result.explanation}</div>}
          {result.test_results && result.test_results.length > 0 && (
            <div style={{ marginTop: 8 }}>
              {result.test_results.filter(t => t.is_public).map((t, i) => (
                <div key={i} style={{ fontSize: 12, color: t.passed ? 'var(--success)' : 'var(--danger)', marginTop: 4 }}>
                  Тест {t.test_number}: {t.passed ? 'пройден' : `ожидалось "${t.expected}", получено "${t.actual}"`}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        {!isCode && !result && (
          <button
            className="btn btn-primary btn-sm"
            onClick={handleCheck}
            disabled={checking || (atype === 'single_choice' && !selectedAnswer) || (atype === 'number' && !numberAnswer)}
            data-testid="check-answer-btn"
          >
            {checking ? 'Проверка...' : 'Проверить ответ'}
          </button>
        )}
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => setHintIdx(Math.min(hintIdx + 1, (exercise.hints || []).length - 1))}
          disabled={!exercise.hints || exercise.hints.length === 0 || hintIdx >= exercise.hints.length - 1}
          data-testid="hint-btn"
        >
          Подсказка {hintIdx >= 0 ? `(${hintIdx + 1}/${exercise.hints?.length || 0})` : ''}
        </button>
        <button className="btn btn-ghost btn-sm" onClick={handleReset} data-testid="reset-btn">Сбросить</button>
        <button className="btn btn-secondary btn-sm" onClick={onNext} style={{ marginLeft: 'auto' }} data-testid="next-exercise-btn">Следующее</button>
        <Link to={theoryLink} className="btn btn-ghost btn-sm">К теории</Link>
      </div>

      {hintIdx >= 0 && exercise.hints && (
        <div style={{ marginTop: 12, padding: 12, background: 'rgba(108,127,216,0.06)', borderRadius: 10, border: '1px solid rgba(108,127,216,0.15)' }}>
          {exercise.hints.slice(0, hintIdx + 1).map((hint, index) => (
            <div key={index} style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: index > 0 ? 6 : 0 }}>
              Подсказка {index + 1}: {hint}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function PracticePage() {
  const [taskNumber, setTaskNumber] = useState(1);
  const [exercises, setExercises] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState([]);
  const [mode, setMode] = useState('training');
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    const nextTask = normalizeTaskNumber(searchParams.get('task'), 1);
    const nextMode = normalizeMode(searchParams.get('mode'));
    setTaskNumber(nextTask);
    setMode(nextMode);
  }, [searchParams]);

  useEffect(() => {
    fetch(`${API}/api/theory`).then(r => r.json()).then(setTasks).catch(() => {});
    fetch(`${API}/api/progress`).then(r => r.json()).then(data => setProgress(data.tasks || [])).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);

    const load = async () => {
      try {
        if (mode === 'weak') {
          const weakTasks = (progress || [])
            .filter(item => (item.accuracy || 0) < 60 && (item.total_attempts || 0) >= 3)
            .map(item => item.task_number);
          const fallbackTask = weakTasks[0] || taskNumber;
          const targetTask = weakTasks.includes(taskNumber) ? taskNumber : fallbackTask;
          if (targetTask !== taskNumber) {
            setSearchParams({ task: String(targetTask), mode: 'weak' });
            return;
          }
        }

        const response = await fetch(`${API}/api/exercises/${taskNumber}`);
        let data = await response.json();

        if (mode === 'control') {
          const sorted = [...data].sort((a, b) => {
            const diffOrder = { easy: 0, medium: 1, hard: 2 };
            return (diffOrder[a.difficulty] ?? 1) - (diffOrder[b.difficulty] ?? 1);
          });
          data = sorted.slice(0, Math.min(sorted.length, 5));
        }

        setExercises(data);
        setCurrentIdx(0);
      } catch (error) {
        console.error(error);
      }
      setLoading(false);
    };

    if (progress.length > 0 || mode !== 'weak') {
      load();
    } else {
      setLoading(false);
    }
  }, [taskNumber, mode, progress, setSearchParams]);

  const handleNext = () => {
    if (currentIdx < exercises.length - 1) setCurrentIdx(currentIdx + 1);
    else setCurrentIdx(0);
  };

  const updateRoute = (nextTask, nextMode = mode) => {
    setSearchParams({ task: String(nextTask), mode: nextMode });
  };

  const weakTaskNumbers = (progress || [])
    .filter(item => (item.accuracy || 0) < 60 && (item.total_attempts || 0) >= 3)
    .map(item => item.task_number);

  return (
    <div className="fade-in" style={{ display: 'flex', gap: 20, height: 'calc(100vh - 104px)' }}>
      <div style={{ width: 200, minWidth: 200, overflowY: 'auto' }} data-testid="practice-task-list">
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 12 }}>Задание</div>
        {(tasks.length > 0 ? tasks : Array.from({ length: 27 }, (_, i) => ({ task_number: i + 1, title: `№${i + 1}` }))).map(t => {
          const isWeak = weakTaskNumbers.includes(t.task_number);
          return (
            <button
              key={t.task_number}
              onClick={() => updateRoute(t.task_number)}
              className={`nav-item ${taskNumber === t.task_number ? 'active' : ''}`}
              style={{ width: '100%', textAlign: 'left', border: 'none', fontSize: 13 }}
              data-testid={`practice-task-${t.task_number}`}
            >
              <span style={{
                width: 22, height: 22, borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 600,
                background: taskNumber === t.task_number ? 'var(--accent)' : 'var(--bg-elevated)',
                color: taskNumber === t.task_number ? 'white' : 'var(--text-secondary)', flexShrink: 0,
              }}>{t.task_number}</span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.title || `Задание ${t.task_number}`}</span>
              {isWeak && <span className="badge badge-danger" style={{ marginLeft: 'auto', fontSize: 10 }}>weak</span>}
            </button>
          );
        })}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
          <div className="segment-control" data-testid="practice-mode">
            {[{ v: 'training', l: 'Тренировка' }, { v: 'control', l: 'Контроль' }, { v: 'weak', l: 'Слабые места' }].map(item => (
              <button
                key={item.v}
                className={`segment-btn ${mode === item.v ? 'active' : ''}`}
                onClick={() => updateRoute(taskNumber, item.v)}
                data-testid={`mode-${item.v}`}
              >
                {item.l}
              </button>
            ))}
          </div>
          {mode === 'control' && <span style={{ color: 'var(--warning)', fontSize: 13 }}>Контроль: показываем до 5 заданий по номеру, отсортированных по сложности.</span>}
          {mode === 'weak' && <span style={{ color: 'var(--danger)', fontSize: 13 }}>Режим слабых мест фокусируется на темах с точностью ниже 60% после 3+ попыток.</span>}
          {exercises.length > 0 && (
            <span style={{ color: 'var(--text-muted)', fontSize: 13 }}>
              Задание {currentIdx + 1} из {exercises.length}
            </span>
          )}
        </div>

        {loading ? (
          <div style={{ color: 'var(--text-muted)', padding: 40, textAlign: 'center' }}>Загрузка заданий...</div>
        ) : exercises.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <div style={{ fontSize: 15, color: 'var(--text-secondary)' }}>
              {mode === 'weak'
                ? 'Пока нет слабых мест по заданию правил режима. Сначала накопите хотя бы 3 попытки с точностью ниже 60%.'
                : 'Задания для этого номера пока не добавлены'}
            </div>
            <Link to={`/theory?task=${taskNumber}`} className="btn btn-secondary btn-sm" style={{ marginTop: 16 }}>Изучить теорию</Link>
          </div>
        ) : (
          <ExerciseCard
            key={exercises[currentIdx]?.exercise_id}
            exercise={exercises[currentIdx]}
            onNext={handleNext}
            theoryLink={`/theory?task=${taskNumber}`}
          />
        )}
      </div>
    </div>
  );
}
