"use client";

import React, { useState, useEffect } from "react";

export default function SkillsPage() {
  const [skills, setSkills] = useState<any[]>([]);
  const [newSkill, setNewSkill] = useState({ slug: "", category: "backend", signal_value: 0.75, self_rating: 4.0, evidence_type: "project" });
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);

  const fetchSkills = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/skills");
      if (res.ok) {
        setSkills(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkills();
  }, []);

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSkill.slug) return;
    setAdding(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/skills/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          skill_slug: newSkill.slug,
          evidence_type: newSkill.evidence_type,
          signal_value: newSkill.signal_value,
          self_rating: newSkill.self_rating
        })
      });
      if (res.ok) {
        setNewSkill({ slug: "", category: "backend", signal_value: 0.75, self_rating: 4.0, evidence_type: "project" });
        await fetchSkills();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAdding(false);
    }
  };

  const handleRate = async (slug: string, rating: number) => {
    try {
      await fetch("http://localhost:8000/api/v1/me/skills/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          skill_slug: slug,
          self_rating: rating,
          signal_value: rating / 5.0,
          evidence_type: "self_report"
        })
      });
      await fetchSkills();
    } catch (e) {
      console.error(e);
    }
  };

  // Group by category
  const categories = Array.from(new Set(skills.map(s => s.category)));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-card p-6 rounded-xl border border-border shadow-sm">
        <div>
          <h1 className="text-2xl font-bold">Skills Graph & Taxonomy</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Calibrated proficiencies, evidence density, and category half-life decay indicators.
          </p>
        </div>
        <div className="text-xs bg-muted px-3 py-1.5 rounded-lg border border-border font-medium">
          Total Skills: <strong className="text-foreground">{skills.length}</strong>
        </div>
      </div>

      {/* Add Skill Form */}
      <form onSubmit={handleAddSkill} className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <h2 className="text-md font-bold">Add Skill with Verified Evidence</h2>
        <div className="grid gap-3 sm:grid-cols-4">
          <div>
            <label className="text-xs font-semibold">Skill Slug / Name</label>
            <input
              required
              placeholder="e.g. kubernetes, redis, graphql"
              value={newSkill.slug}
              onChange={e => setNewSkill({...newSkill, slug: e.target.value.toLowerCase()})}
              className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
            />
          </div>
          <div>
            <label className="text-xs font-semibold">Evidence Type</label>
            <select
              value={newSkill.evidence_type}
              onChange={e => setNewSkill({...newSkill, evidence_type: e.target.value})}
              className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
            >
              <option value="project">Project Work</option>
              <option value="experience">Job Experience</option>
              <option value="github">GitHub Repo</option>
              <option value="certification">Certification</option>
              <option value="assessment">Technical Assessment</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold">Proficiency Signal (0.1 – 1.0)</label>
            <input
              type="number"
              step="0.05"
              min="0.1"
              max="1.0"
              value={newSkill.signal_value}
              onChange={e => setNewSkill({...newSkill, signal_value: parseFloat(e.target.value)})}
              className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={adding || !newSkill.slug}
              className="w-full rounded bg-primary py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition disabled:opacity-50"
            >
              {adding ? "Calibrating..." : "+ Add Evidence"}
            </button>
          </div>
        </div>
      </form>

      {/* Category Sections */}
      {loading ? (
        <div className="text-center py-12 text-sm text-muted-foreground">Loading skills graph...</div>
      ) : (
        <div className="space-y-6">
          {categories.map(cat => (
            <div key={cat} className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
              <h2 className="text-md font-bold uppercase tracking-wider text-xs text-primary">
                {cat.replace("_", " & ")} Domain
              </h2>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {skills.filter(s => s.category === cat).map(skill => (
                  <div key={skill.id} className="p-4 rounded-lg bg-muted/30 border border-border space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm">{skill.name}</span>
                      <span className="text-xs font-bold text-primary">{Math.round(skill.proficiency)}%</span>
                    </div>

                    <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${skill.proficiency}%` }}
                      ></div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-muted-foreground pt-1">
                      <span>Evidence Items: {skill.evidence_count}</span>
                      <span>Conf: {Math.round(skill.confidence * 100)}%</span>
                    </div>

                    {/* Self-Rating Stars */}
                    <div className="pt-1 border-t border-border flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Self-Rating:</span>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map(star => (
                          <button
                            key={star}
                            onClick={() => handleRate(skill.skill_slug, star)}
                            className={`h-5 w-5 rounded text-[11px] font-bold ${
                              star <= Math.round(skill.self_rating)
                                ? "bg-amber-100 text-amber-800"
                                : "bg-muted text-muted-foreground hover:bg-muted/80"
                            }`}
                          >
                            {star}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
