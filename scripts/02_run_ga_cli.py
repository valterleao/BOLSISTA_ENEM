# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from src.config import default_paths
from src.ga.engine import GAConfig, run_ga, save_ga_outputs
from src.ga.fitness import FitnessWeights


def main() -> int:
    ap = argparse.ArgumentParser(description="Executa algoritmo genetico para selecao de bolsistas.")
    ap.add_argument("--population", type=int, default=20)
    ap.add_argument("--generations", type=int, default=100)
    ap.add_argument("--group-size", type=int, default=100)
    ap.add_argument("--w-notas", type=float, default=0.5)
    ap.add_argument("--w-div", type=float, default=0.3)
    ap.add_argument("--w-geo", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    paths = default_paths()
    parquet = paths.processed_dir / "candidates.parquet"
    if not parquet.exists():
        print("candidates.parquet nao encontrado. Execute scripts/01_prepare_data.py primeiro.")
        return 1

    df = pd.read_parquet(parquet)
    ga_cfg = GAConfig(
        population_size=args.population,
        generations=args.generations,
        group_size=args.group_size,
        random_seed=args.seed,
    )
    weights = FitnessWeights(w_notas=args.w_notas, w_diversidade=args.w_div, w_geo=args.w_geo)

    def progress(gen: int, stats: dict) -> None:
        if gen % 10 == 0 or gen == args.generations:
            print(
                f"gen={gen} best={stats['best_fitness']:.4f} "
                f"notas={stats['best_notas']:.3f} div={stats['best_diversidade']:.3f} "
                f"geo={stats['best_cobertura']:.3f}"
            )

    result = run_ga(df, ga_cfg, weights, progress_cb=progress)
    outputs = save_ga_outputs(df, result, paths.processed_dir)
    print(f"OK fitness={result.best_fitness:.4f}")
    print(f"best_group -> {outputs['best_group']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
