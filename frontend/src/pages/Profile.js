import React, { useState, useEffect } from 'react';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ProfilePage({ profile: initialProfile }) {
  const [profile, setProfile] = useState(initialProfile || {});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showReset, setShowReset] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/profile`).then(r => r.json()).then(data => {
      if (data.exists) setProfile(data);
    }).catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch(`${API}/api/profile`, {
        method: 'PUT',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({
          name: profile.name,
          target_score: profile.target_score,
          exam_date: profile.exam_date,
          confidence_level: profile.confidence_level,
          font_size: profile.font_size,
        }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch(e) { console.error(e); }
    setSaving(false);
  };

  const update = (key, val) => setProfile(prev => ({...prev, [key]: val}));

  return (
    <div className="fade-in" style={{maxWidth:600,margin:'0 auto'}}>
      <h1 style={{fontSize:22,fontWeight:700,marginBottom:24}}>Профиль</h1>

      <div className="card" style={{padding:24,marginBottom:20}}>
        <h2 style={{fontSize:16,fontWeight:600,marginBottom:16}}>Личные данные</h2>
        <div style={{display:'flex',flexDirection:'column',gap:16}}>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Имя / ник</label>
            <input className="input" value={profile.name || ''} onChange={e => update('name', e.target.value)} data-testid="profile-name" />
          </div>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Целевой балл</label>
            <input className="input" type="number" min={0} max={100} value={profile.target_score || 80} onChange={e => update('target_score', +e.target.value)} data-testid="profile-score" />
          </div>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Дата экзамена</label>
            <input className="input" type="date" value={profile.exam_date || ''} onChange={e => update('exam_date', e.target.value)} data-testid="profile-date" />
          </div>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Уровень уверенности</label>
            <div className="segment-control" style={{width:'100%'}}>
              {[{v:'low',l:'Начальный'},{v:'medium',l:'Средний'},{v:'high',l:'Уверенный'}].map(o => (
                <button key={o.v} className={`segment-btn ${profile.confidence_level===o.v?'active':''}`}
                  onClick={() => update('confidence_level', o.v)} style={{flex:1}}>{o.l}</button>
              ))}
            </div>
          </div>
          <div>
            <label style={{fontSize:13,color:'var(--text-secondary)',marginBottom:6,display:'block'}}>Размер шрифта редактора</label>
            <input className="input" type="number" min={10} max={24} value={profile.font_size || 14} onChange={e => update('font_size', +e.target.value)} />
          </div>
        </div>

        <div style={{display:'flex',gap:10,marginTop:20,alignItems:'center'}}>
          <button className="btn btn-primary btn-md" onClick={handleSave} disabled={saving} data-testid="save-profile-btn">
            {saving ? 'Сохранение...' : 'Сохранить'}
          </button>
          {saved && <span style={{color:'var(--success)',fontSize:13}}>Сохранено!</span>}
        </div>
      </div>

      {/* Statistics */}
      <div className="card" style={{padding:24,marginBottom:20}}>
        <h2 style={{fontSize:16,fontWeight:600,marginBottom:16}}>Статистика</h2>
        <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12}}>
          <div className="card-elevated" style={{padding:12,textAlign:'center'}}>
            <div style={{fontSize:20,fontWeight:700,color:'var(--accent)'}}>{profile.total_exercises_done || 0}</div>
            <div style={{fontSize:12,color:'var(--text-muted)'}}>Решено заданий</div>
          </div>
          <div className="card-elevated" style={{padding:12,textAlign:'center'}}>
            <div style={{fontSize:20,fontWeight:700,color:'var(--success)'}}>{profile.total_correct || 0}</div>
            <div style={{fontSize:12,color:'var(--text-muted)'}}>Правильных</div>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="card" style={{padding:24,borderColor:'rgba(224,96,112,0.3)'}}>
        <h2 style={{fontSize:16,fontWeight:600,marginBottom:12,color:'var(--danger)'}}>Опасная зона</h2>
        <button className="btn btn-danger btn-sm" onClick={() => setShowReset(true)} data-testid="reset-progress-btn">
          Сбросить весь прогресс
        </button>
        <p style={{color:'var(--text-muted)',fontSize:12,marginTop:8}}>
          Это действие удалит все данные о прогрессе, попытках и пробниках.
        </p>
      </div>

      {/* Reset Confirmation Modal */}
      {showReset && (
        <div className="modal-overlay">
          <div className="modal" style={{textAlign:'center'}} data-testid="reset-modal">
            <h3 style={{fontSize:18,fontWeight:600,marginBottom:12,color:'var(--danger)'}}>Сбросить прогресс?</h3>
            <p style={{color:'var(--text-secondary)',fontSize:14,marginBottom:24}}>
              Все данные будут безвозвратно удалены: прогресс, попытки, пробники, weekly review.
            </p>
            <div style={{display:'flex',gap:10,justifyContent:'center'}}>
              <button className="btn btn-danger btn-md" onClick={async () => {
                await fetch(`${API}/api/profile/reset`, {
                  method: 'POST',
                  headers: {'Content-Type':'application/json'},
                });
                setShowReset(false);
                window.location.reload();
              }} data-testid="confirm-reset-btn">Да, сбросить</button>
              <button className="btn btn-secondary btn-md" onClick={() => setShowReset(false)}>Отмена</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
