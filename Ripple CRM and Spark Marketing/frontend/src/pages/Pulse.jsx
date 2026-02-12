import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowPathIcon,
  ChartBarIcon,
  CheckCircleIcon,
  Cog6ToothIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  LightBulbIcon,
  StarIcon,
  TrophyIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';
import { api } from '../lib/api';
import { toast } from '../components/Toast';
import PulseTargetBar from '../components/PulseTargetBar';

const PACE_LABELS = {
  ahead: { text: 'Ahead of pace', colour: 'text-healthy' },
  on_track: { text: 'On track', colour: 'text-healthy' },
  behind: { text: 'Behind pace', colour: 'text-critical' },
};

const STAGE_COLOURS = {
  lead: 'bg-surface-light',
  qualified: 'bg-purple-500/10 text-purple-400',
  proposal: 'bg-blue-500/10 text-blue-400',
  negotiation: 'bg-warning/10 text-warning',
  closed_won: 'bg-healthy/10 text-healthy',
  closed_lost: 'bg-critical/10 text-critical',
};

function SectionCard({ title, icon: Icon, children, badge }) {
  return (
    <div className="bg-surface rounded-xl border border-border p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {Icon && <Icon className="w-5 h-5 text-gold" />}
          <h2 className="font-heading text-lg font-semibold">{title}</h2>
        </div>
        {badge && (
          <span className="text-xs bg-gold/10 text-gold px-2 py-0.5 rounded-full font-medium">
            {badge}
          </span>
        )}
      </div>
      {children}
    </div>
  );
}

