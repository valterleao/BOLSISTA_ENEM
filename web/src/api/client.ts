export type RunParams = {
  population: number;
  generations: number;
  group_size: number;
  w_notas: number;
  w_div: number;
  w_geo: number;
  seed?: number;
};

export async function health() {
  const r = await fetch("/api/health");
  return r.json();
}

export async function startGa(params: RunParams) {
  const r = await fetch("/api/ga/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getBestGroup() {
  const r = await fetch("/api/results/best-group");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getMetrics() {
  const r = await fetch("/api/results/metrics");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function getCharts() {
  const r = await fetch("/api/results/charts");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export function streamGa(onEvent: (data: Record<string, unknown>) => void): EventSource {
  const es = new EventSource("/api/ga/stream");
  es.onmessage = (ev) => {
    try {
      onEvent(JSON.parse(ev.data));
    } catch {
      /* ignore */
    }
  };
  return es;
}
