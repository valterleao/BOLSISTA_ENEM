# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def export_charts(best_df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="darkgrid")

    nota_cols = ["NU_NOTA_CN", "NU_NOTA_CH", "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
    melted = best_df[nota_cols].melt(var_name="area", value_name="nota")
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=melted, x="area", y="nota")
    plt.title("Distribuicao de notas - grupo ideal")
    plt.tight_layout()
    plt.savefig(out_dir / "notas_boxplot.png", dpi=120)
    plt.close()

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, col, title in zip(
        axes.flatten(),
        ["TP_COR_RACA", "Q007", "Q002", "Q023"],
        ["Cor/Raca", "Renda (Q007)", "Escolaridade mae (Q002)", "Tipo escola (Q023)"],
    ):
        vc = best_df[col].value_counts().sort_index()
        vc.plot(kind="bar", ax=ax, color="#7c3aed")
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    plt.savefig(out_dir / "diversidade_barras.png", dpi=120)
    plt.close()

    uf_counts = best_df["SG_UF_PROVA"].value_counts().sort_values(ascending=False)
    plt.figure(figsize=(12, 5))
    uf_counts.plot(kind="bar", color="#38bdf8")
    plt.title("Distribuicao geografica por UF")
    plt.xlabel("UF")
    plt.ylabel("Quantidade")
    plt.tight_layout()
    plt.savefig(out_dir / "geo_uf.png", dpi=120)
    plt.close()
