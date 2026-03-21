import React, { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import API from '../config/api';

function normalizeTaskNumber(value, fallback = 1) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 27) return fallback;
  return parsed;
}

function difficultyLabel(value) {
  if (value === 'easy') return { text: 'Базовое', badge: 'badge-success' };
  if (value === 'hard') return { text: 'Сложное', badge: 'badge-danger' };
  return { text: 'Среднее', badge: 'badge-warning' };
}

export default function TheoryPage() {
  const [tasks, setTasks] = useState([]);
  const [theory, setTheory] = useState(null);
  const [mode, setMode] = useState('short');
  const [loading, setLoading] = useState(true);
  const [searchValue, setSearchValue] = useState('');
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedTask = normalizeTaskNumber(searchParams.get('task'), 1);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API}/api/theory`).then((r) => r.json()).then((data) => {
      if (!cancelled) { setTasks(data); setLoading(false); }
    }).catch(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API}/api/theory/${selectedTask}`).then((r) => r.json()).then((data) => {
      if (!cancelled) setTheory(data);
    }).catch(() => { if (!cancelled) setTheory(null); });
    return () => { cancelled = true; };
  }, [selectedTask]);

  const taskList = tasks.length > 0 ? tasks : Array.from({ length: 27 }, (_, i) => ({ task_number: i + 1, title: `Задание ${i + 1}` }));
  const filteredTasks = useMemo(() => {
    const normalized = searchValue.trim().toLowerCase();
    if (!normalized) return taskList;
    return taskList.filter((task) => `${task.task_number} ${task.title || ''}`.toLowerCase().includes(normalized));
  }, [searchValue, taskList]);

  const setTask = (taskNumber) => setSearchParams({ task: String(taskNumber) });

  const renderInline = (text) => {
    const parts = [];
    let remaining = text;
    let partKey = 0;
    while (remaining) {
      const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
      const codeMatch = remaining.match(/`(.+?)`/);
      let firstMatch = null;
      let matchType = null;
      if (boldMatch && (!codeMatch || boldMatch.index <= codeMatch.index)) { firstMatch = boldMatch; matchType = 'bold'; }
      else if (codeMatch) { firstMatch = codeMatch; matchType = 'code'; }
      if (!firstMatch) { parts.push(remaining); break; }
      if (firstMatch.index > 0) parts.push(remaining.slice(0, firstMatch.index));
      if (matchType === 'bold') parts.push(<strong key={partKey++}>{firstMatch[1]}</strong>);
      else parts.push(<code key={partKey++}>{firstMatch[1]}</code>);
      remaining = remaining.slice(firstMatch.index + firstMatch[0].length);
    }
    return parts;
  };

  const renderMarkdown = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    const elements = [];
    let inCodeBlock = false;
    let codeLines = [];
    let listItems = [];
    let key = 0;

    const flushList = () => {
      if (listItems.length === 0) return;
      elements.push(<div key={`list-${key++}`} className="markdown-list">{listItems.map((item, index) => (
        <div key={index} className="markdown-list-item"><span className="markdown-list-bullet" /><div>{renderInline(item)}</div></div>
      ))}</div>);
      listItems = [];
    };

    for (const line of lines) {
      if (line.trim().startsWith('```')) {
        flushList();
        if (inCodeBlock) {
          elements.push(<pre key={key++}><code>{codeLines.join('\n')}</code></pre>);
          codeLines = [];
          inCodeBlock = false;
        } else inCodeBlock = true;
        continue;
      }
      if (inCodeBlock) { codeLines.push(line); continue; }
      if (line.startsWith('- ')) { listItems.push(line.slice(2)); continue; }
      flushList();
      if (line.startsWith('## ')) elements.push(<h2 key={key++}>{line.slice(3)}</h2>);
      else if (line.startsWith('### ')) elements.push(<h3 key={key++}>{line.slice(4)}</h3>);
      else if (line.startsWith('| ')) {
        const cells = line.split('|').filter((c) => c.trim()).map((c) => c.trim());
        if (!cells.some((c) => c.match(/^-+$/))) {
          elements.push(<div key={key++} className="markdown-table"><div className="markdown-table-row">{cells.map((c, i) => <div key={i} className="markdown-table-cell">{renderInline(c)}</div>)}</div></div>);
        }
      } else if (line.trim() === '') elements.push(<div key={key++} style={{ height: 6 }} />);
      else elements.push(<p key={key++}>{renderInline(line)}</p>);
    }
    flushList();
    if (codeLines.length > 0) elements.push(<pre key={key++}><code>{codeLines.join('\n')}</code></pre>);
    return elements;
  };

  if (loading) return <div className="page-shell fade-in"><div className="state-card loading-shimmer"><div className="state-title">Загрузка теории</div><div className="state-description">Подтягиваем список заданий и материал по выбранной теме.</div></div></div>;
  if (!theory) return <div className="page-shell fade-in"><div className="state-card"><div className="state-title">Теория пока недоступна</div><div className="state-description">Для этого задания не удалось загрузить теоретический материал из локальной базы.</div><div className="state-actions"><button className="btn btn-secondary btn-sm" onClick={() => setTask(1)}>Вернуться к заданию 1</button></div></div></div>;

  const content = mode === 'short' ? theory?.short_theory : theory?.full_theory;
  const difficulty = difficultyLabel(theory?.difficulty);

  return (
    <div className="page-shell page-shell-wide fade-in">
      <div className="page-columns">
        <aside className="left-rail-card">
          <div className="card">
            <div className="eyebrow">Навигация по темам</div>
            <div className="section-title">Теория ЕГЭ</div>
            <div className="section-description">Быстрый доступ ко всем 27 заданиям в спокойном учебном layout.</div>
            <div style={{ marginTop: 16 }}><input className="input" value={searchValue} onChange={(event) => setSearchValue(event.target.value)} placeholder="Найти номер или тему" /></div>
            <div className="info-grid" style={{ marginTop: 16 }}>
              <div className="info-card"><div className="info-label">Всего заданий</div><div className="info-value">{taskList.length}</div></div>
              <div className="info-card"><div className="info-label">Текущее</div><div className="info-value">№{selectedTask}</div></div>
            </div>
          </div>

          <div className="card">
            <div className="task-nav-list">
              {filteredTasks.map((task) => (
                <button key={task.task_number} onClick={() => setTask(task.task_number)} className={`task-nav-button ${selectedTask === task.task_number ? 'active' : ''}`}>
                  <span className="task-nav-index">{task.task_number}</span>
                  <span className="task-nav-title">{task.title || `Задание ${task.task_number}`}</span>
                  {task.is_code_task ? <span className="badge badge-accent">PY</span> : null}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <section className="page-stack">
          <div className="hero-card dashboard-hero">
            <div className="eyebrow">Учебный контент</div>
            <div className="hero-title">Задание {theory.task_number}: {theory.title}</div>
            <div className="hero-description">{theory.subtitle}</div>
            <div className="row-actions" style={{ marginTop: 16 }}>
              <span className="badge badge-accent">№{theory.task_number}</span>
              {theory.is_code_task ? <span className="badge badge-accent">Python</span> : null}
              <span className={`badge ${difficulty.badge}`}>{difficulty.text}</span>
            </div>
            <div className="row-actions" style={{ marginTop: 18 }}>
              <div className="segment-control">
                <button className={`segment-btn ${mode === 'short' ? 'active' : ''}`} onClick={() => setMode('short')}>Краткая теория</button>
                <button className={`segment-btn ${mode === 'full' ? 'active' : ''}`} onClick={() => setMode('full')}>Полная теория</button>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="theory-content">{renderMarkdown(content)}</div>
            <div className="row-actions" style={{ marginTop: 26 }}>
              <Link to={`/practice?task=${selectedTask}`} className="btn btn-primary btn-md">К практике</Link>
              {selectedTask > 1 ? <button className="btn btn-secondary btn-md" onClick={() => setTask(selectedTask - 1)}>Предыдущее</button> : null}
              {selectedTask < 27 ? <button className="btn btn-secondary btn-md" onClick={() => setTask(selectedTask + 1)}>Следующее</button> : null}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
