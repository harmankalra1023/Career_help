export * from './api';

export type ScoreBand = 'emerging' | 'developing' | 'solid' | 'strong' | 'exceptional';

export interface ScoreDetail {
  value: number;
  band: ScoreBand;
  confidence: number;
  delta_since_last?: number;
  as_of: string;
}

export interface UserDashboardData {
  scores: {
    profile: ScoreDetail;
    technical: ScoreDetail;
    non_technical: ScoreDetail;
    career_match_top?: {
      role_slug: string;
      value: number;
      band: ScoreBand;
    };
    industry_demand?: {
      value: number;
      band: ScoreBand;
      snapshot_id: string;
      stale: boolean;
    };
    job_readiness?: {
      role_slug: string;
      value: number;
      band: ScoreBand;
      time_to_ready_weeks: [number, number];
    };
  };
  dna: {
    archetype: Array<{ name: string; pct: number }>;
    dimensions: Record<string, number>;
  };
  strengths: Array<{
    label: string;
    evidence: string[];
    percentile: number;
  }>;
  gaps: Array<{
    skill: string;
    current: number;
    required: number;
    priority: number;
    jrs_gain: number;
    est_hours: number;
  }>;
}
