"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";

export default function GapsPage() {
  const [dashboard, setDashboard] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/me/dashboard")
      .then(res => res.json())
      .then(data => setDashboard(data))
      .catch(console.error);
  }, []);

  const gaps = dashboard?.gaps || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Skill Gap Analysis</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Deficits between your verified Career Twin and Backend Engineer requirements, ordered by JRS readiness gain.
          </p>
        </div>
        <Link
          href="/roadmap"
          className="rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground shadow hover:bg-primary/90 transition text-center"
        >
          Generate Closing Roadmap &rarr;
        </Link>
      </div>

      {/* Gaps Table */}
      <div className="bg-card rounded-xl border border-border shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-muted/40 border-b border-border text-xs text-muted-foreground uppercase font-semibold">
            <tr>
              <th className="py-3.5 px-6">Skill</th>
              <th className="py-3.5 px-4">Current Level</th>
              <th className="py-3.5 px-4">Role Requirement</th>
              <th className="py-3.5 px-4">Priority Score</th>
              <th className="py-3.5 px-4">Expected JRS Boost</th>
              <th className="py-3.5 px-4">Est. Study Hours</th>
              <th className="py-3.5 px-6 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {gaps.map((gap: any, idx: number) => (
              <tr key={idx} className="hover:bg-muted/20 transition">
                <td className="py-4 px-6 font-bold uppercase text-foreground">{gap.skill}</td>
                <td className="py-4 px-4 font-semibold text-muted-foreground">{gap.current}%</td>
                <td className="py-4 px-4 font-bold text-foreground">{gap.required}%</td>
                <td className="py-4 px-4 font-semibold text-amber-600">{gap.priority}</td>
                <td className="py-4 px-4">
                  <span className="text-xs font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded">
                    +{gap.jrs_gain} JRS
                  </span>
                </td>
                <td className="py-4 px-4 text-muted-foreground font-medium">~{gap.est_hours} hrs</td>
                <td className="py-4 px-6 text-right">
                  <Link
                    href="/skills"
                    className="text-xs font-semibold text-primary hover:underline"
                  >
                    + Add Evidence
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
