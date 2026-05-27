# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

import numpy as np


@dataclass
class Chromosome:
    genes: np.ndarray  # int indices into candidate pool

    def copy(self) -> "Chromosome":
        return Chromosome(genes=self.genes.copy())

    @property
    def size(self) -> int:
        return int(self.genes.size)

    def is_valid(self, pool_size: int) -> bool:
        if self.genes.size == 0:
            return False
        if np.any(self.genes < 0) or np.any(self.genes >= pool_size):
            return False
        return len(set(self.genes.tolist())) == self.genes.size


def random_chromosome(pool_size: int, group_size: int, rng: np.random.Generator) -> Chromosome:
    genes = rng.choice(pool_size, size=group_size, replace=False)
    return Chromosome(genes=genes.astype(np.int64))


def repair_chromosome(genes: np.ndarray, pool_size: int, rng: np.random.Generator) -> np.ndarray:
    genes = genes.astype(np.int64, copy=True)
    used: Set[int] = set()
    for i in range(genes.size):
        g = int(genes[i])
        if g < 0 or g >= pool_size or g in used:
            candidates = np.setdiff1d(np.arange(pool_size, dtype=np.int64), np.fromiter(used, dtype=np.int64))
            if candidates.size == 0:
                genes[i] = int(rng.integers(0, pool_size))
            else:
                genes[i] = int(rng.choice(candidates))
        used.add(int(genes[i]))
    return genes
