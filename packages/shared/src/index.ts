import { z } from "zod";

/** Response of GET /api/v1/health. Shared by the server and the web app. */
export const HealthResponse = z.object({
  ok: z.literal(true),
});
export type HealthResponse = z.infer<typeof HealthResponse>;

export const API_PREFIX = "/api/v1";
