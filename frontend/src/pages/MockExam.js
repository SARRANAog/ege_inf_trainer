import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function MockExamPage() {
  const [status, setStatus] = useState(null);
  const [exam, setExam] = useState(null);
  const [currentTask, setCurrentTask] = useState(0);
  const [answers, setAnswers] = useState({});
  const [codes, setCodes] = useState({});
  const [flags, setFlags] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    fetch(`${API}/api/mock-exam`).then(r => r.json()).then(data => {
      setStatus(data);
      if (data.has_active) {
        setExam(data.exam);
        const saved = {};
        const savedCodes = {};
        const savedFlags = {};
        (data.exam.tasks || []).forEach(t => {
          if (t.answer !== null) saved[t.task_number] = t.answer;
          if (t.code) savedCodes[t.task_number] = t.code;
          if (t.flagged) savedFlags[t.task_number] = true;
        });
        setAnswers(saved);
        setCodes(savedCodes);
        setFlags(savedFlags);
      }
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!exam) return;
    const interval = setInterval(() => setTimer(t => t + 1), 1000);
    return () => clearInterval(interval);
  }, [exam]);

  const handleStart = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/mock-exam/start`, { method: 'POST' });
      const data = await res.json();
      const examRes = await fetch(`${API}/api/mock-exam`);
      const examData = await examRes.json();
      setExam(examData.exam);
      setStatus(examData);
      setCurrentTask(0);
      setTimer(0);
    } catch(e) { console.error(e); }
    setLoading(false);
  };

  const saveAnswer = async (taskNum, answer, code) => {
    if (!exam) return;
    try {
      await fetch(`${API}/api/mock-exam/${exam.exam_id}/answer`, {
        method: 'PUT',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ task_number: taskNum, answer, code }),
      });
    } catch(e) { console.error(e); }
  };

  const handleSubmit = async () => {
    if (!window.confirm('Завершить пробник? Это действие нельзя отменить.')) return;
    setSubmitting(true);
    // Save all answers first
    for (const task of (exam?.tasks || [])) {
      const tn = task.task_number;
      await saveAnswer(tn, answers[tn] || null, codes[tn] || null);
    }
    try {
      const res = await fetch(`${API}/api/mock-exam/${exam.exam_id}/submit`, { method: 'POST' });
      const data = await res.json();
      setResults(data);
      setExam(null);
    } catch(e) { console.error(e); }
    setSubmitting(false);
  };

  const formatTime = (s) => {
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    return `${h > 0 ? h + ':' : ''}${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
  };

  if (loading) return <div style={{color:'var(--text-muted)'}}>Загрузка...</div>;

  // Results screen
  if (results) {
    return (
      <div className="fade-in" style={{maxWidth:700,margin:'0 auto'}}>
        <div className="card" style={{padding:32,textAlign:'center'}}>
          <h1 style={{fontSize:24,fontWeight:700,marginBottom:8}}>Результаты пробника</h1>
          <div style={{fontSize:48,fontWeight:700,color:'var(--accent)',margin:'20px 0'}}>{results.score?.toFixed(0)}%</div>
          <div style={{fontSize:16,color:'var(--text-secondary)',marginBottom:24}}>
            Правильно: {results.correct} из {results.total}
          </div>

          <div style={{display:'flex',flexWrap:'wrap',gap:6,justifyContent:'center',marginBottom:24}}>
            {(results.results || []).map((r, i) => (
              <div key={i} style={{
                width:36,height:36,borderRadius:8,display:'flex',alignItems:'center',justifyContent:'center',fontSize:12,fontWeight:600,
                background: r.correct ? 'rgba(92,184,122,0.15)' : 'rgba(224,96,112,0.15)',
                color: r.correct ? 'var(--success)' : 'var(--danger)',
                border: `1px solid ${r.correct ? 'var(--success)' : 'var(--danger)'}`,
              }}>{r.task_number}</div>
            ))}
          </div>

          <div style={{display:'flex',gap:10,justifyContent:'center'}}>
            <a href="/" className="btn btn-primary btn-md">На дорожку</a>
            <a href="/practice" className="btn btn-secondary btn-md">К практике</a>
            <button className="btn btn-ghost btn-md" onClick={() => { setResults(null); setStatus(null); window.location.reload(); }}>Новый пробник</button>
          </div>
        </div>
      </div>
    );
  }

  // Pre-start screen
  if (!exam) {
    return (
      <div className="fade-in" style={{maxWidth:600,margin:'0 auto'}}>
        <div className="card" style={{padding:32,textAlign:'center'}}>
          <h1 style={{fontSize:22,fontWeight:700,marginBottom:12}}>Пробный экзамен</h1>
          <p style={{color:'var(--text-secondary)',fontSize:14,lineHeight:1.7,marginBottom:24}}>
            Полноценный пробник по формату ЕГЭ. До 27 заданий. Автосохранение. Можно приостановить и продолжить.
          </p>
          <div style={{display:'flex',gap:16,justifyContent:'center',marginBottom:24}}>
            <div className="card-elevated" style={{padding:'12px 20px'}}>
              <div style={{fontSize:20,fontWeight:700}}>27</div>
              <div style={{fontSize:12,color:'var(--text-muted)'}}>заданий</div>
            </div>
            <div className="card-elevated" style={{padding:'12px 20px'}}>
              <div style={{fontSize:20,fontWeight:700}}>235</div>
              <div style={{fontSize:12,color:'var(--text-muted)'}}>мин.</div>
            </div>
          </div>
          <button className="btn btn-primary btn-lg" onClick={handleStart} data-testid="start-exam-btn">Начать пробник</button>

          {(status?.recent_exams || []).length > 0 && (
            <div style={{marginTop:28}}>
              <div style={{fontSize:14,fontWeight:600,marginBottom:10}}>Предыдущие пробники</div>
              {status.recent_exams.map((e, i) => (
                <div key={i} className="card-elevated" style={{padding:'10px 16px',marginBottom:8,display:'flex',alignItems:'center',justifyContent:'space-between'}}>
                  <span style={{fontSize:13,color:'var(--text-secondary)'}}>{e.completed_at?.split('T')[0]}</span>
                  <span style={{fontWeight:600,color: e.score >= 70 ? 'var(--success)' : e.score >= 40 ? 'var(--warning)' : 'var(--danger)'}}>{e.score?.toFixed(0)}%</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Exam in progress
  const tasks = exam.tasks || [];
  const task = tasks[currentTask];
  const exercise = task?.exercise || {};

  return (
    <div className="fade-in" style={{maxWidth:900,margin:'0 auto'}}>
      {/* Top bar */}
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16,flexWrap:'wrap',gap:8}}>
        <div style={{display:'flex',alignItems:'center',gap:12}}>
          <span style={{fontSize:16,fontWeight:600}}>Пробник</span>
          <span style={{color:'var(--text-muted)',fontSize:13}}>Задание {currentTask + 1}/{tasks.length}</span>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:12}}>
          <span style={{fontFamily:'JetBrains Mono',fontSize:16,fontWeight:600,color:'var(--accent)'}}>{formatTime(timer)}</span>
          <button className="btn btn-danger btn-sm" onClick={handleSubmit} disabled={submitting} data-testid="submit-exam-btn">
            {submitting ? 'Завершение...' : 'Завершить'}
          </button>
        </div>
      </div>

      {/* Task navigator */}
      <div style={{display:'flex',gap:4,flexWrap:'wrap',marginBottom:16}}>
        {tasks.map((t, i) => (
          <button
            key={i}
            onClick={() => setCurrentTask(i)}
            style={{
              width:32,height:32,borderRadius:8,border:'1px solid',fontSize:12,fontWeight:600,cursor:'pointer',position:'relative',
              borderColor: i === currentTask ? 'var(--accent)' : answers[t.task_number] !== undefined ? 'var(--success)' : 'var(--border)',
              background: i === currentTask ? 'rgba(108,127,216,0.15)' : answers[t.task_number] !== undefined ? 'rgba(92,184,122,0.08)' : 'var(--bg-elevated)',
              color: i === currentTask ? 'var(--accent)' : 'var(--text-secondary)',
            }}
            data-testid={`exam-task-${t.task_number}`}
          >
            {t.task_number}
            {flags[t.task_number] && <span style={{position:'absolute',top:-2,right:-2,width:6,height:6,borderRadius:3,background:'var(--warning)'}}/>}
          </button>
        ))}
      </div>

      {/* Current task */}
      {task && (
        <div className="card" style={{padding:24}}>
          <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:16}}>
            <span className="badge badge-accent">Задание {task.task_number}</span>
            {exercise.is_code_task || exercise.exercise_type === 'code' ? <span className="badge badge-accent">Python</span> : null}
            <button className="btn btn-ghost btn-sm" onClick={() => {
              setFlags(prev => ({...prev, [task.task_number]: !prev[task.task_number]}));
            }} style={{marginLeft:'auto',color: flags[task.task_number] ? 'var(--warning)' : 'var(--text-muted)'}}>
              {flags[task.task_number] ? 'Снять флаг' : 'Пометить'}
            </button>
          </div>

          <h3 style={{fontSize:15,fontWeight:600,marginBottom:8}}>{exercise.title}</h3>
          <p style={{color:'var(--text-secondary)',fontSize:14,lineHeight:1.7,whiteSpace:'pre-wrap',marginBottom:20}}>{exercise.text}</p>

          {exercise.exercise_type === 'code' ? (
            <div style={{marginBottom:16}}>
              <div style={{border:'1px solid var(--border)',borderRadius:12,overflow:'hidden'}}>
                <Editor
                  height="220px"
                  language="python"
                  theme="vs-dark"
                  value={codes[task.task_number] || exercise.code_template || ''}
                  onChange={(val) => {
                    setCodes(prev => ({...prev, [task.task_number]: val}));
                    setAnswers(prev => ({...prev, [task.task_number]: 'code_submitted'}));
                    saveAnswer(task.task_number, 'code_submitted', val);
                  }}
                  options={{ fontSize:14, minimap:{enabled:false}, wordWrap:'on', lineNumbers:'on', scrollBeyondLastLine:false, automaticLayout:true }}
                />
              </div>
            </div>
          ) : exercise.options ? (
            <div style={{display:'flex',flexDirection:'column',gap:6,marginBottom:16}}>
              {exercise.options.map((opt, i) => (
                <button
                  key={i}
                  onClick={() => {
                    const val = opt.charAt(0);
                    setAnswers(prev => ({...prev, [task.task_number]: val}));
                    saveAnswer(task.task_number, val, null);
                  }}
                  style={{
                    padding:'8px 14px',borderRadius:8,border:'1px solid',textAlign:'left',cursor:'pointer',fontSize:13,
                    borderColor: answers[task.task_number] === opt.charAt(0) ? 'var(--accent)' : 'var(--border)',
                    background: answers[task.task_number] === opt.charAt(0) ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                    color:'var(--text-primary)',
                  }}
                >
                  {opt}
                </button>
              ))}
            </div>
          ) : (
            <input
              className="input"
              style={{maxWidth:300,marginBottom:16}}
              value={answers[task.task_number] || ''}
              onChange={e => {
                const val = e.target.value;
                setAnswers(prev => ({...prev, [task.task_number]: val}));
                saveAnswer(task.task_number, val, null);
              }}
              placeholder="Введите ответ"
              data-testid="exam-answer-input"
            />
          )}

          <div style={{display:'flex',gap:8}}>
            {currentTask > 0 && <button className="btn btn-secondary btn-sm" onClick={() => setCurrentTask(currentTask-1)}>Предыдущее</button>}
            {currentTask < tasks.length-1 && <button className="btn btn-primary btn-sm" onClick={() => setCurrentTask(currentTask+1)}>Следующее</button>}
          </div>
        </div>
      )}
    </div>
  );
}
