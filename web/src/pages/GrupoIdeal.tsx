import { useEffect, useState } from "react";
import { getBestGroup, getMetrics } from "../api/client";

type Row = Record<string, string | number>;

const RACA_LABELS: Record<string, string> = {
  "0": "Nao declarado",
  "1": "Branca",
  "2": "Preta",
  "3": "Parda",
  "4": "Amarela",
  "5": "Indigena",
  "6": "Nao dispoe da informacao",
};

function getRacaLabel(value: string | number | undefined): string {
  const key = String(value ?? "").trim();
  return RACA_LABELS[key] ?? (key || "Nao informado");
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

function getRendaLabel(value: string | number | undefined): string {
  const key = String(value ?? "").trim().toUpperCase();
  return RENDA_LABELS[key] ?? (key || "Nao informado");
}

const ESCOLA_LABELS: Record<string, string> = {
  A: "Somente em escola publica",
  B: "Parte publica e parte privada sem bolsa integral",
  C: "Parte publica e parte privada com bolsa integral",
  D: "Somente escola privada sem bolsa integral",
  E: "Somente escola privada com bolsa integral",
  F: "Nao frequentei escola no Ensino Medio",
};

function getEscolaLabel(value: string | number | undefined): string {
  const key = String(value ?? "").trim().toUpperCase();
  return ESCOLA_LABELS[key] ?? (key || "Nao informado");
}

export default function GrupoIdeal() {
  const [rows, setRows] = useState<Row[]>([]);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  const load = () => {
    Promise.all([getBestGroup(), getMetrics()])
      .then(([bg, m]) => {
        setRows(bg.rows);
        setMetrics(m);
        setError("");
      })
      .catch((e) => setError(String(e)));
  };

  useEffect(() => {
    load();
  }, []);

  const media =
    rows.length > 0
      ? rows.reduce((s, r) => s + Number(r.MEDIA_NOTAS || 0), 0) / rows.length
      : 0;
  const ufs = new Set(rows.map((r) => r.SG_UF_PROVA)).size;

  return (
    <>
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <h2>Grupo Ideal de Bolsistas</h2>
          <button className="primary" onClick={load}>
            Atualizar
          </button>
        </div>
        {error && <p className="error-text">{error}</p>}
        <div className="metrics">
          <div className="metric">
            <span>Bolsistas</span>
            <strong>{rows.length}</strong>
          </div>
          <div className="metric">
            <span>Media do grupo</span>
            <strong>{media.toFixed(1)}</strong>
          </div>
          <div className="metric">
            <span>UFs cobertas</span>
            <strong>{ufs}</strong>
          </div>
          <div className="metric">
            <span>Fitness</span>
            <strong>
              {metrics
                ? Number((metrics as { best_fitness?: number }).best_fitness || 0).toFixed(4)
                : "-"}
            </strong>
          </div>
        </div>
      </div>

      <div className="card" style={{ overflowX: "auto" }}>
        <table>
          <thead>
            <tr>
              <th>Inscricao</th>
              <th>Media</th>
              <th>CN</th>
              <th>CH</th>
              <th>LC</th>
              <th>MT</th>
              <th>Redacao</th>
              <th>UF</th>
              <th>Raca</th>
              <th>Renda</th>
              <th>Escola</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={String(r.NU_INSCRICAO)}>
                <td>{r.NU_INSCRICAO}</td>
                <td>{Number(r.MEDIA_NOTAS).toFixed(1)}</td>
                <td>{Number(r.NU_NOTA_CN).toFixed(0)}</td>
                <td>{Number(r.NU_NOTA_CH).toFixed(0)}</td>
                <td>{Number(r.NU_NOTA_LC).toFixed(0)}</td>
                <td>{Number(r.NU_NOTA_MT).toFixed(0)}</td>
                <td>{Number(r.NU_NOTA_REDACAO).toFixed(0)}</td>
                <td>{r.SG_UF_PROVA}</td>
                <td>{getRacaLabel(r.TP_COR_RACA)}</td>
                <td>{getRendaLabel(r.Q007)}</td>
                <td>{getEscolaLabel(r.Q023)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
