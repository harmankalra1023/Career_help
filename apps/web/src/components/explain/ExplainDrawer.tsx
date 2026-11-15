import React from "react";

interface ExplainDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  factors: Array<{ factor: string; impact: string; weight: number }>;
  dataGaps: string[];
}

export const ExplainDrawer: React.FC<ExplainDrawerProps> = ({
  isOpen,
  onClose,
  title,
  factors,
  dataGaps,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm">
      <div className="w-full max-w-md bg-card p-6 shadow-xl flex flex-col justify-between overflow-y-auto">
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-4">
            <h2 className="text-xl font-bold">{title} Explanation</h2>
            <button
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground text-lg font-bold"
            >
              ×
            </button>
          </div>

          <div>
            <h3 className="text-sm font-semibold mb-2">Contributing Factors</h3>
            <ul className="space-y-2 text-sm">
              {factors.map((f, i) => (
                <li key={i} className="flex justify-between rounded bg-muted/30 p-2">
                  <span>{f.factor}</span>
                  <span className="font-semibold">{f.impact}</span>
                </li>
              ))}
            </ul>
          </div>

          {dataGaps.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-amber-600 mb-2">Data Gaps Affecting Confidence</h3>
              <ul className="list-disc list-inside text-xs text-muted-foreground space-y-1">
                {dataGaps.map((gap, i) => (
                  <li key={i}>{gap}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="mt-6 w-full rounded-md bg-primary py-2 text-sm font-medium text-primary-foreground"
        >
          Close Drawer
        </button>
      </div>
    </div>
  );
};
