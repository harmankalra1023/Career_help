"use client";

import React, { useState, useEffect } from "react";

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  // Replan options
  const [targetRole, setTargetRole] = useState("backend-engineer");
  const [weeklyHours, setWeeklyHours] = useState(8.0);
  const [horizonMonths, setHorizonMonths] = useState(6);
  const [replanning, setReplanning] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const fetchRoadmap = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/roadmaps/current");
      if (res.ok) {
        const data = await res.json();
        setRoadmap(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const handleStatusChange = async (milestoneId: string, newStatus: string) => {
    setUpdatingId(milestoneId);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/me/roadmaps/milestones/${milestoneId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        await fetchRoadmap();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleGenerateRoadmap = async (e: React.FormEvent) => {
    e.preventDefault();
    setReplanning(true);
    setMsg(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/roadmaps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          target_role: targetRole,
          weekly_hours: weeklyHours,
          horizon_months: horizonMonths
        })
      });
      if (res.ok) {
        setMsg("Roadmap successfully generated and optimized for your schedule!");
        await fetchRoadmap();
      }
    } catch (e) {
      setMsg("Error generating roadmap.");
    } finally {
      setReplanning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Execution Roadmap</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Capacity-constrained milestone sequence with dynamic prerequisite bin packing.
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs bg-muted/40 p-3 rounded-lg border border-border">
          <span>Weekly Commitment: <strong>{roadmap?.weekly_hours || weeklyHours} hrs/wk</strong></span>
          <span>&bull;</span>
          <span>Horizon: <strong>{roadmap?.horizon_months || horizonMonths} Months</strong></span>
        </div>
      </div>

      {msg && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-800 font-medium">
          {msg}
        </div>
      )}

      {/* Generator / Replan Controls */}
      <form onSubmit={handleGenerateRoadmap} className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <h2 className="text-md font-bold">Configure & Replan Timeline</h2>
        <div className="grid gap-4 sm:grid-cols-4">
          <div>
            <label className="text-xs font-semibold">Target Career Role</label>
            <select
              value={targetRole}
              onChange={e => setTargetRole(e.target.value)}
              className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
            >
              <option value="backend-engineer">Backend Engineer</option>
              <option value="full-stack-engineer">Full Stack Engineer</option>
              <option value="devops-engineer">DevOps Engineer</option>
              <option value="ai-application-engineer">AI Application Engineer</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold">Weekly Study Hours ({weeklyHours} hrs)</label>
            <input
              type="range"
              min="4"
              max="20"
              step="2"
              value={weeklyHours}
              onChange={e => setWeeklyHours(parseFloat(e.target.value))}
              className="mt-2 w-full"
            />
          </div>
          <div>
            <label className="text-xs font-semibold">Horizon Duration</label>
            <select
              value={horizonMonths}
              onChange={e => setHorizonMonths(parseInt(e.target.value))}
              className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
            >
              <option value={3}>3 Months (Fast-Track)</option>
              <option value={6}>6 Months (Balanced)</option>
              <option value={9}>9 Months (Deep Specialization)</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={replanning}
              className="w-full py-2.5 rounded bg-primary text-primary-foreground font-semibold text-xs hover:bg-primary/90 transition disabled:opacity-50"
            >
              {replanning ? "Planning Bins..." : "Optimize Roadmap"}
            </button>
          </div>
        </div>
      </form>

      {/* Milestones Timeline */}
      {loading ? (
        <div className="text-center py-12 text-sm text-muted-foreground">Loading milestone plan...</div>
      ) : (
        <div className="space-y-4">
          {roadmap?.milestones?.map((m: any) => (
            <div
              key={m.id}
              className={`p-6 rounded-xl border transition shadow-sm bg-card ${
                m.status === "completed"
                  ? "border-emerald-200 bg-emerald-50/20 dark:bg-emerald-950/10"
                  : m.status === "in_progress"
                  ? "border-primary/40"
                  : "border-border"
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    m.status === "completed"
                      ? "bg-emerald-600 text-white"
                      : m.status === "in_progress"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}>
                    {m.sequence_order}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-primary bg-primary/10 px-2 py-0.5 rounded">
                        Month {m.month_index} &bull; {m.phase}
                      </span>
                    </div>
                    <h3 className="font-bold text-base mt-1">{m.title}</h3>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-muted-foreground font-medium">~{m.estimated_hours} Hours</span>
                  <select
                    value={m.status}
                    disabled={updatingId === m.id}
                    onChange={e => handleStatusChange(m.id, e.target.value)}
                    className="text-xs rounded border border-input p-1.5 bg-background font-semibold"
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              </div>

              {/* Skills & Resources */}
              <div className="mt-4 pt-3 border-t border-border flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground font-semibold">Skills:</span>
                  {m.skills?.map((sk: string) => (
                    <span key={sk} className="bg-muted px-2 py-0.5 rounded uppercase font-semibold text-[11px]">
                      {sk}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground font-semibold">Resources:</span>
                  {m.resources?.map((r: any, i: number) => (
                    <span key={i} className="text-primary font-medium">
                      &bull; {r.title}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
