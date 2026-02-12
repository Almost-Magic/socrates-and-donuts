import { useEffect, useState, useCallback } from 'react';
import { PlusIcon, PencilIcon, TrashIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { api } from '../lib/api';
import Modal from '../components/Modal';
import { toast } from '../components/Toast';

const BRAINS = ['fit', 'intent', 'instinct'];
const BRAIN_COLOURS = {
  fit: 'bg-blue-400/10 text-blue-400',
  intent: 'bg-green-400/10 text-green-400',
  instinct: 'bg-purple-400/10 text-purple-400',
};

function RuleForm({ initial = {}, onSubmit, submitLabel = 'Create Rule' }) {
  const [form, setForm] = useState({
    brain: 'fit',
    attribute: '',
    label: '',
    points: 0,
    max_points: 100,
    description: '',
    is_active: true,
    sort_order: 0,
    ...initial,
  });
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }));
  const cls = 'w-full bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold';

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form); }} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-text-muted uppercase tracking-wider">Brain</label>
          <select value={form.brain} onChange={set('brain')} className={`${cls} mt-1`}>
            {BRAINS.map((b) => <option key={b} value={b}>{b.charAt(0).toUpperCase() + b.slice(1)}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-text-muted uppercase tracking-wider">Attribute Key</label>
          <input value={form.attribute} onChange={set('attribute')} required placeholder="e.g. has_email" className={`${cls} mt-1`} />
        </div>
      </div>
      <div>
        <label className="text-xs text-text-muted uppercase tracking-wider">Label</label>
        <input value={form.label} onChange={set('label')} required placeholder="Display name" className={`${cls} mt-1`} />
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label className="text-xs text-text-muted uppercase tracking-wider">Points</label>
          <input type="number" value={form.points} onChange={set('points')} className={`${cls} mt-1`} />
        </div>
        <div>
          <label className="text-xs text-text-muted uppercase tracking-wider">Max Points</label>
          <input type="number" value={form.max_points} onChange={set('max_points')} className={`${cls} mt-1`} />
        </div>
        <div>
          <label className="text-xs text-text-muted uppercase tracking-wider">Sort Order</label>
          <input type="number" value={form.sort_order} onChange={set('sort_order')} className={`${cls} mt-1`} />
        </div>
      </div>
      <div>
        <label className="text-xs text-text-muted uppercase tracking-wider">Description</label>
        <textarea value={form.description || ''} onChange={set('description')} rows={2} placeholder="Optional description" className={`${cls} mt-1`} />
      </div>
      <label className="flex items-center gap-2 text-sm text-text-primary">
        <input type="checkbox" checked={form.is_active} onChange={set('is_active')}
          className="w-4 h-4 rounded border-border bg-midnight" />
        Active
      </label>
      <button type="submit" className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm transition-colors">
        {submitLabel}
      </button>
    </form>
  );
}

export default function ScoringRules() {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [brainFilter, setBrainFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [editingRule, setEditingRule] = useState(null);

  const fetchRules = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (brainFilter) params.set('brain', brainFilter);
      const data = await api.get(`/scoring/rules?${params}`);
      setRules(data.items);
    } catch (err) {
      toast(err.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [brainFilter]);

  useEffect(() => { fetchRules(); }, [fetchRules]);

  const handleCreate = async (form) => {
    try {
      form.points = parseFloat(form.points);
      form.max_points = parseFloat(form.max_points);
      form.sort_order = parseInt(form.sort_order);
      await api.post('/scoring/rules', form);
      toast('Rule created');
      setShowCreate(false);
      fetchRules();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleUpdate = async (form) => {
    try {
      form.points = parseFloat(form.points);
      form.max_points = parseFloat(form.max_points);
      form.sort_order = parseInt(form.sort_order);
      await api.put(`/scoring/rules/${editingRule.id}`, form);
      toast('Rule updated');
      setEditingRule(null);
      fetchRules();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  const handleDelete = async (ruleId) => {
    if (!confirm('Delete this scoring rule?')) return;
    try {
      await api.delete(`/scoring/rules/${ruleId}`);
      toast('Rule deleted');
      fetchRules();
    } catch (err) {
      toast(err.message, 'error');
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center gap-2">
            <SparklesIcon className="w-6 h-6 text-gold" />
            <h1 className="font-heading text-2xl font-semibold">Scoring Rules</h1>
          </div>
          <p className="text-text-secondary text-sm mt-1">Configure Three Brains lead scoring rules</p>
        </div>
        <button onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-gold hover:bg-gold-light text-midnight font-medium px-4 py-2 rounded-lg text-sm transition-colors">
          <PlusIcon className="w-4 h-4" /> Add Rule
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        <button onClick={() => setBrainFilter('')}
          className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${!brainFilter ? 'bg-gold/10 text-gold font-medium' : 'text-text-muted hover:text-text-primary'}`}>
          All
        </button>
        {BRAINS.map((b) => (
          <button key={b} onClick={() => setBrainFilter(b)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${brainFilter === b ? 'bg-gold/10 text-gold font-medium' : 'text-text-muted hover:text-text-primary'}`}>
            {b.charAt(0).toUpperCase() + b.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-text-muted text-sm py-8 text-center">Loading rules...</div>
      ) : rules.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <SparklesIcon className="w-12 h-12 text-text-muted mx-auto mb-3" />
          <p className="text-lg mb-2">No scoring rules yet</p>
          <p className="text-sm">Add rules to customise how contacts are scored across the three brains.</p>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">Brain</th>
                <th className="text-left px-4 py-3">Label</th>
                <th className="text-left px-4 py-3">Attribute</th>
                <th className="text-right px-4 py-3">Points</th>
                <th className="text-right px-4 py-3">Max</th>
                <th className="text-center px-4 py-3">Active</th>
                <th className="text-right px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rules.map((r) => (
                <tr key={r.id} className="border-b border-border hover:bg-surface-light transition-colors">
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${BRAIN_COLOURS[r.brain] || 'bg-surface-light text-text-muted'}`}>
                      {r.brain}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-text-primary">{r.label}</td>
                  <td className="px-4 py-3 text-text-secondary font-mono text-xs">{r.attribute}</td>
                  <td className="px-4 py-3 text-right text-text-primary">{r.points}</td>
                  <td className="px-4 py-3 text-right text-text-muted">{r.max_points}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`w-2 h-2 rounded-full inline-block ${r.is_active ? 'bg-green-400' : 'bg-red-400'}`} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex gap-1 justify-end">
                      <button onClick={() => setEditingRule(r)}
                        className="p-1.5 hover:bg-surface-light rounded text-text-secondary"><PencilIcon className="w-3.5 h-3.5" /></button>
                      <button onClick={() => handleDelete(r.id)}
                        className="p-1.5 hover:bg-critical/10 rounded text-critical"><TrashIcon className="w-3.5 h-3.5" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Create Scoring Rule">
        <RuleForm onSubmit={handleCreate} />
      </Modal>

      <Modal open={!!editingRule} onClose={() => setEditingRule(null)} title="Edit Scoring Rule">
        {editingRule && <RuleForm initial={editingRule} onSubmit={handleUpdate} submitLabel="Update Rule" />}
      </Modal>
    </div>
  );
}
