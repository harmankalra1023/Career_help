"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

interface ScoreDetail {
  value: number;
  band: string;
  confidence: number;
  delta_since_last: number;
  as_of: string;
}

interface DashboardState {
  scores: {
    profile: ScoreDetail;
    technical: ScoreDetail;
    non_technical: ScoreDetail;
    job_readiness: ScoreDetail;
    career_match_top?: { role_slug: string; value: number; band: string };
    industry_demand?: { value: number; band: string };
  };
  dna: {
    dimensions: Record<string, number>;
    archetype: Array<{ name: string; pct: number }>;
    narrative: string;
  };
  strengths: Array<{ label: string; evidence: string[]; percentile: number }>;
  gaps: Array<{ skill: string; current: number; required: number; priority: number; jrs_gain: number; est_hours: number }>;
  data_quality: { completeness: number };
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardState | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const fetchDashboard = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/dashboard");
      if (res.ok) {
        const json = await res.json();
        setData(json);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleGenerateTwin = async () => {
    setGenerating(true);
    setMessage(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/twin/generate", {
        method: "POST"
      });
      if (res.ok) {
        setMessage("Career Twin successfully recomputed with latest evidence!");
        await fetchDashboard();
      } else {
        setMessage("Recomputation failed.");
      }
    } catch (e) {
      setMessage("Error connecting to scoring service.");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center space-y-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto"></div>
          <p className="text-sm text-muted-foreground">Calibrating verified Career Twin data...</p>
        </div>
      </div>
    );
  }

  const scores = data?.scores;
  const dna = data?.dna;
  const gaps = data?.gaps || [];
  const strengths = data?.strengths || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between bg-card p-6 rounded-xl border border-border shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">Career Twin Dashboard</h1>
            <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded-full">
              Live Twin
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Engine v1.0.0 &bull; Target Role: <strong className="text-foreground">Backend Engineer</strong> &bull; Region: Global
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateTwin}
            disabled={generating}
            className="rounded-md bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow hover:bg-primary/90 transition disabled:opacity-50 flex items-center gap-2"
          >
            {generating && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>}
            {generating ? "Recomputing..." : "Recompute Career Twin"}
          </button>
        </div>
      </div>

      {message && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-800 font-medium">
          {message}
        </div>
      )}

      {/* Primary Score Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* PPS */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Profile Strength (PPS)</span>
            {scores?.profile.delta_since_last ? (
              <span className="text-xs font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded">
                +{scores.profile.delta_since_last}
              </span>
            ) : null}
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">{scores?.profile.value.toFixed(1)}</span>
            <span className="text-xs uppercase text-muted-foreground font-semibold">{scores?.profile.band}</span>
          </div>
          <div className="mt-3">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Confidence</span>
              <span>{Math.round((scores?.profile.confidence || 0) * 100)}%</span>
            </div>
            <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
              <div className="h-full bg-blue-600 rounded-full" style={{ width: `${scores?.profile.value}%` }}></div>
            </div>
          </div>
        </div>

        {/* TSS */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Technical Skill (TSS)</span>
            {scores?.technical.delta_since_last ? (
              <span className="text-xs font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded">
                +{scores.technical.delta_since_last}
              </span>
            ) : null}
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">{scores?.technical.value.toFixed(1)}</span>
            <span className="text-xs uppercase text-muted-foreground font-semibold">{scores?.technical.band}</span>
          </div>
          <div className="mt-3">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Depth & Breadth</span>
              <span>{Math.round((scores?.technical.confidence || 0) * 100)}%</span>
            </div>
            <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
              <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${scores?.technical.value}%` }}></div>
            </div>
          </div>
        </div>

        {/* NTSS */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Non-Technical (NTSS)</span>
            <span className="text-xs font-semibold text-muted-foreground bg-muted px-2 py-0.5 rounded">Traits</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">{scores?.non_technical.value.toFixed(1)}</span>
            <span className="text-xs uppercase text-muted-foreground font-semibold">{scores?.non_technical.band}</span>
          </div>
          <div className="mt-3">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Team Collaboration</span>
              <span>{Math.round((scores?.non_technical.confidence || 0) * 100)}%</span>
            </div>
            <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
              <div className="h-full bg-amber-500 rounded-full" style={{ width: `${scores?.non_technical.value}%` }}></div>
            </div>
          </div>
        </div>

        {/* JRS */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex justify-between items-start">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Job Readiness (JRS)</span>
            <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-0.5 rounded">Backend</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold">{scores?.job_readiness.value.toFixed(1)}</span>
            <span className="text-xs uppercase text-muted-foreground font-semibold">{scores?.job_readiness.band}</span>
          </div>
          <div className="mt-3">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Est. 10–14 Weeks</span>
              <span>{Math.round((scores?.job_readiness.confidence || 0) * 100)}%</span>
            </div>
            <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
              <div className="h-full bg-emerald-600 rounded-full" style={{ width: `${scores?.job_readiness.value}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Middle Grid: DNA Archetype & Priority Skill Gaps */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Career DNA */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <h2 className="text-lg font-bold">Career DNA & Archetypes</h2>
              <p className="text-xs text-muted-foreground">Centroid proximity clustering from validated competencies</p>
            </div>
            <Link href="/dna" className="text-xs font-semibold text-primary hover:underline">
              View Dimensions &rarr;
            </Link>
          </div>
          <div className="space-y-3 pt-1">
            {dna?.archetype.map((arch, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-sm font-semibold">
                  <span>{arch.name}</span>
                  <span className="text-primary">{Math.round(arch.pct * 100)}% Match</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${arch.pct * 100}%` }}></div>
                </div>
              </div>
            ))}
          </div>
          {dna?.narrative && (
            <p className="text-xs text-muted-foreground bg-muted/40 p-3 rounded-lg leading-relaxed">
              &ldquo;{dna.narrative}&rdquo;
            </p>
          )}
        </div>

        {/* Priority Gaps */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div>
              <h2 className="text-lg font-bold">Priority Skill Gaps</h2>
              <p className="text-xs text-muted-foreground">Highest JRS gain towards Backend Engineer</p>
            </div>
            <Link href="/gaps" className="text-xs font-semibold text-primary hover:underline">
              All Gaps &rarr;
            </Link>
          </div>
          <div className="space-y-3">
            {gaps.map((gap, idx) => (
              <div key={idx} className="flex items-center justify-between p-3.5 bg-muted/30 rounded-lg border border-border">
                <div>
                  <div className="font-semibold text-sm">{gap.skill.toUpperCase()}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Current: {gap.current}% &bull; Target: {gap.required}%
                  </div>
                </div>
                <div className="text-right">
                  <span className="inline-block text-xs font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded">
                    +{gap.jrs_gain} JRS
                  </span>
                  <div className="text-xs text-muted-foreground mt-1">~{gap.est_hours} hrs</div>
                </div>
              </div>
            ))}
          </div>
          <div className="pt-2">
            <Link
              href="/roadmap"
              className="block w-full text-center py-2.5 rounded-lg bg-secondary text-secondary-foreground font-semibold text-xs hover:bg-secondary/80 transition"
            >
              Generate Execution Roadmap to Close Gaps
            </Link>
          </div>
        </div>
      </div>

      {/* Strengths & Quick Action Links */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-xl border border-border bg-card p-6 shadow-sm space-y-4">
          <h2 className="text-lg font-bold">Verified Top Strengths</h2>
          <div className="grid gap-3 sm:grid-cols-3">
            {strengths.map((str, idx) => (
              <div key={idx} className="p-4 rounded-lg bg-muted/20 border border-border space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-sm">{str.label}</span>
                  <span className="text-xs font-bold text-primary">{str.percentile}th %ile</span>
                </div>
                <ul className="text-xs text-muted-foreground space-y-1">
                  {str.evidence.map((ev, i) => (
                    <li key={i} className="flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                      <span>{ev}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Tools */}
        <div className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-3">
          <h2 className="text-lg font-bold">Quick Career Tools</h2>
          <div className="space-y-2 text-sm">
            <Link
              href="/simulator"
              className="flex items-center justify-between p-3 rounded-lg border border-border hover:border-primary hover:bg-muted/40 transition font-medium"
            >
              <span>Monte Carlo Salary Simulator</span>
              <span>&rarr;</span>
            </Link>
            <Link
              href="/mentor"
              className="flex items-center justify-between p-3 rounded-lg border border-border hover:border-primary hover:bg-muted/40 transition font-medium"
            >
              <span>Chat with Groq AI Mentor</span>
              <span>&rarr;</span>
            </Link>
            <Link
              href="/assessments"
              className="flex items-center justify-between p-3 rounded-lg border border-border hover:border-primary hover:bg-muted/40 transition font-medium"
            >
              <span>Take Big 5 / RIASEC Quiz</span>
              <span>&rarr;</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
