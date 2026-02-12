import { useEffect, useState } from 'react';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { toast } from '../components/Toast';

export default function PulseSettings() {
  const navigate = useNavigate();
  const [targets, setTargets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    period_type: 'monthly',
    period_label: '',
    period_start: '',
    period_end: '',
    target_value: '',
    currency: 'AUD',
    notes: '',
  });

  const cls =
    'bg-midnight border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-gold w-full';

  useEffect(() => {
    fetchTargets();
  }, []);

  const fetchTargets = async () => {
    try {
      const data = await api.get('/pulse/targets');
      setTargets(data.items || []);
    } catch (e) {
      toast('Failed to load targets', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...form,
        target_value: parseFloat(form.target_value),
      };
      await api.post('/pulse/targets', payload);
      toast('Target created');
      setShowForm(false);
      setForm({
        period_type: 'monthly',
        period_label: '',
        period_start: '',
        period_end: '',
        target_value: '',
        currency: 'AUD',
        notes: '',
      });
      fetchTargets();
    } catch (e) {
      toast(`Error: ${e.message}`, 'error');
    }
  };

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  if (loading) return <div className="p-6 text-text-muted">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/pulse')}
          className="p-1.5 rounded-lg hover:bg-surface-light text-text-secondary"
        >
          <ArrowLeftIcon className="w-5 h-5" />
        </button>
        <h1 className="font-heading text-2xl font-semibold">Pulse Settings</h1>
      </div>

      {/* Targets List */}
      <div className="bg-surface rounded-xl border border-border p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-heading text-lg font-semibold">Sales Targets</h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="px-3 py-1.5 bg-gold hover:bg-gold-light text-midnight rounded-lg text-sm font-medium"
          >
            {showForm ? 'Cancel' : 'New Target'}
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleCreate} className="space-y-3 mb-6 p-4 bg-midnight rounded-lg border border-border">
            <div className="grid grid-cols-2 gap-3">
              <select value={form.period_type} onChange={set('period_type')} className={cls}>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
              </select>
              <input
                placeholder="Label (e.g. February 2026)"
                value={form.period_label}
                onChange={set('period_label')}
                required
                className={cls}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input type="date" value={form.period_start} onChange={set('period_start')} required className={cls} />
              <input type="date" value={form.period_end} onChange={set('period_end')} required className={cls} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input
                type="number"
                step="0.01"
                placeholder="Target value ($)"
                value={form.target_value}
                onChange={set('target_value')}
                required
                className={cls}
              />
              <select value={form.currency} onChange={set('currency')} className={cls}>
                <option value="AUD">AUD</option>
                <option value="USD">USD</option>
              </select>
            </div>
            <input placeholder="Notes (optional)" value={form.notes} onChange={set('notes')} className={cls} />
            <button
              type="submit"
              className="w-full bg-gold hover:bg-gold-light text-midnight font-medium py-2 rounded-lg text-sm"
            >
              Create Target
            </button>
          </form>
        )}

        {targets.length === 0 ? (
          <p className="text-sm text-text-muted py-4 text-center">No targets set yet</p>
        ) : (
          <div className="space-y-2">
            {targets.map((t) => (
              <div
                key={t.id}
                className="flex items-center justify-between p-3 bg-midnight rounded-lg border border-border"
              >
                <div>
                  <p className="text-sm font-medium text-text-primary">{t.period_label}</p>
                  <p className="text-xs text-text-muted">
                    {t.period_type} | {t.period_start} to {t.period_end}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-mono text-gold">
                    ${Number(t.target_value).toLocaleString('en-AU')}
                  </p>
                  <p className="text-xs text-text-muted">{t.currency}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
