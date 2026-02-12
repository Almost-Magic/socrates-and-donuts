import { useEffect, useState } from 'react';
import {
  ShieldCheckIcon,
  DocumentArrowDownIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  TrashIcon,
  ClipboardDocumentListIcon,
} from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import { toast } from '../components/Toast';

function ConsentBadge({ granted }) {
  return granted ? (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-green-400/10 text-green-400">
      <CheckCircleIcon className="w-3.5 h-3.5" /> Granted
    </span>
  ) : (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-400/10 text-red-400">
      <XCircleIcon className="w-3.5 h-3.5" /> Revoked
    </span>
  );
}

const STATUS_COLOURS = {
  pending: 'bg-amber-400/10 text-amber-400',
  processing: 'bg-blue-400/10 text-blue-400',
  completed: 'bg-green-400/10 text-green-400',
  rejected: 'bg-red-400/10 text-red-400',
};

export default function Privacy() {
  const [tab, setTab] = useState('dsar');
  const [contactId, setContactId] = useState('');
  const [report, setReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState(null);

  const [consents, setConsents] = useState([]);
  const [consentLoading, setConsentLoading] = useState(false);
  const [consentTotal, setConsentTotal] = useState(0);

  const [contacts, setContacts] = useState([]);

  // Phase 3: DSAR requests state
  const [dsarRequests, setDsarRequests] = useState([]);
  const [dsarLoading, setDsarLoading] = useState(false);
  const [dsarTotal, setDsarTotal] = useState(0);

  // Load contacts for the dropdown
  useEffect(() => {
    api.get('/contacts?page_size=200')
      .then((d) => setContacts(d.items || []))
      .catch(() => {});
  }, []);

  // Load consents
  const fetchConsents = async () => {
    setConsentLoading(true);
    try {
      const d = await api.get('/privacy/consents?page_size=100');
      setConsents(d.items || []);
      setConsentTotal(d.total || 0);
    } catch { /* ignore */ } finally {
      setConsentLoading(false);
    }
  };

  // Load DSAR requests
  const fetchDsarRequests = async () => {
    setDsarLoading(true);
    try {
      const d = await api.get('/privacy/dsar-requests?page_size=100');
      setDsarRequests(d.items || []);
      setDsarTotal(d.total || 0);
    } catch { /* ignore */ } finally {
      setDsarLoading(false);
    }
  };

  useEffect(() => {
    if (tab === 'consents') fetchConsents();
    if (tab === 'requests') fetchDsarRequests();
  }, [tab]);

  const generateReport = async () => {
    if (!contactId) return;
    setReportLoading(true);
    setReportError(null);
    setReport(null);
    try {
      const data = await api.get(`/privacy/contacts/${contactId}/report`);
      setReport(data);
    } catch (e) {
      setReportError(e.message);
    } finally {
      setReportLoading(false);
    }
  };

  const exportContactData = async () => {
    if (!contactId) return;
    try {
      const res = await fetch(`/api/privacy/contacts/${contactId}/export`);
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contact_${contactId.slice(0, 8)}_export.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast('Data exported');
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  const requestDeletion = async () => {
    if (!contactId) return;
    if (!confirm('Request deletion of all data for this contact? This will create a formal DSAR request.')) return;
    try {
      await api.post(`/privacy/contacts/${contactId}/deletion-request`);
      toast('Deletion request created');
      fetchDsarRequests();
      setTab('requests');
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  const updateDsarStatus = async (requestId, newStatus) => {
    try {
      await api.put(`/privacy/dsar-requests/${requestId}`, { status: newStatus });
      toast(`Request ${newStatus}`);
      fetchDsarRequests();
    } catch (e) {
      toast(e.message, 'error');
    }
  };

  const recordConsent = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const payload = {
      contact_id: form.get('contact_id'),
      consent_type: form.get('consent_type'),
      granted: form.get('granted') === 'true',
      source: form.get('source') || 'manual',
    };
    if (!payload.contact_id || !payload.consent_type) return;
    try {
      await api.post('/privacy/consents', payload);
      e.target.reset();
      fetchConsents();
      toast('Consent recorded');
    } catch { /* ignore */ }
  };

  const createDsarRequest = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const payload = {
      contact_id: form.get('contact_id'),
      request_type: form.get('request_type'),
      notes: form.get('notes') || null,
    };
    if (!payload.contact_id || !payload.request_type) return;
    try {
      await api.post('/privacy/dsar-requests', payload);
      e.target.reset();
      fetchDsarRequests();
      setTab('requests');
      toast('DSAR request created');
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <ShieldCheckIcon className="w-7 h-7 text-gold" />
        <div>
          <h1 className="font-heading text-2xl font-semibold text-text-primary">Transparency Portal</h1>
          <p className="text-sm text-text-muted">Privacy management under the Australian Privacy Act 1988</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface rounded-lg p-1 border border-border w-fit">
        {[
          { key: 'dsar', label: 'DSAR Report' },
          { key: 'consents', label: 'Consent Log' },
          { key: 'requests', label: 'DSAR Requests' },
          { key: 'record', label: 'Record Consent' },
          { key: 'new-request', label: 'New Request' },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              tab === t.key
                ? 'bg-gold/10 text-gold'
                : 'text-text-secondary hover:text-text-primary hover:bg-surface-light'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* DSAR Report Tab */}
      {tab === 'dsar' && (
        <div className="bg-surface rounded-xl border border-border p-6 space-y-6">
          <div>
            <h2 className="font-heading text-lg font-semibold text-text-primary mb-1">
              Data Subject Access Request
            </h2>
            <p className="text-sm text-text-muted">
              Generate a complete report of all data held about a contact (APP 12).
            </p>
          </div>

          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-sm text-text-secondary mb-1">Select Contact</label>
              <select
                value={contactId}
                onChange={(e) => setContactId(e.target.value)}
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Choose a contact...</option>
                {contacts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.first_name} {c.last_name} {c.email ? `(${c.email})` : ''}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={generateReport}
              disabled={!contactId || reportLoading}
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2"
            >
              {reportLoading ? (
                <ArrowPathIcon className="w-4 h-4 animate-spin" />
              ) : (
                <DocumentArrowDownIcon className="w-4 h-4" />
              )}
              Generate Report
            </button>
            <button
              onClick={exportContactData}
              disabled={!contactId}
              className="bg-surface-light hover:bg-surface-light/80 text-text-primary px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2 border border-border"
            >
              <DocumentArrowDownIcon className="w-4 h-4" />
              Export JSON
            </button>
            <button
              onClick={requestDeletion}
              disabled={!contactId}
              className="bg-red-500/10 hover:bg-red-500/20 text-red-400 px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40 flex items-center gap-2 border border-red-500/20"
            >
              <TrashIcon className="w-4 h-4" />
              Request Deletion
            </button>
          </div>

          {reportError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
              <p className="text-red-400 text-sm">{reportError}</p>
            </div>
          )}

          {report && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="font-heading font-semibold text-text-primary">
                  DSAR Report — {report.contact.first_name} {report.contact.last_name}
                </h3>
                <span className="text-xs text-text-muted">
                  Generated {new Date(report.report_generated_at).toLocaleString('en-AU')}
                </span>
              </div>

              {report.compliance_note && (
                <div className="bg-blue-400/5 border border-blue-400/20 rounded-lg p-3">
                  <p className="text-xs text-blue-400">{report.compliance_note}</p>
                </div>
              )}

              {/* Contact Details */}
              <div className="bg-surface-light rounded-lg p-4">
                <h4 className="text-sm font-medium text-text-primary mb-2">Personal Data</h4>
                <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
                  {Object.entries(report.contact)
                    .filter(([k]) => k !== 'id')
                    .map(([k, v]) => (
                      <div key={k} className="flex justify-between">
                        <dt className="text-text-muted capitalize">{k.replace(/_/g, ' ')}</dt>
                        <dd className="text-text-primary">{v || '\u2014'}</dd>
                      </div>
                    ))}
                </dl>
              </div>

              {/* Summary Stats */}
              <div className="grid grid-cols-4 gap-4">
                {[
                  { label: 'Interactions', val: report.total_interactions },
                  { label: 'Notes', val: report.total_notes },
                  { label: 'Commitments', val: report.total_commitments },
                  { label: 'Emails', val: report.total_emails },
                ].map((s) => (
                  <div key={s.label} className="bg-surface-light rounded-lg p-4 text-center">
                    <p className="text-2xl font-heading font-semibold text-text-primary">{s.val}</p>
                    <p className="text-xs text-text-muted">{s.label}</p>
                  </div>
                ))}
              </div>

              {/* Interactions List */}
              {report.interactions.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Interactions ({report.interactions.length})</h4>
                  <div className="divide-y divide-border bg-surface-light rounded-lg overflow-hidden">
                    {report.interactions.map((i) => (
                      <div key={i.id} className="px-4 py-2 text-sm flex items-center justify-between">
                        <div>
                          <span className="font-medium text-text-primary">{i.subject}</span>
                          <span className="text-text-muted ml-2">({i.type})</span>
                        </div>
                        <span className="text-xs text-text-muted">
                          {i.occurred_at ? new Date(i.occurred_at).toLocaleDateString('en-AU') : '\u2014'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Emails */}
              {report.emails && report.emails.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Emails ({report.emails.length})</h4>
                  <div className="divide-y divide-border bg-surface-light rounded-lg overflow-hidden">
                    {report.emails.map((e) => (
                      <div key={e.id} className="px-4 py-2 text-sm flex items-center justify-between">
                        <div>
                          <span className={`text-xs px-1.5 py-0.5 rounded font-medium mr-2 ${e.direction === 'in' ? 'bg-blue-400/10 text-blue-400' : 'bg-gold/10 text-gold'}`}>
                            {e.direction === 'in' ? 'IN' : 'OUT'}
                          </span>
                          <span className="font-medium text-text-primary">{e.subject || '(no subject)'}</span>
                        </div>
                        <span className="text-xs text-text-muted">
                          {e.created_at ? new Date(e.created_at).toLocaleDateString('en-AU') : '\u2014'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes */}
              {report.notes.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Notes ({report.notes.length})</h4>
                  <div className="space-y-2">
                    {report.notes.map((n) => (
                      <div key={n.id} className="bg-surface-light rounded-lg p-3 text-sm">
                        <p className="text-text-primary">{n.content}</p>
                        <p className="text-xs text-text-muted mt-1">
                          {n.created_at ? new Date(n.created_at).toLocaleDateString('en-AU') : '\u2014'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Commitments */}
              {report.commitments.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Commitments ({report.commitments.length})</h4>
                  <div className="divide-y divide-border bg-surface-light rounded-lg overflow-hidden">
                    {report.commitments.map((c) => (
                      <div key={c.id} className="px-4 py-2 text-sm flex items-center justify-between">
                        <div>
                          <span className="font-medium text-text-primary">{c.description}</span>
                          <span className="text-text-muted ml-2">({c.committed_by})</span>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          c.status === 'fulfilled' ? 'bg-green-400/10 text-green-400' :
                          c.status === 'broken' ? 'bg-red-400/10 text-red-400' :
                          'bg-amber-400/10 text-amber-400'
                        }`}>
                          {c.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Consents */}
              {report.consents.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-text-primary mb-2">Consent Records ({report.consents.length})</h4>
                  <div className="divide-y divide-border bg-surface-light rounded-lg overflow-hidden">
                    {report.consents.map((c) => (
                      <div key={c.id} className="px-4 py-2 text-sm flex items-center justify-between">
                        <div>
                          <span className="font-medium text-text-primary">{c.consent_type}</span>
                          <span className="text-text-muted ml-2">via {c.source || 'unknown'}</span>
                        </div>
                        <ConsentBadge granted={c.granted} />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Consent Log Tab */}
      {tab === 'consents' && (
        <div className="bg-surface rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary">
              Consent Log
              <span className="text-sm text-text-muted font-normal ml-2">({consentTotal} records)</span>
            </h2>
            <button
              onClick={fetchConsents}
              className="p-2 rounded-lg hover:bg-surface-light text-text-muted hover:text-text-primary"
            >
              <ArrowPathIcon className={`w-4 h-4 ${consentLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {consents.length === 0 ? (
            <p className="text-sm text-text-muted text-center py-8">No consent records yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-text-muted border-b border-border">
                    <th className="pb-2 font-medium">Contact</th>
                    <th className="pb-2 font-medium">Type</th>
                    <th className="pb-2 font-medium">Status</th>
                    <th className="pb-2 font-medium">Source</th>
                    <th className="pb-2 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {consents.map((c) => {
                    const contact = contacts.find((ct) => ct.id === c.contact_id);
                    return (
                      <tr key={c.id} className="text-text-primary">
                        <td className="py-2">
                          {contact ? `${contact.first_name} ${contact.last_name}` : c.contact_id.slice(0, 8)}
                        </td>
                        <td className="py-2">{c.consent_type}</td>
                        <td className="py-2"><ConsentBadge granted={c.granted} /></td>
                        <td className="py-2 text-text-muted">{c.source || '\u2014'}</td>
                        <td className="py-2 text-text-muted">
                          {c.created_at ? new Date(c.created_at).toLocaleDateString('en-AU') : '\u2014'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* DSAR Requests Tab */}
      {tab === 'requests' && (
        <div className="bg-surface rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-lg font-semibold text-text-primary">
              DSAR Requests
              <span className="text-sm text-text-muted font-normal ml-2">({dsarTotal} requests)</span>
            </h2>
            <button
              onClick={fetchDsarRequests}
              className="p-2 rounded-lg hover:bg-surface-light text-text-muted hover:text-text-primary"
            >
              <ArrowPathIcon className={`w-4 h-4 ${dsarLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {dsarRequests.length === 0 ? (
            <p className="text-sm text-text-muted text-center py-8">No DSAR requests yet</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-text-muted border-b border-border">
                    <th className="pb-2 font-medium">Contact</th>
                    <th className="pb-2 font-medium">Type</th>
                    <th className="pb-2 font-medium">Status</th>
                    <th className="pb-2 font-medium">Requested</th>
                    <th className="pb-2 font-medium">Completed</th>
                    <th className="pb-2 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {dsarRequests.map((r) => {
                    const contact = contacts.find((ct) => ct.id === r.contact_id);
                    return (
                      <tr key={r.id} className="text-text-primary">
                        <td className="py-2">
                          {contact ? `${contact.first_name} ${contact.last_name}` : r.contact_id.slice(0, 8)}
                        </td>
                        <td className="py-2 capitalize">{r.request_type}</td>
                        <td className="py-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLOURS[r.status] || ''}`}>
                            {r.status}
                          </span>
                        </td>
                        <td className="py-2 text-text-muted">
                          {r.requested_at ? new Date(r.requested_at).toLocaleDateString('en-AU') : '\u2014'}
                        </td>
                        <td className="py-2 text-text-muted">
                          {r.completed_at ? new Date(r.completed_at).toLocaleDateString('en-AU') : '\u2014'}
                        </td>
                        <td className="py-2">
                          {r.status === 'pending' && (
                            <div className="flex gap-1">
                              <button onClick={() => updateDsarStatus(r.id, 'processing')}
                                className="text-xs px-2 py-1 bg-blue-400/10 text-blue-400 rounded hover:bg-blue-400/20">
                                Process
                              </button>
                              <button onClick={() => updateDsarStatus(r.id, 'rejected')}
                                className="text-xs px-2 py-1 bg-red-400/10 text-red-400 rounded hover:bg-red-400/20">
                                Reject
                              </button>
                            </div>
                          )}
                          {r.status === 'processing' && (
                            <button onClick={() => updateDsarStatus(r.id, 'completed')}
                              className="text-xs px-2 py-1 bg-green-400/10 text-green-400 rounded hover:bg-green-400/20">
                              Complete
                            </button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Record Consent Tab */}
      {tab === 'record' && (
        <div className="bg-surface rounded-xl border border-border p-6 max-w-lg">
          <h2 className="font-heading text-lg font-semibold text-text-primary mb-4">Record New Consent</h2>
          <form onSubmit={recordConsent} className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1">Contact</label>
              <select
                name="contact_id"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Choose a contact...</option>
                {contacts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.first_name} {c.last_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Consent Type</label>
              <select
                name="consent_type"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Select type...</option>
                <option value="email_marketing">Email Marketing</option>
                <option value="data_processing">Data Processing</option>
                <option value="third_party_sharing">Third Party Sharing</option>
                <option value="analytics">Analytics</option>
                <option value="profiling">Profiling</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Status</label>
              <select
                name="granted"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="true">Granted</option>
                <option value="false">Revoked</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Source</label>
              <input
                name="source"
                placeholder="e.g. email, phone, in-person"
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              />
            </div>
            <button
              type="submit"
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium"
            >
              Record Consent
            </button>
          </form>
        </div>
      )}

      {/* New DSAR Request Tab */}
      {tab === 'new-request' && (
        <div className="bg-surface rounded-xl border border-border p-6 max-w-lg">
          <h2 className="font-heading text-lg font-semibold text-text-primary mb-1">New DSAR Request</h2>
          <p className="text-sm text-text-muted mb-4">
            Create a formal Data Subject Access Request under the Australian Privacy Act 1988.
          </p>
          <form onSubmit={createDsarRequest} className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1">Contact</label>
              <select
                name="contact_id"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Choose a contact...</option>
                {contacts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.first_name} {c.last_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Request Type</label>
              <select
                name="request_type"
                required
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              >
                <option value="">Select type...</option>
                <option value="access">Access (APP 12)</option>
                <option value="export">Export (data portability)</option>
                <option value="deletion">Deletion (APP 13)</option>
                <option value="rectification">Rectification (APP 13)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-text-secondary mb-1">Notes</label>
              <textarea
                name="notes"
                rows={3}
                placeholder="Additional context for this request..."
                className="w-full bg-surface-light border border-border rounded-lg px-3 py-2 text-sm text-text-primary"
              />
            </div>
            <button
              type="submit"
              className="bg-gold hover:bg-gold/90 text-midnight px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2"
            >
              <ClipboardDocumentListIcon className="w-4 h-4" />
              Submit Request
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
