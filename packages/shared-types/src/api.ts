/**
 * Placeholder for generated OpenAPI client types.
 * Regenerate with: pnpm generate:types
 */

export interface HealthCheckResponse {
  status: 'ok' | 'degraded' | 'error';
  timestamp: string;
  version: string;
}

export interface ReadyCheckResponse {
  status: 'ok' | 'not_ready';
  database: boolean;
  redis: boolean;
  migrations_at_head: boolean;
}
