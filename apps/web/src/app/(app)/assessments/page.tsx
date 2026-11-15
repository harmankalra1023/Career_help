"use client";

import React, { useState, useEffect } from "react";

export default function AssessmentsPage() {
  const [instruments, setInstruments] = useState<any[]>([]);
  const [activeInst, setActiveInst] = useState<string | null>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/assessments/instruments")
      .then(res => res.json())
      .then(data => setInstruments(data))
      .catch(console.error);
  }, []);

  const startQuiz = async (instId: string) => {
    setActiveInst(instId);
    setAnswers({});
    setResult(null);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/assessments/questions/${instId}`);
      if (res.ok) {
        const data = await res.json();
        setQuestions(data.items || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectOption = (itemId: string, value: number) => {
    setAnswers(prev => ({ ...prev, [itemId]: value }));
  };

  const handleSubmit = async () => {
    if (!activeInst) return;
    setSubmitting(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/assessments/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          instrument_id: activeInst,
          answers: answers
        })
      });
      if (res.ok) {
        const json = await res.json();
        setResult(json.trait_scores);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Psychometric & Career Assessments</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Calibrate your non-technical traits, execution discipline, and Holland occupational interests.
          </p>
        </div>
      </div>

      {/* Instrument Picker */}
      {!activeInst && (
        <div className="grid gap-6 sm:grid-cols-2">
          {instruments.map(inst => (
            <div key={inst.id} className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-4 flex flex-col justify-between">
              <div className="space-y-2">
                <span className="text-xs uppercase font-bold text-primary tracking-wider">Validated Instrument</span>
                <h2 className="text-lg font-bold">{inst.name}</h2>
                <p className="text-xs text-muted-foreground leading-relaxed">{inst.description}</p>
                <div className="flex gap-4 text-xs text-muted-foreground pt-2">
                  <span>Questions: <strong>{inst.questions_count}</strong></span>
                  <span>Est. Time: <strong>{inst.estimated_minutes} mins</strong></span>
                </div>
              </div>
              <button
                onClick={() => startQuiz(inst.id)}
                className="w-full py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-semibold hover:bg-primary/90 transition shadow-sm"
              >
                Start Assessment &rarr;
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Active Quiz Runner */}
      {activeInst && !result && (
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-6 max-w-3xl mx-auto">
          <div className="flex justify-between items-center border-b border-border pb-4">
            <div>
              <h2 className="text-lg font-bold">
                {activeInst === "big5" ? "Big Five Personality Inventory" : "Holland Occupational Interests"}
              </h2>
              <span className="text-xs text-muted-foreground">
                Answered {Object.keys(answers).length} of {questions.length} items
              </span>
            </div>
            <button
              onClick={() => setActiveInst(null)}
              className="text-xs text-muted-foreground hover:text-foreground font-semibold"
            >
              Cancel
            </button>
          </div>

          <div className="space-y-6">
            {questions.map((q, idx) => (
              <div key={q.id} className="p-4 rounded-xl bg-muted/30 border border-border space-y-3">
                <div className="text-sm font-semibold">
                  <span className="text-primary mr-2">#{idx + 1}</span> {q.text}
                </div>
                <div className="grid grid-cols-5 gap-2 text-center">
                  {[
                    { label: "Disagree", val: 1 },
                    { label: "Slightly Disagree", val: 2 },
                    { label: "Neutral", val: 3 },
                    { label: "Slightly Agree", val: 4 },
                    { label: "Agree", val: 5 },
                  ].map(opt => (
                    <button
                      key={opt.val}
                      type="button"
                      onClick={() => handleSelectOption(q.id, opt.val)}
                      className={`p-2 rounded-lg border text-xs font-semibold transition ${
                        answers[q.id] === opt.val
                          ? "bg-primary text-primary-foreground border-primary"
                          : "bg-background border-border hover:bg-muted text-muted-foreground"
                      }`}
                    >
                      {opt.val}
                      <span className="hidden sm:block text-[10px] mt-0.5">{opt.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="flex justify-end pt-4">
            <button
              onClick={handleSubmit}
              disabled={submitting || Object.keys(answers).length < questions.length}
              className="px-6 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90 transition disabled:opacity-50"
            >
              {submitting ? "Computing Traits..." : "Submit & Calculate Trait Profile"}
            </button>
          </div>
        </div>
      )}

      {/* Results View */}
      {result && (
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm space-y-6 max-w-2xl mx-auto">
          <div className="text-center space-y-1">
            <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">Completed</span>
            <h2 className="text-xl font-bold">Computed Psychometric Profile</h2>
            <p className="text-xs text-muted-foreground">Normalized trait dimensions stored in your Career Twin state</p>
          </div>

          <div className="space-y-4 pt-2">
            {Object.entries(result).map(([trait, score]: [string, any]) => (
              <div key={trait} className="space-y-1">
                <div className="flex justify-between text-sm font-semibold capitalize">
                  <span>{trait.replace("_", " ")}</span>
                  <span className="text-primary">{Math.round(score)}%</span>
                </div>
                <div className="h-2.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full transition-all" style={{ width: `${score}%` }}></div>
                </div>
              </div>
            ))}
          </div>

          <div className="pt-4 flex justify-center">
            <button
              onClick={() => setActiveInst(null)}
              className="px-5 py-2 rounded-lg bg-secondary text-secondary-foreground text-xs font-semibold hover:bg-secondary/80"
            >
              Take Another Assessment
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
