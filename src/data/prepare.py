# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List

import numpy as np
import pandas as pd


NOTA_COLS = [
    "NU_NOTA_CN",
    "NU_NOTA_CH",
    "NU_NOTA_LC",
    "NU_NOTA_MT",
    "NU_NOTA_REDACAO",
]

PRES_COLS = [
    "TP_PRESENCA_CN",
    "TP_PRESENCA_CH",
    "TP_PRESENCA_LC",
    "TP_PRESENCA_MT",
]


@dataclass(frozen=True)
class PrepareConfig:
    chunksize: int = 200_000
    pool_size: int = 40_000
    cap_per_uf: int = 2_000
    random_seed: int = 42


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _iter_chunks(csv_path: Path, usecols: List[str], chunksize: int) -> Iterator[pd.DataFrame]:
    return pd.read_csv(
        csv_path,
        sep=";",
        encoding="latin-1",
        dtype="string",
        usecols=usecols,
        chunksize=chunksize,
        low_memory=False,
    )


def _eligible_mask(resultados: pd.DataFrame) -> pd.Series:
    pres = resultados[PRES_COLS].apply(pd.to_numeric, errors="coerce")
    notas = resultados[NOTA_COLS].apply(pd.to_numeric, errors="coerce")
    return (pres == 1).all(axis=1) & notas.notna().all(axis=1)


def _chunk_to_df(part_ok: pd.DataFrame, res_ok: pd.DataFrame) -> pd.DataFrame:
    notas = res_ok[NOTA_COLS].apply(pd.to_numeric, errors="coerce")
    df = pd.DataFrame(
        {
            "NU_INSCRICAO": part_ok["NU_INSCRICAO"].astype(str),
            "SG_UF_PROVA": part_ok["SG_UF_PROVA"].astype(str).str.strip(),
            "NO_MUNICIPIO_PROVA": part_ok["NO_MUNICIPIO_PROVA"].astype(str),
            "TP_COR_RACA": part_ok["TP_COR_RACA"].astype(str),
            "Q002": part_ok["Q002"].astype(str),
            "Q007": part_ok["Q007"].astype(str),
            "Q023": part_ok["Q023"].astype(str),
            "NU_NOTA_CN": notas["NU_NOTA_CN"],
            "NU_NOTA_CH": notas["NU_NOTA_CH"],
            "NU_NOTA_LC": notas["NU_NOTA_LC"],
            "NU_NOTA_MT": notas["NU_NOTA_MT"],
            "NU_NOTA_REDACAO": notas["NU_NOTA_REDACAO"],
        }
    )
    df["MEDIA_NOTAS"] = notas.mean(axis=1)
    return df[df["SG_UF_PROVA"].ne("")]


def build_candidate_pool(
    participantes_csv: Path,
    resultados_csv: Path,
    processed_dir: Path,
    cfg: PrepareConfig,
) -> Path:
    _safe_mkdir(processed_dir)

    part_usecols = [
        "NU_INSCRICAO",
        "SG_UF_PROVA",
        "NO_MUNICIPIO_PROVA",
        "TP_COR_RACA",
        "Q002",
        "Q007",
        "Q023",
    ]
    res_usecols = PRES_COLS + NOTA_COLS

    top_by_uf: Dict[str, pd.DataFrame] = {}
    stats = {
        "chunksize": cfg.chunksize,
        "pool_size_target": cfg.pool_size,
        "cap_per_uf": cfg.cap_per_uf,
        "eligible_rows_seen": 0,
        "rows_seen": 0,
    }

    part_iter = _iter_chunks(participantes_csv, part_usecols, cfg.chunksize)
    res_iter = _iter_chunks(resultados_csv, res_usecols, cfg.chunksize)

    for part_chunk, res_chunk in zip(part_iter, res_iter):
        stats["rows_seen"] += len(part_chunk)
        mask = _eligible_mask(res_chunk)
        if not bool(mask.any()):
            continue

        chunk_df = _chunk_to_df(part_chunk.loc[mask], res_chunk.loc[mask])
        stats["eligible_rows_seen"] += len(chunk_df)

        for uf, grp in chunk_df.groupby("SG_UF_PROVA", sort=False):
            top = grp.nlargest(cfg.cap_per_uf, "MEDIA_NOTAS")
            if uf not in top_by_uf:
                top_by_uf[uf] = top
            else:
                top_by_uf[uf] = (
                    pd.concat([top_by_uf[uf], top], ignore_index=True)
                    .nlargest(cfg.cap_per_uf, "MEDIA_NOTAS")
                )

    if not top_by_uf:
        raise RuntimeError("No eligible candidates found. Check CSV files and filters.")

    df = pd.concat(top_by_uf.values(), ignore_index=True)
    per_uf_counts = df.groupby("SG_UF_PROVA").size().to_dict()

    ufs = sorted(per_uf_counts.keys())
    base_quota = max(cfg.pool_size // max(len(ufs), 1), 1)
    quotas: Dict[str, int] = {uf: min(base_quota, per_uf_counts[uf]) for uf in ufs}

    remaining = cfg.pool_size - sum(quotas.values())
    if remaining > 0:
        order = sorted(ufs, key=lambda u: per_uf_counts[u] - quotas[u], reverse=True)
        idx = 0
        while remaining > 0 and order:
            uf = order[idx % len(order)]
            if quotas[uf] < per_uf_counts[uf]:
                quotas[uf] += 1
                remaining -= 1
            idx += 1

    df = df.sort_values(["SG_UF_PROVA", "MEDIA_NOTAS"], ascending=[True, False])
    df["__rank_uf"] = df.groupby("SG_UF_PROVA").cumcount() + 1
    df["__quota"] = df["SG_UF_PROVA"].map(quotas).astype(int)
    df_pool = df[df["__rank_uf"] <= df["__quota"]].drop(columns=["__rank_uf", "__quota"])

    if len(df_pool) > cfg.pool_size:
        df_pool = df_pool.sort_values("MEDIA_NOTAS", ascending=False).head(cfg.pool_size)
    elif len(df_pool) < cfg.pool_size:
        needed = cfg.pool_size - len(df_pool)
        used_idx = set(df_pool.index)
        df_rest = df[~df.index.isin(used_idx)].sort_values("MEDIA_NOTAS", ascending=False).head(needed)
        df_pool = pd.concat([df_pool, df_rest], ignore_index=True)

    df_pool = df_pool.reset_index(drop=True)
    df_pool.insert(0, "CAND_ID", np.arange(len(df_pool), dtype=np.int64))

    out_parquet = processed_dir / "candidates.parquet"
    df_pool.to_parquet(out_parquet, index=False)

    stats_out = {
        **stats,
        "pool_rows": int(len(df_pool)),
        "ufs_in_pool": int(df_pool["SG_UF_PROVA"].nunique()),
        "quota_by_uf": quotas,
        "available_by_uf_in_topk": {k: int(v) for k, v in per_uf_counts.items()},
        "columns": list(df_pool.columns),
    }
    with open(processed_dir / "pool_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats_out, f, ensure_ascii=False, indent=2)

    return out_parquet
