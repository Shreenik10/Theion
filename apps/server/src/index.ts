import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { buildApp } from "./app.ts";

const mock = process.argv.includes("--mock") || process.env.MOCK_MODE === "1";

// Real mode reads the repo-root .env if it exists. Mock mode never reads it,
// so it runs with no API keys.
const envPath = fileURLToPath(new URL("../../../.env", import.meta.url));
if (!mock && existsSync(envPath)) {
  process.loadEnvFile(envPath);
}

const host = process.env.HOST ?? "127.0.0.1";
const port = Number(process.env.PORT ?? 3001);

const app = buildApp({ logger: true });
await app.listen({ host, port });
app.log.info(
  mock
    ? "Mock mode: no API keys are used and no external network calls are made."
    : "Real mode: providers are chosen from environment variables.",
);
