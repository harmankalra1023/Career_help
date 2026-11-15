"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

export default function CareersPage() {
  const [careers, setCareers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/careers")
      .then(res => res.json())
      .then(data => setCareers(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Career Pathways & Roles</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Target pathways ranked by evidence skill fit, transferable credits, and Holland interest alignment.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-sm text-muted-foreground">Calculating pathway matches...</div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2">
          {careers.map(role => (
            <div key={role.slug} className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4 flex flex-col justify-between hover:border-primary transition">
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">{role.category}</span>
                    <h2 className="text-lg font-bold">{role.title}</h2>
                  </div>
                  <div className="text-right">
                    <span className="text-xl font-black text-primary">{Math.round(role.match_score)}%</span>
                    <span className="block text-[10px] uppercase font-bold text-muted-foreground">{role.band}</span>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground leading-relaxed line-clamp-2">{role.description}</p>

                <div className="grid grid-cols-2 gap-2 text-xs pt-1">
                  <div className="bg-muted/40 p-2.5 rounded-lg border border-border">
                    <span className="text-muted-foreground block text-[11px]">Skill Fit</span>
                    <strong className="text-foreground text-sm">{Math.round(role.skill_fit)}%</strong>
                  </div>
                  <div className="bg-muted/40 p-2.5 rounded-lg border border-border">
                    <span className="text-muted-foreground block text-[11px]">Market Demand</span>
                    <strong className="text-foreground text-sm">{role.demand_score}/100</strong>
                  </div>
                </div>

                <div className="flex justify-between items-center text-xs text-muted-foreground pt-1">
                  <span>Salary: <strong className="text-foreground">{role.salary_range}</strong></span>
                  <span>Gaps to Close: <strong className="text-primary">{role.gap_count}</strong></span>
                </div>
              </div>

              <div className="pt-2">
                <Link
                  href={`/careers/${role.slug}`}
                  className="block w-full py-2.5 text-center rounded-lg bg-secondary text-secondary-foreground font-semibold text-xs hover:bg-secondary/80 transition"
                >
                  View Gap Breakdown & Requirements &rarr;
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
