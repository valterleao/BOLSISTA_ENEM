from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paths:
    project_root: Path
    microdados_dir: Path
    dados_dir: Path
    processed_dir: Path

    @property
    def participantes_csv(self) -> Path:
        return self.dados_dir / "PARTICIPANTES_2024.csv"

    @property
    def resultados_csv(self) -> Path:
        return self.dados_dir / "RESULTADOS_2024.csv"


def default_paths(project_root: Path | None = None) -> Paths:
    root = project_root or Path(__file__).resolve().parents[1]
    microdados_dir = root / "microdados_enem_2024"
    dados_dir = microdados_dir / "DADOS"
    processed_dir = root / "data" / "processed"
    return Paths(
        project_root=root,
        microdados_dir=microdados_dir,
        dados_dir=dados_dir,
        processed_dir=processed_dir,
    )

