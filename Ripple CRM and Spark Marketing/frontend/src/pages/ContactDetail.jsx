import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, PencilIcon, TrashIcon, PlusIcon, PhoneIcon, EnvelopeIcon, CalendarIcon, DocumentTextIcon, PaperAirplaneIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const TYPE_ICONS = { email: EnvelopeIcon, call: PhoneIcon, meeting: CalendarIcon, note: DocumentTextIcon };
const TYPE_COLOURS = { email: 'text-gold bg-gold/10', call: 'text-healthy bg-healthy/10', meeting: 'text-purple bg-purple/10', note: 'text-text-secondary bg-surface-light' };

function Field({ label, value, editing, name, onChange }) {
  return (
    <div>
      <label className="text-xs text-text-muted uppercase tracking-wider">{label}</label>
      {editing ? (
        <input value={value || ''} onChange={(e) => onChange(name, e.target.value)}
          className="w-full bg-midnight border border-border rounded px-2 py-1.5 text-sm text-text-primary mt-1 focus:outline-none focus:border-gold" />
      ) : (
        <p className="text-sm text-text-primary mt-1">{value || '—'}</p>
      )}
    </div>
  );
}

function ScoreBrain({ label, score, colour }) {
  return (
    <div className="text-center">
      <div className={`text-2xl font-bold ${colour}`}>{score != null ? Math.round(score) : '--'}</div>
      <div className="text-xs text-text-muted mt-0.5">{label}</div>
    </div>
  );
}

