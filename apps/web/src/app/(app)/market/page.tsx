"use client";

import React, { useState } from "react";

export default function MarketIntelPage() {
  const [region, setRegion] = useState("global");

  const regions = [
    { id: "global", name: "Global Market (USD)" },
    { id: "north_america", name: "North America (USD)" },
    { id: "europe", name: "Europe (EUR)" },
    { id: "india", name: "India (INR)" },
  ];

  const emergingSkills = [
    { skill: "LLM Application Development & RAG", growth: "+48%", demand: 94, category: "AI & ML" },
    { skill: "Kubernetes & Cloud Native Infra", growth: "+22%", demand: 88, category: "DevOps" },
    { skill: "Vector Databases (pgvector, Pinecone)", growth: "+36%", demand: 85, category: "Data & AI" },
    { skill: "FastAPI & High-Throughput Async Python", growth: "+18%", demand: 82, category: "Backend" },
    { skill: "TypeScript & Next.js App Router", growth: "+15%", demand: 80, category: "Frontend" },
  ];

  const salaryBands = [
    { role: "Backend Engineer", junior: "$70k", mid: "$110k", senior: "$155k", lead: "$195k" },
    { role: "Full Stack Engineer", junior: "$65k", mid: "$105k", senior: "$148k", lead: "$185k" },
    { role: "DevOps / Platform Engineer", junior: "$75k", mid: "$120k", senior: "$168k", lead: "$210k" },
    { role: "AI / ML Engineer", junior: "$85k", mid: "$135k", senior: "$185k", lead: "$230k" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Industry Market Intelligence</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Aggregated hiring signals, skill decay indices, and salary percentiles across global regions.
          </p>
        </div>
        <select
          value={region}
          onChange={e => setRegion(e.target.value)}
          className="rounded-lg border border-input p-2 text-sm bg-background font-semibold"
        >
          {regions.map(r => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select>
      </div>

      {/* Market Snapshot Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="p-5 bg-card rounded-xl border border-border shadow-sm">
          <span className="text-xs uppercase font-semibold text-muted-foreground">Snapshot Sample Size</span>
          <div className="mt-2 text-3xl font-extrabold text-foreground">15,420</div>
          <p className="text-xs text-muted-foreground mt-1">Verified postings analyzed</p>
        </div>
        <div className="p-5 bg-card rounded-xl border border-border shadow-sm">
          <span className="text-xs uppercase font-semibold text-muted-foreground">Backend Hiring Velocity</span>
          <div className="mt-2 text-3xl font-extrabold text-emerald-600">+14.2%</div>
          <p className="text-xs text-muted-foreground mt-1">Quarter-over-quarter expansion</p>
        </div>
        <div className="p-5 bg-card rounded-xl border border-border shadow-sm">
          <span className="text-xs uppercase font-semibold text-muted-foreground">Snapshot Freshness</span>
          <div className="mt-2 text-3xl font-extrabold text-primary">Live</div>
          <p className="text-xs text-muted-foreground mt-1">Updated November 15, 2026</p>
        </div>
      </div>

      {/* Emerging Skills Forecast */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-border pb-3">
          <h2 className="text-lg font-bold">Fastest Growing High-Demand Skills</h2>
          <span className="text-xs text-primary font-semibold">12-Month Projection</span>
        </div>
        <div className="space-y-3">
          {emergingSkills.map((sk, idx) => (
            <div key={idx} className="p-3.5 bg-muted/30 rounded-lg border border-border flex items-center justify-between">
              <div>
                <span className="font-bold text-sm">{sk.skill}</span>
                <span className="text-xs text-muted-foreground block mt-0.5">{sk.category}</span>
              </div>
              <div className="flex items-center gap-4 text-right">
                <div>
                  <span className="text-xs font-bold text-emerald-600 bg-emerald-50 dark:bg-emerald-950 px-2 py-0.5 rounded">
                    {sk.growth} YoY
                  </span>
                  <div className="text-[11px] text-muted-foreground mt-1">Demand Index: {sk.demand}/100</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Salary Distributions Table */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <h2 className="text-lg font-bold">Salary Distribution Benchmarks ({region.toUpperCase()})</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-muted/40 border-b border-border text-xs text-muted-foreground uppercase font-semibold">
              <tr>
                <th className="py-3 px-4">Role Title</th>
                <th className="py-3 px-4">Junior (0–2 yrs)</th>
                <th className="py-3 px-4">Mid-Level (2–5 yrs)</th>
                <th className="py-3 px-4">Senior (5–8 yrs)</th>
                <th className="py-3 px-4">Lead / Staff (8+ yrs)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {salaryBands.map((band, idx) => (
                <tr key={idx} className="hover:bg-muted/20">
                  <td className="py-3.5 px-4 font-bold">{band.role}</td>
                  <td className="py-3.5 px-4 text-muted-foreground">{band.junior}</td>
                  <td className="py-3.5 px-4 font-semibold text-primary">{band.mid}</td>
                  <td className="py-3.5 px-4 font-semibold text-foreground">{band.senior}</td>
                  <td className="py-3.5 px-4 font-bold text-emerald-600">{band.lead}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
