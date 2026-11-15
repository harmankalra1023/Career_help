"use client";

import React, { useState, useEffect } from "react";

interface Message {
  role: "user" | "mentor";
  content: string;
  provider?: string;
  model?: string;
  actions?: string[];
}

export default function MentorPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "mentor",
      content: "Hello Alex! I am your Digital Career Twin AI Mentor powered by Groq. I have access to your verified skills, project evidence, and target role requirements (Backend Engineer). How can I assist your career progression today?",
      actions: [
        "How do I close my Docker gap quickly?",
        "What system design topics are essential for backend roles?",
        "How does my profile compare against Senior requirements?"
      ]
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/me/mentor/status")
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(console.error);
  }, []);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || loading) return;

    const userMsg: Message = { role: "user", content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/v1/me/mentor/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, target_role: "Backend Engineer" })
      });

      if (res.ok) {
        const data = await res.json();
        const mentorMsg: Message = {
          role: "mentor",
          content: data.reply,
          provider: data.provider,
          model: data.model,
          actions: data.suggested_actions
        };
        setMessages(prev => [...prev, mentorMsg]);
      } else {
        setMessages(prev => [...prev, {
          role: "mentor",
          content: "Sorry, I encountered an issue connecting to the LLM service. Please verify your Groq API key in .env."
        }]);
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        role: "mentor",
        content: "Network error connecting to backend service."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold">AI Career Mentor</h1>
            <span className="text-xs bg-orange-100 text-orange-800 font-bold px-2 py-0.5 rounded">
              Groq Cloud LLM
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-0.5">
            Context-grounded guidance calibrated directly against your verified Career Twin data.
          </p>
        </div>
        <div className="text-xs text-muted-foreground bg-muted/40 p-2.5 rounded-lg border border-border">
          Model: <strong className="text-foreground">{status?.model || "llama-3.3-70b-versatile"}</strong>
        </div>
      </div>

      {/* Chat Box */}
      <div className="bg-card rounded-xl border border-border shadow-sm flex flex-col h-[520px]">
        {/* Messages Stream */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-primary text-primary-foreground rounded-br-none"
                    : "bg-muted/60 text-foreground rounded-bl-none border border-border"
                }`}
              >
                {m.content}

                {/* Suggested Action Chips */}
                {m.actions && m.actions.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50 flex flex-wrap gap-1.5">
                    {m.actions.map((act, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(act)}
                        className="text-xs bg-card hover:bg-muted text-primary font-medium px-2.5 py-1 rounded-full border border-border transition"
                      >
                        {act}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {m.model && (
                <span className="text-[10px] text-muted-foreground mt-1 px-1">
                  Generated with {m.model}
                </span>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted/40 p-3 rounded-lg w-max">
              <span className="h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent"></span>
              <span>Mentor is analyzing your Career Twin and formulating advice...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-border bg-card rounded-b-xl flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend()}
            placeholder="Ask your AI Career Mentor about roadmaps, skill gaps, or interview readiness..."
            className="flex-1 rounded-lg border border-input p-2.5 text-sm bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="px-5 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold text-sm hover:bg-primary/90 transition disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
