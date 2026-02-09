const App = {
  state: { role:null, theme:'dark', onboarded:false, checkins:[], symptoms:[], medications:[], appointments:[], gooddays:[], journal:[], doctorQuestions:[], handoffs:[] },
  _importFile:null, _breathInterval:null, _breathRunning:false, _currentSev:5, _glossaryCat:'all',

  init() {
    this.load();
    if(this.state.theme==='light') document.documentElement.setAttribute('data-theme','light');
    document.getElementById('theme-btn').textContent = this.state.theme==='dark'?'🌙':'☀️';
    if(this.state.onboarded && this.state.role) this.go('screen-home');
    this.buildSev();
    this.renderAll();
  },

  save() { try{localStorage.setItem('besideyou',JSON.stringify(this.state))}catch(e){} },
  load() { try{const s=localStorage.getItem('besideyou');if(s)this.state={...this.state,...JSON.parse(s)}}catch(e){} },

  go(id) {
    document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    const nav=!['screen-welcome','screen-role'].includes(id);
    document.getElementById('bottom-nav').style.display=nav?'flex':'none';
    const fab=!['screen-welcome','screen-role','screen-crisis'].includes(id);
    document.getElementById('crisis-fab').classList.toggle('visible',fab);
    const nm={'screen-home':0,'screen-symptoms':1,'screen-checkin':1,'screen-medications':2,'screen-gooddays':3,'screen-resources':4,'screen-crisis':4};
    document.querySelectorAll('.nav-item').forEach((n,i)=>n.classList.toggle('active',i===nm[id]));
    if(id==='screen-home') this.updateGreeting();
    window.scrollTo(0,0);
  },
  nav(s,e){this.go(s)},

  setRole(role) {
    this.state.role=role; this.state.onboarded=true; this.save();
    document.getElementById('qa-carer').style.display=role==='carer'?'block':'none';
    document.getElementById('qa-patient').style.display=role==='carer'?'none':'block';
    this.go('screen-home');
  },

  toggleTheme() {
    this.state.theme=this.state.theme==='dark'?'light':'dark';
    if(this.state.theme==='light') document.documentElement.setAttribute('data-theme','light');
    else document.documentElement.removeAttribute('data-theme');
    document.getElementById('theme-btn').textContent=this.state.theme==='dark'?'🌙':'☀️';
    this.save();
  },

  updateGreeting() {
    const h=new Date().getHours();
    document.getElementById('greeting').textContent=h<12?'Good morning.':h<17?'Good afternoon.':'Good evening.';
    document.getElementById('qa-carer').style.display=this.state.role==='carer'?'block':'none';
    document.getElementById('qa-patient').style.display=this.state.role==='carer'?'none':'block';
  },

  // Check-in
  pickMood(btn) { document.querySelectorAll('#mood-grid .mood-btn').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); },
  saveCheckin() {
    const mood=document.querySelector('#mood-grid .mood-btn.active')?.dataset.mood||'';
    const syms=Array.from(document.querySelectorAll('#checkin-symptoms .pill.active')).map(p=>p.textContent);
    const notes=document.getElementById('ci-notes').value;
    const good=document.getElementById('ci-good').value;
    this.state.checkins.unshift({id:Date.now(),date:new Date().toISOString(),mood,symptoms:syms,notes,good});
    if(good.trim()) this.state.gooddays.unshift({id:Date.now()+1,date:new Date().toISOString(),text:good.trim()});
    this.save(); this.toast('Check-in saved ✓');
    document.querySelectorAll('#mood-grid .mood-btn').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('#checkin-symptoms .pill').forEach(p=>p.classList.remove('active'));
    document.getElementById('ci-notes').value=''; document.getElementById('ci-good').value='';
    this.go('screen-home'); this.renderAll();
  },

  // Symptoms
  pickSymType(btn) {
    document.querySelectorAll('#modal-symptom .pill').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active'); document.getElementById('sym-name').value=btn.textContent;
  },
  buildSev() {
    const el=document.getElementById('sev-scale'); if(!el)return; el.innerHTML='';
    for(let i=1;i<=10;i++){const b=document.createElement('button');b.className='sev-btn';b.textContent=i;
    b.onclick=()=>{document.querySelectorAll('.sev-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');this._currentSev=i;};el.appendChild(b);}
  },
  saveSymptom() {
    const name=document.getElementById('sym-name').value.trim();
    if(!name){this.toast('Please enter a symptom');return;}
    this.state.symptoms.unshift({id:Date.now(),date:new Date().toISOString(),name,severity:this._currentSev,notes:document.getElementById('sym-notes').value});
    this.save(); this.closeModal('modal-symptom'); this.toast('Symptom logged ✓'); this.renderSymptoms();
  },
  renderSymptoms() {
    const el=document.getElementById('symptom-list');
    if(!this.state.symptoms.length){el.innerHTML='<div class="empty"><div class="ei">💓</div><h3>No symptoms logged yet</h3><p class="sub mt-8">When you\'re ready, tap above to log your first symptom.</p></div>';return;}
    el.innerHTML=this.state.symptoms.map(s=>`<div class="li" style="margin-bottom:8px;cursor:default"><div class="li-icon" style="background:${s.severity<=3?'var(--sage)':s.severity<=6?'var(--warm)':'var(--rose)'};color:#fff;font-size:.8rem;font-weight:600;width:36px;height:36px">${s.severity}</div><div style="flex:1;min-width:0"><div class="li-t">${this.esc(s.name)}</div><div class="li-s">${this.fmtDate(s.date)}${s.notes?' · '+this.esc(s.notes):''}</div></div><button class="del-btn" onclick="App.del('symptoms',${s.id})">✕</button></div>`).join('');
  },

  // Medications
  saveMed() {
    const name=document.getElementById('med-name').value.trim();
    if(!name){this.toast('Please enter a medication name');return;}
    this.state.medications.unshift({id:Date.now(),name,dose:document.getElementById('med-dose').value,frequency:document.getElementById('med-freq').value,purpose:document.getElementById('med-purpose').value,questions:document.getElementById('med-q').value,date:new Date().toISOString()});
    this.save(); this.closeModal('modal-med'); this.toast('Medication added ✓'); this.renderMeds();
  },
  renderMeds() {
    const el=document.getElementById('med-list');
    if(!this.state.medications.length){el.innerHTML='<div class="empty"><div class="ei">💊</div><h3>No medications added yet</h3><p class="sub mt-8">Add your medications so you have them all in one place.</p></div>';return;}
    el.innerHTML=this.state.medications.map(m=>`<div class="li" style="margin-bottom:8px;cursor:default"><div class="li-icon warm">💊</div><div style="flex:1;min-width:0"><div class="li-t">${this.esc(m.name)}${m.dose?' — '+this.esc(m.dose):''}</div><div class="li-s">${m.frequency?this.esc(m.frequency):''}${m.purpose?' · '+this.esc(m.purpose):''}</div>${m.questions?'<div class="li-s" style="color:var(--sky);margin-top:4px">❓ '+this.esc(m.questions)+'</div>':''}</div><button class="del-btn" onclick="App.del('medications',${m.id})">✕</button></div>`).join('');
  },

  // Appointments
  saveAppt() {
    const type=document.getElementById('appt-type').value.trim();
    if(!type){this.toast('Please enter the appointment type');return;}
    this.state.appointments.unshift({id:Date.now(),type,date:document.getElementById('appt-date').value,time:document.getElementById('appt-time').value,location:document.getElementById('appt-loc').value,notes:document.getElementById('appt-notes').value});
    this.save(); this.closeModal('modal-appt'); this.toast('Appointment added ✓'); this.renderAppts();
  },
  renderAppts() {
    const el=document.getElementById('appt-list');
    if(!this.state.appointments.length){el.innerHTML='<div class="empty" style="padding:24px"><div class="ei">📅</div><h3>No appointments yet</h3></div>';return;}
    el.innerHTML=this.state.appointments.map(a=>`<div class="li" style="margin-bottom:8px;cursor:default"><div class="li-icon gold">📅</div><div style="flex:1;min-width:0"><div class="li-t">${this.esc(a.type)}</div><div class="li-s">${a.date?this.fmtDateShort(a.date):'No date'}${a.time?' at '+a.time:''}${a.location?' · '+this.esc(a.location):''}</div>${a.notes?'<div class="li-s" style="margin-top:4px">'+this.esc(a.notes)+'</div>':''}</div><button class="del-btn" onclick="App.del('appointments',${a.id})">✕</button></div>`).join('');
  },

  // Doctor Questions
  addDQ() {
    const inp=document.getElementById('dq-input');const q=inp.value.trim();if(!q)return;
    this.state.doctorQuestions.unshift({id:Date.now(),text:q,done:false});inp.value='';this.save();this.renderDQ();
  },
  toggleDQ(id) { const q=this.state.doctorQuestions.find(x=>x.id===id);if(q)q.done=!q.done;this.save();this.renderDQ(); },
  renderDQ() {
    const el=document.getElementById('dq-list');if(!this.state.doctorQuestions.length){el.innerHTML='';return;}
    el.innerHTML=this.state.doctorQuestions.map(q=>`<div class="dq"><button class="dq-check ${q.done?'done':''}" onclick="App.toggleDQ(${q.id})">${q.done?'✓':''}</button><div class="dq-text" style="${q.done?'text-decoration:line-through;color:var(--t3)':''}">${this.esc(q.text)}</div><button class="del-btn" onclick="App.del('doctorQuestions',${q.id})" style="width:24px;height:24px">✕</button></div>`).join('');
  },

  // Good Days Jar
  addGoodDay() {
    const inp=document.getElementById('gd-input');const t=inp.value.trim();if(!t)return;
    this.state.gooddays.unshift({id:Date.now(),date:new Date().toISOString(),text:t});inp.value='';this.save();this.toast('Moment saved ✨');this.renderGoodDays();
  },
  renderGoodDays() {
    const el=document.getElementById('gd-list');
    if(!this.state.gooddays.length){el.innerHTML='<div class="empty"><div class="ei">✨</div><h3>Your jar is waiting</h3><p class="sub mt-8">Add your first moment above.</p></div>';return;}
    el.innerHTML=this.state.gooddays.map(g=>`<div class="gd-moment"><div class="gd-icon">✨</div><div class="gd-body"><div class="gd-text">${this.esc(g.text)}</div><div class="gd-date">${this.fmtDate(g.date)}</div></div><button class="del-btn" onclick="App.del('gooddays',${g.id})">✕</button></div>`).join('');
  },

  // Journal
  saveJournal() {
    const inp=document.getElementById('journal-input');const t=inp.value.trim();if(!t)return;
    this.state.journal.unshift({id:Date.now(),date:new Date().toISOString(),text:t});inp.value='';this.save();this.toast('Entry saved ✓');this.renderJournal();
  },
  renderJournal() {
    const el=document.getElementById('journal-list');
    if(!this.state.journal.length){el.innerHTML='<div class="empty"><div class="ei">📝</div><h3>No entries yet</h3><p class="sub mt-8">Write whatever is on your mind.</p></div>';return;}
    el.innerHTML=this.state.journal.map(j=>`<div class="j-entry"><div class="j-date">${this.fmtDate(j.date)}</div><div class="j-text">${this.esc(j.text)}</div><button class="del-btn mt-8" onclick="App.del('journal',${j.id})">✕</button></div>`).join('');
  },

  // Glossary
  filterGlossary() {
    const q=document.getElementById('glossary-search').value.toLowerCase();
    this.renderGlossary(q);
  },
  filterGlossaryCat(btn,cat) {
    document.querySelectorAll('#glossary-filters .pill').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active'); this._glossaryCat=cat; this.renderGlossary();
  },
  renderGlossary(search) {
    const q=(search||document.getElementById('glossary-search')?.value||'').toLowerCase();
    const cat=this._glossaryCat;
    let terms=GLOSSARY.filter(t=>{
      if(cat!=='all'&&t.cat!==cat)return false;
      if(q&&!t.term.toLowerCase().includes(q)&&!t.def.toLowerCase().includes(q))return false;
      return true;
    });
    const el=document.getElementById('glossary-list');
    if(!terms.length){el.innerHTML='<div class="empty" style="padding:32px"><p class="sub">No terms found. Try a different search.</p></div>';return;}
    el.innerHTML=terms.map(t=>`<div class="gl-term" onclick="this.classList.toggle('open')"><div class="gl-name">${this.esc(t.term)}</div><div class="gl-def">${this.esc(t.def)}</div><div class="gl-cat">${t.cat}</div></div>`).join('');
  },

  // Resources
  filterRes(btn,cat) {
    document.querySelectorAll('#screen-resources .pill').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active'); this.renderResources(cat);
  },
  renderResources(cat) {
    cat=cat||'all';
    const el=document.getElementById('resources-list');
    let res=RESOURCES.filter(r=>cat==='all'||r.cat===cat);
    el.innerHTML=res.map(r=>`<div class="rcard"><div class="rcard-t">${this.esc(r.name)}</div><div class="rcard-d">${this.esc(r.desc)}</div><div style="margin-top:8px;display:flex;gap:12px">${r.phone?`<a href="tel:${r.phone.replace(/\s/g,'')}" class="rcard-a">📞 ${r.phone}</a>`:''}${r.url?`<a href="${r.url}" target="_blank" rel="noopener" class="rcard-a">🔗 Website</a>`:''}</div><div style="margin-top:6px;display:flex;gap:4px">${r.who.split(',').map(w=>`<span style="font-size:.7rem;padding:2px 8px;border-radius:10px;background:var(--sage-s);color:var(--sage)">${w.trim()}</span>`).join('')}</div></div>`).join('');
  },

  // Handoff
  saveHandoff() {
    const meds=document.getElementById('ho-meds').value;
    const mood=document.getElementById('ho-mood').value;
    const notes=document.getElementById('ho-notes').value;
    const upcoming=document.getElementById('ho-upcoming').value;
    if(!meds&&!mood&&!notes&&!upcoming){this.toast('Add at least one detail');return;}
    this.state.handoffs.unshift({id:Date.now(),date:new Date().toISOString(),meds,mood,notes,upcoming});
    this.save();this.toast('Handoff saved ✓');
    ['ho-meds','ho-mood','ho-notes','ho-upcoming'].forEach(id=>document.getElementById(id).value='');
    this.renderHandoffs();
  },
  copyHandoff() {
    const m=document.getElementById('ho-meds').value;const mo=document.getElementById('ho-mood').value;
    const n=document.getElementById('ho-notes').value;const u=document.getElementById('ho-upcoming').value;
    const text=`CARER HANDOFF — ${new Date().toLocaleString()}\n\nMedications: ${m||'—'}\nHow they're doing: ${mo||'—'}\nThings to know: ${n||'—'}\nComing up: ${u||'—'}`;
    navigator.clipboard.writeText(text).then(()=>this.toast('Copied to clipboard ✓')).catch(()=>this.toast('Could not copy'));
  },
  renderHandoffs() {
    const el=document.getElementById('handoff-list');
    if(!this.state.handoffs.length){el.innerHTML='';return;}
    el.innerHTML=this.state.handoffs.slice(0,10).map(h=>`<div class="ho-card"><div class="ho-date">${this.fmtDate(h.date)}</div>${h.meds?'<div class="ho-section"><strong>Meds</strong><p>'+this.esc(h.meds)+'</p></div>':''}${h.mood?'<div class="ho-section"><strong>Status</strong><p>'+this.esc(h.mood)+'</p></div>':''}${h.notes?'<div class="ho-section"><strong>Notes</strong><p>'+this.esc(h.notes)+'</p></div>':''}${h.upcoming?'<div class="ho-section"><strong>Coming up</strong><p>'+this.esc(h.upcoming)+'</p></div>':''}<button class="del-btn mt-4" onclick="App.del('handoffs',${h.id})">✕</button></div>`).join('');
  },

  // Breathing
  startBreathing() {
    if(this._breathRunning){this.stopBreathing();return;}
    this._breathRunning=true;
    document.getElementById('breath-btn').textContent='Stop';
    const circle=document.getElementById('breath-circle');const text=document.getElementById('breath-text');
    let phase='inhale';
    const cycle=()=>{
      if(phase==='inhale'){circle.className='breath-circle inhale';text.textContent='Breathe in...';phase='hold1';}
      else if(phase==='hold1'){text.textContent='Hold...';phase='exhale';}
      else if(phase==='exhale'){circle.className='breath-circle exhale';text.textContent='Breathe out...';phase='hold2';}
      else{text.textContent='Hold...';phase='inhale';}
    };
    cycle();
    this._breathInterval=setInterval(cycle,4000);
  },
  stopBreathing() {
    this._breathRunning=false;clearInterval(this._breathInterval);
    document.getElementById('breath-btn').textContent='Start breathing';
    document.getElementById('breath-circle').className='breath-circle';
    document.getElementById('breath-text').textContent='Tap to begin';
  },

  // Export / Import with encryption
  exportData() { this.openModal('modal-export'); },
  async doExport() {
    const p1=document.getElementById('exp-pass').value;const p2=document.getElementById('exp-pass2').value;
    if(!p1){this.toast('Please enter a passphrase');return;}
    if(p1!==p2){this.toast('Passphrases don\'t match');return;}
    try {
      const data=JSON.stringify(this.state);
      const enc=new TextEncoder();const keyMaterial=await crypto.subtle.importKey('raw',enc.encode(p1),'PBKDF2',false,['deriveKey']);
      const salt=crypto.getRandomValues(new Uint8Array(16));const iv=crypto.getRandomValues(new Uint8Array(12));
      const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt,iterations:100000,hash:'SHA-256'},keyMaterial,{name:'AES-GCM',length:256},false,['encrypt']);
      const encrypted=await crypto.subtle.encrypt({name:'AES-GCM',iv},key,enc.encode(data));
      const result=new Uint8Array(salt.length+iv.length+encrypted.byteLength);
      result.set(salt,0);result.set(iv,salt.length);result.set(new Uint8Array(encrypted),salt.length+iv.length);
      const blob=new Blob([result],{type:'application/octet-stream'});
      const url=URL.createObjectURL(blob);const a=document.createElement('a');
      a.href=url;a.download='besideyou-backup-'+new Date().toISOString().slice(0,10)+'.besideyou';
      a.click();URL.revokeObjectURL(url);
      this.closeModal('modal-export');this.toast('Backup downloaded ✓');
      document.getElementById('exp-pass').value='';document.getElementById('exp-pass2').value='';
    } catch(e) { this.toast('Export failed: '+e.message); }
  },
  importData(event) {
    const file=event.target.files[0];if(!file)return;
    const reader=new FileReader();
    reader.onload=()=>{this._importFile=reader.result;this.openModal('modal-import');};
    reader.readAsArrayBuffer(file);
    event.target.value='';
  },
  async doImport() {
    const pass=document.getElementById('imp-pass').value;
    if(!pass){this.toast('Please enter your passphrase');return;}
    try {
      const data=new Uint8Array(this._importFile);
      const salt=data.slice(0,16);const iv=data.slice(16,28);const encrypted=data.slice(28);
      const enc=new TextEncoder();const keyMaterial=await crypto.subtle.importKey('raw',enc.encode(pass),'PBKDF2',false,['deriveKey']);
      const key=await crypto.subtle.deriveKey({name:'PBKDF2',salt,iterations:100000,hash:'SHA-256'},keyMaterial,{name:'AES-GCM',length:256},false,['decrypt']);
      const decrypted=await crypto.subtle.decrypt({name:'AES-GCM',iv},key,encrypted);
      const json=new TextDecoder().decode(decrypted);
      this.state={...this.state,...JSON.parse(json)};this.save();
      this.closeModal('modal-import');this.toast('Data restored ✓');
      document.getElementById('imp-pass').value='';this.renderAll();
    } catch(e) { this.toast('Wrong passphrase or corrupted file'); }
  },

  // Modals
  openModal(id) {
    if(id==='modal-symptom'){document.getElementById('sym-name').value='';document.getElementById('sym-notes').value='';document.querySelectorAll('#modal-symptom .pill').forEach(p=>p.classList.remove('active'));document.querySelectorAll('.sev-btn').forEach(b=>b.classList.remove('active'));this._currentSev=5;}
    if(id==='modal-med'){['med-name','med-dose','med-freq','med-purpose','med-q'].forEach(x=>document.getElementById(x).value='');}
    if(id==='modal-appt'){['appt-type','appt-date','appt-time','appt-loc','appt-notes'].forEach(x=>document.getElementById(x).value='');}
    document.getElementById(id).classList.add('active');
  },
  closeModal(id) { document.getElementById(id).classList.remove('active'); },

  // Delete
  del(collection, id) {
    this.state[collection]=this.state[collection].filter(x=>x.id!==id);this.save();this.renderAll();
  },

  // Render all
  renderAll() {
    this.renderSymptoms();this.renderMeds();this.renderAppts();this.renderDQ();
    this.renderGoodDays();this.renderJournal();this.renderGlossary();this.renderResources();this.renderHandoffs();
  },

  // Toast
  toast(msg) {
    const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
    setTimeout(()=>t.classList.remove('show'),2500);
  },

  // Helpers
  esc(s) { if(!s)return'';const d=document.createElement('div');d.textContent=s;return d.innerHTML; },
  fmtDate(iso) {
    try{const d=new Date(iso);return d.toLocaleDateString('en-AU',{day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});}catch(e){return iso;}
  },
  fmtDateShort(ds) {
    try{const d=new Date(ds+'T00:00:00');return d.toLocaleDateString('en-AU',{weekday:'short',day:'numeric',month:'short'});}catch(e){return ds;}
  }
};

document.addEventListener('DOMContentLoaded',()=>App.init());
