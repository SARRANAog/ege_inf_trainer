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

function sourceLabel(source) {
  const normalized = String(source || 'mixed').toLowerCase();
  if (normalized === 'fipi') return 'ФИПИ';
  if (normalized === 'reshu') return 'Решу ЕГЭ';
  if (normalized === 'author') return 'Авторское';
  return 'Смешанный источник';
}

export default function TheoryPage() {
  const [tasks, setTasks] = useState([]);
  const [theory, setTheory] = useState(null);
  const [generalTheory, setGeneralTheory] = useState(null);
  const [scope, setScope] = useState('task');
  const [mode, setMode] = useState('short');
  const [loading, setLoading] = useState(true);
  const [searchValue, setSearchValue] = useState('');
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedTask = normalizeTaskNumber(searchParams.get('task'), 1);

  useEffect(() => {
    let cancelled = false;
    async function loadStatic() {
      setLoading(true);
      try {
        const [tasksRes, generalRes] = await Promise.all([
          fetch(`${API}/api/theory`),
          fetch(`${API}/api/theory/general`),
        ]);
        const [tasksData, generalData] = await Promise.all([tasksRes.json(), generalRes.json()]);
        if (cancelled) return;
        setTasks(Array.isArray(tasksData) ? tasksData : []);
        setGeneralTheory(generalData || null);
      } catch (error) {
        console.error(error);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadStatic();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (scope !== 'task') return;
    let cancelled = false;
    async function loadTaskTheory() {
      try {
        const response = await fetch(`${API}/api/theory/${selectedTask}`);
        const data = await response.json();
        if (!cancelled) setTheory(data);
      } catch (error) {
        console.error(error);
        if (!cancelled) setTheory(null);
      }
    }
    loadTaskTheory();
    return () => {
      cancelled = true;
    };
  }, [scope, selectedTask]);

  const taskList = tasks.length > 0 ? tasks : Array.from({ length: 27 }, (_, i) => ({ task_number: i + 1, title: `Задание ${i + 1}` }));

  const filteredTasks = useMemo(() => {
    const normalized = searchValue.trim().toLowerCase();
    if (!normalized) return taskList;
    return taskList.filter((task) => `${task.task_number} ${task.title || ''}`.toLowerCase().includes(normalized));
  }, [searchValue, taskList]);

  const setTask = (taskNumber) => {
    setScope('task');
    setSearchParams({ task: String(taskNumber) });
  };

  const renderInline = (text) => {
    const parts = [];
    let remaining = text;
    let partKey = 0;
    while (remaining) {
      const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
      const codeMatch = remaining.match(/`(.+?)`/);
      let firstMatch = null;
      let matchType = null;
      if (boldMatch && (!codeMatch || boldMatch.index <= codeMatch.index)) {
        firstMatch = boldMatch;
        matchType = 'bold';
      } else if (codeMatch) {
        firstMatch = codeMatch;
        matchType = 'code';
      }
      if (!firstMatch) {
        parts.push(remaining);
        break;
      }
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
    let tableRows = [];
    let key = 0;

    const flushList = () => {
      if (listItems.length === 0) return;
      elements.push(
        <div key={`list-${key++}`} className="markdown-list">
          {listItems.map((item, index) => (
            <div key={index} className="markdown-list-item">
              <span className="markdown-list-bullet" />
              <div>{renderInline(item)}</div>
            </div>
          ))}
        </div>,
      );
      listItems = [];
    };

    const flushTable = () => {
      if (tableRows.length === 0) return;
      elements.push(
        <div key={`table-${key++}`} className="markdown-table">
          {tableRows.map((cells, rowIndex) => (
            <div key={rowIndex} className="markdown-table-row">
              {cells.map((cell, cellIndex) => <div key={cellIndex} className="markdown-table-cell">{renderInline(cell)}</div>)}
            </div>
          ))}
        </div>,
      );
      tableRows = [];
    };

    const parseTableCells = (line) => {
      const trimmed = line.trim();
      if (!trimmed.startsWith('|')) return null;
      const inner = trimmed.replace(/^\|/, '').replace(/\|$/, '');
      const cells = inner.split('|').map((cell) => cell.trim());
      if (cells.every((cell) => cell === '')) return null;
      return cells;
    };

    const isSeparatorRow = (cells) => cells.every((cell) => /^:?-{3,}:?$/.test(cell));

    for (const line of lines) {
      if (line.trim().startsWith('```')) {
        flushList();
        flushTable();
        if (inCodeBlock) {
          elements.push(<pre key={key++}><code>{codeLines.join('\n')}</code></pre>);
          codeLines = [];
          inCodeBlock = false;
        } else {
          inCodeBlock = true;
        }
        continue;
      }

      if (inCodeBlock) {
        codeLines.push(line);
        continue;
      }

      if (line.startsWith('- ')) {
        flushTable();
        listItems.push(line.slice(2));
        continue;
      }

      flushList();
      const tableCells = parseTableCells(line);
      if (tableCells) {
        if (!isSeparatorRow(tableCells)) tableRows.push(tableCells);
        continue;
      }

      flushTable();
      if (line.startsWith('## ')) elements.push(<h2 key={key++}>{line.slice(3)}</h2>);
      else if (line.startsWith('### ')) elements.push(<h3 key={key++}>{line.slice(4)}</h3>);
      else if (line.trim() === '') elements.push(<div key={key++} style={{ height: 6 }} />);
      else elements.push(<p key={key++}>{renderInline(line)}</p>);
    }

    flushList();
    flushTable();
    if (codeLines.length > 0) elements.push(<pre key={key++}><code>{codeLines.join('\n')}</code></pre>);
    return elements;
  };

  if (loading) {
    return (
      <div className="page-shell fade-in">
        <div className="state-card loading-shimmer">
          <div className="state-title">Загрузка теории</div>
          <div className="state-description">Подтягиваем теорию по номерам и общий теоретический блок.</div>
        </div>
      </div>
    );
  }

  const activeTheory = scope === 'general' ? generalTheory : theory;
  if (!activeTheory) {
    return (
      <div className="page-shell fade-in">
        <div className="state-card">
          <div className="state-title">Теория пока недоступна</div>
          <div className="state-description">Не удалось загрузить теоретический материал из локальной базы.</div>
          <div className="state-actions">
            <button className="btn btn-secondary btn-sm" onClick={() => setTask(1)}>Перейти к заданию 1</button>
          </div>
        </div>
      </div>
    );
  }

  const content = mode === 'short' ? activeTheory?.short_theory : activeTheory?.full_theory;
  const difficulty = difficultyLabel(activeTheory?.difficulty);

  return (
    <div className="page-shell page-shell-wide fade-in">
      <div className="page-columns">
        <aside className="left-rail-card">
          <div className="card">
            <div className="eyebrow">Навигация по темам</div>
            <div className="section-title">Теория ЕГЭ</div>
            <div className="section-description">Краткая и полная теория по каждому номеру, плюс общий блок подготовки.</div>
            <div style={{ marginTop: 16 }}>
              <input className="input" value={searchValue} onChange={(event) => setSearchValue(event.target.value)} placeholder="Найти номер или тему" />
            </div>

            <div className="row-actions" style={{ marginTop: 14 }}>
              <button className={`btn btn-sm ${scope === 'general' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setScope('general')}>Общая теория</button>
              <button className={`btn btn-sm ${scope === 'task' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setScope('task')}>По номерам</button>
            </div>

            <div className="info-grid" style={{ marginTop: 16 }}>
              <div className="info-card"><div className="info-label">Всего заданий</div><div className="info-value">{taskList.length}</div></div>
              <div className="info-card"><div className="info-label">Текущее</div><div className="info-value">{scope === 'general' ? 'Общая' : `№${selectedTask}`}</div></div>
            </div>
          </div>

          <div className="card">
            <div className="task-nav-list">
              {filteredTasks.map((task) => (
                <button key={task.task_number} onClick={() => setTask(task.task_number)} className={`task-nav-button ${scope === 'task' && selectedTask === task.task_number ? 'active' : ''}`}>
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
            <div className="hero-title">
              {scope === 'general'
                ? activeTheory.title || 'Общая теория'
                : `Задание ${activeTheory.task_number}: ${activeTheory.title}`}
            </div>
            <div className="hero-description">{activeTheory.subtitle}</div>
            <div className="row-actions" style={{ marginTop: 16 }}>
              {scope === 'task' ? <span className="badge badge-accent">№{activeTheory.task_number}</span> : <span className="badge badge-accent">Стратегия</span>}
              {scope === 'task' && activeTheory.is_code_task ? <span className="badge badge-accent">Python</span> : null}
              {scope === 'task' ? <span className={`badge ${difficulty.badge}`}>{difficulty.text}</span> : null}
              {scope === 'task' ? <span className="badge badge-muted">{sourceLabel(activeTheory.source)}</span> : null}
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
              {scope === 'task' ? <Link to={`/practice?task=${selectedTask}`} className="btn btn-primary btn-md">К практике</Link> : <Link to="/practice?mode=guided" className="btn btn-primary btn-md">К дорожке практики</Link>}
              <Link to="/task-bank" className="btn btn-secondary btn-md">К банку задач</Link>
              {scope === 'task' && selectedTask > 1 ? <button className="btn btn-secondary btn-md" onClick={() => setTask(selectedTask - 1)}>Предыдущее</button> : null}
              {scope === 'task' && selectedTask < 27 ? <button className="btn btn-secondary btn-md" onClick={() => setTask(selectedTask + 1)}>Следующее</button> : null}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}