import { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { useTheme } from "../context/ThemeContext";

type GenNode = {
  id: string;
  gen: number;
  fitness: number;
};

type GenLink = { source: string; target: string };

type Props = {
  history: Array<{ generation: number; best_fitness: number }>;
  running?: boolean;
};

const GRAPH_HEIGHT = 560;
const NODE_COLOR = "#7c3aed"; // mesma cor do botao Executar selecao (--accent)

export default function EvolutionGraph({ history, running = false }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(700);
  const { graphBackground, graphLinkColor } = useTheme();

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const update = () => setWidth(el.clientWidth);
    update();

    const observer = new ResizeObserver(update);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const nodes: GenNode[] = history.map((h) => ({
    id: `g${h.generation}`,
    gen: h.generation,
    fitness: h.best_fitness,
  }));

  const links: GenLink[] = [];
  for (let i = 1; i < nodes.length; i++) {
    links.push({ source: nodes[i - 1].id, target: nodes[i].id });
  }

  const latest = history.length > 0 ? history[history.length - 1] : null;

  return (
    <div ref={containerRef} className="card evolution-graph-card">
      <div className="evolution-graph-header">
        <h3>Evolucao do processamento</h3>
        {latest && (
          <span className="evolution-status">
            Gen {latest.generation} | fitness {latest.best_fitness.toFixed(4)}
          </span>
        )}
        {running && !latest && (
          <span className="evolution-status">Iniciando...</span>
        )}
      </div>

      {nodes.length === 0 ? (
        <div className="evolution-placeholder">
          <p>Aguardando execucao do algoritmo genetico...</p>
        </div>
      ) : (
        <ForceGraph2D
          graphData={{ nodes, links }}
          width={width - 32}
          height={GRAPH_HEIGHT}
          nodeLabel={(n: GenNode) => `Gen ${n.gen}: ${n.fitness.toFixed(4)}`}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const n = node as GenNode & { x?: number; y?: number };
            const r = 4 + n.fitness * 8;
            ctx.beginPath();
            ctx.arc(n.x ?? 0, n.y ?? 0, r / globalScale, 0, 2 * Math.PI);
            ctx.fillStyle = NODE_COLOR;
            ctx.fill();
          }}
          linkColor={() => graphLinkColor}
          backgroundColor={graphBackground}
        />
      )}
    </div>
  );
}
