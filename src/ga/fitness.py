# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from src.ga.chromosome import Chromosome


@dataclass(frozen=True)
class FitnessWeights:
    w_notas: float = 0.5
    w_diversidade: float = 0.3
    w_geo: float = 0.2
    max_uf_share: float = 0.4
    penalty_concentration: float = 0.05


@dataclass
class CandidateArrays:
    media: np.ndarray
    cor_raca: np.ndarray
    q002: np.ndarray
    q007: np.ndarray
    q023: np.ndarray
    uf: np.ndarray
    media_min: float
    media_max: float
    n_ufs_total: int


def load_candidate_arrays(df) -> CandidateArrays:
    media = df["MEDIA_NOTAS"].to_numpy(dtype=np.float64)
    return CandidateArrays(
        media=media,
        cor_raca=df["TP_COR_RACA"].astype(str).to_numpy(),
        q002=df["Q002"].astype(str).to_numpy(),
        q007=df["Q007"].astype(str).to_numpy(),
        q023=df["Q023"].astype(str).to_numpy(),
        uf=df["SG_UF_PROVA"].astype(str).to_numpy(),
        media_min=float(media.min()),
        media_max=float(media.max()),
        n_ufs_total=int(df["SG_UF_PROVA"].nunique()),
    )


def _norm_entropy(labels: np.ndarray) -> float:
    if labels.size == 0:
        return 0.0
    _, counts = np.unique(labels, return_counts=True)
    p = counts / counts.sum()
    ent = -np.sum(p * np.log(p + 1e-12))
    max_ent = np.log(len(counts) + 1e-12)
    if max_ent <= 0:
        return 0.0
    return float(ent / max_ent)


def score_notas(genes: np.ndarray, arr: CandidateArrays) -> float:
    medias = arr.media[genes]
    denom = arr.media_max - arr.media_min
    if denom <= 1e-9:
        return 1.0
    return float((medias.mean() - arr.media_min) / denom)


def score_diversidade(genes: np.ndarray, arr: CandidateArrays) -> float:
    parts = [
        _norm_entropy(arr.cor_raca[genes]),
        _norm_entropy(arr.q002[genes]),
        _norm_entropy(arr.q007[genes]),
        _norm_entropy(arr.q023[genes]),
    ]
    return float(np.mean(parts))


def score_cobertura(genes: np.ndarray, arr: CandidateArrays, n_ufs_brasil: int = 27) -> float:
    ufs = arr.uf[genes]
    n_unique = len(np.unique(ufs))
    return float(min(n_unique / n_ufs_brasil, 1.0))


def evaluate(
    chrom: Chromosome,
    arr: CandidateArrays,
    weights: FitnessWeights,
    pool_size: int,
    n_ufs_brasil: int = 27,
) -> Tuple[float, Dict[str, float]]:
    if not chrom.is_valid(pool_size):
        return -1.0, {"notas": 0.0, "diversidade": 0.0, "cobertura": 0.0, "penalty": 1.0}

    genes = chrom.genes
    s_notas = score_notas(genes, arr)
    s_div = score_diversidade(genes, arr)
    s_geo = score_cobertura(genes, arr, n_ufs_brasil=n_ufs_brasil)

    ufs, counts = np.unique(arr.uf[genes], return_counts=True)
    max_share = float(counts.max() / genes.size) if genes.size else 0.0
    penalty = 0.0
    if max_share > weights.max_uf_share:
        penalty = weights.penalty_concentration * (max_share - weights.max_uf_share)

    total = (
        weights.w_notas * s_notas
        + weights.w_diversidade * s_div
        + weights.w_geo * s_geo
        - penalty
    )
    return float(total), {
        "notas": s_notas,
        "diversidade": s_div,
        "cobertura": s_geo,
        "penalty": penalty,
        "ufs": float(len(ufs)),
    }
