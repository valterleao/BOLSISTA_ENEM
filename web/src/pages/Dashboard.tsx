import { useEffect, useState } from "react";
import EvolutionGraph from "../components/EvolutionGraph";
import ExecutionLogModal from "../components/ExecutionLogModal";
import ThemeToggle from "../components/ThemeToggle";
import { health, startGa, streamGa } from "../api/client";

type HistoryItem = {
  generation: number;
  best_fitness: number;
  best_notas?: number;
  best_diversidade?: number;
  best_cobertura?: number;
};

export default function Dashboard() {
  const [wNotas, setWNotas] = useState(0.5);
  const [wDiv, setWDiv] = useState(0.3);
  const [wGeo, setWGeo] = useState(0.2);
  const [population, setPopulation] = useState(20);
  const [generations, setGenerations] = useState(100);
  const [groupSize, setGroupSize] = useState(100);
  const [running, setRunning] = useState(false);
  const [ready, setReady] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [log, setLog] = useState<string[]>([]);
  const [showLogModal, setShowLogModal] = useState(false);

  useEffect(() => {
    health().then((h) => setReady(Boolean(h.candidates_ready)));
  }, []);

  const run = async () => {
    setHistory([]);
    setLog([]);
    setRunning(true);
    try {
      const es = streamGa((data) => {
        if (data.error) {
          setLog((l) => [...l, `ERRO: ${data.error}`]);
          setRunning(false);
          es.close();
          return;
        }
        if (data.done) {
          setLog((l) => [...l, "Concluido."]);
          setRunning(false);
          es.close();
          return;
        }
        if (typeof data.generation === "number") {
          const item = data as HistoryItem;
          setHistory((h) => {
            const next = [...h];
            const idx = next.findIndex((x) => x.generation === item.generation);
            if (idx >= 0) next[idx] = item;
            else next.push(item);
            return next.sort((a, b) => a.generation - b.generation);
          });
          setLog((l) => [
            ...l.slice(-80),
            `Gen ${item.generation}: fitness=${item.best_fitness?.toFixed(4)}`,
          ]);
        }
      });

      await startGa({
        population,
        generations,
        group_size: groupSize,
        w_notas: wNotas,
        w_div: wDiv,
        w_geo: wGeo,
      });
    } catch (e) {
      setLog((l) => [...l, String(e)]);
      setRunning(false);
    }
  };

  return (
    <>
      <div className="card">
        <div className="config-header">
          <h2>Configuracao</h2>
          <ThemeToggle />
        </div>
        {!ready && (
          <p className="error-text">
            Pool nao encontrado. Execute: python scripts/01_prepare_data.py
          </p>
        )}
        <div className="grid-2">
          <div>
            <label>Notas: {wNotas.toFixed(2)}</label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={wNotas}
              onChange={(e) => setWNotas(Number(e.target.value))}
            />
            <label>Diversidade: {wDiv.toFixed(2)}</label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={wDiv}
              onChange={(e) => setWDiv(Number(e.target.value))}
            />
            <label>Cobertura: {wGeo.toFixed(2)}</label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={wGeo}
              onChange={(e) => setWGeo(Number(e.target.value))}
            />
          </div>
          <div>
            <label>Populacao: {population}</label>
            <input
              type="range"
              min={10}
              max={50}
              value={population}
              onChange={(e) => setPopulation(Number(e.target.value))}
            />
            <label>Geracoes: {generations}</label>
            <input
              type="range"
              min={20}
              max={200}
              value={generations}
              onChange={(e) => setGenerations(Number(e.target.value))}
            />
            <label>Tamanho do grupo: {groupSize}</label>
            <input
              type="range"
              min={50}
              max={150}
              value={groupSize}
              onChange={(e) => setGroupSize(Number(e.target.value))}
            />
          </div>
        </div>
        <div className="action-buttons">
          <button className="primary" disabled={running || !ready} onClick={run}>
            {running ? "Executando..." : "Executar selecao"}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={() => setShowLogModal(true)}
          >
            Log de execucao
          </button>
        </div>
      </div>

      <EvolutionGraph history={history} running={running} />

      <ExecutionLogModal
        open={showLogModal}
        logs={log}
        onClose={() => setShowLogModal(false)}
      />
    </>
  );
}
