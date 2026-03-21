import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import API from '../config/api';

function normalizeTaskNumber(value, fallback = 1) {
    const parsed = Number(value);
    if (!Number.isInteger(parsed) || parsed < 1 || parsed > 27) return fallback;
    return parsed;
}

export default function TheoryPage() {
    const [tasks, setTasks] = useState([]);
    const [theory, setTheory] = useState(null);
    const [mode, setMode] = useState('short');
    const [loading, setLoading] = useState(true);
    const [searchParams, setSearchParams] = useSearchParams();

    const selectedTask = normalizeTaskNumber(searchParams.get('task'), 1);

    useEffect(() => {
        fetch(`${API}/api/theory`)
            .then((r) => r.json())
            .then((data) => {
                setTasks(data);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    useEffect(() => {
        fetch(`${API}/api/theory/${selectedTask}`)
            .then((r) => r.json())
            .then(setTheory)
            .catch(() => { });
    }, [selectedTask]);

    const setTask = (taskNumber) => {
        setSearchParams({ task: String(taskNumber) });
    };

    const renderMarkdown = (text) => {
        if (!text) return null;

        const lines = text.split('\n');
        const elements = [];
        let inCodeBlock = false;
        let codeLines = [];
        let key = 0;

        for (const line of lines) {
            if (line.trim().startsWith('```')) {
                if (inCodeBlock) {
                    elements.push(
                        <pre key={key++} className="code-block">
                            <code>{codeLines.join('\n')}</code>
                        </pre>
                    );
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

            if (line.startsWith('## ')) {
                elements.push(<h2 key={key++}>{line.slice(3)}</h2>);
            } else if (line.startsWith('### ')) {
                elements.push(<h3 key={key++}>{line.slice(4)}</h3>);
            } else if (line.startsWith('- ')) {
                elements.push(
                    <li key={key++} style={{ marginLeft: 16 }}>
                        {renderInline(line.slice(2))}
                    </li>
                );
            } else if (line.startsWith('| ')) {
                const cells = line
                    .split('|')
                    .filter((c) => c.trim())
                    .map((c) => c.trim());

                if (cells.some((c) => c.match(/^-+$/))) continue;

                elements.push(
                    <div key={key++} style={{ display: 'flex', gap: 2, fontSize: 13 }}>
                        {cells.map((c, i) => (
                            <div
                                key={i}
                                style={{
                                    flex: 1,
                                    padding: '4px 8px',
                                    background: 'var(--bg-app)',
                                    borderRadius: 4,
                                    color: 'var(--text-secondary)',
                                }}
                            >
                                {renderInline(c)}
                            </div>
                        ))}
                    </div>
                );
            } else if (line.trim() === '') {
                elements.push(<div key={key++} style={{ height: 8 }} />);
            } else {
                elements.push(<p key={key++}>{renderInline(line)}</p>);
            }
        }

        return elements;
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

            if (firstMatch.index > 0) {
                parts.push(remaining.slice(0, firstMatch.index));
            }

            if (matchType === 'bold') {
                parts.push(<strong key={partKey++}>{firstMatch[1]}</strong>);
            } else {
                parts.push(
                    <code
                        key={partKey++}
                        style={{
                            background: 'var(--bg-app)',
                            padding: '1px 4px',
                            borderRadius: 3,
                            fontSize: 13,
                            color: 'var(--accent)',
                        }}
                    >
                        {firstMatch[1]}
                    </code>
                );
            }

            remaining = remaining.slice(firstMatch.index + firstMatch[0].length);
        }

        return parts;
    };

    if (loading) {
        return <div style={{ color: 'var(--text-muted)' }}>Загрузка теории...</div>;
    }

    const content = mode === 'short' ? theory?.short_theory : theory?.full_theory;

    return (
        <div
            className="fade-in"
            style={{ display: 'flex', gap: 20, height: 'calc(100vh - 104px)' }}
        >
            <div
                style={{ width: 220, minWidth: 220, overflowY: 'auto', paddingRight: 8 }}
                data-testid="theory-task-list"
            >
                <div
                    style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: 'var(--text-secondary)',
                        marginBottom: 12,
                    }}
                >
                    Задания ЕГЭ
                </div>

                {(tasks.length > 0
                    ? tasks
                    : Array.from({ length: 27 }, (_, i) => ({
                        task_number: i + 1,
                        title: `Задание ${i + 1}`,
                    }))
                ).map((t) => (
                    <button
                        key={t.task_number}
                        onClick={() => setTask(t.task_number)}
                        className={`nav-item ${selectedTask === t.task_number ? 'active' : ''}`}
                        style={{
                            width: '100%',
                            textAlign: 'left',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: 13,
                        }}
                        data-testid={`theory-task-${t.task_number}`}
                    >
                        <span
                            style={{
                                width: 24,
                                height: 24,
                                borderRadius: 7,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: 12,
                                fontWeight: 600,
                                background:
                                    selectedTask === t.task_number
                                        ? 'var(--accent)'
                                        : 'var(--bg-elevated)',
                                color:
                                    selectedTask === t.task_number ? 'white' : 'var(--text-secondary)',
                                flexShrink: 0,
                            }}
                        >
                            {t.task_number}
                        </span>

                        <span
                            style={{
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                            }}
                        >
                            {t.title || `Задание ${t.task_number}`}
                        </span>

                        {t.is_code_task && (
                            <span
                                style={{
                                    fontSize: 10,
                                    color: 'var(--accent)',
                                    marginLeft: 'auto',
                                    flexShrink: 0,
                                }}
                            >
                                PY
                            </span>
                        )}
                    </button>
                ))}
            </div>

            <div style={{ flex: 1, overflowY: 'auto', minWidth: 0 }}>
                {theory && (
                    <>
                        <div
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                marginBottom: 20,
                                flexWrap: 'wrap',
                                gap: 12,
                            }}
                        >
                            <div>
                                <h1 style={{ fontSize: 20, fontWeight: 700 }}>
                                    Задание {theory.task_number}: {theory.title}
                                </h1>
                                <p
                                    style={{
                                        color: 'var(--text-secondary)',
                                        fontSize: 13,
                                        marginTop: 4,
                                    }}
                                >
                                    {theory.subtitle}
                                </p>
                            </div>

                            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                {theory.is_code_task && (
                                    <span className="badge badge-accent">Python</span>
                                )}
                                <span
                                    className={`badge ${theory.difficulty === 'easy'
                                            ? 'badge-success'
                                            : theory.difficulty === 'hard'
                                                ? 'badge-danger'
                                                : 'badge-warning'
                                        }`}
                                >
                                    {theory.difficulty === 'easy'
                                        ? 'Лёгкое'
                                        : theory.difficulty === 'hard'
                                            ? 'Сложное'
                                            : 'Среднее'}
                                </span>
                            </div>
                        </div>

                        <div
                            className="segment-control"
                            style={{ marginBottom: 20 }}
                            data-testid="theory-mode-toggle"
                        >
                            <button
                                className={`segment-btn ${mode === 'short' ? 'active' : ''}`}
                                onClick={() => setMode('short')}
                                data-testid="theory-short-btn"
                            >
                                Краткая теория
                            </button>
                            <button
                                className={`segment-btn ${mode === 'full' ? 'active' : ''}`}
                                onClick={() => setMode('full')}
                                data-testid="theory-full-btn"
                            >
                                Полная теория
                            </button>
                        </div>

                        <div className="theory-content" style={{ maxWidth: 720 }}>
                            {renderMarkdown(content)}
                        </div>

                        <div
                            style={{
                                display: 'flex',
                                gap: 10,
                                marginTop: 28,
                                paddingBottom: 20,
                            }}
                        >
                            <Link
                                to={`/practice?task=${selectedTask}`}
                                className="btn btn-primary btn-md"
                                data-testid="go-to-practice-btn"
                            >
                                К практике
                            </Link>

                            {selectedTask > 1 && (
                                <button
                                    className="btn btn-secondary btn-md"
                                    onClick={() => setTask(selectedTask - 1)}
                                    data-testid="prev-task-btn"
                                >
                                    Предыдущее
                                </button>
                            )}

                            {selectedTask < 27 && (
                                <button
                                    className="btn btn-secondary btn-md"
                                    onClick={() => setTask(selectedTask + 1)}
                                    data-testid="next-task-btn"
                                >
                                    Следующее
                                </button>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
