# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import default_paths
from src.data.prepare import PrepareConfig, build_candidate_pool


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Prepara pool de candidatos ENEM 2024 para o algoritmo genetico."
    )
    ap.add_argument("--chunksize", type=int, default=200_000)
    ap.add_argument("--pool-size", type=int, default=40_000)
    ap.add_argument("--cap-per-uf", type=int, default=2_000)
    args = ap.parse_args()

    paths = default_paths()
    cfg = PrepareConfig(
        chunksize=args.chunksize,
        pool_size=args.pool_size,
        cap_per_uf=args.cap_per_uf,
    )

    out = build_candidate_pool(
        participantes_csv=paths.participantes_csv,
        resultados_csv=paths.resultados_csv,
        processed_dir=paths.processed_dir,
        cfg=cfg,
    )
    print(f"OK: gerado {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
