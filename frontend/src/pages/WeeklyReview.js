import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function WeeklyReviewPage() {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [started, setStarted] = useState(false);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState({});

  useEffect(() => {
    fetch(`${API}/api/weekly-review`).then(r => r.json()).then(data => {
      setReview(data);
      if (data.status === 'active') setStarted(true);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleStart = async () => {
    await fetch(`${API}/api/weekly-review/start`, { method: 'POST' });
    setStarted(true);
  };

  const handleComplete = async () => {
    await fetch(`${API}/api/weekly-review/complete`, { method: 'POST' });
    setStarted(false);
    setReview(prev => ({ ...prev, status: 'completed' }));
  };

  const handleCheck = async (exercise) => {
    const answer = answers[exercise.exercise_id];
    if (!answer && answer !== 0) return;
    try {
      const res = await fetch(`${API}/api/exercises/check`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ exercise_id: exercise.exercise_id, answer }),
      });
      const data = await res.json();
      setResults(prev => ({ ...prev, [exercise.exercise_id]: data }));
    } catch(e) { console.error(e); }
  };

  if (loading) return <div style={{color:'var(--text-muted)'}}>Загрузка...</div>;

  const exercises = review?.exercises || [];
  const completedCount = Object.keys(results).length;

  if (!started) {
    return (
      <div className="fade-in" style={{maxWidth:640,margin:'0 auto'}}>
        <div className="card" style={{padding:32,textAlign:'center'}}>
          <h1 style={{fontSize:22,fontWeight:700,marginBottom:12}}>Weekly Review</h1>
          <p style={{color:'var(--text-secondary)',fontSize:14,lineHeight:1.7,marginBottom:24}}>
            Еженедельное повторение помогает закрепить материал и выявить слабые места.
            {review?.status === 'completed' && ' Ваш последний review завершён.'}
          </p>

          <div style={{display:'flex',gap:16,justifyContent:'center',marginBottom:24,flexWrap:'wrap'}}>
            <div className="card-elevated" style={{padding:'12px 20px',textAlign:'center'}}>
              <div style={{fontSize:24,fontWeight:700,color:'var(--accent)'}}>{exercises.length}</div>
              <div style={{fontSize:12,color:'var(--text-muted)'}}>заданий</div>
            </div>
            <div className="card-elevated" style={{padding:'12px 20px',textAlign:'center'}}>
              <div style={{fontSize:24,fontWeight:700,color:'var(--accent)'}}>{review?.estimated_time || 30}</div>
              <div style={{fontSize:12,color:'var(--text-muted)'}}>мин.</div>
            </div>
            <div className="card-elevated" style={{padding:'12px 20px',textAlign:'center'}}>
              <div style={{fontSize:24,fontWeight:700,color:'var(--warning)'}}>{(review?.weak_tasks || []).length}</div>
              <div style={{fontSize:12,color:'var(--text-muted)'}}>слабых тем</div>
            </div>
          </div>

          {(review?.weak_tasks || []).length > 0 && (
            <div style={{marginBottom:20}}>
              <div style={{fontSize:13,color:'var(--text-secondary)',marginBottom:8}}>Включённые темы:</div>
              <div style={{display:'flex',gap:6,justifyContent:'center',flexWrap:'wrap'}}>
                {(review?.review_tasks || []).map(tn => (
                  <span key={tn} className="badge badge-muted">№{tn}</span>
                ))}
              </div>
            </div>
          )}

          <button className="btn btn-primary btn-lg" onClick={handleStart} data-testid="start-review-btn">
            Начать Weekly Review
          </button>
        </div>
      </div>
    );
  }

  const currentExercise = exercises[currentIdx];

  return (
    <div className="fade-in" style={{maxWidth:720,margin:'0 auto'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:20}}>
        <div>
          <h2 style={{fontSize:18,fontWeight:600}}>Weekly Review</h2>
          <span style={{color:'var(--text-secondary)',fontSize:13}}>Задание {currentIdx + 1} из {exercises.length}</span>
        </div>
        <div style={{display:'flex',gap:8,alignItems:'center'}}>
          <div className="progress-bar" style={{width:120}}>
            <div className="progress-fill" style={{width:`${(completedCount/exercises.length)*100}%`}}/>
          </div>
          <span style={{fontSize:12,color:'var(--text-muted)'}}>{completedCount}/{exercises.length}</span>
        </div>
      </div>

      {/* Exercise Grid */}
      <div style={{display:'flex',gap:4,flexWrap:'wrap',marginBottom:16}}>
        {exercises.map((ex, i) => (
          <button
            key={i}
            onClick={() => setCurrentIdx(i)}
            style={{
              width:28,height:28,borderRadius:6,border:'1px solid',fontSize:11,fontWeight:600,cursor:'pointer',
              borderColor: results[ex.exercise_id] ? (results[ex.exercise_id].correct ? 'var(--success)' : 'var(--danger)') : i === currentIdx ? 'var(--accent)' : 'var(--border)',
              background: results[ex.exercise_id] ? (results[ex.exercise_id].correct ? 'rgba(92,184,122,0.15)' : 'rgba(224,96,112,0.15)') : i === currentIdx ? 'rgba(108,127,216,0.15)' : 'var(--bg-elevated)',
              color: i === currentIdx ? 'var(--accent)' : 'var(--text-secondary)',
            }}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {currentExercise && (
        <div className="card" style={{padding:24}}>
          <div style={{display:'flex',gap:8,marginBottom:12}}>
            <span className="badge badge-accent">№{currentExercise.task_number}</span>
            <span className="badge badge-muted">{currentExercise.difficulty}</span>
          </div>
          <h3 style={{fontSize:15,fontWeight:600,marginBottom:8}}>{currentExercise.title}</h3>
          <p style={{color:'var(--text-secondary)',fontSize:14,lineHeight:1.7,whiteSpace:'pre-wrap',marginBottom:16}}>{currentExercise.text}</p>

          {currentExercise.answer_type === 'number' || (!currentExercise.options && currentExercise.exercise_type !== 'code') ? (
            <input
              className="input"
              style={{maxWidth:300,marginBottom:12}}
              value={answers[currentExercise.exercise_id] || ''}
              onChange={e => setAnswers(prev => ({...prev, [currentExercise.exercise_id]: e.target.value}))}
              placeholder="Введите ответ"
              data-testid="review-answer-input"
            />
          ) : currentExercise.options ? (
            <div style={{display:'flex',flexDirection:'column',gap:6,marginBottom:12}}>
              {currentExercise.options.map((opt, i) => (
                <button
                  key={i}
                  onClick={() => setAnswers(prev => ({...prev, [currentExercise.exercise_id]: opt.charAt(0)}))}
                  style={{
                    padding:'8px 14px',borderRadius:8,border:'1px solid',textAlign:'left',cursor:'pointer',fontSize:13,
                    borderColor: answers[currentExercise.exercise_id] === opt.charAt(0) ? 'var(--accent)' : 'var(--border)',
                    background: answers[currentExercise.exercise_id] === opt.charAt(0) ? 'rgba(108,127,216,0.1)' : 'var(--bg-elevated)',
                    color:'var(--text-primary)',
                  }}
                >
                  {opt}
                </button>
              ))}
            </div>
          ) : null}

          {results[currentExercise.exercise_id] && (
            <div style={{
              padding:12,borderRadius:10,marginBottom:12,
              background: results[currentExercise.exercise_id].correct ? 'rgba(92,184,122,0.08)' : 'rgba(224,96,112,0.08)',
              border: `1px solid ${results[currentExercise.exercise_id].correct ? 'var(--success)' : 'var(--danger)'}`,
              fontSize:13,
            }}>
              <strong style={{color: results[currentExercise.exercise_id].correct ? 'var(--success)' : 'var(--danger)'}}>
                {results[currentExercise.exercise_id].correct ? 'Правильно!' : 'Неправильно'}
              </strong>
              {results[currentExercise.exercise_id].feedback && (
                <div style={{color:'var(--text-secondary)',marginTop:4}}>{results[currentExercise.exercise_id].feedback}</div>
              )}
            </div>
          )}

          <div style={{display:'flex',gap:8}}>
            {!results[currentExercise.exercise_id] && (
              <button className="btn btn-primary btn-sm" onClick={() => handleCheck(currentExercise)} data-testid="check-review-btn">
                Проверить
              </button>
            )}
            {currentIdx < exercises.length - 1 && (
              <button className="btn btn-secondary btn-sm" onClick={() => setCurrentIdx(currentIdx + 1)}>Следующее</button>
            )}
            {completedCount >= exercises.length && (
              <button className="btn btn-primary btn-sm" onClick={handleComplete} data-testid="complete-review-btn">
                Завершить Review
              </button>
            )}
          </div>
        </div>
      )}

      <div style={{display:'flex',gap:10,marginTop:20,justifyContent:'center'}}>
        <a href="/" className="btn btn-ghost btn-sm">На дорожку</a>
        {completedCount >= exercises.length * 0.8 && (
          <button className="btn btn-primary btn-sm" onClick={handleComplete} data-testid="finish-review-btn">
            Завершить Review
          </button>
        )}
      </div>
    </div>
  );
}
