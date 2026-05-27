# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
import json
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import default_paths
from src.ga.engine import GAConfig, run_ga, save_ga_outputs
from src.ga.fitness import FitnessWeights
from src.reporting.charts import export_charts

paths = default_paths()
app = FastAPI(title="ENEM Bolsa GA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_state_lock = threading.Lock()
_run_state: Dict[str, Any] = {
    "running": False,
    "history": [],
    "last_result": None,
    "error": None,
}


class RunRequest(BaseModel):
    population: int = 20
    generations: int = 100
    group_size: int = 100
    w_notas: float = Field(0.5, ge=0.0, le=1.0)
    w_div: float = Field(0.3, ge=0.0, le=1.0)
    w_geo: float = Field(0.2, ge=0.0, le=1.0)
    seed: int = 42


def _load_candidates() -> pd.DataFrame:
    parquet = paths.processed_dir / "candidates.parquet"
    if not parquet.exists():
        raise HTTPException(
            status_code=400,
            detail="candidates.parquet ausente. Execute scripts/01_prepare_data.py.",
        )
    return pd.read_parquet(parquet)


def _normalize_weights(req: RunRequest) -> FitnessWeights:
    total = req.w_notas + req.w_div + req.w_geo
    if total <= 0:
        raise HTTPException(status_code=400, detail="Soma dos pesos deve ser > 0.")
    return FitnessWeights(
        w_notas=req.w_notas / total,
        w_diversidade=req.w_div / total,
        w_geo=req.w_geo / total,
    )


def _run_ga_thread(req: RunRequest) -> None:
    global _run_state
    try:
        df = _load_candidates()
        ga_cfg = GAConfig(
            population_size=req.population,
            generations=req.generations,
            group_size=req.group_size,
            random_seed=req.seed,
        )
        weights = _normalize_weights(req)

        history: List[Dict[str, Any]] = []

        def progress_cb(gen: int, stats: dict) -> None:
            history.append(stats)
            with _state_lock:
                _run_state["history"] = history.copy()

        result = run_ga(df, ga_cfg, weights, progress_cb=progress_cb)
        outputs = save_ga_outputs(df, result, paths.processed_dir)
        best_df = df.iloc[result.best.genes].copy()
        export_charts(best_df, paths.processed_dir / "charts")

        with _state_lock:
            _run_state["last_result"] = {
                "fitness": result.best_fitness,
                "components": result.best_components,
                "outputs": {k: str(v) for k, v in outputs.items()},
            }
            _run_state["error"] = None
    except Exception as exc:  # noqa: BLE001
        with _state_lock:
            _run_state["error"] = str(exc)
    finally:
        with _state_lock:
            _run_state["running"] = False


@app.get("/api/health")
def health() -> dict:
    parquet = paths.processed_dir / "candidates.parquet"
    return {
        "ok": True,
        "candidates_ready": parquet.exists(),
        "running": _run_state["running"],
    }


@app.post("/api/ga/run")
def start_ga(req: RunRequest) -> dict:
    with _state_lock:
        if _run_state["running"]:
            raise HTTPException(status_code=409, detail="GA ja em execucao.")
        _run_state["running"] = True
        _run_state["history"] = []
        _run_state["error"] = None
        _run_state["last_result"] = None

    thread = threading.Thread(target=_run_ga_thread, args=(req,), daemon=True)
    thread.start()
    return {"status": "started"}


@app.get("/api/ga/status")
def ga_status() -> dict:
    with _state_lock:
        return {
            "running": _run_state["running"],
            "history": _run_state["history"],
            "last_result": _run_state["last_result"],
            "error": _run_state["error"],
        }


@app.get("/api/ga/stream")
async def ga_stream() -> StreamingResponse:
    async def event_generator():
        last_len = 0
        while True:
            with _state_lock:
                history = _run_state["history"]
                running = _run_state["running"]
                error = _run_state["error"]
                last_result = _run_state["last_result"]

            if len(history) > last_len:
                for item in history[last_len:]:
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
                last_len = len(history)

            if error:
                yield f"data: {json.dumps({'error': error})}\n\n"
                break

            if not running and last_result is not None:
                yield f"data: {json.dumps({'done': True, 'result': last_result})}\n\n"
                break

            if not running and last_len == 0 and error is None:
                yield f"data: {json.dumps({'waiting': True})}\n\n"

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/results/best-group")
def best_group() -> dict:
    csv_path = paths.processed_dir / "best_group.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="best_group.csv nao encontrado. Execute o GA.")
    df = pd.read_csv(csv_path)
    return {"rows": df.to_dict(orient="records"), "count": len(df)}


@app.get("/api/results/metrics")
def metrics() -> dict:
    summary_path = paths.processed_dir / "ga_summary.json"
    if not summary_path.exists():
        raise HTTPException(status_code=404, detail="ga_summary.json nao encontrado.")
    with open(summary_path, encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/results/charts")
def charts_data() -> dict:
    csv_path = paths.processed_dir / "best_group.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="best_group.csv nao encontrado.")
    df = pd.read_csv(csv_path)

    nota_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    notas = {c: df[c].astype(float).tolist() for c in nota_cols}

    diversidade = {
        "cor_raca": df["TP_COR_RACA"].value_counts().to_dict(),
        "renda": df["Q007"].value_counts().to_dict(),
        "escolaridade_mae": df["Q002"].value_counts().to_dict(),
        "tipo_escola": df["Q023"].value_counts().to_dict(),
    }
    geo = df["SG_UF_PROVA"].value_counts().to_dict()

    return {
        "notas": notas,
        "diversidade": diversidade,
        "geo": geo,
        "media_grupo": float(df["MEDIA_NOTAS"].mean()),
        "ufs_cobertas": int(df["SG_UF_PROVA"].nunique()),
    }
