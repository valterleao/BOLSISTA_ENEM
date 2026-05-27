# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from src.ga.chromosome import Chromosome, repair_chromosome


def tournament_select(
    population: List[Chromosome],
    fitnesses: List[float],
    rng: np.random.Generator,
    k: int = 3,
) -> Chromosome:
    idxs = rng.choice(len(population), size=min(k, len(population)), replace=False)
    best_i = max(idxs, key=lambda i: fitnesses[i])
    return population[best_i].copy()


def crossover(
    p1: Chromosome,
    p2: Chromosome,
    rng: np.random.Generator,
    pool_size: int,
) -> Tuple[Chromosome, Chromosome]:
    n = p1.size
    cut = int(rng.integers(1, n))
    g1 = np.concatenate([p1.genes[:cut], p2.genes[cut:]])
    g2 = np.concatenate([p2.genes[:cut], p1.genes[cut:]])
    g1 = repair_chromosome(g1, pool_size, rng)
    g2 = repair_chromosome(g2, pool_size, rng)
    return Chromosome(g1), Chromosome(g2)


def mutate(chrom: Chromosome, rng: np.random.Generator, pool_size: int, n_swaps: int = 2) -> Chromosome:
    genes = chrom.genes.copy()
    used = set(genes.tolist())
    for _ in range(n_swaps):
        i = int(rng.integers(0, genes.size))
        available = np.setdiff1d(
            np.arange(pool_size, dtype=np.int64),
            np.fromiter(used - {int(genes[i])}, dtype=np.int64),
        )
        if available.size == 0:
            continue
        old = int(genes[i])
        genes[i] = int(rng.choice(available))
        used.discard(old)
        used.add(int(genes[i]))
    return Chromosome(genes)
