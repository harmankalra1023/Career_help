"use client";

import React, { useState, useEffect } from "react";

export default function CareerDnaPage() {
  const [dashboard, setDashboard] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/me/dashboard")
      .then(res => res.json())
      .then(data => setDashboard(data))
      .catch(console.error);
  }, []);

  const dna = dashboard?.dna;
  const dimensions = dna?.dimensions || {
    technical_depth: 78,
    systems_thinking: 72,
    execution_speed: 68,
    collaboration: 65,
    creative_exploration: 55,
    product_sense: 60
  };

  const archetypes = [
    {
      title: "Systems Builder",
      desc: "Excels at core architecture, backend systems, scalability, distributed resilience, and database performance.",
      match: dna?.archetype?.find((a: any) => a.name === "Systems Builder")?.pct || 0.62,
      traits: ["High Systems Thinking", "Technical Depth", "Infrastructure Rigor"]
    },
    {
      title: "Applied Researcher",
      desc: "Thrives at the intersection of machine learning, algorithms, mathematical modeling, and empirical experimental rigor.",
      match: dna?.archetype?.find((a: any) => a.name === "Applied Researcher")?.pct || 0.21,
      traits: ["High Exploration", "Scientific Method", "Algorithm Optimization"]
    },
    {
      title: "Product Craftsman",
      desc: "Deep focus on user experience ergonomics, frontend fidelity, design token systems, and rapid prototyping velocity.",
      match: dna?.archetype?.find((a: any) => a.name === "Product Craftsman")?.pct || 0.17,
      traits: ["Product Intuition", "UI Polish", "Rapid Interaction Velocity"]
    },
    {
      title: "Engineering Orchestrator",
      desc: "Specializes in cross-functional delivery, technical leadership, developer enablement, and unblocking execution bottlenecks.",
      match: 0.14,
      traits: ["High Collaboration", "Organizational Agility", "Stakeholder Communication"]
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Career DNA & Archetypes</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Multi-dimensional psychometric and technical centroid clustering per PRD §9.9.
          </p>
        </div>
      </div>

      {/* 6 Dimension Radar Breakdown */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-6">
        <h2 className="text-lg font-bold">Core Competency Dimensions</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(dimensions).map(([dim, val]: [string, any]) => (
            <div key={dim} className="p-4 rounded-xl bg-muted/30 border border-border space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-xs capitalize tracking-wide text-muted-foreground">
                  {dim.replace("_", " ")}
                </span>
                <span className="font-bold text-sm text-primary">{Math.round(val)}%</span>
              </div>
              <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${val}%` }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Archetype Cards */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold">Archetype Proximity Clustering</h2>
        <div className="grid gap-6 sm:grid-cols-2">
          {archetypes.map((arch, idx) => (
            <div key={idx} className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex justify-between items-start">
                  <h3 className="font-bold text-base">{arch.title}</h3>
                  <span className="text-sm font-bold text-primary">{Math.round(arch.match * 100)}% Match</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full" style={{ width: `${arch.match * 100}%` }}></div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">{arch.desc}</p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {arch.traits.map((t, i) => (
                    <span key={i} className="text-[11px] bg-muted px-2 py-0.5 rounded font-medium text-muted-foreground">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
