import { afterAll, describe, expect, it } from "vitest";
import { HealthResponse } from "@theiaxr/shared";
import { buildApp } from "../src/app.ts";

describe("GET /api/v1/health", () => {
  const app = buildApp();
  afterAll(() => app.close());

  it("answers { ok: true }", async () => {
    const res = await app.inject({ method: "GET", url: "/api/v1/health" });
    expect(res.statusCode).toBe(200);
    expect(res.json()).toEqual({ ok: true });
    expect(HealthResponse.safeParse(res.json()).success).toBe(true);
  });
});
