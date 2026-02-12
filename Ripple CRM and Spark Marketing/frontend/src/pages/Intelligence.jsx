import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowPathIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  SignalIcon,
} from '@heroicons/react/24/outline';

function ScoreBadge({ score }) {
  if (score == null) return <span className="text-xs text-text-muted">--</span>;
  const colour =
    score >= 70 ? 'bg-green-400/10 text-green-400' :
    score >= 40 ? 'bg-amber-400/10 text-amber-400' :
    'bg-red-400/10 text-red-400';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colour}`}>
      {Math.round(score)}
    </span>
  );
}

function DecayBadge({ status }) {
  const styles = {
    healthy: 'bg-green-400/10 text-green-400',
    cooling: 'bg-amber-400/10 text-amber-400',
    at_risk: 'bg-red-400/10 text-red-400',
    dormant: 'bg-red-600/10 text-red-500',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${styles[status] || 'bg-surface-light text-text-muted'}`}>
      {(status || 'unknown').replace('_', ' ')}
    </span>
  );
}

export default function Intelligence() {
  const [leaderboard, setLeaderboard] = useState(null);
  const [atRisk, setAtRisk] = useState(null);
  const [channelSummary, setChannelSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [lb, risk, ch] = await Promise.all([
        fetch('/api/lead-scores/top?limit=15').then(r => r.json()),
        fetch('/api/trust-decay/at-risk').then(r => r.json()),
        fetch('/api/channel-dna/summary').then(r => r.json()),
      ]);
      setLeaderboard(lb);
      setAtRisk(risk);
      setChannelSummary(ch);
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
        <p className="text-red-400 font-medium">Failed to load intelligence</p>
        <p className="text-text-muted text-sm mt-1">{error}</p>
        <button onClick={fetchData} className="mt-3 text-sm text-gold hover:underline">Retry</button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-semibold text-text-primary">Relationship Intelligence</h1>
          <p className="text-sm text-text-muted mt-1">Three Brains scoring, trust decay, and channel insights</p>
        </div>
        <button
          onClick={fetchData}
          className="p-2 rounded-lg hover:bg-surface-light text-text-muted hover:text-text-primary transition-colors"
          title="Refresh"
        >
          <ArrowPathIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Three Brains Leaderboard */}
      <div className="bg-surface rounded-xl border border-border p-5">
        <div className="flex items-center gap-2 mb-4">
          <SparklesIcon className="w-5 h-5 text-gold" />
          <h2 className="font-heading text-lg font-semibold text-text-primary">Three Brains Leaderboard</h2>
        </div>
        {(!leaderboard?.items || leaderboard.items.length === 0) ? (
          <p className="text-sm text-text-muted py-4 text-center">
            No scores yet. Score contacts from their profile page.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-text-muted text-xs uppercase tracking-wide border-b border-border">
                  <th className="pb-2 pr-4">#</th>
                  <th className="pb-2 pr-4">Contact</th>
                  <th className="pb-2 pr-4 text-center">Composite</th>
                  <th className="pb-2 pr-4 text-center">Fit</th>
                  <th className="pb-2 pr-4 text-center">Intent</th>
                  <th className="pb-2 text-center">Instinct</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {leaderboard.items.map((item, i) => (
                  <tr key={item.contact_id} className="hover:bg-surface-light transition-colors">
                    <td className="py-2.5 pr-4 text-text-muted">{i + 1}</td>
                    <td className="py-2.5 pr-4">
                      <Link to={`/contacts/${item.contact_id}`} className="text-text-primary hover:text-gold transition-colors">
                        {item.contact_name}
                      </Link>
                    </td>
                    <td className="py-2.5 pr-4 text-center"><ScoreBadge score={item.composite_score} /></td>
                    <td className="py-2.5 pr-4 text-center text-text-muted">{Math.round(item.fit_score)}</td>
                    <td className="py-2.5 pr-4 text-center text-text-muted">{Math.round(item.intent_score)}</td>
                    <td className="py-2.5 text-center text-text-muted">{Math.round(item.instinct_score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Trust Decay At-Risk */}
        <div className="bg-surface rounded-xl border border-border p-5">
          <div className="flex items-center gap-2 mb-4">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-400" />
            <h2 className="font-heading text-lg font-semibold text-text-primary">Trust Decay Alerts</h2>
          </div>
          {(!atRisk?.items || atRisk.items.length === 0) ? (
            <p className="text-sm text-text-muted py-4 text-center">No at-risk contacts</p>
          ) : (
            <div className="space-y-2">
              {atRisk.items.map((c) => (
                <Link
                  key={c.contact_id}
                  to={`/contacts/${c.contact_id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-light transition-colors"
                >
                  <div>
                    <p className="text-sm font-medium text-text-primary">{c.contact_name}</p>
                    <p className="text-xs text-text-muted">
                      {c.days_since_last != null ? `${c.days_since_last} days since last contact` : 'No interactions'}
                    </p>
                  </div>
                  <DecayBadge status={c.status} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Channel DNA Summary */}
        <div className="bg-surface rounded-xl border border-border p-5">
          <div className="flex items-center gap-2 mb-4">
            <SignalIcon className="w-5 h-5 text-blue-400" />
            <h2 className="font-heading text-lg font-semibold text-text-primary">Channel DNA</h2>
          </div>
          {(!channelSummary?.items || channelSummary.items.length === 0) ? (
            <p className="text-sm text-text-muted py-4 text-center">
              No channel data yet. Refresh from contact profiles.
            </p>
          ) : (
            <div className="space-y-3">
              {channelSummary.items.map((ch) => (
                <div key={ch.channel} className="flex items-center justify-between p-3 rounded-lg bg-surface-light">
                  <div>
                    <p className="text-sm font-medium text-text-primary capitalize">{ch.channel}</p>
                    <p className="text-xs text-text-muted">
                      {ch.contact_count} contacts · {ch.total_interactions} interactions
                    </p>
                  </div>
                  {ch.avg_sentiment != null && (
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      ch.avg_sentiment >= 0.3 ? 'bg-green-400/10 text-green-400' :
                      ch.avg_sentiment >= -0.3 ? 'bg-surface text-text-muted' :
                      'bg-red-400/10 text-red-400'
                    }`}>
                      {ch.avg_sentiment > 0 ? '+' : ''}{ch.avg_sentiment.toFixed(1)}
                    </span>
                  )}
                </div>
              ))}
              <p className="text-xs text-text-muted text-center mt-2">
                {channelSummary.total_contacts_analysed} contacts analysed
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
