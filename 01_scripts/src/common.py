"""Petits outils communs : chemins, nettoyage, variables et prétraitement."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer, MissingIndicator
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "04_results/tables"
FIGURES = ROOT / "05_figures"
SEED = 42
TARGETS = ["Hinselmann", "Schiller", "Citology", "Biopsy"]
DX = ["Dx:Cancer", "Dx:CIN", "Dx:HPV", "Dx"]
DELAYS = ["STDs: Time since first diagnosis", "STDs: Time since last diagnosis"]
NUM = ["Age", "First sexual intercourse", "Number of sexual partners",
       "Num of pregnancies", "Smokes (years)", "Smokes (packs/year)",
       "Hormonal Contraceptives (years)", "IUD (years)", "STDs (number)",
       "STDs: Number of diagnosis"]
BIN = ["Smokes", "Hormonal Contraceptives", "IUD", "STDs",
       "STDs:condylomatosis", "STDs:cervical condylomatosis",
       "STDs:vaginal condylomatosis", "STDs:vulvo-perineal condylomatosis",
       "STDs:syphilis", "STDs:pelvic inflammatory disease", "STDs:genital herpes",
       "STDs:molluscum contagiosum", "STDs:AIDS", "STDs:HIV",
       "STDs:Hepatitis B", "STDs:HPV"]
FEATURES = NUM + BIN
LOG = NUM[2:]  # Comprimer les comptes et durées ; préserver les deux âges.
MISSING = ["Number of sexual partners", "First sexual intercourse",
           "Num of pregnancies", "Smokes", "Hormonal Contraceptives", "IUD", "STDs"]
CLUSTER = [c for c in NUM if c not in ["Smokes (packs/year)", "STDs: Number of diagnosis"]]


def load_data():
    """Lire la source intacte et produire une copie nettoyée, sans imputation."""
    raw = pd.read_csv(ROOT / "02_data/raw/cervical_cancer.csv", na_values="?")
    raw = raw.apply(pd.to_numeric, errors="raise")
    clean = raw.copy()
    impossible = clean["First sexual intercourse"] > clean["Age"]
    # On ignore lequel des deux âges est faux : convention prudente documentée.
    clean.loc[impossible, "First sexual intercourse"] = np.nan
    return raw, clean


def get_x(data, columns=FEATURES):
    """log1p ne dépend d'aucune statistique apprise : possible avant le split."""
    x = data[columns].copy()
    to_log = [c for c in LOG if c in columns]
    x[to_log] = np.log1p(x[to_log])  # Les NaN restent NaN ; zéro reste zéro.
    return x


def preprocessor(strategy="median", scale=True, indicators=True):
    """Toutes les statistiques seront apprises par fit, dans chaque pli."""
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy=strategy, keep_empty_features=True)),
        ("scale", StandardScaler() if scale else "passthrough")])
    parts = [("num", numeric, NUM),
             ("bin", SimpleImputer(strategy="most_frequent", keep_empty_features=True), BIN)]
    if indicators:
        # Une seule colonne par domaine, pour ne pas répéter le même signal.
        parts.append(("missing", MissingIndicator(features="all"), MISSING))
    return ColumnTransformer(parts, verbose_feature_names_out=False)


def save_table(data, name, index=False):
    TABLES.mkdir(parents=True, exist_ok=True)
    data.to_csv(TABLES / f"{name}.csv", index=index)


def save_figure(name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    temporary = FIGURES / f"{name}.tmp.png"
    plt.savefig(temporary, dpi=180, bbox_inches="tight")
    plt.close()
    temporary.replace(FIGURES / f"{name}.png")  # Rendre disponible l'image complète.


def set_style():
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.figsize": (9, 5),
                         "axes.titleweight": "bold", "axes.titlepad": 14})
