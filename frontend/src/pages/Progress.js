import React, { useState, useEffect } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const API = process.env.REACT_APP_BACKEND_URL;

function StatCard({ label, value, color, icon }) {
  return (
    <div className="card" style={{padding:'16px 20px',textAlign:'center'}} data-testid={`stat-${label}`}>
      <div style={{fontSize:28,fontWeight:700,color:`var(${color})`}}>{value}</div>
      <div style={{fontSize:12,color:'var(--text-muted)',marginTop:4}}>{label}</div>
    </div>
  );
}

export default function ProgressPage() {
  const [progress, setProgress] = useState(null);
  const [theory, setTheory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/progress`).then(r => r.json()),
      fetch(`${API}/api/theory`).then(r => r.json()),
    ]).then(([pr, th]) => {
      setProgress(pr);
      setTheory(th);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div style={{color:'var(--text-muted)',padding:40,textAlign:'center'}}>Загрузка прогресса...</div>;
  if (!progress) return <div style={{color:'var(--text-muted)',padding:40,textAlign:'center'}}>Нет данных</div>;

  const est = progress.estimated_score || {};
  const tasks = progress.tasks || [];
  const taskMap = {};
  tasks.forEach(t => { taskMap[t.task_number] = t; });

  const theoryMap = {};
  theory.forEach(t => { theoryMap[t.task_number] = t; });

  // Chart data: accuracy by task
  const taskNumbers = Array.from({length:27}, (_,i) => i+1);
  const accuracies = taskNumbers.map(tn => taskMap[tn]?.accuracy || 0);
  const attempts = taskNumbers.map(tn => taskMap[tn]?.total_attempts || 0);

  const barData = {
    labels: taskNumbers.map(n => `${n}`),
    datasets: [{
      label: 'Точность (%)',
      data: accuracies,
      backgroundColor: accuracies.map(a => a >= 80 ? 'rgba(92,184,122,0.7)' : a >= 60 ? 'rgba(108,127,216,0.7)' : a > 0 ? 'rgba(224,160,80,0.7)' : 'rgba(94,107,125,0.3)'),
      borderRadius: 4,
      borderSkipped: false,
    }]
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#1a2029',
        borderColor: '#2a3444',
        borderWidth: 1,
        titleColor: '#e8edf4',
        bodyColor: '#8b97a8',
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          label: (ctx) => `Точность: ${ctx.raw.toFixed(0)}%`,
          afterLabel: (ctx) => `Попыток: ${attempts[ctx.dataIndex]}`
        }
      }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#5e6b7d', font: { size: 11 } } },
      y: { max: 100, grid: { color: 'rgba(42,52,68,0.5)' }, ticks: { color: '#5e6b7d', font: { size: 11 }, callback: v => v + '%' } }
    }
  };

  // Doughnut: coverage
  const practiced = tasks.filter(t => t.total_attempts > 0).length;
  const strong = tasks.filter(t => t.accuracy >= 80).length;
  const weak = tasks.filter(t => t.accuracy > 0 && t.accuracy < 60).length;
  const notStarted = 27 - practiced;

  const doughnutData = {
    labels: ['Отлично (>80%)', 'Хорошо (60-80%)', 'Слабо (<60%)', 'Не начато'],
    datasets: [{
      data: [strong, practiced - strong - weak, weak, notStarted],
      backgroundColor: ['rgba(92,184,122,0.8)', 'rgba(108,127,216,0.8)', 'rgba(224,160,80,0.8)', 'rgba(94,107,125,0.3)'],
      borderWidth: 0,
      spacing: 2,
    }]
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: '#8b97a8', padding: 12, usePointStyle: true, pointStyleWidth: 10, font: { size: 12 } }
      }
    }
  };

  // Categorize tasks
  const strongTasks = taskNumbers.filter(tn => (taskMap[tn]?.accuracy || 0) >= 80);
  const weakTasks = taskNumbers.filter(tn => {
    const t = taskMap[tn];
    return t && t.total_attempts >= 2 && t.accuracy < 60;
  });
  const needsReview = taskNumbers.filter(tn => {
    const t = taskMap[tn];
    return t && t.total_attempts > 0 && t.accuracy >= 60 && t.accuracy < 80;
  });

  return (
    <div className="fade-in" style={{maxWidth:960,margin:'0 auto'}}>
      {/* Overview Cards */}
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(140px,1fr))',gap:12,marginBottom:24}}>
        <StatCard label="Покрытие" value={`${progress.coverage?.toFixed(0) || 0}%`} color="--accent" />
        <StatCard label="Точность" value={`${progress.avg_accuracy?.toFixed(0) || 0}%`} color="--success" />
        <StatCard label="Решено" value={progress.total_attempts || 0} color="--accent" />
        <StatCard label="Правильно" value={progress.total_correct || 0} color="--success" />
        <StatCard label="Пробники" value={progress.mock_exams_completed || 0} color="--warning" />
        <StatCard label="Reviews" value={progress.weekly_reviews_completed || 0} color="--accent" />
      </div>

      {/* Score Estimate */}
      {est.min !== undefined && (
        <div className="card" style={{padding:24,marginBottom:24}} data-testid="score-estimate">
          <div style={{display:'flex',alignItems:'center',gap:24,flexWrap:'wrap'}}>
            <div style={{flex:1,minWidth:200}}>
              <h3 style={{fontSize:16,fontWeight:600,marginBottom:8}}>Ориентировочный балл ЕГЭ</h3>
              {est.min > 0 ? (
                <>
                  <div style={{fontSize:40,fontWeight:700,color:'var(--accent)',lineHeight:1.1}}>{est.min}–{est.max}</div>
                  <div style={{color:'var(--text-secondary)',fontSize:13,marginTop:8}}>{est.description}</div>
                  <div style={{marginTop:10}}>
                    <span className={`badge ${est.level==='strong'?'badge-success':est.level==='good'?'badge-accent':est.level==='medium'?'badge-warning':'badge-muted'}`} style={{fontSize:13,padding:'4px 14px'}}>
                      {est.level === 'strong' ? 'Отличная подготовка' : est.level === 'good' ? 'Хорошая подготовка' : est.level === 'medium' ? 'Средний уровень' : 'Начальный этап'}
                    </span>
                  </div>
                </>
              ) : (
                <div style={{color:'var(--text-muted)',fontSize:14}}>Решите больше заданий для оценки</div>
              )}
            </div>
            <div style={{width:140,height:140}}>
              <Doughnut data={doughnutData} options={doughnutOptions} />
            </div>
          </div>
        </div>
      )}

      {/* Accuracy Chart */}
      <div className="card" style={{padding:24,marginBottom:24}} data-testid="accuracy-chart">
        <h3 style={{fontSize:16,fontWeight:600,marginBottom:16}}>Точность по заданиям</h3>
        <div style={{height:200}}>
          <Bar data={barData} options={barOptions} />
        </div>
        <div style={{display:'flex',gap:16,marginTop:12,justifyContent:'center',fontSize:12,color:'var(--text-muted)'}}>
          <span><span style={{display:'inline-block',width:10,height:10,borderRadius:2,background:'rgba(92,184,122,0.7)',marginRight:4}}/>80%+</span>
          <span><span style={{display:'inline-block',width:10,height:10,borderRadius:2,background:'rgba(108,127,216,0.7)',marginRight:4}}/>60-80%</span>
          <span><span style={{display:'inline-block',width:10,height:10,borderRadius:2,background:'rgba(224,160,80,0.7)',marginRight:4}}/>&lt;60%</span>
          <span><span style={{display:'inline-block',width:10,height:10,borderRadius:2,background:'rgba(94,107,125,0.3)',marginRight:4}}/>Не начато</span>
        </div>
      </div>

      {/* Strong / Weak Areas */}
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:12,marginBottom:24}}>
        {strongTasks.length > 0 && (
          <div className="card" style={{padding:18}}>
            <h4 style={{fontSize:14,fontWeight:600,color:'var(--success)',marginBottom:10}}>Сильные стороны</h4>
            <div style={{display:'flex',flexWrap:'wrap',gap:6}}>
              {strongTasks.map(tn => (
                <span key={tn} className="badge badge-success" style={{fontSize:12}}>№{tn}</span>
              ))}
            </div>
          </div>
        )}
        {needsReview.length > 0 && (
          <div className="card" style={{padding:18}}>
            <h4 style={{fontSize:14,fontWeight:600,color:'var(--accent)',marginBottom:10}}>Требует повторения</h4>
            <div style={{display:'flex',flexWrap:'wrap',gap:6}}>
              {needsReview.map(tn => (
                <span key={tn} className="badge badge-accent" style={{fontSize:12}}>№{tn}</span>
              ))}
            </div>
          </div>
        )}
        {weakTasks.length > 0 && (
          <div className="card" style={{padding:18}}>
            <h4 style={{fontSize:14,fontWeight:600,color:'var(--danger)',marginBottom:10}}>Слабые места</h4>
            <div style={{display:'flex',flexWrap:'wrap',gap:6}}>
              {weakTasks.map(tn => (
                <span key={tn} className="badge badge-danger" style={{fontSize:12}}>№{tn}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Tasks Breakdown */}
      <h2 style={{fontSize:17,fontWeight:600,marginBottom:16}}>Разбивка по заданиям</h2>
      <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(290px,1fr))',gap:10,marginBottom:24}}>
        {taskNumbers.map(tn => {
          const t = taskMap[tn] || {};
          const th = theoryMap[tn] || {};
          const acc = t.accuracy || 0;
          const att = t.total_attempts || 0;
          const status = att === 0 ? 'not_started' : acc >= 80 ? 'strong' : acc >= 60 ? 'good' : acc >= 30 ? 'weak' : 'very_weak';
          const statusColors = { not_started: '--text-muted', strong: '--success', good: '--accent', weak: '--warning', very_weak: '--danger' };
          const statusLabels = { not_started: 'Не начато', strong: 'Отлично', good: 'Хорошо', weak: 'Слабо', very_weak: 'Очень слабо' };

          return (
            <div key={tn} className="card-elevated" style={{padding:'12px 16px',display:'flex',alignItems:'center',gap:12}} data-testid={`progress-task-${tn}`}>
              <div style={{
                width:32,height:32,borderRadius:8,display:'flex',alignItems:'center',justifyContent:'center',fontSize:13,fontWeight:700,
                background: status === 'not_started' ? 'var(--bg-app)' : `color-mix(in srgb, var(${statusColors[status]}) 15%, transparent)`,
                color: `var(${statusColors[status]})`,
                border: `1.5px solid var(${statusColors[status]})`,
                flexShrink:0,
              }}>{tn}</div>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontSize:13,fontWeight:500,marginBottom:2,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
                  {th.title || `Задание ${tn}`}
                </div>
                <div className="progress-bar" style={{height:4}}>
                  <div className="progress-fill" style={{width:`${Math.min(acc,100)}%`,background: acc>=80?'var(--success)':acc>=60?'var(--accent)':acc>0?'var(--warning)':'transparent'}}/>
                </div>
              </div>
              <div style={{textAlign:'right',flexShrink:0}}>
                <div style={{fontSize:14,fontWeight:600,color:`var(${statusColors[status]})`}}>{acc > 0 ? `${acc.toFixed(0)}%` : '—'}</div>
                <div style={{fontSize:11,color:'var(--text-muted)'}}>{statusLabels[status]}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Actions */}
      <div style={{display:'flex',gap:10,justifyContent:'center',paddingBottom:24}}>
        <a href="/practice" className="btn btn-primary btn-md" data-testid="go-practice">Решать задания</a>
        <a href="/theory" className="btn btn-secondary btn-md">Изучить теорию</a>
        <a href="/mock-exam" className="btn btn-ghost btn-md">Начать пробник</a>
        <a href="/" className="btn btn-ghost btn-md">На дорожку</a>
      </div>
    </div>
  );
}
