"""Exécuter tout le projet : python 01_scripts/run_project.py (ou F5 dans Spyder)."""
import json
import platform
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Sauver les figures, même sans écran ; pas de fenêtres bloquantes.
import sklearn
from src.common import ROOT, load_data, set_style
from src import audit, supervised, unsupervised


def main():
    start = time.perf_counter()
    set_style()
    raw, clean = load_data()
    print("1/3 - Audit des données", flush=True)
    audit.run(raw, clean)
    print("2/3 - Apprentissage supervisé", flush=True)
    dev, test = supervised.run(clean)
    print("3/3 - PCA et clustering", flush=True)
    unsupervised.run(clean, dev, test)
    versions = {"python": platform.python_version(), "numpy": np.__version__,
                "pandas": pd.__version__, "matplotlib": matplotlib.__version__,
                "scikit-learn": sklearn.__version__,
                "duration_seconds": round(time.perf_counter() - start, 1)}
    (ROOT / "04_results/tables/00_execution.json").write_text(json.dumps(versions, indent=2))
    print("Terminé. Consulter 04_results/tables et 05_figures.", flush=True)


if __name__ == "__main__":
    main()