export default function Pulse() {
  const [pulse, setPulse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchPulse = useCallback(async () => {
    try {
      const data = await api.get('/pulse');
      setPulse(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPulse();
  }, [fetchPulse]);

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const data = await api.post('/pulse/generate');
      setPulse(data);
      toast('Pulse regenerated');
    } catch (e) {
      toast(`Regeneration failed: ${e.message}`, 'error');
    } finally {
      setRegenerating(false);
    }
  };

  const handleCompleteAction = async (actionId) => {
    try {
      await api.put(`/pulse/actions/${actionId}/complete`);
      setPulse((prev) => ({
        ...prev,
        actions: prev.actions.map((a) =>
          a.id === actionId ? { ...a, is_completed: true } : a
        ),
      }));
      toast('Action completed');
    } catch (e) {
      toast(`Error: ${e.message}`, 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-text-muted">Generating your daily Pulse...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-critical/10 border border-critical/30 rounded-xl p-6 text-critical">
        <p className="font-medium">Failed to load Pulse</p>
        <p className="text-sm mt-1">{error}</p>
        <button onClick={fetchPulse} className="mt-3 text-sm underline">
          Retry
        </button>
      </div>
    );
  }

  if (!pulse) return null;

  const target = pulse.target_vs_actual;
  const actions = pulse.actions || [];
  const easyWins = pulse.easy_wins || [];
  const pipeline = pulse.pipeline || {};
  const relationships = pulse.relationships || {};
  const coaching = pulse.coaching || {};
  const wisdom = pulse.wisdom;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-semibold">Pulse</h1>
          <p className="text-sm text-text-muted mt-0.5">
            {new Date().toLocaleDateString('en-AU', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => navigate('/pulse/settings')}
            className="p-2 rounded-lg hover:bg-surface-light text-text-secondary"
            title="Pulse settings"
          >
            <Cog6ToothIcon className="w-5 h-5" />
          </button>
          <button
            onClick={handleRegenerate}
            disabled={regenerating}
            className="flex items-center gap-2 px-3 py-1.5 bg-gold hover:bg-gold-light text-midnight rounded-lg text-sm font-medium disabled:opacity-50"
          >
            <ArrowPathIcon className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
            {regenerating ? 'Generating...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* 1. TARGET VS ACTUAL */}
      {target && (
        <SectionCard title="Target vs Actual" icon={TrophyIcon}>
          <PulseTargetBar
            actual={target.actual_value}
            target={target.target_value}
            label={target.period_label}
          />
          <div className="flex items-center gap-2 mt-3">
            <span
              className={`text-sm font-medium ${PACE_LABELS[target.pace]?.colour || 'text-text-secondary'}`}
            >
              {PACE_LABELS[target.pace]?.text || target.pace}
            </span>
          </div>
          {target.commentary && (
            <p className="text-sm text-text-secondary mt-3 leading-relaxed">
              {target.commentary}
            </p>
          )}
        </SectionCard>
      )}

      {/* 2. TOP 5 ACTIONS */}
      <SectionCard
        title="Today's Actions"
        icon={CheckCircleIcon}
        badge={`${actions.filter((a) => a.is_completed).length}/${actions.length}`}
      >
        {actions.length === 0 ? (
          <p className="text-sm text-text-muted py-2">No actions generated yet. Hit Refresh to generate.</p>
        ) : (
          <div className="space-y-2">
            {actions.map((action, i) => (
              <div
                key={action.id}
                className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                  action.is_completed
                    ? 'bg-healthy/5 border-healthy/20 opacity-70'
                    : 'bg-midnight border-border hover:border-gold/30'
                }`}
              >
                <button
                  onClick={() => !action.is_completed && handleCompleteAction(action.id)}
                  disabled={action.is_completed}
                  className="mt-0.5 shrink-0"
                >
                  {action.is_completed ? (
                    <CheckCircleSolid className="w-5 h-5 text-healthy" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-text-muted hover:border-gold" />
                  )}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gold font-mono font-medium">#{i + 1}</span>
                    <p
                      className={`text-sm font-medium ${
                        action.is_completed ? 'line-through text-text-muted' : 'text-text-primary'
                      }`}
                    >
                      {action.title}
                    </p>
                  </div>
                  {action.reason && (
                    <p className="text-xs text-text-muted mt-1">{action.reason}</p>
                  )}
                </div>
                {action.estimated_minutes && (
                  <span className="shrink-0 flex items-center gap-1 text-xs text-text-muted">
                    <ClockIcon className="w-3.5 h-3.5" />
                    {action.estimated_minutes}m
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      {/* 3. EASY WINS */}
      {easyWins.length > 0 && (
        <SectionCard title="Easy Wins" icon={LightBulbIcon} badge={`${easyWins.length} opportunities`}>
          <div className="space-y-2">
            {easyWins.slice(0, 8).map((win, i) => (
              <div
                key={win.deal_id || i}
                className="flex items-center justify-between p-3 bg-midnight rounded-lg border border-border hover:border-gold/30 transition-colors cursor-pointer"
                onClick={() => win.deal_id && navigate(`/deals`)}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-text-primary truncate">
                      {win.deal_title}
                    </p>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                        STAGE_COLOURS[win.stage] || 'bg-surface-light'
                      }`}
                    >
                      {win.stage}
                    </span>
                  </div>
                  {win.contact_name && (
                    <p className="text-xs text-text-muted mt-0.5">{win.contact_name}</p>
                  )}
                </div>
                <div className="text-right shrink-0 ml-3">
                  {win.value > 0 && (
                    <p className="text-sm font-mono text-gold">
                      ${Number(win.value).toLocaleString('en-AU')}
                    </p>
                  )}
                  {win.days_since_contact != null && (
                    <p className="text-[10px] text-text-muted">
                      {win.days_since_contact}d since contact
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      )}

      {/* 4. PIPELINE HEALTH */}
      <SectionCard title="Pipeline Health" icon={ChartBarIcon}>
        {/* Stage breakdown */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2 mb-4">
          {(pipeline.stages || []).map((s) => (
            <div key={s.stage} className="p-2 bg-midnight rounded-lg border border-border text-center">
              <p className="text-[10px] text-text-muted uppercase tracking-wider">{s.stage.replace('_', ' ')}</p>
              <p className="text-lg font-heading font-semibold mt-0.5">{s.count}</p>
              {s.value > 0 && (
                <p className="text-xs font-mono text-gold">
                  ${Number(s.value).toLocaleString('en-AU')}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Win rates */}
        <div className="flex gap-4 mb-4">
          {pipeline.win_rate_30d != null && (
            <div className="text-sm">
              <span className="text-text-muted">30d win rate: </span>
              <span className="font-mono font-medium text-text-primary">{pipeline.win_rate_30d}%</span>
            </div>
          )}
          {pipeline.win_rate_60d != null && (
            <div className="text-sm">
              <span className="text-text-muted">60d: </span>
              <span className="font-mono font-medium text-text-primary">{pipeline.win_rate_60d}%</span>
            </div>
          )}
          {pipeline.avg_deal_velocity_days != null && (
            <div className="text-sm">
              <span className="text-text-muted">Avg velocity: </span>
              <span className="font-mono font-medium text-text-primary">{pipeline.avg_deal_velocity_days} days</span>
            </div>
          )}
        </div>

        {/* Stalled deals */}
        {(pipeline.stalled_deals || []).length > 0 && (
          <div>
            <h3 className="text-xs text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1">
              <ExclamationTriangleIcon className="w-3.5 h-3.5 text-warning" />
              Stalled Deals
            </h3>
            <div className="space-y-1">
              {pipeline.stalled_deals.map((d) => (
                <div
                  key={d.deal_id}
                  className="flex items-center justify-between p-2 bg-midnight rounded-lg border border-warning/20 text-sm"
                >
                  <div>
                    <span className="text-text-primary font-medium">{d.title}</span>
                    {d.contact_name && (
                      <span className="text-text-muted ml-2">({d.contact_name})</span>
                    )}
                  </div>
                  <span className="text-xs text-warning font-mono">{d.days_in_stage}d stalled</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {pipeline.narrative && (
          <p className="text-sm text-text-secondary mt-3 leading-relaxed">{pipeline.narrative}</p>
        )}
      </SectionCard>

      {/* 5. RELATIONSHIPS */}
      <SectionCard title="Relationship Intelligence" icon={UserGroupIcon}>
        {/* Decaying */}
        {(relationships.decaying || []).length > 0 && (
          <div className="mb-4">
            <h3 className="text-xs text-text-muted uppercase tracking-wider mb-2">Needs Attention</h3>
            <div className="space-y-1">
              {relationships.decaying.map((c) => (
                <div
                  key={c.contact_id}
                  className="flex items-center justify-between p-2 bg-midnight rounded-lg border border-border hover:border-warning/30 cursor-pointer transition-colors"
                  onClick={() => navigate(`/contacts/${c.contact_id}`)}
                >
                  <span className="text-sm text-text-primary">{c.contact_name}</span>
                  <div className="flex items-center gap-2">
                    {c.health_score != null && (
                      <span
                        className={`text-xs font-mono px-2 py-0.5 rounded-full ${
                          c.health_score >= 40
                            ? 'bg-warning/10 text-warning'
                            : 'bg-critical/10 text-critical'
                        }`}
                      >
                        {Math.round(c.health_score)}
                      </span>
                    )}
                    {c.last_interaction_days != null && (
                      <span className="text-[10px] text-text-muted">{c.last_interaction_days}d ago</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Champions */}
        {(relationships.champions || []).length > 0 && (
          <div>
            <h3 className="text-xs text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1">
              <StarIcon className="w-3.5 h-3.5 text-gold" /> Champions
            </h3>
            <div className="flex flex-wrap gap-2">
              {relationships.champions.map((c) => (
                <span
                  key={c.contact_id}
                  className="inline-flex items-center gap-1 px-2.5 py-1 bg-gold/10 text-gold rounded-full text-xs font-medium cursor-pointer hover:bg-gold/20"
                  onClick={() => navigate(`/contacts/${c.contact_id}`)}
                >
                  <StarIcon className="w-3 h-3" />
                  {c.contact_name}
                  {c.health_score != null && (
                    <span className="font-mono">({Math.round(c.health_score)})</span>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}

        {(relationships.decaying || []).length === 0 && (relationships.champions || []).length === 0 && (
          <p className="text-sm text-text-muted py-2 text-center">All relationships healthy</p>
        )}
      </SectionCard>

      {/* 6. COACHING & WINS */}
      <SectionCard title="Coaching & Wins" icon={TrophyIcon}>
        {coaching.streak_days > 0 && (
          <div className="flex items-center gap-3 p-3 bg-gold/5 border border-gold/20 rounded-lg mb-3">
            <TrophyIcon className="w-6 h-6 text-gold shrink-0" />
            <div>
              <p className="text-sm font-medium text-gold">{coaching.streak_days}-day win streak!</p>
              <p className="text-xs text-text-muted">Keep the momentum going</p>
            </div>
          </div>
        )}

        {(coaching.personal_bests || []).length > 0 && (
          <div className="space-y-1 mb-3">
            {coaching.personal_bests.map((b, i) => (
              <p key={i} className="text-sm text-text-secondary flex items-center gap-2">
                <span className="text-gold">*</span> {b}
              </p>
            ))}
          </div>
        )}

        {(coaching.coaching_tips || []).length > 0 && (
          <div className="mt-3 p-3 bg-midnight rounded-lg border border-border">
            <h3 className="text-xs text-text-muted uppercase tracking-wider mb-2">Coaching Tips</h3>
            {coaching.coaching_tips.map((tip, i) => (
              <p key={i} className="text-sm text-text-secondary leading-relaxed">
                {tip}
              </p>
            ))}
          </div>
        )}

        {coaching.streak_days === 0 && (coaching.personal_bests || []).length === 0 && (
          <p className="text-sm text-text-muted py-2 text-center">Close a deal to start your streak</p>
        )}
      </SectionCard>

      {/* 7. WISDOM QUOTE */}
      {wisdom && (
        <div className="bg-surface rounded-xl border border-gold/20 p-6 text-center">
          <p className="text-base italic text-text-secondary leading-relaxed">
            "{wisdom.quote}"
          </p>
          <p className="text-sm text-gold mt-3 font-medium">
            -- {wisdom.author}
            {wisdom.source && (
              <span className="text-text-muted font-normal">, {wisdom.source}</span>
            )}
          </p>
        </div>
      )}
    </div>
  );
}

