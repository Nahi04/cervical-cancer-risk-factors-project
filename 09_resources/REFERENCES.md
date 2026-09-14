# Références et traçabilité

Sources consultées le 13 septembre 2026. Les nombres de patientes, métriques et
figures du projet sont calculés à partir du CSV joint. Les liens ci-dessous
justifient le contexte et les outils ; ils ne sont pas la source de nos scores.

| Réf. | Source | Utilisation et portée |
|---|---|---|
| R1 | Fernandes K., Cardoso J., Fernandes J. (2017). [Cervical Cancer (Risk Factors), UCI](https://doi.org/10.24432/C5Z310). [Fiche](https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors). | Provenance, quatre cibles, absences, licence. Les définitions et dates de recueil détaillées ne sont pas toutes disponibles. |
| R2 | OMS. [Cancer du col de l'utérus](https://www.who.int/fr/news-room/fact-sheets/detail/cervical-cancer). | Contexte du HPV et de la prévention ; aucune extrapolation d'incidence mondiale à notre échantillon. |
| R3 | OMS. [Papillomavirus humain et cancer](https://www.who.int/fr/news-room/fact-sheets/detail/human-papilloma-virus-and-cancer). | Persistance d'une infection HPV à haut risque et distinction entre infection et lésions. |
| R4 | scikit-learn 1.8. [Common pitfalls](https://scikit-learn.org/1.8/common_pitfalls.html). | Pipelines et prévention des fuites. |
| R5 | scikit-learn 1.8. [Imputation](https://scikit-learn.org/1.8/modules/impute.html). | SimpleImputer et indicateurs d'absence. |
| R6 | scikit-learn 1.8. [StratifiedGroupKFold](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html). | Découpages conservant les groupes et approximativement les proportions. |
| R7 | scikit-learn 1.8. [LogisticRegression](https://scikit-learn.org/1.8/modules/generated/sklearn.linear_model.LogisticRegression.html). | L2, C et class_weight. |
| R8 | scikit-learn 1.8. [RandomForestClassifier](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestClassifier.html). | Forêt de classification, limites de profondeur et feuilles. |
| R9 | scikit-learn 1.8. [Average precision](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.average_precision_score.html). | AP distincte de l'intégration trapézoïdale. |
| R10 | scikit-learn 1.8. [Probability calibration](https://scikit-learn.org/1.8/modules/calibration.html). | Lecture de la calibration et du Brier. |
| R11 | scikit-learn 1.8. [Clustering](https://scikit-learn.org/1.8/modules/clustering.html). | K-means, silhouette, CH, DB et ARI. |
| R12 | scikit-learn 1.8. [PCA](https://scikit-learn.org/1.8/modules/decomposition.html#pca). | Variance, projection et reconstruction. |
| R13 | scikit-learn 1.8. [Permutation importance](https://scikit-learn.org/1.8/modules/permutation_importance.html). | Importance conditionnelle au modèle et aux variables corrélées. |
| R14 | Fernandes K., Chicco D., Cardoso J. S., Fernandes J. (2018). [Supervised deep learning embeddings for the prediction of cervical cancer diagnosis](https://doi.org/10.7717/peerj-cs.154). [Résumé indexé](https://pubmed.ncbi.nlm.nih.gov/33816808/). | Positionnement : les auteurs étudient la prédiction de la biopsie et un apprentissage conjoint de représentation et classification. Le résumé a été consulté ; aucune comparaison chiffrée à un tableau non vérifié n'est revendiquée. |
| R15 | GitHub. [Importer un projet local](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github). | Commandes de publication. |
| R16 | GitHub. [Cloner un dépôt](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository). | Différence entre cloner et publier. |

Le document de consignes fourni par l'utilisateur est la source des exigences
de l'UE : Python, quelques méthodes approfondies, scripts reproductibles et oral
de dix minutes. Le rapport ajouté dans ce dépôt répond à la demande de l'utilisateur.

L'article introductif référencé par UCI est Fernandes, Cardoso et Fernandes (2017),
*Transfer Learning with Partial Observability Applied to Cervical Cancer Screening*.
Sa présence dans la fiche est vérifiée. Son texte intégral n'a pas été utilisé
pour inventer une performance de comparaison.

Comparer des scores publiés exigerait la même cible, les mêmes prédicteurs,
la même gestion des répétitions, les mêmes découpages et les mêmes métriques.
Un score annoncé sur un autre protocole ne démontre pas une amélioration sur ce projet.
