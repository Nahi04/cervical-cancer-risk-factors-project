"""Deux classifieurs, une base naïve et un test réservé : aucune recherche massive."""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (StratifiedGroupKFold, GridSearchCV,
                                    cross_val_predict, cross_validate)
from sklearn.pipeline import Pipeline
from .common import (ROOT, SEED, NUM, BIN, FEATURES, get_x, preprocessor,
                     save_table, save_figure)
from . import audit, evaluation


def run(clean):
    x, y = get_x(clean), clean.Biopsy.astype(int)
    # Profils identiques = même groupe ; ce n'est PAS un identifiant de patiente.
    groups = pd.util.hash_pandas_object(x, index=False).to_numpy()
    outer = StratifiedGroupKFold(n_splits=4, shuffle=True, random_state=SEED)
    dev, test = next(outer.split(x, y, groups))  # Premier pli fixé, jamais le meilleur.
    xd, xt, yd, yt = x.iloc[dev], x.iloc[test], y.iloc[dev], y.iloc[test]
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED + 1)
    folds = list(cv.split(xd, yd, groups[dev]))
    assert not set(groups[dev]) & set(groups[test])
    split = pd.DataFrame({"source_row": clean.index + 2, "group": groups.astype(str),
                          "subset": "development", "validation_fold": -1, "Biopsy": y})
    split.loc[test, "subset"] = "test"
    for fold, (train, valid) in enumerate(folds, start=1):
        assert not set(groups[dev][train]) & set(groups[dev][valid])
        assert yd.iloc[valid].nunique() == 2
        split.loc[dev[valid], "validation_fold"] = fold
    split.to_csv(ROOT / "02_data/processed/split.csv", index=False)
    save_table(split.groupby("subset").agg(n=("Biopsy", "size"), positives=("Biopsy", "sum")),
               "02_effectifs", index=True)
    audit.describe_development(clean, dev)
    scoring = {"AP": "average_precision", "ROC_AUC": "roc_auc", "balanced_accuracy": "balanced_accuracy"}
    base = DummyClassifier(strategy="prior").fit(xd, yd)
    baseline_cv = cross_validate(base, xd, yd, cv=folds, scoring=scoring, return_train_score=True)
    summary = [{"model": "Base", "AP_mean": baseline_cv["test_AP"].mean(),
                "AP_std": baseline_cv["test_AP"].std(), "train_AP_mean": baseline_cv["train_AP"].mean(),
                "ROC_AUC_mean": baseline_cv["test_ROC_AUC"].mean()}]
    # L2 est la pénalisation par défaut de LogisticRegression.
    definitions = {
        "Logistique": (LogisticRegression(max_iter=2000), {"model__C": [0.1, 1.0]}),
        "Foret": (RandomForestClassifier(n_estimators=200, max_depth=5,
                   random_state=SEED, n_jobs=1), {"model__min_samples_leaf": [5, 15]})}
    fitted, thresholds, settings = {"Base": base}, {"Base": 0.5}, {}
    oof_table = pd.DataFrame({"source_row": dev + 2, "Biopsy": yd.to_numpy()})
    cv_details = [{"model": "Base", "fold": i + 1, "AP": score}
                  for i, score in enumerate(baseline_cv["test_AP"])]
    for name, (model, grid) in definitions.items():
        print(f"  Ajustement de {name} : 8 configurations, 5 plis", flush=True)
        pipe = Pipeline([("pre", preprocessor(scale=name == "Logistique")),
                         ("constant", VarianceThreshold()), ("model", model)])
        grid.update({"pre__num__impute__strategy": ["median", "mean"],
                     "model__class_weight": [None, "balanced"]})
        search = GridSearchCV(pipe, grid, scoring=scoring, refit="AP", cv=folds,
                              return_train_score=True, n_jobs=1, error_score="raise")
        search.fit(xd, yd)  # Le pipeline apprend imputation et échelle dans chaque pli.
        results = pd.DataFrame(search.cv_results_)
        save_table(results, f"02_grille_{name}")
        best = results.iloc[search.best_index_]
        summary.append({"model": name, "AP_mean": best.mean_test_AP,
                        "AP_std": best.std_test_AP, "train_AP_mean": best.mean_train_AP,
                        "ROC_AUC_mean": best.mean_test_ROC_AUC})
        cv_details.extend({"model": name, "fold": i + 1, "AP": best[f"split{i}_test_AP"]}
                          for i in range(5))
        fitted[name] = search.best_estimator_
        settings[name] = search.best_params_
        # OOF : chaque score vient d'un modèle n'ayant pas appris cette ligne.
        oof = cross_val_predict(clone(fitted[name]), xd, yd, cv=folds,
                                method="predict_proba")[:, 1]
        oof_table[name] = oof
        thresholds[name], curve = evaluation.choose_threshold(yd, oof)
        save_table(curve, f"02_seuils_OOF_{name}")
    comparison = pd.DataFrame(summary)
    # Sélection par AP CV, avant le moindre calcul de score sur le test.
    winner = comparison.loc[comparison.model != "Base"].sort_values(
        "AP_mean", ascending=False, kind="stable").iloc[0].model
    save_table(comparison, "02_comparaison_cv")
    save_table(pd.DataFrame(cv_details), "02_cv_par_pli")
    save_table(oof_table, "02_predictions_OOF")
    selection = {"winner": winner, "thresholds": thresholds, "parameters": settings,
                 "selection": "Average precision moyenne des 5 plis de développement"}
    (ROOT / "04_results/tables/02_selection.json").write_text(json.dumps(selection, indent=2))

    # Analyse de sensibilité : supprimer les indicateurs d'absence, sans nouveau réglage.
    ablated = clone(fitted[winner]).set_params(pre=preprocessor(
        strategy=settings[winner]["pre__num__impute__strategy"],
        scale=winner == "Logistique", indicators=False))
    ablation = cross_validate(ablated, xd, yd, cv=folds, scoring=scoring)
    save_table(pd.DataFrame({"fold": range(1, 6), "AP_without_indicators": ablation["test_AP"]}),
               "02_sensibilite_indicateurs")

    # Le test est ouvert après avoir figé famille, hyperparamètres et seuils.
    probabilities = {name: model.predict_proba(xt)[:, 1] for name, model in fitted.items()}
    rows = []
    predictions = pd.DataFrame({"source_row": test + 2, "Biopsy": yt.to_numpy()})
    for name, p in probabilities.items():
        predictions[f"score_{name}"] = p
        predictions[f"prediction_{name}"] = (p >= thresholds[name]).astype(int)
        choices = {"0.5": 0.5} if name == "Base" else {"0.5": 0.5, "F2_OOF": thresholds[name]}
        for rule, threshold in choices.items():
            rows.append({"model": name, "rule": rule, "threshold": threshold,
                         **evaluation.metrics(yt, p, threshold)})
    save_table(pd.DataFrame(rows), "02_metriques_test")
    save_table(predictions, "02_predictions_test")
    evaluation.uncertainty(yt.to_numpy(), probabilities, thresholds, groups[test], winner)
    evaluation.plots(yt.to_numpy(), probabilities, thresholds, comparison)
    interpretation(fitted, xt, yt, winner)
    print(f"  Modèle choisi en CV : {winner}. Test : {len(test)} lignes, {yt.sum()} positives.", flush=True)
    return dev, test


