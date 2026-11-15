export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Career Twin Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Snapshot as of November 15, 2026 • Verified against live market intelligence
          </p>
        </div>
        <button className="self-start rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors">
          Recompute Twin
        </button>
      </div>

      {/* Primary Scores Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="text-sm font-medium text-muted-foreground">Profile Strength (PPS)</div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold">64.2</span>
            <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-1.5 py-0.5 rounded">
              +3.1
            </span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Band: Solid (Confidence: 78%)</p>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="text-sm font-medium text-muted-foreground">Technical Skill Score (TSS)</div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold">68.0</span>
            <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-1.5 py-0.5 rounded">
              +2.0
            </span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Band: Solid (Confidence: 82%)</p>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="text-sm font-medium text-muted-foreground">Non-Technical Score (NTSS)</div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold">59.5</span>
            <span className="text-xs text-muted-foreground">0.0</span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Band: Solid (Confidence: 55%)</p>
        </div>

        <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
          <div className="text-sm font-medium text-muted-foreground">Target Role Readiness (JRS)</div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-bold">58.3</span>
            <span className="text-xs font-medium text-primary">Backend Eng.</span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Est. 10–16 weeks to ready</p>
        </div>
      </div>

      {/* DNA and Career Match Overview */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-lg border border-border bg-card p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Career DNA Archetype</h2>
          <p className="text-xs text-muted-foreground mb-4">
            Deterministic personality and technical dimension clustering
          </p>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm font-medium mb-1">
                <span>Systems Builder</span>
                <span>62%</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary" style={{ width: "62%" }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm font-medium mb-1">
                <span>Applied Researcher</span>
                <span>21%</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500" style={{ width: "21%" }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-border bg-card p-6 shadow-sm">
          <h2 className="text-lg font-semibold">Priority Skill Gaps</h2>
          <p className="text-xs text-muted-foreground mb-4">
            Closing these skills provides the highest readiness gain
          </p>
          <ul className="space-y-2 text-sm">
            <li className="flex items-center justify-between rounded bg-muted/40 p-2">
              <div>
                <span className="font-semibold">Docker</span>
                <span className="text-xs text-muted-foreground ml-2">Current: 22% → Goal: 60%</span>
              </div>
              <span className="text-xs font-bold text-emerald-600">+4.2 JRS (~18 hrs)</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
