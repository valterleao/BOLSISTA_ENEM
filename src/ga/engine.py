# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from src.ga.chromosome import Chromosome, random_chromosome
from src.ga.fitness import CandidateArrays, FitnessWeights, evaluate, load_candidate_arrays
from src.ga.operators import crossover, mutate, tournament_select


@dataclass
class GAConfig:
    population_size: int = 20
    generations: int = 100
    group_size: int = 100
    crossover_rate: float = 0.8
    mutation_rate: float = 0.2
    elitism: int = 1
    random_seed: int = 42


@dataclass
class GAResult:
    best: Chromosome
    best_fitness: float
    best_components: Dict[str, float]
    history: List[Dict[str, object]] = field(default_factory=list)


ProgressCallback = Callable[[int, Dict[str, object]], None]


def run_ga(
    candidates_df: pd.DataFrame,
    ga_cfg: GAConfig,
    weights: FitnessWeights,
    progress_cb: Optional[ProgressCallback] = None,
) -> GAResult:
    rng = np.random.default_rng(ga_cfg.random_seed)
    pool_size = len(candidates_df)
    arr = load_candidate_arrays(candidates_df)

    population: List[Chromosome] = [
        random_chromosome(pool_size, ga_cfg.group_size, rng) for _ in range(ga_cfg.population_size)
    ]

    def fitness_list(pop: List[Chromosome]) -> List[float]:
        return [evaluate(c, arr, weights, pool_size)[0] for c in pop]

    fitnesses = fitness_list(population)
    history: List[Dict[str, object]] = []

    best_idx = int(np.argmax(fitnesses))
    best = population[best_idx].copy()
    best_fit, best_comp = evaluate(best, arr, weights, pool_size)

    for gen in range(ga_cfg.generations + 1):
        gen_stats = {
            "generation": gen,
            "best_fitness": float(max(fitnesses)),
            "avg_fitness": float(np.mean(fitnesses)),
            "best_notas": best_comp.get("notas", 0.0),
            "best_diversidade": best_comp.get("diversidade", 0.0),
            "best_cobertura": best_comp.get("cobertura", 0.0),
            "best_genes": best.genes.tolist(),
        }
        history.append(gen_stats)
        if progress_cb:
            progress_cb(gen, gen_stats)

        if gen == ga_cfg.generations:
            break

        new_pop: List[Chromosome] = []
        elite_idxs = list(np.argsort(fitnesses)[-ga_cfg.elitism :])
        for i in elite_idxs:
            new_pop.append(population[i].copy())

        while len(new_pop) < ga_cfg.population_size:
            p1 = tournament_select(population, fitnesses, rng)
            p2 = tournament_select(population, fitnesses, rng)
            if rng.random() < ga_cfg.crossover_rate:
                c1, c2 = crossover(p1, p2, rng, pool_size)
            else:
                c1, c2 = p1, p2
            if rng.random() < ga_cfg.mutation_rate:
                c1 = mutate(c1, rng, pool_size)
            if rng.random() < ga_cfg.mutation_rate:
                c2 = mutate(c2, rng, pool_size)
            new_pop.append(c1)
            if len(new_pop) < ga_cfg.population_size:
                new_pop.append(c2)

        population = new_pop[: ga_cfg.population_size]
        fitnesses = fitness_list(population)

        cur_idx = int(np.argmax(fitnesses))
        cur_fit, cur_comp = evaluate(population[cur_idx], arr, weights, pool_size)
        if cur_fit > best_fit:
            best = population[cur_idx].copy()
            best_fit = cur_fit
            best_comp = cur_comp

    return GAResult(best=best, best_fitness=best_fit, best_components=best_comp, history=history)


def save_ga_outputs(
    candidates_df: pd.DataFrame,
    result: GAResult,
    processed_dir: Path,
) -> Dict[str, Path]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    best_df = candidates_df.iloc[result.best.genes].copy()
    best_csv = processed_dir / "best_group.csv"
    best_df.to_csv(best_csv, index=False, encoding="utf-8")

    history_path = processed_dir / "ga_history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(result.history, f, ensure_ascii=False, indent=2)

    summary = {
        "best_fitness": result.best_fitness,
        "components": result.best_components,
        "group_size": int(result.best.size),
    }
    summary_path = processed_dir / "ga_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return {"best_group": best_csv, "history": history_path, "summary": summary_path}