def interpretation(fitted, xt, yt, winner):
    """Descriptions après évaluation ; aucune sélection de variables sur le test."""
    logit = fitted["Logistique"]
    names = logit.named_steps["pre"].get_feature_names_out()
    keep = logit.named_steps["constant"].get_support()
    coefficients = pd.DataFrame({"feature": names[keep], "coefficient": logit.named_steps["model"].coef_[0]})
    save_table(coefficients, "02_coefficients_logistique")
    constants = pd.DataFrame({"feature": names, "retained": keep})
    save_table(constants, "02_variables_apres_pipeline")
    for name, model in fitted.items():
        if name == "Base":
            continue
        pre = model.named_steps["pre"]
        stats = list(pre.named_transformers_["num"].named_steps["impute"].statistics_)
        stats += list(pre.named_transformers_["bin"].statistics_)
        save_table(pd.DataFrame({"feature": NUM + BIN, "imputed_value_model_space": stats}),
                   f"02_imputation_{name}")
    result = permutation_importance(fitted[winner], xt, yt, scoring="average_precision",
                                    n_repeats=15, random_state=SEED, n_jobs=1)
    importance = pd.DataFrame({"feature": FEATURES, "AP_drop_mean": result.importances_mean,
                               "AP_drop_std": result.importances_std}).sort_values("AP_drop_mean")
    save_table(importance, "02_importance_permutation")
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    top = coefficients.loc[coefficients.coefficient.abs().nlargest(10).index].sort_values("coefficient")
    axes[0].barh(top.feature, top.coefficient, color="#168a92")
    axes[0].axvline(0, color="grey", linewidth=1)
    axes[0].set(title="Logistique : coefficients pénalisés", xlabel="Échelle propre à chaque variable")
    top = importance.tail(10)
    axes[1].barh(top.feature, top.AP_drop_mean, xerr=top.AP_drop_std, color="#cf7354")
    axes[1].axvline(0, color="grey", linewidth=1)
    axes[1].set(title=f"{winner} : importance sur le test", xlabel="Baisse d'AP ± écart-type des permutations")
    save_figure("02_interpretation")
