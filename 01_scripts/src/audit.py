"""Décrire les valeurs réellement présentes, sans inventer de correction."""
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .common import ROOT, FEATURES, NUM, BIN, TARGETS, save_table, save_figure


def run(raw, clean):
    summary = raw.describe().T
    summary["missing_n"] = raw.isna().sum()
    summary["missing_pct"] = 100 * raw.isna().mean()
    summary["unique_n"] = raw.nunique()
    save_table(summary, "01_description_variables", index=True)
    targets = pd.DataFrame({"positives": raw[TARGETS].sum(),
                            "negatives": (raw[TARGETS] == 0).sum()})
    targets["positive_pct"] = 100 * targets.positives / len(raw)
    save_table(targets, "01_cibles", index=True)
    # source_row est le numéro de ligne CSV, en comptant l'en-tête comme ligne 1.
    anomalies = raw.loc[raw["First sexual intercourse"] > raw.Age,
                       ["Age", "First sexual intercourse"]].copy()
    anomalies.insert(0, "source_row", anomalies.index + 2)
    anomalies["action"] = "Premier rapport rendu manquant ; âge conservé par convention"
    save_table(anomalies, "01_anomalies")
    duplicates = raw.loc[raw.duplicated(keep=False)].copy()
    duplicates.insert(0, "source_row", duplicates.index + 2)
    save_table(duplicates, "01_lignes_identiques")

    checks = [{"controle": "valeurs négatives", "n": int(raw.lt(0).sum().sum())},
              {"controle": "valeurs binaires hors 0/1", "n": int(sum(
                  (~raw[c].dropna().isin([0, 1])).sum() for c in BIN + TARGETS))}]
    for status, duration in [("Smokes", "Smokes (years)"),
                             ("Hormonal Contraceptives", "Hormonal Contraceptives (years)"),
                             ("IUD", "IUD (years)")]:
        checks.append({"controle": f"{status}=0 et durée>0",
                       "n": int(((raw[status] == 0) & (raw[duration] > 0)).sum())})
        checks.append({"controle": f"{duration} > âge",
                       "n": int((raw[duration] > raw.Age).sum())})
    save_table(pd.DataFrame(checks), "01_controles_logiques")
    facts = {"rows": len(raw), "columns": len(raw.columns),
             "positives": int(raw.Biopsy.sum()), "exact_duplicates": int(raw.duplicated().sum()),
             "missing_cells": int(raw.isna().sum().sum()),
             "complete_all36": len(raw.dropna()),
             "complete_core26": len(clean[FEATURES].dropna()),
             "age_conflicts": len(anomalies),
             "sha256": hashlib.sha256((ROOT / "02_data/raw/cervical_cancer.csv").read_bytes()).hexdigest()}
    (ROOT / "04_results/tables/01_audit.json").write_text(json.dumps(facts, indent=2))

    missing = summary.missing_pct.sort_values()
    plt.figure(figsize=(10, 10))
    plt.barh(missing.index, missing, color="#168a92")
    plt.axvline(80, color="#cf7354", linestyle="--", label="Repère descriptif : 80 %")
    plt.xlabel("Valeurs manquantes (%)")
    plt.title("Audit des 858 lignes : des absences très inégales")
    plt.legend()
    save_figure("01_valeurs_manquantes")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(["Négative", "Positive"], raw.Biopsy.value_counts().reindex([0, 1]),
                color=["#168a92", "#cf7354"])
    for i, n in enumerate(raw.Biopsy.value_counts().reindex([0, 1])):
        axes[0].text(i, n + 10, str(n), ha="center")
    axes[0].set(title="Biopsy : 55 positives / 858", ylabel="Nombre de lignes", ylim=(0, 880))
    axes[1].hist(raw.Age, bins=np.arange(10, 90, 5), color="#168a92", edgecolor="white")
    axes[1].set(title="Âge : conserver les valeurs extrêmes plausibles", xlabel="Âge (ans)", ylabel="Effectif")
    save_figure("01_population")


def describe_development(clean, dev):
    """Examens détaillés limités au développement ; le test reste réservé."""
    d = clean.iloc[dev]
    save_table(d[FEATURES].describe().T, "01_developpement_description", index=True)
    save_table(d[FEATURES].isna().mean().rename("missing_fraction").to_frame(),
               "01_developpement_missing", index=True)
    q1, q3 = d[NUM].quantile(0.25), d[NUM].quantile(0.75)
    outliers = ((d[NUM] < q1 - 1.5 * (q3 - q1)) | (d[NUM] > q3 + 1.5 * (q3 - q1))).sum()
    save_table(outliers.rename("outside_1_5_IQR").to_frame(), "01_valeurs_extremes", index=True)
    masks = d[["Smokes", "Hormonal Contraceptives", "IUD", "STDs"]].isna()
    save_table(masks.value_counts().rename("n").reset_index(), "01_profils_absence")
    corr = d[NUM].corr(method="spearman")
    save_table(corr, "01_correlations_spearman", index=True)
    plt.figure(figsize=(10, 8))
    plt.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    plt.xticks(range(len(NUM)), NUM, rotation=70, ha="right")
    plt.yticks(range(len(NUM)), NUM)
    plt.colorbar(label="Corrélation de Spearman (paires observées)")
    plt.title("Développement : redondance entre mesures numériques")
    save_figure("01_correlations")
    fig, axes = plt.subplots(2, 4, figsize=(13, 6))
    for ax, c in zip(axes.flat, NUM[2:]):
        ax.hist(np.log1p(d[c].dropna()), bins=18, color="#168a92", edgecolor="white")
        ax.set(title=c, xlabel="log(1 + valeur)", ylabel="Effectif")
        ax.title.set_fontsize(9)
    save_figure("01_distributions_log")
