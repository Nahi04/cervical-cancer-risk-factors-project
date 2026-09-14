"""Évaluer les prédictions et leur incertitude, sans réentraîner sur le test."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, average_precision_score,
    balanced_accuracy_score, brier_score_loss, confusion_matrix, f1_score,
    fbeta_score, matthews_corrcoef, precision_score, recall_score, roc_auc_score,
    roc_curve, precision_recall_curve, ConfusionMatrixDisplay)
from .common import SEED, save_table, save_figure


def metrics(y, probability, threshold=0.5):
    prediction = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return {"AP": average_precision_score(y, probability),
            "ROC_AUC": roc_auc_score(y, probability),
            "Brier": brier_score_loss(y, probability),
            "accuracy": accuracy_score(y, prediction),
            "balanced_accuracy": balanced_accuracy_score(y, prediction),
            "recall": recall_score(y, prediction, zero_division=0),
            "specificity": tn / (tn + fp),
            "precision": precision_score(y, prediction, zero_division=0),
            "F1": f1_score(y, prediction, zero_division=0),
            "F2": fbeta_score(y, prediction, beta=2, zero_division=0),
            "MCC": matthews_corrcoef(y, prediction),
            "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)}


def choose_threshold(y, probability):
    """Maximiser F2 sur les prédictions OOF du développement uniquement."""
    precision, recall, thresholds = precision_recall_curve(y, probability)
    f2 = 5 * precision[:-1] * recall[:-1] / (4 * precision[:-1] + recall[:-1] + 1e-15)
    best = np.flatnonzero(np.isclose(f2, f2.max()))[-1]
    curve = pd.DataFrame({"threshold": thresholds, "precision": precision[:-1],
                          "recall": recall[:-1], "F2": f2})
    return float(thresholds[best]), curve


def uncertainty(y, probabilities, thresholds, groups, winner):
    """Bootstrap par groupes : préserver les profils répétés dans chaque tirage."""
    rng = np.random.default_rng(SEED + 5)
    group_rows = [np.flatnonzero(groups == g) for g in np.unique(groups)]
    rows, differences = [], []
    for repetition in range(1000):
        chosen = rng.integers(0, len(group_rows), size=len(group_rows))
        idx = np.concatenate([group_rows[i] for i in chosen])
        if len(np.unique(y[idx])) < 2:
            continue  # ROC-AUC n'est pas définie avec une seule classe.
        scores = metrics(y[idx], probabilities[winner][idx], thresholds[winner])
        rows.append({key: scores[key] for key in
                     ["AP", "ROC_AUC", "recall", "specificity", "precision", "F2", "Brier"]})
        differences.append({name: scores["AP"] - average_precision_score(y[idx], p[idx])
                            for name, p in probabilities.items() if name != winner})
    boot = pd.DataFrame(rows)
    interval = pd.DataFrame({"low_95": boot.quantile(0.025), "high_95": boot.quantile(0.975)})
    point = metrics(y, probabilities[winner], thresholds[winner])
    interval.insert(0, "estimate", pd.Series(point))
    interval["bootstrap_valid_n"] = len(boot)
    save_table(interval, "02_test_uncertainty", index=True)
    delta = pd.DataFrame(differences)
    paired = pd.DataFrame({"difference_AP": {name: point["AP"] - average_precision_score(y, probabilities[name])
                                             for name in delta},
                           "low_95": delta.quantile(0.025), "high_95": delta.quantile(0.975)})
    save_table(paired, "02_test_paired_AP", index=True)


def plots(y, probabilities, thresholds, comparison):
    colors = {"Base": "#89959f", "Logistique": "#168a92", "Foret": "#cf7354"}
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    curves = []
    for name, p in probabilities.items():
        fpr, tpr, _ = roc_curve(y, p)
        precision, recall, _ = precision_recall_curve(y, p)
        axes[0].plot(fpr, tpr, color=colors[name], label=f"{name} : {roc_auc_score(y, p):.3f}")
        axes[1].step(recall, precision, where="post", color=colors[name],
                     label=f"{name} : AP = {average_precision_score(y, p):.3f}")
        curves.extend({"model": name, "curve": "ROC", "x": a, "y": b} for a, b in zip(fpr, tpr))
        curves.extend({"model": name, "curve": "PR", "x": a, "y": b} for a, b in zip(recall, precision))
    save_table(pd.DataFrame(curves), "02_test_courbes")
    axes[0].plot([0, 1], [0, 1], "--", color="grey")
    axes[1].axhline(y.mean(), linestyle="--", color="grey", label=f"Prévalence : {y.mean():.3f}")
    axes[0].set(title="Test réservé : ROC", xlabel="Taux de faux positifs", ylabel="Rappel")
    axes[1].set(title="Test réservé : précision-rappel", xlabel="Rappel", ylabel="Précision")
    for ax in axes:
        ax.set(xlim=(0, 1), ylim=(0, 1.03))
        ax.legend(fontsize=8)
    save_figure("02_courbes_test")

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    for ax, (name, p) in zip(axes, probabilities.items()):
        ConfusionMatrixDisplay.from_predictions(y, p >= thresholds[name], labels=[0, 1],
            display_labels=["Négative", "Positive"], ax=ax, colorbar=False, cmap="Blues")
        ax.set(title=f"{name} | seuil {thresholds[name]:.3f}", xlabel="Prédiction", ylabel="Observation")
    save_figure("02_confusions_test")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    calibration_rows = []
    for name, p in probabilities.items():
        d = pd.DataFrame({"p": p, "y": y})
        # Quantiles : environ 43 patientes par point ; regrouper les scores égaux.
        d["bin"] = pd.qcut(d.p, q=5, duplicates="drop") if np.unique(p).size > 1 else 0
        bins = d.groupby("bin", observed=True).agg(mean_score=("p", "mean"),
                positive_fraction=("y", "mean"), n=("y", "size"), positives=("y", "sum"))
        bins["model"] = name
        calibration_rows.append(bins.reset_index(drop=True))
        axes[0].plot(bins.mean_score, bins.positive_fraction, "o-", label=name, color=colors[name])
        axes[1].hist(p, bins=np.linspace(0, 1, 21), alpha=0.35, label=name, color=colors[name])
    save_table(pd.concat(calibration_rows), "02_calibration_bins")
    axes[0].plot([0, 1], [0, 1], "--", color="grey")
    axes[0].set(title="Calibration : lecture exploratoire", xlabel="Score moyen", ylabel="Fraction positive", xlim=(0, 1), ylim=(0, 1))
    axes[1].set(title="Distribution des scores sur le test", xlabel="Score prédit", ylabel="Effectif")
    for ax in axes:
        ax.legend(fontsize=8)
    save_figure("02_calibration_test")
    plt.figure(figsize=(8, 4))
    plt.bar(comparison.model, comparison.AP_mean, yerr=comparison.AP_std,
            color=[colors[n] for n in comparison.model], capsize=6)
    plt.ylabel("Average precision : moyenne ± écart-type des 5 plis")
    plt.title("Développement : scores de sélection, potentiellement optimistes")
    save_figure("02_comparaison_cv")
