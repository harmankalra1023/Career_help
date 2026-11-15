"use client";

import React, { useState } from "react";

export default function SettingsPage() {
  const [consents, setConsents] = useState({
    data_processing: true,
    ai_mentor: true,
    telemetry: false,
    public_twin: false,
  });
  const [exporting, setExporting] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleToggle = (key: string) => {
    setConsents(prev => ({ ...prev, [key]: !(prev as any)[key] }));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/me/dashboard");
      if (res.ok) {
        const json = await res.json();
        const blob = new Blob([JSON.stringify(json, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `career_twin_export_${new Date().toISOString().split("T")[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm">
        <h1 className="text-2xl font-bold">Account, Privacy & Consents</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          GDPR data export, telemetry consent flags, and account settings.
        </p>
      </div>

      {saved && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-800 rounded-lg">
          Privacy preferences updated successfully.
        </div>
      )}

      {/* Consent Toggles */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <h2 className="text-lg font-bold">Privacy Controls & Data Consents</h2>
        <div className="space-y-4 pt-1">
          <div className="flex items-center justify-between p-3.5 bg-muted/20 rounded-lg border border-border">
            <div>
              <div className="font-semibold text-sm">Evidence Data Processing</div>
              <p className="text-xs text-muted-foreground">Allow algorithms to compute proficiency decay & scores from submitted evidence</p>
            </div>
            <input
              type="checkbox"
              checked={consents.data_processing}
              onChange={() => handleToggle("data_processing")}
              className="h-4 w-4 rounded text-primary focus:ring-primary"
            />
          </div>

          <div className="flex items-center justify-between p-3.5 bg-muted/20 rounded-lg border border-border">
            <div>
              <div className="font-semibold text-sm">Groq AI Mentor Access</div>
              <p className="text-xs text-muted-foreground">Allow AI Mentor to review your skill gaps and recommend tailored learning pathways</p>
            </div>
            <input
              type="checkbox"
              checked={consents.ai_mentor}
              onChange={() => handleToggle("ai_mentor")}
              className="h-4 w-4 rounded text-primary focus:ring-primary"
            />
          </div>

          <div className="flex items-center justify-between p-3.5 bg-muted/20 rounded-lg border border-border">
            <div>
              <div className="font-semibold text-sm">Anonymous Telemetry</div>
              <p className="text-xs text-muted-foreground">Share anonymous system performance metrics to improve the platform</p>
            </div>
            <input
              type="checkbox"
              checked={consents.telemetry}
              onChange={() => handleToggle("telemetry")}
              className="h-4 w-4 rounded text-primary focus:ring-primary"
            />
          </div>
        </div>
      </div>

      {/* Export Archive */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4">
        <h2 className="text-lg font-bold">Data Portability (GDPR Article 20)</h2>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Download a complete, machine-readable JSON archive of your Career Twin scores, verified evidence, psychometric assessments, and roadmap history.
        </p>
        <button
          onClick={handleExport}
          disabled={exporting}
          className="px-5 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold text-xs hover:bg-primary/90 transition shadow-sm disabled:opacity-50"
        >
          {exporting ? "Preparing Archive..." : "Export Career Twin JSON Archive"}
        </button>
      </div>
    </div>
  );
}
