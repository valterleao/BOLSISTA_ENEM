# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.config import default_paths
from src.reporting.charts import export_charts


def main() -> int:
    paths = default_paths()
    best_csv = paths.processed_dir / "best_group.csv"
    summary_path = paths.processed_dir / "ga_summary.json"
    pool_stats = paths.processed_dir / "pool_stats.json"

    if not best_csv.exists():
        print("Execute o GA antes: scripts/02_run_ga_cli.py")
        return 1

    best_df = pd.read_csv(best_csv)
    charts_dir = paths.processed_dir / "charts"
    export_charts(best_df, charts_dir)

    summary = {}
    if summary_path.exists():
        with open(summary_path, encoding="utf-8") as f:
            summary = json.load(f)

    pool = {}
    if pool_stats.exists():
        with open(pool_stats, encoding="utf-8") as f:
            pool = json.load(f)

    docs = paths.project_root / "docs"
    docs.mkdir(exist_ok=True)
    report = docs / "RELATORIO_BOLSAS_ENEM.md"

    content = f"""# Relatorio - Bolsas ENEM com Algoritmo Genetico

## Contexto

Fundacao educacional seleciona **100 bolsistas** a partir dos microdados ENEM 2024,
otimizando desempenho academico, diversidade socioeconomica/racial e cobertura geografica.

Fonte oficial: [Microdados ENEM - INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem)

## Mapeamento de variaveis (PDF vs microdados 2024)

| PDF | Coluna real | Observacao |
|-----|-------------|------------|
| NU_NOTA_RED | NU_NOTA_REDACAO | Nota da redacao |
| TP_ESCOLA | Q023 | Tipo de escola no EM |
| Q006 (renda) | Q007 | Renda familiar |
| Q002 | Q002 | Escolaridade da mae |
| SG_UF_RESIDENCIA | SG_UF_PROVA | Proxy geografico (UF da prova) |

## Preparacao dos dados

- Join PARTICIPANTES + RESULTADOS por ordem de linha (mesma estrategia do trabalho OLAP).
- Filtro: presenca em todas as areas e notas validas.
- Pool estratificado: **{pool.get('pool_rows', 'N/A')}** candidatos em **{pool.get('ufs_in_pool', 'N/A')}** UFs.

## Algoritmo genetico

- Cromossomo: 100 indices unicos no pool.
- Populacao: 20 | Geracoes: 100
- Fitness = 0.5*notas + 0.3*diversidade + 0.2*cobertura (pesos configuraveis na WEB)

### Resultado da ultima execucao

```json
{json.dumps(summary, ensure_ascii=False, indent=2)}
```

## Grupo ideal (amostra)

| NU_INSCRICAO | MEDIA_NOTAS | UF | COR_RACA |
|--------------|-------------|----|---------|
"""
    for _, row in best_df.head(10).iterrows():
        content += f"| {row['NU_INSCRICAO']} | {row['MEDIA_NOTAS']:.1f} | {row['SG_UF_PROVA']} | {row['TP_COR_RACA']} |\n"

    content += f"""
## Graficos

![Notas]({charts_dir.as_posix()}/notas_boxplot.png)
![Diversidade]({charts_dir.as_posix()}/diversidade_barras.png)
![Geografia]({charts_dir.as_posix()}/geo_uf.png)

## Limitacoes

- UF de prova como proxy de residencia.
- Pool amostrado (~40k) para viabilidade computacional.
- Questionario: renda em Q007 (nao Q006).

## Video demonstrativo (roteiro)

1. Executar `scripts/01_prepare_data.py`
2. Abrir interface WEB (`uvicorn` + `npm run dev`)
3. Ajustar pesos e rodar GA (grafo de evolucao)
4. Mostrar paginas Grupo Ideal e Analises
5. Destacar trade-off entre nota, diversidade e cobertura
"""
    report.write_text(content, encoding="utf-8")
    print(f"OK: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
