import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getCharts } from "../api/client";

function SingleLineTick(props: {
  x?: number;
  y?: number;
  payload?: { value?: string };
}) {
  const { x = 0, y = 0, payload } = props;
  const value = String(payload?.value ?? "");
  return (
    <g transform={`translate(${x},${y})`}>
      <text
        x={-8}
        y={0}
        dy={4}
        textAnchor="end"
        fill="#94a3b8"
        style={{ whiteSpace: "nowrap" }}
      >
        {value}
      </text>
    </g>
  );
}

const RENDA_LABELS: Record<string, string> = {
  A: "Nenhuma renda",
  B: "Ate R$ 1.412,00",
  C: "R$ 1.412,01 a R$ 2.118,00",
  D: "R$ 2.118,01 a R$ 2.824,00",
  E: "R$ 2.824,01 a R$ 3.530,00",
  F: "R$ 3.530,01 a R$ 4.236,00",
  G: "R$ 4.236,01 a R$ 5.648,00",
  H: "R$ 5.648,01 a R$ 7.060,00",
  I: "R$ 7.060,01 a R$ 8.472,00",
  J: "R$ 8.472,01 a R$ 9.884,00",
  K: "R$ 9.884,01 a R$ 11.296,00",
  L: "R$ 11.296,01 a R$ 12.708,00",
  M: "R$ 12.708,01 a R$ 14.120,00",
  N: "R$ 14.120,01 a R$ 16.944,00",
  O: "R$ 16.944,01 a R$ 21.180,00",
  P: "R$ 21.180,01 a R$ 28.240,00",
  Q: "Acima de R$ 28.240,00",
};

const ESCOLA_LABELS: Record<string, string> = {
  A: "Somente em escola publica",
  B: "Parte publica e parte privada sem bolsa integral",
  C: "Parte publica e parte privada com bolsa integral",
  D: "Somente escola privada sem bolsa integral",
  E: "Somente escola privada com bolsa integral",
  F: "Nao frequentei escola no Ensino Medio",
};

const COR_RACA_LABELS: Record<string, string> = {
  "0": "Nao declarado",
  "1": "Branca",
  "2": "Preta",
  "3": "Parda",
  "4": "Amarela",
  "5": "Indigena",
  "6": "Nao dispoe da informacao",
};

const AREA_LABELS: Record<string, string> = {
  CN: "CN - Ciencias Naturais",
  CH: "CH - Ciencias Humanas",
  LC: "LC - Linguagens e Codigos",
  MT: "MT - Matematica",
  REDACAO: "Redacao",
};

export default function Analises() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getCharts()
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  if (error) return <div className="card"><p className="error-text">{error}</p></div>;
  if (!data) return <div className="card">Carregando...</div>;

  const geo = Object.entries((data.geo as Record<string, number>) || {}).map(([uf, qtd]) => ({
    uf,
    qtd,
  }));

  const cor = Object.entries(
    ((data.diversidade as Record<string, Record<string, number>>)?.cor_raca) || {}
  ).map(([k, v]) => ({ categoria: COR_RACA_LABELS[k] ?? k, qtd: v }));

  const renda = Object.entries(
    ((data.diversidade as Record<string, Record<string, number>>)?.renda) || {}
  ).map(([k, v]) => ({ categoria: RENDA_LABELS[k] ?? k, qtd: v }));
  const rendaHeight = Math.max(260, renda.length * 34);

  const notas = data.notas as Record<string, number[]>;
  const mediaPorArea = Object.entries(notas || {}).map(([area, vals]) => ({
    area: AREA_LABELS[area.replace("NU_NOTA_", "")] ?? area.replace("NU_NOTA_", ""),
    media: vals.reduce((a, b) => a + b, 0) / (vals.length || 1),
  }));

  const tooltip2 = (value: unknown) => {
    const n = Number(value);
    return Number.isFinite(n) ? n.toFixed(2) : String(value);
  };

  const tooltipInt = (value: unknown) => {
    const n = Number(value);
    if (!Number.isFinite(n)) return String(value);
    return Math.round(n).toString();
  };

  const tooltipQuantidade = (value: unknown) => [tooltipInt(value), "Quantidade"] as const;

  return (
    <>
      <div className="card metrics">
        <div className="metric">
          <span>Media grupo</span>
          <strong>{Number(data.media_grupo).toFixed(1)}</strong>
        </div>
        <div className="metric">
          <span>UFs</span>
          <strong>{String(data.ufs_cobertas)}</strong>
        </div>
      </div>

      <div className="card">
        <h3>Notas (media por area)</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={mediaPorArea}>
            <XAxis dataKey="area" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip formatter={tooltip2} />
            <Bar dataKey="media" fill="#7c3aed" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3>Diversidade - Cor/Raca</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={cor}>
              <XAxis dataKey="categoria" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip formatter={tooltipQuantidade} />
              <Bar dataKey="qtd" fill="#a78bfa" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3>Diversidade - Renda</h3>
          <div className="chart-scroll" style={{ maxHeight: 260 }}>
            <div style={{ height: rendaHeight }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={renda}
                  layout="vertical"
                  margin={{ top: 8, right: 16, bottom: 8, left: 16 }}
                >
                  <XAxis type="number" stroke="#94a3b8" />
                  <YAxis
                    type="category"
                    dataKey="categoria"
                    stroke="#94a3b8"
                    width={260}
                    interval={0}
                    tick={<SingleLineTick />}
                  />
                  <Tooltip formatter={tooltipQuantidade} />
                  <Bar dataKey="qtd" fill="#38bdf8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Distribuicao geografica (UF)</h3>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={geo}>
            <XAxis dataKey="uf" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip formatter={tooltipQuantidade} />
            <Legend />
            <Bar dataKey="qtd" fill="#38bdf8" name="Bolsistas" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
