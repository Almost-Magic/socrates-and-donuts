import { useEffect, useState } from 'react';

export default function PulseTargetBar({ actual, target, label, currency = '$' }) {
  const [width, setWidth] = useState(0);
  const percentage = target > 0 ? Math.min((actual / target) * 100, 100) : 0;
  const gap = target - actual;

  useEffect(() => {
    const timer = setTimeout(() => setWidth(percentage), 100);
    return () => clearTimeout(timer);
  }, [percentage]);

  const barColour =
    percentage >= 80
      ? 'bg-healthy'
      : percentage >= 50
        ? 'bg-warning'
        : 'bg-critical';

  const textColour =
    percentage >= 80
      ? 'text-healthy'
      : percentage >= 50
        ? 'text-warning'
        : 'text-critical';

  return (
    <div>
      {label && (
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-text-secondary">{label}</span>
          <span className={`text-sm font-mono font-medium ${textColour}`}>
            {percentage.toFixed(0)}%
          </span>
        </div>
      )}
      <div className="w-full h-4 bg-midnight rounded-full overflow-hidden border border-border">
        <div
          className={`h-full ${barColour} rounded-full transition-all duration-700 ease-out`}
          style={{ width: `${width}%` }}
        />
      </div>
      <div className="flex items-center justify-between mt-1.5">
        <span className="text-xs text-text-muted">
          {currency}{Number(actual).toLocaleString('en-AU', { minimumFractionDigits: 0 })}
        </span>
        <span className="text-xs text-text-muted">
          Target: {currency}{Number(target).toLocaleString('en-AU', { minimumFractionDigits: 0 })}
        </span>
      </div>
      {gap > 0 && (
        <p className="text-xs text-text-muted mt-1">
          {currency}{Number(gap).toLocaleString('en-AU', { minimumFractionDigits: 0 })} to go
        </p>
      )}
    </div>
  );
}
