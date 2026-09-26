# Cervical Cancer Risk Factors — Machine Learning in Python

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Dataset](https://img.shields.io/badge/Dataset-UCI-2E8B57)](https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors)

A reproducible machine-learning project on the **UCI Cervical Cancer Risk Factors** dataset, developed for the 5BM753 course.

The project combines a rigorous supervised-learning workflow with exploratory unsupervised analysis while explicitly addressing **missing data, class imbalance, data leakage, validation strategy, uncertainty and clinical over-interpretation**.

## Project at a glance

**Dataset:** 858 patient records, 36 variables  
**Primary target:** Biopsy  
**Positive class prevalence:** 55 / 858 = 6.4%  
**Main language:** Python  
**Core libraries:** pandas, NumPy, Matplotlib, scikit-learn  
**Supervised models:** Logistic Regression and Random Forest  
**Unsupervised methods:** PCA and k-means

## Questions

### Supervised learning

Can a positive biopsy result be predicted from information available before the screening examinations?

### Unsupervised learning

Can the patient records be grouped into coherent descriptive profiles without using the biopsy outcome during clustering?

## Why this dataset is challenging

The dataset is small, highly imbalanced and contains substantial missingness.

A naive model can obtain high accuracy by predicting almost every patient as negative. For that reason, the project does **not** use accuracy as the primary model-selection metric.

Instead, the analysis emphasizes:

- Average Precision
- ROC-AUC
- recall / sensitivity
- specificity
- precision
- F1 and F2 scores
- Matthews correlation coefficient
- Brier score
- confusion matrices
- bootstrap uncertainty

## Methodological safeguards

The project was structured to reduce common sources of optimistic bias.

Key choices include:

- one predefined target: Biopsy;
- exclusion of other examination outcomes from the predictors;
- exclusion of variables whose timing could create leakage;
- preprocessing learned only inside training folds;
- grouped train/test splitting for duplicated predictor profiles;
- grouped cross-validation within the development set;
- a completely held-out test set;
- threshold selection based only on out-of-fold development predictions;
- a naive DummyClassifier baseline;
- no model choice based on the final test set;
- automated integrity tests for split consistency and exported results.

The complete protocol is documented in:

[09_resources/01_documentation/00_protocole_avant_resultats.md](09_resources/01_documentation/00_protocole_avant_resultats.md)

## Supervised-learning workflow

### Models

Three prediction strategies are compared:

1. **Dummy baseline** — predicts the learned class prior
2. **L2 Logistic Regression** — regularized linear classifier
3. **Random Forest** — nonlinear ensemble model

Hyperparameters, imputation strategy and class weighting are selected by grouped cross-validation on the development set.

### Main results

| Model | CV Average Precision | Test Average Precision | Test recall at selected threshold |
|---|---:|---:|---:|
| Dummy baseline | 0.064 ± 0.003 | 0.065 | 0 / 14 |
| L2 Logistic Regression | 0.135 ± 0.029 | 0.086 | 5 / 14 |
| Random Forest | 0.217 ± 0.036 | 0.082 | 2 / 14 |

The Random Forest achieved the highest Average Precision during cross-validation and was therefore selected **before** opening the final test set.

On the reserved test set, however, its discrimination remained weak and only slightly above the naive reference.

This is an important result: **the project does not support clinical deployment of the model**.

The analysis therefore illustrates a complete and transparent ML workflow rather than trying to turn a weak predictive signal into an exaggerated clinical claim.

![ROC and precision-recall curves on the reserved test set](05_figures/02_courbes_test.png)

## Unsupervised analysis

A separate exploratory analysis uses **PCA and k-means** to identify groups of similar patient records without using Biopsy to build the clusters.

The workflow includes:

- median imputation
- standardization
- evaluation of k from 2 to 5
- silhouette score
- Calinski-Harabasz score
- Davies-Bouldin score
- cluster-size constraints
- stability assessment by repeated subsampling
- sensitivity analysis to preprocessing choices
- PCA projection and reconstruction analysis

Cluster membership is interpreted descriptively and is **not** presented as a validated clinical subtype.

## Repository structure

| Path | Purpose |
|---|---|
| [01_scripts](01_scripts) | Reproducible Python pipeline |
| [02_data](02_data) | Source data and reproducible split information |
| [03_notebooks](03_notebooks) | Optional notebooks for exploration |
| [04_results](04_results) | Exported metrics and tables |
| [05_figures](05_figures) | Automatically generated figures |
| [06_report](06_report) | Full scientific report |
| [08_slides](08_slides) | Oral presentation |
| [09_resources](09_resources) | Detailed documentation and references |

## Reproduce the analysis

From the repository root with Python 3.12:

    python -m pip install -r requirements.txt
    python 01_scripts/run_project.py

The pipeline regenerates the main tables and figures.

To run the integrity tests:

    python -m unittest discover -s 01_scripts/tests -v

A Conda environment is also provided:

    conda env create -f environment.yml
    conda activate cervical-cancer-python

## Code organization

The project is intentionally modular:

- run_project.py — orchestrates the full analysis
- src/common.py — data loading and preprocessing
- src/audit.py — data audit and descriptive checks
- src/supervised.py — supervised modelling and validation
- src/evaluation.py — metrics, thresholds, uncertainty and plots
- src/unsupervised.py — PCA and clustering
- tests/test_integrity.py — leakage and output consistency checks

For a guided reading of the code:

[09_resources/01_documentation/09_lire_et_modifier_le_code.md](09_resources/01_documentation/09_lire_et_modifier_le_code.md)

## Scientific interpretation

The available risk factors provide some predictive information, but the held-out test performance is too weak and uncertain to justify a clinical prediction tool.

The test set contains only 14 positive biopsies, so uncertainty is substantial. This limitation is explicitly quantified with grouped bootstrap intervals.

The project therefore emphasizes three principles:

1. strong validation matters more than training performance;
2. class imbalance can make accuracy misleading;
3. negative or weak results are still scientifically useful when the methodology is sound.

## References

- Fernandes K., Cardoso J., Fernandes J.  
  [UCI Cervical Cancer (Risk Factors)](https://doi.org/10.24432/C5Z310)

- World Health Organization  
  [Cervical cancer](https://www.who.int/news-room/fact-sheets/detail/cervical-cancer)

- scikit-learn  
  [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)

A complete annotated bibliography is available in:

[09_resources/REFERENCES.md](09_resources/REFERENCES.md)

## Author

**Nahi El Akoum**  
Master 2 — Artificial Intelligence and Data Analysis in Biology (AIDA)  
Sorbonne Université
