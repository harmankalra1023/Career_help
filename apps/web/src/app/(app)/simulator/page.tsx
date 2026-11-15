"use client";

import React, { useState, useEffect } from "react";

export default function SimulatorPage() {
  const [params, setParams] = useState({
    base_salary: 75000,
    current_level: "Mid",
    jrs: 58.3,
    weekly_hours: 8.0,
    years: 4
  });
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runSimulation = async () => {
    setRunning(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/simulator/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(params)
      });
      if (res.ok) {
        setResult(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Monte Carlo Career & Salary Simulator</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Stochastic simulation of promotion hazards, skill acquisition velocity, and salary percentiles (P10, P50, P90).
          </p>
        </div>
      </div>

      {/* Simulator Inputs */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <h2 className="text-md font-bold">Simulation Parameters</h2>
        <div className="grid gap-4 sm:grid-cols-4">
          <div>
            <label className="text-xs font-semibold">Starting Base Salary ($)</label>
            <input
              type="number"
              step="5000"
              value={params.base_salary}
              onChange={e => setParams({...params, base_salary: parseFloat(e.target.value)})}
              className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
            />
          </div>
          <div>
            <label className="text-xs font-semibold">Weekly Study Hours ({params.weekly_hours} hrs)</label>
            <input
              type="range"
              min="0"
              max="20"
              step="2"
              value={params.weekly_hours}
              onChange={e => setParams({...params, weekly_hours: parseFloat(e.target.value)})}
              className="mt-2 w-full"
            />
          </div>
          <div>
            <label className="text-xs font-semibold">Target Projection Horizon</label>
            <select
              value={params.years}
              onChange={e => setParams({...params, years: parseInt(e.target.value)})}
              className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
            >
              <option value={2}>2 Years</option>
              <option value={3}>3 Years</option>
              <option value={4}>4 Years</option>
              <option value={5}>5 Years</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={runSimulation}
              disabled={running}
              className="w-full py-2.5 rounded bg-primary text-primary-foreground font-semibold text-xs hover:bg-primary/90 transition disabled:opacity-50"
            >
              {running ? "Simulating 1,000 runs..." : "Run Monte Carlo (1k Runs)"}
            </button>
          </div>
        </div>
      </div>

      {/* Results Overview Cards */}
      {result && (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="p-5 bg-card rounded-xl border border-border shadow-sm">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Promotion Probability</span>
              <div className="mt-2 text-3xl font-extrabold text-primary">
                {Math.round(result.promotion_probability * 100)}%
              </div>
              <p className="text-xs text-muted-foreground mt-1">Over {result.years} years horizon</p>
            </div>
            <div className="p-5 bg-card rounded-xl border border-border shadow-sm">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Projected Median (P50)</span>
              <div className="mt-2 text-3xl font-extrabold text-foreground">
                ${result.projected_median_final.toLocaleString()}
              </div>
              <p className="text-xs text-emerald-600 font-semibold mt-1">
                +${(result.projected_median_final - result.starting_salary).toLocaleString()} total growth
              </p>
            </div>
            <div className="p-5 bg-card rounded-xl border border-border shadow-sm">
              <span className="text-xs font-semibold uppercase text-muted-foreground">Iterations</span>
              <div className="mt-2 text-3xl font-extrabold text-muted-foreground">
                {result.n_simulations}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Seeded deterministic NumPy RNG</p>
            </div>
          </div>

          {/* Year by Year Table */}
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
            <h2 className="text-lg font-bold">Yearly Salary Trajectory Percentiles</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-border text-xs text-muted-foreground">
                    <th className="pb-3 font-semibold">Timeframe</th>
                    <th className="pb-3 font-semibold text-rose-600">P10 (Conservative)</th>
                    <th className="pb-3 font-semibold text-primary">P50 (Median Expected)</th>
                    <th className="pb-3 font-semibold text-emerald-600">P90 (High Performer)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {result.trajectory?.map((pt: any, i: number) => (
                    <tr key={i} className="hover:bg-muted/20">
                      <td className="py-3 font-bold">{pt.year}</td>
                      <td className="py-3 text-rose-600 font-medium">${pt.p10.toLocaleString()}</td>
                      <td className="py-3 text-primary font-bold">${pt.p50.toLocaleString()}</td>
                      <td className="py-3 text-emerald-600 font-semibold">${pt.p90.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
