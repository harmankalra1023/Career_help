"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

export default function CareerDetailPage({ params }: { params: { slug: string } }) {
  const [detail, setDetail] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:8000/api/v1/careers/${params.slug}`)
      .then(res => res.json())
      .then(data => setDetail(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [params.slug]);

  if (loading) {
    return <div className="text-center py-12 text-sm text-muted-foreground">Loading role requirements...</div>;
  }

  if (!detail) {
    return <div className="text-center py-12 text-sm text-muted-foreground">Role not found.</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Link href="/careers" className="hover:underline">Careers</Link>
        <span>&rsaquo;</span>
        <span>{detail.title}</span>
      </div>

      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
          <div>
            <span className="text-xs font-bold text-primary uppercase tracking-wider">{detail.category}</span>
            <h1 className="text-2xl font-bold">{detail.title}</h1>
            <p className="text-xs text-muted-foreground mt-1">{detail.description}</p>
          </div>
          <div className="text-right">
            <span className="text-3xl font-black text-primary">{Math.round(detail.match_score)}%</span>
            <span className="block text-xs uppercase font-bold text-muted-foreground">{detail.band} Match</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="p-3 bg-muted/40 rounded-lg">
            <span className="text-xs text-muted-foreground block">Skill Fit</span>
            <strong className="text-sm font-bold text-foreground">{Math.round(detail.skill_fit)}%</strong>
          </div>
          <div className="p-3 bg-muted/40 rounded-lg">
            <span className="text-xs text-muted-foreground block">Market Demand</span>
            <strong className="text-sm font-bold text-foreground">{detail.demand_score}/100</strong>
          </div>
          <div className="p-3 bg-muted/40 rounded-lg">
            <span className="text-xs text-muted-foreground block">Salary Range</span>
            <strong className="text-sm font-bold text-foreground">{detail.salary_range}</strong>
          </div>
        </div>
      </div>

      {/* Required Skills Table */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <h2 className="text-lg font-bold">Role Skill Requirements</h2>
        <div className="space-y-3">
          {detail.required_skills?.map((req: any, idx: number) => (
            <div key={idx} className="p-3.5 bg-muted/30 rounded-lg border border-border flex items-center justify-between">
              <div>
                <span className="font-bold text-sm uppercase">{req.skill_slug}</span>
                <span className="text-xs text-muted-foreground block mt-0.5">Importance Weight: {req.importance * 100}%</span>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold">Min Target: <strong>{req.minimum_level}%</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Gaps to Close */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <h2 className="text-lg font-bold">Identified Gaps</h2>
          <span className="text-xs text-muted-foreground">{detail.gaps?.length || 0} skills below target</span>
        </div>
        <div className="space-y-3">
          {detail.gaps?.map((gap: any, idx: number) => (
            <div key={idx} className="p-3.5 bg-muted/30 rounded-lg border border-border flex items-center justify-between">
              <div>
                <span className="font-bold text-sm uppercase">{gap.skill}</span>
                <div className="text-xs text-muted-foreground mt-0.5">
                  Current: {gap.current}% &bull; Target: {gap.required}%
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                  +{gap.jrs_gain} JRS
                </span>
                <div className="text-xs text-muted-foreground mt-1">Est. {gap.est_hours} hrs</div>
              </div>
            </div>
          ))}
        </div>
        <div className="pt-2">
          <Link
            href="/roadmap"
            className="block w-full py-2.5 text-center rounded-lg bg-primary text-primary-foreground font-semibold text-xs hover:bg-primary/90 transition shadow-sm"
          >
            Generate Custom Execution Roadmap for {detail.title} &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}
