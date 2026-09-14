"""PCA pour voir les profils ; k-means sur les huit dimensions pour les regrouper."""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import (silhouette_score, silhouette_samples, adjusted_rand_score,
                             calinski_harabasz_score, davies_bouldin_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from .common import ROOT, SEED, CLUSTER, get_x, save_table, save_figure


def cluster_metrics(z, labels):
    if len(np.unique(labels)) < 2:
        return {"silhouette": np.nan, "Calinski_Harabasz": np.nan, "Davies_Bouldin": np.nan}
    return {"silhouette": silhouette_score(z, labels),
            "Calinski_Harabasz": calinski_harabasz_score(z, labels),
            "Davies_Bouldin": davies_bouldin_score(z, labels)}


def run(clean, dev, test):
    x = get_x(clean, CLUSTER)
    xd, xt = x.iloc[dev], x.iloc[test]
    prep = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    zd, zt = prep.fit_transform(xd), prep.transform(xt)
    candidates, models = [], {}
    for k in range(2, 6):
        model = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(zd)
        sizes = np.bincount(model.labels_, minlength=k)
        candidates.append({"k": k, "inertia": model.inertia_, "min_size": sizes.min(),
                           "max_size": sizes.max(), "eligible": sizes.min() >= 0.05 * len(dev),
                           **cluster_metrics(zd, model.labels_)})
        models[k] = model
    scores = pd.DataFrame(candidates)
    save_table(scores, "03_choix_k")
    eligible = scores.loc[scores.eligible]
    if eligible.empty:
        raise ValueError("Aucun k ne satisfait la taille minimale : ne pas forcer une conclusion.")
    k = int(eligible.sort_values("silhouette", ascending=False).iloc[0].k)
    model = models[k]
    labels, test_labels = model.labels_, model.predict(zt)
    save_table(pd.DataFrame([{"subset": "development", **cluster_metrics(zd, labels)},
                             {"subset": "test", **cluster_metrics(zt, test_labels)}]), "03_evaluation")

    # Refaire aussi le prétraitement sur 20 sous-échantillons de groupes à 80 %.
    groups = pd.util.hash_pandas_object(get_x(clean).iloc[dev], index=False).to_numpy()
    unique_groups = np.unique(groups)
    rng = np.random.default_rng(SEED)
    stability = []
    for repetition in range(20):
        selected = rng.choice(unique_groups, int(0.8 * len(unique_groups)), replace=False)
        idx = np.flatnonzero(np.isin(groups, selected))
        new_prep = clone(prep)
        z_sub = new_prep.fit_transform(xd.iloc[idx])
        new_model = KMeans(n_clusters=k, n_init=20, random_state=SEED + repetition).fit(z_sub)
        new_labels = new_model.predict(new_prep.transform(xd))
        stability.append({"repetition": repetition + 1, "n_fit": len(idx),
                          "ARI_vs_reference": adjusted_rand_score(labels, new_labels)})
    save_table(pd.DataFrame(stability), "03_stabilite")
    # Sensibilité à l'imputation et aux valeurs extrêmes, même k, sans changer le choix.
    alternatives = {"mean_imputation": clone(prep).set_params(impute__strategy="mean").fit_transform(xd),
                    "clip_1_99_percent": clone(prep).fit_transform(
                        xd.clip(lower=xd.quantile(0.01), upper=xd.quantile(0.99), axis=1))}
    sensitivity = []
    for name, z in alternatives.items():
        new_labels = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit_predict(z)
        sensitivity.append({"alternative": name, "ARI_vs_reference": adjusted_rand_score(labels, new_labels),
                            **cluster_metrics(z, new_labels)})
    save_table(pd.DataFrame(sensitivity), "03_sensibilite")

    # PCA apprise seulement sur le développement ; aucun y fourni.
    pca = PCA().fit(zd)
    pc_dev, pc_test = pca.transform(zd), pca.transform(zt)
    variance = pd.DataFrame({"component": np.arange(1, len(CLUSTER) + 1),
                             "variance_ratio": pca.explained_variance_ratio_,
                             "cumulative": pca.explained_variance_ratio_.cumsum()})
    save_table(variance, "03_pca_variance")
    save_table(pd.DataFrame(pca.components_.T, index=CLUSTER,
                           columns=[f"PC{i+1}" for i in range(len(CLUSTER))]), "03_pca_axes", index=True)
    reconstruction = []
    for name, z, pc in [("development", zd, pc_dev), ("test", zt, pc_test)]:
        restored = pc[:, :2] @ pca.components_[:2] + pca.mean_
        reconstruction.append({"subset": name, "MSE_standardized_2D": np.mean((z - restored) ** 2)})
    save_table(pd.DataFrame(reconstruction), "03_pca_reconstruction")
    profiles, assigned = [], []
    for name, idx, lab, pc in [("development", dev, labels, pc_dev), ("test", test, test_labels, pc_test)]:
        d = clean.iloc[idx].copy()
        d["cluster"] = lab + 1  # Numéros sans ordre biologique.
        stats = d.groupby("cluster").agg(n=("Biopsy", "size"), positives=("Biopsy", "sum"))
        stats["positive_fraction"] = stats.positives / stats.n
        stats["subset"] = name
        profiles.append(stats.reset_index())
        save_table(d.groupby("cluster")[CLUSTER].median(), f"03_profils_medianes_{name}", index=True)
        save_table(d.groupby("cluster")[CLUSTER].count(), f"03_profils_observes_n_{name}", index=True)
        d["missing_fraction"] = d[CLUSTER].isna().mean(axis=1)
        save_table(d.groupby("cluster").missing_fraction.mean().to_frame(),
                   f"03_profils_absence_{name}", index=True)
        assigned.append(pd.DataFrame({"source_row": idx + 2, "subset": name,
            "cluster": lab + 1, "PC1": pc[:, 0], "PC2": pc[:, 1], "Biopsy": d.Biopsy.to_numpy()}))
    save_table(pd.concat(profiles), "03_effectifs_clusters")
    save_table(pd.concat(assigned), "03_affectations")
    metadata = {"k": k, "features": CLUSTER, "minimum_cluster_fraction": 0.05,
                "PCA_2D_variance": float(variance.cumulative.iloc[1]),
                "components_for_90pct": int((variance.cumulative < 0.90).sum() + 1),
                "ARI_subsamples_mean": float(pd.DataFrame(stability).ARI_vs_reference.mean())}
    (ROOT / "04_results/tables/03_selection.json").write_text(json.dumps(metadata, indent=2))
    plots(zd, labels, scores, pc_dev, pc_test, test_labels, variance, model.cluster_centers_, stability)
    print(f"  k = {k} ; silhouette développement = {silhouette_score(zd, labels):.3f}", flush=True)


def plots(zd, labels, scores, pc_dev, pc_test, test_labels, variance, centers, stability):
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7))
    for ax, metric in zip(axes, ["inertia", "silhouette", "Davies_Bouldin"]):
        ax.plot(scores.k, scores[metric], "o-", color="#168a92")
        ax.set(xlabel="Nombre de groupes k", ylabel=metric, xticks=scores.k)
    axes[0].set_title("Compacité (plus petit)")
    axes[1].set_title("Séparation (plus grand)")
    axes[2].set_title("Davies-Bouldin (plus petit)")
    save_figure("03_choix_k")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for ax, pc, lab, name in [(axes[0], pc_dev, labels, "Développement"),
                               (axes[1], pc_test, test_labels, "Test projeté sans réajustement")]:
        for c in np.unique(labels):
            ax.scatter(pc[lab == c, 0], pc[lab == c, 1], s=18, alpha=0.65, label=f"Groupe {c+1}")
        ax.set(title=name, xlabel=f"PC1 ({100*variance.variance_ratio.iloc[0]:.1f} %)",
               ylabel=f"PC2 ({100*variance.variance_ratio.iloc[1]:.1f} %)")
        ax.legend(fontsize=8)
    save_figure("03_pca_clusters")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].bar(variance.component, variance.variance_ratio, color="#168a92", label="Par composante")
    axes[0].plot(variance.component, variance.cumulative, "o-", color="#cf7354", label="Cumulée")
    axes[0].axhline(0.9, color="grey", linestyle="--")
    axes[0].set(title="PCA : quelle information reste en 2D ?", xlabel="Composante", ylabel="Fraction de variance")
    axes[0].legend()
    s = silhouette_samples(zd, labels)
    for c in np.unique(labels):
        axes[1].hist(s[labels == c], bins=np.linspace(-0.5, 1, 25), alpha=0.5, label=f"Groupe {c+1}")
    axes[1].axvline(0, color="grey", linestyle="--")
    axes[1].set(title="Silhouette par patiente : voir les chevauchements", xlabel="Silhouette", ylabel="Effectif")
    axes[1].legend()
    save_figure("03_evaluation_pca_silhouette")
    plt.figure(figsize=(10, 4.5))
    plt.imshow(centers, cmap="RdBu_r", vmin=-2, vmax=2, aspect="auto")
    plt.xticks(range(len(CLUSTER)), CLUSTER, rotation=35, ha="right")
    plt.yticks(range(len(centers)), [f"Groupe {i+1}" for i in range(len(centers))])
    plt.colorbar(label="Centre : unités standardisées après log et imputation")
    for i in range(len(centers)):
        for j in range(len(CLUSTER)):
            plt.text(j, i, f"{centers[i,j]:.1f}", ha="center", va="center", fontsize=9,
                     color="white" if abs(centers[i,j]) > 1.4 else "black")
    plt.title("Profils des groupes : différences descriptives")
    save_figure("03_profils_clusters")
    plt.figure(figsize=(8, 3.5))
    plt.plot(range(1, 21), pd.DataFrame(stability).ARI_vs_reference, "o-", color="#168a92")
    plt.ylim(-0.05, 1.05)
    plt.xlabel("Sous-échantillon de 80 % des groupes de profils")
    plt.ylabel("ARI avec la partition de référence")
    plt.title("Stabilité : prétraitement et k-means réappris à chaque fois")
    save_figure("03_stabilite")
