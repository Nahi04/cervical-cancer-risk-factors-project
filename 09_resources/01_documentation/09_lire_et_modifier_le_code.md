# Lire le code dans un ordre simple

## Commencer par 01_scripts/run_project.py

Le programme lit les données, exécute l'audit, exécute le supervisé, puis exécute
le non supervisé. Ce sont les quatre actions principales. Les autres fonctions
servent surtout à sauvegarder les résultats et à produire les graphiques.
Tu n'as pas à mémoriser toutes les métriques pour comprendre cet enchaînement.

| Fichier | À lire en premier | Ce que cela explique |
|---|---|---|
| `01_scripts/run_project.py` | `main()` | Ordre du projet et enregistrement des versions. |
| `01_scripts/src/common.py` | `load_data`, `get_x` | Lecture, copie, règle de cohérence et log1p. |
| `01_scripts/src/common.py` | `preprocessor` | Numériques, binaires et indicateurs d'absence. |
| `01_scripts/src/audit.py` | `run`, `describe_development` | Statistiques, contrôles et exploration. |
| `01_scripts/src/supervised.py` | `run`, jusqu'à la boucle des modèles | x, y, groupes, split et validation. |
| `01_scripts/src/supervised.py` | boucle `definitions` | Même protocole pour les deux familles. |
| `01_scripts/src/evaluation.py` | `metrics`, `choose_threshold` | Scores et seuil OOF. |
| `01_scripts/src/evaluation.py` | `uncertainty`, `plots` | Bootstrap et visualisations. |
| `01_scripts/src/supervised.py` | `interpretation` | Coefficients, constantes et permutations. |
| `01_scripts/src/unsupervised.py` | `run` | Huit variables, k, stabilité et PCA. |

`src` est un dossier de modules Python ordinaires. Il n'y a ni classe personnalisée
de machine learning, ni bibliothèque de deep learning, ni API externe à configurer.
Le cœur statistique utilise NumPy, pandas, Matplotlib et scikit-learn.
La génération facultative du rapport PDF ajoute reportlab.

## Six expressions Python qui reviennent souvent

| Expression | Sens dans le projet |
|---|---|
| `x.iloc[dev]` | Prendre les lignes aux positions contenues dans dev. |
| `data[columns]` | Garder les colonnes nommées dans la liste. |
| `model.fit(x, y)` | Apprendre les paramètres avec x et les réponses y. |
| `model.transform(x)` | Appliquer un prétraitement déjà appris. |
| `predict_proba(x)[:, 1]` | Garder le score de la classe positive. |
| `clone(model)` | Copier la configuration et repartir sans paramètres appris. |

`Pipeline` applique les opérations dans l'ordre. `ColumnTransformer` applique
des traitements différents aux colonnes numériques et binaires. Les doubles
traits de soulignement de `pre__num__impute__strategy` signifient : dans le pipeline,
aller dans `pre`, puis `num`, puis `impute`, puis modifier `strategy`.
C'est uniquement une adresse de paramètre, pas une nouvelle méthode statistique.

## Pourquoi plusieurs petits modules ?

Toutes les évaluations demandées ne tiennent pas honnêtement dans dix lignes.
La séparation garde le programme principal court et évite de répéter les mêmes
calculs pour chaque modèle. La partie la plus longue concerne les exports et
figures, pas les algorithmes. Les exemples courts des guides montrent leur noyau,
et les scripts complets conservent les précautions nécessaires au projet réel.

## Comment exécuter sans chemin compliqué

Dans Spyder, ouvre `01_scripts/run_project.py` et exécute le fichier entier avec F5. Les chemins de
données sont calculés à partir de l'emplacement des scripts. Il faut conserver
le dossier `src` et les données à côté de `01_scripts/run_project.py`. Si Spyder ne trouve pas `src`,
choisis le dossier du projet comme répertoire de travail et relance le noyau.

Les figures sont enregistrées en PNG dans `05_figures`. Le backend `Agg`
évite d'ouvrir de nombreuses fenêtres. Tu peux ouvrir les PNG depuis l'explorateur
ou les afficher dans Spyder avec `plt.imread` et `plt.imshow`.

## Modifications utiles et modifications qui changent l'expérience

Tu peux changer la langue des titres, les couleurs, l'ordre des graphiques ou
ajouter un tableau descriptif sans modifier le protocole statistique. En revanche,
changer la cible, les variables, les graines, la grille ou le seuil crée une autre
expérience. Une fois le test consulté, un nouveau choix inspiré par ses résultats
nécessiterait une nouvelle évaluation indépendante pour être annoncé comme validé.

Le rapport et les guides décrivent cette exécution du fichier fourni. Si tu
modifies l'analyse, relance les scripts, régénère le rapport et relis les
interprétations. Ne change pas seulement un chiffre dans le PDF.

## Relier une affirmation à une sortie

Le rapport cite les noms des tables. Pour vérifier « la forêt a détecté 2 cas »,
ouvre `02_metriques_test.csv`, ligne `Foret` et règle `F2_OOF`, colonne `TP`.
Pour vérifier le nombre de groupes, ouvre `03_choix_k.csv` puis `03_selection.json`.
Pour vérifier que le test n'a pas été mélangé à la validation, consulte `split.csv`
et les contrôles automatisés dans `01_scripts/tests/test_integrity.py`.
