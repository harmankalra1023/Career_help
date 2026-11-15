import React from "react";

interface ScoreGaugeProps {
  value: number;
  label: string;
  band: string;
  confidence: number;
  delta?: number;
  onClick?: () => void;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  value,
  label,
  band,
  confidence,
  delta,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      className="group relative cursor-pointer rounded-lg border border-border bg-card p-4 transition-all hover:border-primary shadow-sm"
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">{label}</span>
        {delta !== undefined && (
          <span
            className={`text-xs font-semibold px-1.5 py-0.5 rounded ${
              delta >= 0
                ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-950"
                : "bg-rose-50 text-rose-600 dark:bg-rose-950"
            }`}
          >
            {delta > 0 ? `+${delta}` : delta}
          </span>
        )}
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-extrabold tracking-tight">{value.toFixed(1)}</span>
        <span className="text-xs uppercase tracking-wider text-muted-foreground">{band}</span>
      </div>
      <div className="mt-3">
        <div className="flex justify-between text-xs text-muted-foreground mb-1">
          <span>Confidence</span>
          <span>{Math.round(confidence * 100)}%</span>
        </div>
        <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all"
            style={{ width: `${Math.min(100, confidence * 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};
