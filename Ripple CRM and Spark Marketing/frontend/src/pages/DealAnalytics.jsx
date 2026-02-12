import { useEffect, useState } from 'react';
import {
  ArrowPathIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';

const stageColours = {
  lead: 'bg-blue-400/10 text-blue-400',
  qualified: 'bg-cyan-400/10 text-cyan-400',
  proposal: 'bg-amber-400/10 text-amber-400',
  negotiation: 'bg-purple-400/10 text-purple-400',
  closed_won: 'bg-green-400/10 text-green-400',
  closed_lost: 'bg-red-400/10 text-red-400',
};

function StageBar({ stage, count, totalValue, maxCount }) {
  const pct = maxCount > 0 ? Math.round((count / maxCount) * 100) : 0;
  return (
    <div className="flex items-center gap-4">
      <span className={`text-xs font-medium px-2 py-0.5 rounded-full w-24 text-center ${stageColours[stage] || 'bg-surface-light text-text-muted'}`}>
        {stage.replace('_', ' ')}
      </span>
      <div className="flex-1">
        <div className="h-6 bg-surface-light rounded-lg overflow-hidden">
          <div
            className="h-full bg-gold/30 rounded-lg flex items-center px-2 transition-all"
            style={{ width: `${Math.max(pct, 8)}%` }}
          >
            <span className="text-xs font-medium text-text-primary">{count}</span>
          </div>
        </div>
      </div>
      <span className="text-sm text-text-muted w-28 text-right">
        ${totalValue.toLocaleString('en-AU')}
      </span>
    </div>
  );
}

export default function DealAnalytics() {
  const [pipeline, setPipeline] = useState(null);
  const [velocity, setVelocity] = useState(null);
  const [stalled, setStalled] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [p, v, s] = await Promise.all([
        fetch('/api/deal-analytics/pipeline').then(r => r.json()),
        fetch('/api/deal-analytics/velocity').then(r => r.json()),
        fetch('/api/deal-analytics/stalled').then(r => r.json()),
      ]);
      setPipeline(p);
      setVelocity(v);
      setStalled(s);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="w-8 h-8 text-text-muted animate-spin" />
      </div>
    );
  }
  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
        <p className="text-red-400 font-medium">Failed to load analytics</p>
        <p className="text-text-muted text-sm mt-1">{error}</p>
        <button onClick={fetchData} className="mt-3 text-sm text-gold hover:underline">Retry</button>
      </div>
    );
  }

  const maxCount = pipeline?.stages ? Math.max(...pipeline.stages.map(s => s.count), 1) : 1;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-semibold text-text-primary">Deal Analytics</h1>
          <p className="text-sm text-text-muted mt-1">Pipeline intelligence and deal velocity</p>
        </div>
        <button
          onClick={fetchData}
          className="p-2 rounded-lg hover:bg-surface-light text-text-muted hover:text-text-primary transition-colors"
          title="Refresh"
        >
          <ArrowPathIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Summary Cards */}
      {pipeline && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-surface rounded-xl border border-border p-5">
            <p className="text-xs text-text-muted uppercase tracking-wide">Total Deals</p>
            <p className="text-3xl font-heading font-semibold mt-1 text-text-primary">{pipeline.total_deals}</p>
          </div>
          <div className="bg-surface rounded-xl border border-border p-5">
            <p className="text-xs text-text-muted uppercase tracking-wide">Pipeline Value</p>
            <p className="text-3xl font-heading font-semibold mt-1 text-gold">
              ${pipeline.total_pipeline_value.toLocaleString('en-AU')}
            </p>
          </div>
          <div className="bg-surface rounded-xl border border-border p-5">
            <p className="text-xs text-text-muted uppercase tracking-wide">Win Rate</p>
            <p className="text-3xl font-heading font-semibold mt-1 text-green-400">
              {pipeline.win_rate != null ? `${pipeline.win_rate}%` : '--'}
            </p>
            <p className="text-xs text-text-muted mt-1">{pipeline.win_count}W / {pipeline.loss_count}L</p>
          </div>
          <div className="bg-surface rounded-xl border border-border p-5">
            <p className="text-xs text-text-muted uppercase tracking-wide">Avg Cycle</p>
            <p className="text-3xl font-heading font-semibold mt-1 text-text-primary">
              {velocity?.avg_cycle_days != null ? `${velocity.avg_cycle_days}d` : '--'}
            </p>
          </div>
        </div>
      )}

      {/* Pipeline Stage Distribution */}
      {pipeline?.stages && (
        <div className="bg-surface rounded-xl border border-border p-5">
          <div className="flex items-center gap-2 mb-4">
            <ChartBarIcon className="w-5 h-5 text-gold" />
            <h2 className="font-heading text-lg font-semibold text-text-primary">Pipeline by Stage</h2>
          </div>
          <div className="space-y-3">
            {pipeline.stages.map(s => (
              <StageBar key={s.stage} stage={s.stage} count={s.count} totalValue={s.total_value} maxCount={maxCount} />
            ))}
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Stage Velocity */}
        {velocity?.stages && (
          <div className="bg-surface rounded-xl border border-border p-5">
            <div className="flex items-center gap-2 mb-4">
              <ClockIcon className="w-5 h-5 text-blue-400" />
              <h2 className="font-heading text-lg font-semibold text-text-primary">Stage Velocity</h2>
            </div>
            <div className="space-y-2">
              {velocity.stages.map(s => (
                <div key={s.stage} className="flex items-center justify-between p-3 rounded-lg bg-surface-light">
                  <span className="text-sm text-text-primary capitalize">{s.stage.replace('_', ' ')}</span>
                  <div className="text-right">
                    <span className="text-sm font-medium text-text-primary">
                      {s.avg_days > 0 ? `${s.avg_days} days` : '--'}
                    </span>
                    <span className="text-xs text-text-muted ml-2">({s.deal_count} deals)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Stalled Deals */}
        {stalled && (
          <div className="bg-surface rounded-xl border border-border p-5">
            <div className="flex items-center gap-2 mb-4">
              <ExclamationCircleIcon className="w-5 h-5 text-red-400" />
              <h2 className="font-heading text-lg font-semibold text-text-primary">
                Stalled Deals ({stalled.total})
              </h2>
            </div>
            {stalled.items.length === 0 ? (
              <p className="text-sm text-text-muted py-4 text-center">No stalled deals</p>
            ) : (
              <div className="space-y-2">
                {stalled.items.map((d) => (
                  <div key={d.id} className="flex items-center justify-between p-3 rounded-lg bg-red-500/5 border border-red-500/10">
                    <div>
                      <p className="text-sm font-medium text-text-primary">{d.title}</p>
                      <p className="text-xs text-text-muted">
                        {d.stage.replace('_', ' ')} · {d.contact_name || 'No contact'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-red-400">{d.days_stalled}d stalled</p>
                      {d.value && <p className="text-xs text-text-muted">${d.value.toLocaleString('en-AU')}</p>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