export default function ContactDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [contact, setContact] = useState(null);
  const [editing, setEditing] = useState(false);
  const [editData, setEditData] = useState({});
  const [loading, setLoading] = useState(true);
  const [timeline, setTimeline] = useState([]);
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [showLogInteraction, setShowLogInteraction] = useState(false);
  const [interactionForm, setInteractionForm] = useState({ type: 'email', subject: '', content: '', channel: '', duration_minutes: '' });

  // Phase 2: Email + Scoring state
  const [activeTab, setActiveTab] = useState('activity');
  const [emails, setEmails] = useState([]);
  const [showCompose, setShowCompose] = useState(false);
  const [composeForm, setComposeForm] = useState({ to_addresses: [], subject: '', body_text: '' });
  const [leadScore, setLeadScore] = useState(null);
  const [scoringLoading, setScoringLoading] = useState(false);

  // Phase 3: Consent preferences
  const [consentPrefs, setConsentPrefs] = useState(null);
  const [consentSaving, setConsentSaving] = useState(false);

  useEffect(() => {
    api.get(`/contacts/${id}`)
      .then((c) => { setContact(c); setEditData(c); setLoading(false); })
      .catch(() => { toast('Contact not found', 'error'); navigate('/contacts'); });
  }, [id, navigate]);

  const fetchTimeline = useCallback(async () => {
    try {
      const data = await api.get(`/contacts/${id}/interactions?page_size=50`);
      setTimeline(data.items);
    } catch { /* ignore */ }
  }, [id]);

  const fetchNotes = useCallback(async () => {
    try {
      const data = await api.get(`/notes?contact_id=${id}&page_size=50`);
      setNotes(data.items);
    } catch { /* ignore */ }
  }, [id]);

  const fetchEmails = useCallback(async () => {
    try {
      const data = await api.get(`/contacts/${id}/emails?page_size=50`);
      setEmails(data.items);
    } catch { /* ignore */ }
  }, [id]);

  const fetchLeadScore = useCallback(async () => {
    try {
      const data = await api.get(`/contacts/${id}/lead-score`);
      setLeadScore(data);
    } catch { /* no score yet */ }
  }, [id]);

  const fetchConsentPrefs = useCallback(async () => {
    try {
      const data = await api.get(`/contacts/${id}/consent-preferences`);
      setConsentPrefs(data);
    } catch { /* no prefs yet */ }
  }, [id]);

  useEffect(() => { fetchTimeline(); fetchNotes(); fetchEmails(); fetchLeadScore(); fetchConsentPrefs(); }, [fetchTimeline, fetchNotes, fetchEmails, fetchLeadScore, fetchConsentPrefs]);

  const handleFieldChange = (name, value) => {
    setEditData((d) => ({ ...d, [name]: value }));
  };

  const handleSave = async () => {
    try {
      const updated = await api.put(`/contacts/${id}`, editData);
      setContact(updated);
      setEditData(updated);
      setEditing(false);
      toast('Contact updated');
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Delete this contact? This action cannot be undone.')) return;
    try {
      await api.delete(`/contacts/${id}`);
      toast('Contact deleted');
      navigate('/contacts');
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleRecalculateScore = async () => {
    setScoringLoading(true);
    try {
      const data = await api.post(`/contacts/${id}/lead-score/recalculate`);
      setLeadScore(data);
      toast('Score recalculated');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setScoringLoading(false);
    }
  };

  const handleSendEmail = async (e) => {
    e.preventDefault();
    const toAddrs = composeForm.to_addresses.length > 0
      ? composeForm.to_addresses
      : (contact.email ? [contact.email] : []);
    if (toAddrs.length === 0) { toast('No email address available', 'error'); return; }
    try {
      await api.post('/emails/send', {
        contact_id: id,
        to_addresses: toAddrs,
        subject: composeForm.subject,
        body_text: composeForm.body_text,
      });
      toast('Email queued');
      setShowCompose(false);
      setComposeForm({ to_addresses: [], subject: '', body_text: '' });
      fetchEmails();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleConsentToggle = async (key) => {
    if (!consentPrefs) return;
    setConsentSaving(true);
    try {
      const updated = await api.put(`/contacts/${id}/consent-preferences`, {
        [key]: !consentPrefs[key],
      });
      setConsentPrefs(updated);
      toast('Consent updated');
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setConsentSaving(false);
    }
  };

  if (loading) return <div className="text-text-muted py-8 text-center">Loading...</div>;
  if (!contact) return null;

  const healthScore = contact.relationship_health_score;
  const healthColour = healthScore == null ? 'text-text-muted' : healthScore >= 70 ? 'text-healthy' : healthScore >= 40 ? 'text-warning' : 'text-critical';
  const healthLabel = healthScore == null ? 'Not scored' : healthScore >= 70 ? 'Healthy' : healthScore >= 40 ? 'Warning' : 'Critical';

  const compositeScore = leadScore?.composite_score;
  const isMql = leadScore?.is_mql;

  return (
    <div>
      <button onClick={() => navigate('/contacts')} className="flex items-center gap-1 text-text-secondary text-sm hover:text-text-primary mb-4">
        <ArrowLeftIcon className="w-4 h-4" /> Back to Contacts
      </button>

      <div className="bg-surface border border-border rounded-xl p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-heading text-2xl font-semibold">
              {contact.first_name} {contact.last_name}
              {isMql && (
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs font-medium bg-gold/20 text-gold">MQL</span>
              )}
            </h1>
            <div className="flex items-center gap-3 mt-2">
              {contact.role && <span className="text-text-secondary text-sm">{contact.role}</span>}
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                contact.type === 'customer' ? 'bg-healthy/10 text-healthy' :
                contact.type === 'contact' ? 'bg-gold/10 text-gold' :
                'bg-surface-light text-text-secondary'
              }`}>{contact.type}</span>
              <span className={`text-xs font-medium ${healthColour}`}>
                {healthScore != null && `${Math.round(healthScore)} — `}{healthLabel}
              </span>
              {contact.trust_decay_days != null && (
                <span className="text-xs text-warning">
                  {contact.trust_decay_days}d since last interaction
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            {editing ? (
              <>
                <button onClick={handleSave}
                  className="px-3 py-1.5 bg-gold text-midnight text-sm font-medium rounded-lg">Save</button>
                <button onClick={() => { setEditing(false); setEditData(contact); }}
                  className="px-3 py-1.5 bg-surface-light text-text-secondary text-sm rounded-lg">Cancel</button>
              </>
            ) : (
              <>
                <button onClick={() => setEditing(true)}
                  className="p-2 hover:bg-surface-light rounded-lg text-text-secondary"><PencilIcon className="w-4 h-4" /></button>
                <button onClick={handleDelete}
                  className="p-2 hover:bg-critical/10 rounded-lg text-critical"><TrashIcon className="w-4 h-4" /></button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Three Brains Score Panel */}
      <div className="bg-surface border border-border rounded-xl p-5 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <SparklesIcon className="w-5 h-5 text-gold" />
            <h2 className="font-heading text-base font-semibold">Three Brains Score</h2>
            {compositeScore != null && (
              <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                compositeScore >= 70 ? 'bg-green-400/10 text-green-400' :
                compositeScore >= 40 ? 'bg-amber-400/10 text-amber-400' :
                'bg-red-400/10 text-red-400'
              }`}>{Math.round(compositeScore)}</span>
            )}
          </div>
          <button onClick={handleRecalculateScore} disabled={scoringLoading}
            className="text-xs bg-gold/10 text-gold px-3 py-1.5 rounded-lg hover:bg-gold/20 disabled:opacity-50">
            {scoringLoading ? 'Scoring...' : 'Recalculate'}
          </button>
        </div>
        {leadScore ? (
          <div className="grid grid-cols-4 gap-4">
            <ScoreBrain label="Fit" score={leadScore.fit_score}
              colour={leadScore.fit_score >= 70 ? 'text-green-400' : leadScore.fit_score >= 40 ? 'text-amber-400' : 'text-red-400'} />
            <ScoreBrain label="Intent" score={leadScore.intent_score}
              colour={leadScore.intent_score >= 70 ? 'text-green-400' : leadScore.intent_score >= 40 ? 'text-amber-400' : 'text-red-400'} />
            <ScoreBrain label="Instinct" score={leadScore.instinct_score}
              colour={leadScore.instinct_score >= 70 ? 'text-green-400' : leadScore.instinct_score >= 40 ? 'text-amber-400' : 'text-red-400'} />
            <ScoreBrain label="Composite" score={leadScore.composite_score}
              colour={leadScore.composite_score >= 70 ? 'text-green-400' : leadScore.composite_score >= 40 ? 'text-amber-400' : 'text-red-400'} />
          </div>
        ) : (
          <p className="text-text-muted text-sm text-center py-2">No score yet. Click Recalculate to generate.</p>
        )}
      </div>

      <div className="bg-surface border border-border rounded-xl p-6 mb-6">
        <h2 className="font-heading text-lg font-semibold mb-4">Details</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <Field label="First Name" value={editing ? editData.first_name : contact.first_name}
            editing={editing} name="first_name" onChange={handleFieldChange} />
          <Field label="Last Name" value={editing ? editData.last_name : contact.last_name}
            editing={editing} name="last_name" onChange={handleFieldChange} />
          <Field label="Email" value={editing ? editData.email : contact.email}
            editing={editing} name="email" onChange={handleFieldChange} />
          <Field label="Phone" value={editing ? editData.phone : contact.phone}
            editing={editing} name="phone" onChange={handleFieldChange} />
          <Field label="Role" value={editing ? editData.role : contact.role}
            editing={editing} name="role" onChange={handleFieldChange} />
          <Field label="Source" value={editing ? editData.source : contact.source}
            editing={editing} name="source" onChange={handleFieldChange} />
          <Field label="LinkedIn" value={editing ? editData.linkedin_url : contact.linkedin_url}
            editing={editing} name="linkedin_url" onChange={handleFieldChange} />
          <Field label="Timezone" value={editing ? editData.timezone : contact.timezone}
            editing={editing} name="timezone" onChange={handleFieldChange} />
          <Field label="Preferred Channel" value={editing ? editData.preferred_channel : contact.preferred_channel}
            editing={editing} name="preferred_channel" onChange={handleFieldChange} />
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-1 mb-4 border-b border-border">
        {[
          { key: 'activity', label: 'Activity', count: timeline.length },
          { key: 'emails', label: 'Emails', count: emails.length },
          { key: 'notes', label: 'Notes', count: notes.length },
          { key: 'consent', label: 'Consent', count: 0 },
        ].map((tab) => (
          <button key={tab.key} onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'border-gold text-gold'
                : 'border-transparent text-text-muted hover:text-text-primary'
            }`}>
            {tab.label}
            {tab.count > 0 && <span className="ml-1.5 text-xs text-text-muted">({tab.count})</span>}
          </button>
        ))}
      </div>

      {/* Activity Tab */}
      {activeTab === 'activity' && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold">Activity Timeline</h2>
            <button onClick={() => setShowLogInteraction(true)}
              className="flex items-center gap-1 text-xs bg-gold/10 text-gold px-3 py-1.5 rounded-lg hover:bg-gold/20">
              <PlusIcon className="w-3 h-3" /> Log Interaction
            </button>
          </div>
          {timeline.length === 0 ? (
            <p className="text-text-secondary text-sm">No interactions yet. Log your first touchpoint.</p>
          ) : (
            <div>
              {timeline.map((i) => {
                const Icon = TYPE_ICONS[i.type] || DocumentTextIcon;
                const colour = TYPE_COLOURS[i.type] || 'text-text-muted bg-surface-light';
                const dt = new Date(i.occurred_at);
                return (
                  <div key={i.id} className="flex gap-4 group">
                    <div className="flex flex-col items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${colour}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="w-px flex-1 bg-border mt-1" />
                    </div>
                    <div className="pb-4 flex-1">
                      <div className="flex items-baseline justify-between">
                        <h4 className="text-sm font-medium text-text-primary">
                          {i.subject || i.type.charAt(0).toUpperCase() + i.type.slice(1)}
                        </h4>
                        <span className="text-xs text-text-muted shrink-0 ml-2">
                          {dt.toLocaleDateString('en-AU', { day: 'numeric', month: 'short' })}
                        </span>
                      </div>
                      {i.content && <p className="text-xs text-text-secondary mt-1 line-clamp-2">{i.content}</p>}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Emails Tab */}
      {activeTab === 'emails' && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold">Email Conversations</h2>
            <button onClick={() => {
              setComposeForm({
                to_addresses: contact.email ? [contact.email] : [],
                subject: '',
                body_text: '',
              });
              setShowCompose(true);
            }}
              className="flex items-center gap-1 text-xs bg-gold/10 text-gold px-3 py-1.5 rounded-lg hover:bg-gold/20">
              <PaperAirplaneIcon className="w-3 h-3" /> Compose
            </button>
          </div>
          {emails.length === 0 ? (
            <p className="text-text-secondary text-sm">No emails yet. Sync or compose your first email.</p>
          ) : (
            <div className="space-y-2">
              {emails.map((em) => {
                const dt = new Date(em.sent_at || em.created_at);
                const isIn = em.direction === 'in';
                return (
                  <div key={em.id} className={`border border-border rounded-lg p-3 ${isIn ? 'bg-midnight' : 'bg-surface-light'}`}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${isIn ? 'bg-blue-400/10 text-blue-400' : 'bg-gold/10 text-gold'}`}>
                            {isIn ? 'IN' : 'OUT'}
                          </span>
                          <span className="text-sm font-medium text-text-primary truncate">{em.subject || '(no subject)'}</span>
                          {em.status === 'pending' && (
                            <span className="text-xs px-1.5 py-0.5 rounded bg-amber-400/10 text-amber-400">pending</span>
                          )}
                        </div>
                        <p className="text-xs text-text-muted mt-1">
                          {isIn ? `From: ${em.from_address}` : `To: ${(em.to_addresses || []).join(', ')}`}
                        </p>
                        {em.body_text && (
                          <p className="text-xs text-text-secondary mt-1 line-clamp-2">{em.body_text}</p>
                        )}
                      </div>
                      <span className="text-xs text-text-muted shrink-0">
                        {dt.toLocaleDateString('en-AU', { day: 'numeric', month: 'short' })}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Notes Tab */}
      {activeTab === 'notes' && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <h2 className="font-heading text-lg font-semibold mb-4">Notes</h2>
          <div className="flex gap-2 mb-4">
            <input value={newNote} onChange={(e) => setNewNote(e.target.value)} placeholder="Add a note..."
              className="flex-1 bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold"
              onKeyDown={async (e) => {
                if (e.key === 'Enter' && newNote.trim()) {
                  try {
                    await api.post('/notes', { contact_id: id, content: newNote.trim() });
                    setNewNote('');
                    fetchNotes();
                    toast('Note added');
                  } catch (err) { toast(err.message, 'error'); }
                }
              }} />
            <button onClick={async () => {
              if (!newNote.trim()) return;
              try {
                await api.post('/notes', { contact_id: id, content: newNote.trim() });
                setNewNote('');
                fetchNotes();
                toast('Note added');
              } catch (err) { toast(err.message, 'error'); }
            }} className="px-3 py-2 bg-gold text-midnight text-sm font-medium rounded-lg">Add</button>
          </div>
          {notes.length === 0 ? (
            <p className="text-text-muted text-sm">No notes yet.</p>
          ) : (
            <div className="space-y-3">
              {notes.map((n) => (
                <div key={n.id} className="bg-midnight border border-border rounded-lg p-3">
                  <p className="text-sm text-text-primary">{n.content}</p>
                  <span className="text-xs text-text-muted mt-1 block">
                    {new Date(n.created_at).toLocaleDateString('en-AU', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Consent Preferences Tab */}
      {activeTab === 'consent' && (
        <div className="bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold">Consent Preferences</h2>
            <span className="text-xs text-text-muted">Australian Privacy Act 1988</span>
          </div>
          {consentPrefs ? (
            <div className="space-y-3">
              {[
                { key: 'email_marketing', label: 'Email Marketing', desc: 'Receive marketing and promotional emails' },
                { key: 'data_processing', label: 'Data Processing', desc: 'Allow processing of personal data for CRM purposes' },
                { key: 'third_party_sharing', label: 'Third Party Sharing', desc: 'Share data with authorised third parties' },
                { key: 'analytics', label: 'Analytics', desc: 'Include in analytics and reporting' },
                { key: 'profiling', label: 'Profiling', desc: 'Use data for lead scoring and profiling' },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-3 bg-midnight border border-border rounded-lg">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{item.label}</p>
                    <p className="text-xs text-text-muted mt-0.5">{item.desc}</p>
                  </div>
                  <button
                    onClick={() => handleConsentToggle(item.key)}
                    disabled={consentSaving}
                    className={`relative w-10 h-5 rounded-full transition-colors ${
                      consentPrefs[item.key] ? 'bg-green-500' : 'bg-surface-light'
                    }`}
                  >
                    <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                      consentPrefs[item.key] ? 'translate-x-5' : 'translate-x-0.5'
                    }`} />
                  </button>
                </div>
              ))}
              <p className="text-xs text-text-muted mt-4">
                Under the Australian Privacy Act 1988, individuals have the right to know how their data is collected,
                used, and disclosed. These preferences control how this contact&apos;s data is processed within Ripple CRM.
              </p>
            </div>
          ) : (
            <p className="text-text-muted text-sm text-center py-4">Loading consent preferences...</p>
          )}
        </div>
      )}

      {/* Log Interaction Modal */}
      <Modal open={showLogInteraction} onClose={() => setShowLogInteraction(false)} title="Log Interaction">
        <form onSubmit={async (e) => {
          e.preventDefault();
          const payload = { contact_id: id, ...interactionForm };
          if (!payload.subject) delete payload.subject;
          if (!payload.content) delete payload.content;
          if (!payload.channel) delete payload.channel;
          if (payload.duration_minutes) payload.duration_minutes = parseInt(payload.duration_minutes);
          else delete payload.duration_minutes;
          try {
            await api.post('/interactions', payload);
            toast('Interaction logged');
            setShowLogInteraction(false);
            setInteractionForm({ type: 'email', subject: '', content: '', channel: '', duration_minutes: '' });
            fetchTimeline();
          } catch (err) { toast(err.message, 'error'); }
        }} className="space-y-3">
          {(() => {
            const cls = 'bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold';
            const set = (k) => (e) => setInteractionForm((f) => ({ ...f, [k]: e.target.value }));
            return <>
              <select value={interactionForm.type} onChange={set('type')} className={`w-full ${cls}`}>
                <option value="email">Email</option>
                <option value="call">Call</option>
                <option value="meeting">Meeting</option>
                <option value="note">Note</option>
              </select>
              <input placeholder="Subject" value={interactionForm.subject} onChange={set('subject')} className={`w-full ${cls}`} />
              <textarea placeholder="Content" value={interactionForm.content} onChange={set('content')} rows={3} className={`w-full ${cls}`} />
              <div className="grid grid-cols-2 gap-3">
                <input placeholder="Channel" value={interactionForm.channel} onChange={set('channel')} className={cls} />
                <input placeholder="Duration (min)" type="number" min="0" value={interactionForm.duration_minutes} onChange={set('duration_minutes')} className={cls} />
              </div>
              <button type="submit" className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">Log Interaction</button>
            </>;
          })()}
        </form>
      </Modal>

      {/* Compose Email Modal */}
      <Modal open={showCompose} onClose={() => setShowCompose(false)} title="Compose Email">
        <form onSubmit={handleSendEmail} className="space-y-3">
          <div>
            <label className="text-xs text-text-muted uppercase tracking-wider">To</label>
            <input
              value={composeForm.to_addresses.join(', ')}
              onChange={(e) => setComposeForm((f) => ({ ...f, to_addresses: e.target.value.split(',').map(s => s.trim()).filter(Boolean) }))}
              placeholder={contact.email || 'recipient@example.com'}
              className="w-full bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold mt-1"
            />
          </div>
          <div>
            <label className="text-xs text-text-muted uppercase tracking-wider">Subject</label>
            <input
              value={composeForm.subject}
              onChange={(e) => setComposeForm((f) => ({ ...f, subject: e.target.value }))}
              required
              placeholder="Email subject"
              className="w-full bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold mt-1"
            />
          </div>
          <div>
            <label className="text-xs text-text-muted uppercase tracking-wider">Body</label>
            <textarea
              value={composeForm.body_text}
              onChange={(e) => setComposeForm((f) => ({ ...f, body_text: e.target.value }))}
              rows={6}
              placeholder="Write your email..."
              className="w-full bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold mt-1"
            />
          </div>
          <p className="text-xs text-text-muted">Email will be stored locally. Actual sending requires SMTP config (Phase 3).</p>
          <button type="submit" className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors flex items-center justify-center gap-2">
            <PaperAirplaneIcon className="w-4 h-4" /> Queue Email
          </button>
        </form>
      </Modal>
    </div>
  );
}
