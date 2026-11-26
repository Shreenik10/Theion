import { useEffect, useState } from "react";
import { API_PREFIX, HealthResponse } from "@theiaxr/shared";

type Status = "checking" | "ok" | "unreachable";

export function App() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    fetch(`${API_PREFIX}/health`)
      .then((r) => r.json())
      .then((body) => setStatus(HealthResponse.safeParse(body).success ? "ok" : "unreachable"))
      .catch(() => setStatus("unreachable"));
  }, []);

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "3rem", textAlign: "center" }}>
      <h1>TheiaXR</h1>
      <p>Server: {status}</p>
    </main>
  );
}
