import Fastify, { type FastifyInstance } from "fastify";
import { API_PREFIX, HealthResponse } from "@theiaxr/shared";

export interface AppOptions {
  logger?: boolean;
}

/** Builds the Fastify app without starting it, so tests can call it directly. */
export function buildApp(options: AppOptions = {}): FastifyInstance {
  const app = Fastify({ logger: options.logger ?? false });

  app.get(`${API_PREFIX}/health`, async () => HealthResponse.parse({ ok: true }));

  return app;
}
