"use client";

import React, { useState, useEffect } from "react";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [completeness, setCompleteness] = useState<any>(null);
  const [resumeText, setResumeText] = useState("");
  const [parsing, setParsing] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  // Form states
  const [showEduModal, setShowEduModal] = useState(false);
  const [newEdu, setNewEdu] = useState({ institution: "", degree: "", level: "bachelors", branch: "", start_year: 2021, end_year: 2025 });

  const [showExpModal, setShowExpModal] = useState(false);
  const [newExp, setNewExp] = useState({ company: "", title: "", start_date: "2024-01-01", description: "", skills: "python, fastapi" });

  const [showProjModal, setShowProjModal] = useState(false);
  const [newProj, setNewProj] = useState({ title: "", description: "", repo_url: "", skills: "docker, postgresql" });

  const loadData = async () => {
    try {
      const [profRes, compRes] = await Promise.all([
        fetch("http://localhost:8000/api/v1/me/profile"),
        fetch("http://localhost:8000/api/v1/me/profile/completeness")
      ]);
      if (profRes.ok) setProfile(await profRes.json());
      if (compRes.ok) setCompleteness(await compRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleParseResume = async () => {
    if (!resumeText.trim()) return;
    setParsing(true);
    setStatusMsg(null);
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/ingest/resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resumeText })
      });
      if (res.ok) {
        const json = await res.json();
        setStatusMsg(`Successfully extracted ${json.skills_extracted_count} skills: ${json.skills.join(", ")}`);
        setResumeText("");
        await loadData();
      }
    } catch (e) {
      setStatusMsg("Error parsing resume.");
    } finally {
      setParsing(false);
    }
  };

  const handleAddEdu = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/profile/education", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newEdu)
      });
      if (res.ok) {
        setShowEduModal(false);
        await loadData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddExp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/profile/experience", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newExp,
          skills_used: newExp.skills.split(",").map(s => s.trim())
        })
      });
      if (res.ok) {
        setShowExpModal(false);
        await loadData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddProj = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/profile/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newProj,
          skills_used: newProj.skills.split(",").map(s => s.trim())
        })
      });
      if (res.ok) {
        setShowProjModal(false);
        await loadData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Completeness */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Profile & Verification</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Calibrate your verified education, work history, projects, and certifications.
          </p>
        </div>
        <div className="bg-muted/40 p-4 rounded-xl border border-border min-w-[240px]">
          <div className="flex justify-between items-center text-xs font-semibold mb-1.5">
            <span>Profile Completeness</span>
            <span className="text-primary font-bold">{Math.round((completeness?.completeness || 0) * 100)}%</span>
          </div>
          <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${(completeness?.completeness || 0) * 100}%` }}></div>
          </div>
          <div className="mt-2 text-[11px] text-muted-foreground">
            Completed: {completeness?.completed_sections?.join(", ") || "None"}
          </div>
        </div>
      </div>

      {statusMsg && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-800 font-medium">
          {statusMsg}
        </div>
      )}

      {/* Resume Ingestion Section */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold">Resume & Document Ingestion</h2>
            <p className="text-xs text-muted-foreground">
              Paste plain resume text to automatically extract verified skills and career evidence.
            </p>
          </div>
          <span className="text-xs bg-primary/10 text-primary font-semibold px-2.5 py-1 rounded">
            Auto-Extractor
          </span>
        </div>
        <textarea
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          placeholder="Paste resume text here (e.g. Built microservices with Python and FastAPI, configured Docker containers, engineered PostgreSQL schemas...)"
          rows={3}
          className="w-full rounded-lg border border-input p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-background"
        />
        <button
          onClick={handleParseResume}
          disabled={parsing || !resumeText.trim()}
          className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 transition disabled:opacity-50"
        >
          {parsing ? "Parsing & Calibrating..." : "Parse Resume & Calibrate Skills"}
        </button>
      </div>

      {/* Profile Sections Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Education */}
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h2 className="text-lg font-bold">Education</h2>
            <button
              onClick={() => setShowEduModal(true)}
              className="text-xs font-semibold text-primary bg-primary/10 hover:bg-primary/20 px-2.5 py-1 rounded transition"
            >
              + Add Education
            </button>
          </div>
          <div className="space-y-3">
            {profile?.education?.length === 0 ? (
              <p className="text-xs text-muted-foreground">No education items recorded.</p>
            ) : (
              profile?.education?.map((edu: any) => (
                <div key={edu.id} className="p-3.5 rounded-lg bg-muted/30 border border-border space-y-1">
                  <div className="flex justify-between font-semibold text-sm">
                    <span>{edu.degree}</span>
                    <span className="text-xs text-muted-foreground">{edu.start_year} – {edu.end_year || "Present"}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">{edu.institution} ({edu.branch})</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Experience */}
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h2 className="text-lg font-bold">Work Experience</h2>
            <button
              onClick={() => setShowExpModal(true)}
              className="text-xs font-semibold text-primary bg-primary/10 hover:bg-primary/20 px-2.5 py-1 rounded transition"
            >
              + Add Experience
            </button>
          </div>
          <div className="space-y-3">
            {profile?.experiences?.length === 0 ? (
              <p className="text-xs text-muted-foreground">No work experience recorded.</p>
            ) : (
              profile?.experiences?.map((exp: any) => (
                <div key={exp.id} className="p-3.5 rounded-lg bg-muted/30 border border-border space-y-1.5">
                  <div className="flex justify-between font-semibold text-sm">
                    <span>{exp.title}</span>
                    <span className="text-xs text-muted-foreground">{exp.start_date} – {exp.end_date || "Present"}</span>
                  </div>
                  <div className="text-xs font-medium text-primary">{exp.company} &bull; {exp.location || "Remote"}</div>
                  <p className="text-xs text-muted-foreground line-clamp-2">{exp.description}</p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Projects */}
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h2 className="text-lg font-bold">Verified Projects</h2>
            <button
              onClick={() => setShowProjModal(true)}
              className="text-xs font-semibold text-primary bg-primary/10 hover:bg-primary/20 px-2.5 py-1 rounded transition"
            >
              + Add Project
            </button>
          </div>
          <div className="space-y-3">
            {profile?.projects?.map((proj: any) => (
              <div key={proj.id} className="p-3.5 rounded-lg bg-muted/30 border border-border space-y-1.5">
                <div className="flex justify-between font-semibold text-sm items-center">
                  <span>{proj.title}</span>
                  {proj.verified && (
                    <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.5 rounded">
                      Verified GitHub
                    </span>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">{proj.description}</p>
                {proj.repo_url && (
                  <a href={proj.repo_url} target="_blank" className="text-xs text-primary hover:underline block truncate">
                    {proj.repo_url}
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Certifications */}
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <h2 className="text-lg font-bold">Certifications & Credentials</h2>
          </div>
          <div className="space-y-3">
            {profile?.certifications?.map((cert: any) => (
              <div key={cert.id} className="p-3.5 rounded-lg bg-muted/30 border border-border space-y-1">
                <div className="font-semibold text-sm">{cert.name}</div>
                <div className="text-xs text-muted-foreground">{cert.issuer} &bull; Issued {cert.issued_on}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Add Education Modal */}
      {showEduModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <form onSubmit={handleAddEdu} className="w-full max-w-md bg-card p-6 rounded-xl border border-border space-y-4 shadow-xl">
            <h3 className="text-lg font-bold">Add Education</h3>
            <div>
              <label className="text-xs font-semibold">Institution</label>
              <input
                required
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                value={newEdu.institution}
                onChange={e => setNewEdu({...newEdu, institution: e.target.value})}
              />
            </div>
            <div>
              <label className="text-xs font-semibold">Degree</label>
              <input
                required
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                value={newEdu.degree}
                onChange={e => setNewEdu({...newEdu, degree: e.target.value})}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-semibold">Start Year</label>
                <input
                  type="number"
                  className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                  value={newEdu.start_year}
                  onChange={e => setNewEdu({...newEdu, start_year: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <label className="text-xs font-semibold">End Year</label>
                <input
                  type="number"
                  className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                  value={newEdu.end_year}
                  onChange={e => setNewEdu({...newEdu, end_year: parseInt(e.target.value)})}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowEduModal(false)} className="px-4 py-2 text-xs rounded border border-border">Cancel</button>
              <button type="submit" className="px-4 py-2 text-xs rounded bg-primary text-primary-foreground font-semibold">Save</button>
            </div>
          </form>
        </div>
      )}

      {/* Add Experience Modal */}
      {showExpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <form onSubmit={handleAddExp} className="w-full max-w-md bg-card p-6 rounded-xl border border-border space-y-4 shadow-xl">
            <h3 className="text-lg font-bold">Add Work Experience</h3>
            <div>
              <label className="text-xs font-semibold">Company</label>
              <input
                required
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                value={newExp.company}
                onChange={e => setNewExp({...newExp, company: e.target.value})}
              />
            </div>
            <div>
              <label className="text-xs font-semibold">Title</label>
              <input
                required
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                value={newExp.title}
                onChange={e => setNewExp({...newExp, title: e.target.value})}
              />
            </div>
            <div>
              <label className="text-xs font-semibold">Skills (comma-separated)</label>
              <input
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                value={newExp.skills}
                onChange={e => setNewExp({...newExp, skills: e.target.value})}
              />
            </div>
            <div>
              <label className="text-xs font-semibold">Description</label>
              <textarea
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                rows={3}
                value={newExp.description}
                onChange={e => setNewExp({...newExp, description: e.target.value})}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowExpModal(false)} className="px-4 py-2 text-xs rounded border border-border">Cancel</button>
              <button type="submit" className="px-4 py-2 text-xs rounded bg-primary text-primary-foreground font-semibold">Save</button>
            </div>
          </form>
        </div>
      )}

      {/* Add Project Modal */}
      {showProjModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <form onSubmit={handleAddProj} className="w-full max-w-md bg-card p-6 rounded-xl border border-border space-y-4 shadow-xl">
            <h3 className="text-lg font-bold">Add Verified Project</h3>
            <div>
              <label className="text-xs font-semibold">Project Title</label>
              <input
                required
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                value={newProj.title}
                onChange={e => setNewProj({...newProj, title: e.target.value})}
              />
            </div>
            <div>
              <label className="text-xs font-semibold">Repository URL</label>
              <input
                type="url"
                placeholder="https://github.com/..."
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                value={newProj.repo_url}
                onChange={e => setNewProj({...newProj, repo_url: e.target.value})}
              />
            </div>
            <div>
              <label className="text-xs font-semibold">Description</label>
              <textarea
                className="mt-1 w-full rounded border border-input p-2 text-sm bg-background"
                rows={3}
                value={newProj.description}
                onChange={e => setNewProj({...newProj, description: e.target.value})}
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button type="button" onClick={() => setShowProjModal(false)} className="px-4 py-2 text-xs rounded border border-border">Cancel</button>
              <button type="submit" className="px-4 py-2 text-xs rounded bg-primary text-primary-foreground font-semibold">Save</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
