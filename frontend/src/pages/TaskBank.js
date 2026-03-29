import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import API from '../config/api';

function normalizeTaskNumber(value, fallback = 1) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 27) return fallback;
  return parsed;
}

function sourceLabel(source) {
  const normalized = String(source || 'mixed').toLowerCase();
  if (normalized === 'fipi') return 'ФИПИ';
  if (normalized === 'reshu') return 'Решу ЕГЭ';
  if (normalized === 'author') return 'Авторское';
  return 'Смешанный';
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

export default function TaskBankPage({ profile }) {
  const [summary, setSummary] = useState(null);
  const [selectedTask, setSelectedTask] = useState(1);
  const [bankMode, setBankMode] = useState('any');
  const [exercise, setExercise] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingExercise, setLoadingExercise] = useState(false);

  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [multiAnswers, setMultiAnswers] = useState([]);
  const [numberAnswer, setNumberAnswer] = useState('');
  const [code, setCode] = useState('');
  const [stdinPath, setStdinPath] = useState('');
  const [result, setResult] = useState(null);
  const [runResult, setRunResult] = useState(null);
  const [attemptCount, setAttemptCount] = useState(0);
  const [checking, setChecking] = useState(false);
  const [running, setRunning] = useState(false);

  const editorFontSize = profile?.font_size || 14;

  const loadSummary = async () => {
    setLoadingSummary(true);
    try {
      const response = await fetch(`${API}/api/task-bank/summary`);
      const data = await response.json();
      setSummary(data);
      if (Array.isArray(data?.tasks) && data.tasks.length > 0) {
        setSelectedTask((prev) => normalizeTaskNumber(prev, data.tasks[0].task_number));
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoadingSummary(false);
    }
  };

  const loadExercise = async (taskNumber = selectedTask, mode = bankMode) => {
    setLoadingExercise(true);
    setResult(null);
    setRunResult(null);
    setAttemptCount(0);
    try {
      const response = await fetch(`${API}/api/task-bank/${taskNumber}/next?mode=${mode}`);
      if (!response.ok) {
        setExercise(null);
        return;
      }
      const data = await response.json();
      setExercise(data);
      setSelectedAnswer(null);
      setMultiAnswers([]);
      setNumberAnswer('');
      setCode(data?.code_template || '');
      const firstFile = Array.isArray(data?.files) && data.files.length > 0 ? String(data.files[0]) : '';
      setStdinPath(firstFile);
    } catch (error) {
      console.error(error);
      setExercise(null);
    } finally {
      setLoadingExercise(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  useEffect(() => {
    if (!loadingSummary) {
      loadExercise(selectedTask, bankMode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTask, bankMode, loadingSummary]);

  const taskMap = useMemo(() => {
    const map = {};
    (summary?.tasks || []).forEach((item) => {
      map[item.task_number] = item;
    });
    return map;
  }, [summary]);

  const isCode = exercise?.exercise_type === 'code';

  const canSubmit = useMemo(() => {
    if (!exercise) return false;
    if (isCode) return Boolean(code.trim());
    if (exercise.answer_type === 'single_choice') return Boolean(selectedAnswer);
    if (exercise.answer_type === 'multiple_choice') return multiAnswers.length > 0;
    if (exercise.answer_type === 'number') return numberAnswer !== '';
    return false;
  }, [code, exercise, isCode, multiAnswers, numberAnswer, selectedAnswer]);

  const toggleMulti = (value) => {
    setMultiAnswers((prev) => (prev.includes(value) ? prev.filter((item) => item !== value) : [...prev, value]));
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
      setRunResult(await response.json());
    } catch (error) {
      console.error(error);
    } finally {
      setRunning(false);
    }
  };

  const handleCheck = async () => {
    if (!exercise) return;
    const nextAttemptCount = attemptCount + 1;
    setChecking(true);
    try {
      const payload = {
        exercise_id: exercise.exercise_id,
        attempt_count: nextAttemptCount,
      };
      if (isCode) {
        payload.code = code;
      } else if (exercise.answer_type === 'multiple_choice') {
        payload.answer = multiAnswers;
      } else if (exercise.answer_type === 'number') {
        payload.answer = numberAnswer;
      } else {
        payload.answer = selectedAnswer;
      }

      const response = await fetch(`${API}/api/task-bank/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      setResult(data);
      setAttemptCount(nextAttemptCount);
      if (data?.correct) {
        await loadSummary();
      }
    } catch (error) {
      console.error(error);
    } finally {
      setChecking(false);
    }
  };

  const taskStats = taskMap[selectedTask] || null;

  if (loadingSummary) {
    return (
      <div className="page-shell fade-in">
        <div className="state-card loading-shimmer">
          <div className="state-title">Загрузка банка заданий</div>
          <div className="state-description">Готовим статистику по номерам и подбираем случайное задание.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell page-shell-wide fade-in">
      <div className="page-columns">
        <aside className="left-rail-card">
          <div className="card">
            <div className="eyebrow">Банк заданий</div>
            <div className="section-title">Случайная практика</div>
            <div className="section-description">Отдельный режим для самостоятельной тренировки. Статистика банка не влияет на дорожку и пробники.</div>
            <div className="info-grid" style={{ marginTop: 16 }}>
              <div className="info-card">
                <div className="info-label">Всего попыток</div>
                <div className="info-value">{summary?.total_attempts || 0}</div>
              </div>
              <div className="info-card">
                <div className="info-label">Точность банка</div>
                <div className="info-value">{summary?.overall_accuracy?.toFixed?.(0) || 0}%</div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="segment-control" style={{ marginBottom: 12 }}>
              <button className={`segment-btn ${bankMode === 'any' ? 'active' : ''}`} onClick={() => setBankMode('any')}>Любой</button>
              <button className={`segment-btn ${bankMode === 'training' ? 'active' : ''}`} onClick={() => setBankMode('training')}>Учебный</button>
              <button className={`segment-btn ${bankMode === 'prototype' ? 'active' : ''}`} onClick={() => setBankMode('prototype')}>Прототип</button>
            </div>
            <div className="task-nav-list">
              {(summary?.tasks || []).map((task) => (
                <button
                  key={task.task_number}
                  className={`task-nav-button ${selectedTask === task.task_number ? 'active' : ''}`}
                  onClick={() => setSelectedTask(task.task_number)}
                >
                  <span className="task-nav-index">{task.task_number}</span>
                  <span className="task-nav-title">{task.title || `Задание ${task.task_number}`}</span>
                  <span className={`badge ${task.accuracy >= 80 ? 'badge-success' : task.accuracy >= 60 ? 'badge-accent' : 'badge-warning'}`}>
                    {task.accuracy?.toFixed?.(0) || 0}%
                  </span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="page-stack">
          <div className="hero-card dashboard-hero">
            <div className="eyebrow">Task Bank</div>
            <div className="hero-title">Задание {selectedTask}</div>
            <div className="hero-description">Случайная выдача для самостоятельной проверки по выбранному номеру.</div>
            <div className="task-chip-row" style={{ marginTop: 16 }}>
              <span className="badge badge-accent">Режим: {bankMode}</span>
              {taskStats?.is_code_task ? <span className="badge badge-accent">Python</span> : null}
              {taskStats ? <span className="badge badge-muted">Источник: {sourceLabel(taskStats.source)}</span> : null}
              {taskStats ? <span className="badge badge-muted">Попыток: {taskStats.attempts}</span> : null}
            </div>
          </div>

          {loadingExercise ? (
            <div className="state-card loading-shimmer">
              <div className="state-title">Подбираем задание</div>
              <div className="state-description">Ищем случайный элемент банка для номера {selectedTask}.</div>
            </div>
          ) : !exercise ? (
            <div className="state-card">
              <div className="state-title">Нет доступного задания</div>
              <div className="state-description">Для выбранного номера пока не найдено упражнений под выбранный режим.</div>
            </div>
          ) : (
            <div className="card">
              <div className="task-chip-row">
                <span className="badge badge-accent">№{exercise.task_number}</span>
                <span className="badge badge-muted">{sourceLabel(exercise.source)}</span>
                <span className={`badge ${exercise.exercise_mode === 'prototype' ? 'badge-warning' : 'badge-success'}`}>{exercise.exercise_mode === 'prototype' ? 'Прототип' : 'Учебное'}</span>
                {isCode ? <span className="badge badge-accent">{exercise.code_step || 'full_code'}</span> : null}
              </div>

              <div className="section-title" style={{ marginTop: 14 }}>{exercise.title}</div>
              <div style={{ marginTop: 10, fontSize: 14, lineHeight: 1.75, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
                {exercise.text}
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
                      options={{
                        fontSize: editorFontSize,
                        minimap: { enabled: false },
                        wordWrap: 'on',
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        padding: { top: 14 },
                      }}
                    />
                  </div>

                  {Array.isArray(exercise.files) && exercise.files.length > 0 ? (
                    <div className="info-grid" style={{ marginTop: 14 }}>
                      <div className="info-card" style={{ gridColumn: '1 / -1' }}>
                        <div className="info-label">Файлы задания</div>
                        <div className="row-actions" style={{ marginTop: 10 }}>
                          {exercise.files.map((filePath) => (
                            <a
                              key={`file-${filePath}`}
                              className="btn btn-ghost btn-sm"
                              href={`${API}/api/content/file?path=${encodeURIComponent(filePath)}&download=true`}
                              target="_blank"
                              rel="noreferrer"
                            >
                              Скачать {String(filePath).split('/').pop()}
                            </a>
                          ))}
                        </div>
                        <div style={{ marginTop: 12, maxWidth: 360 }}>
                          <label className="info-label">Использовать файл как stdin</label>
                          <select className="input" value={stdinPath} onChange={(event) => setStdinPath(event.target.value)}>
                            <option value="">Без файла</option>
                            {exercise.files.map((filePath) => (
                              <option key={`stdin-${filePath}`} value={filePath}>{filePath}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                  ) : null}

                  <div className="exercise-toolbar" style={{ marginTop: 14 }}>
                    <button className="btn btn-secondary btn-sm" onClick={handleRunCode} disabled={running}>{running ? 'Запуск...' : 'Запустить код'}</button>
                    <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking || !canSubmit}>{checking ? 'Проверка...' : 'Проверить'}</button>
                    <button className="btn btn-ghost btn-sm" onClick={() => loadExercise()}>Следующее случайное</button>
                  </div>

                  {runResult ? (
                    <div className="code-block" style={{ marginTop: 14 }}>
                      {runResult.stdout ? <div>stdout: {runResult.stdout}</div> : null}
                      {runResult.stderr ? <div style={{ marginTop: 10, color: 'var(--danger)' }}>stderr: {runResult.stderr}</div> : null}
                    </div>
                  ) : null}
                </div>
              ) : exercise.answer_type === 'single_choice' && exercise.options ? (
                <div className="choice-list" style={{ marginTop: 20 }}>
                  {exercise.options.map((option, index) => {
                    const value = option.charAt(0);
                    return <ChoiceButton key={index} active={selectedAnswer === value} leading={value} label={option} onClick={() => setSelectedAnswer(value)} />;
                  })}
                </div>
              ) : exercise.answer_type === 'multiple_choice' && exercise.options ? (
                <div className="choice-list" style={{ marginTop: 20 }}>
                  {exercise.options.map((option, index) => {
                    const value = option.charAt(0);
                    const active = multiAnswers.includes(value);
                    return <ChoiceButton key={index} active={active} leading={active ? '✓' : '+'} label={option} onClick={() => toggleMulti(value)} />;
                  })}
                </div>
              ) : (
                <div style={{ marginTop: 20, maxWidth: 300 }}>
                  <input className="input" type="number" value={numberAnswer} onChange={(event) => setNumberAnswer(event.target.value)} placeholder="Введите числовой ответ" />
                </div>
              )}

              {!isCode ? (
                <div className="exercise-toolbar" style={{ marginTop: 20 }}>
                  <button className="btn btn-primary btn-sm" onClick={handleCheck} disabled={checking || !canSubmit}>{checking ? 'Проверка...' : 'Проверить'}</button>
                  <button className="btn btn-ghost btn-sm" onClick={() => loadExercise()}>Следующее случайное</button>
                  <Link className="btn btn-ghost btn-sm" to={`/theory?task=${selectedTask}`}>Теория номера</Link>
                </div>
              ) : null}

              {result ? (
                <div className={`status-banner ${result.correct ? 'success' : 'danger'}`} style={{ marginTop: 18 }}>
                  <div style={{ fontWeight: 780, fontSize: 15 }}>{result.correct ? 'Ответ принят' : 'Пока неверно'}</div>
                  {result.hint ? <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}><strong>Подсказка:</strong> {result.hint}</div> : null}
                  {Array.isArray(result.hints_shown) && result.hints_shown.length > 0 ? (
                    <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>
                      {result.hints_shown.map((hint, index) => <div key={`hint-${index}`}>Подсказка {index + 1}: {hint}</div>)}
                    </div>
                  ) : null}
                  {result.details ? <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap', color: 'var(--text-secondary)' }}>{result.details}</div> : null}
                  {result.expected !== undefined && !isCode ? <div style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Ожидаемый ответ: <strong>{Array.isArray(result.expected) ? result.expected.join(', ') : String(result.expected)}</strong></div> : null}
                  {result.explanation ? <div style={{ marginTop: 8, fontSize: 13, lineHeight: 1.7, color: 'var(--text-secondary)' }}>{result.explanation}</div> : null}
                </div>
              ) : null}

              <TestsList testResults={result?.test_results} />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}