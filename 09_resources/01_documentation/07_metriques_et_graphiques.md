# Comprendre les métriques et chaque graphique supervisé

## Quatre nombres avant tous les scores

| Situation | Nom | Colonne exportée |
|---|---|---|
| Biopsie positive, modèle positif | Vrai positif | TP |
| Biopsie négative, modèle positif | Faux positif | FP |
| Biopsie positive, modèle négatif | Faux négatif | FN |
| Biopsie négative, modèle négatif | Vrai négatif | TN |

Dans nos matrices, les lignes sont les observations et les colonnes les prédictions.
La case en haut à gauche contient TN, celle en bas à droite TP. La ligne du bas
est essentielle : elle montre combien de biopsies positives ont été manquées.

## Les scores dépendant d'un seuil

| Métrique | Calcul ou sens | Bonne lecture |
|---|---|---|
| Accuracy | (TP+TN) / effectif total | Proportion globale correcte ; trompeuse avec une classe rare. |
| Rappel / sensibilité | TP / (TP+FN) | Parmi les positives, quelle fraction est détectée ? |
| Spécificité | TN / (TN+FP) | Parmi les négatives, quelle fraction est correctement classée ? |
| Précision / VPP | TP / (TP+FP) | Parmi les alertes, quelle fraction est réellement positive ? |
| Balanced accuracy | (sensibilité + spécificité) / 2 | Donne le même poids aux deux classes. |
| F1 | 2TP / (2TP+FP+FN) | Compromis précision-rappel, sans tenir compte des vrais négatifs. |
| F2 | 5TP / (5TP+FP+4FN) | Donne davantage de poids aux faux négatifs que F1. |
| MCC | Corrélation entre classe observée et prédite | Prend en compte les quatre cases ; proche de 0 sans association. |

Quand il n'y a aucune prédiction positive, la précision est mathématiquement
indéfinie. Le code utilise la convention `zero_division=0` : il affiche zéro.
Dans cette situation, F1 et F2 valent zéro. Pour une prédiction constante, scikit-learn
renvoie MCC=0. Ces conventions évitent de lire une absence d'alerte comme une bonne
précision. La base obtient ainsi 93,49 % d'accuracy sur le test, mais aucun vrai positif.

## Les scores indépendants du seuil

L'AP, ou average precision, mesure le classement des positives à mesure que le
seuil varie. Elle pondère la précision par les gains de rappel. Ce n'est pas
l'aire trapézoïdale de la courbe précision-rappel et ce n'est pas la précision
au seuil sélectionné. Pour un score identique donné à toutes les patientes,
l'AP est exactement la fraction positive du jeu évalué, ici 14/215 = 0,0651.
Pour un classement aléatoire fini, la distribution d'AP fluctue : cette prévalence
est un repère, pas un test de significativité automatique.

La ROC-AUC évalue le classement relatif des positives et négatives, en comptant
les égalités de score à moitié. 0,5 correspond à une absence de discrimination.
Elle reste utile, mais peut donner une impression favorable alors que la précision
des alertes est faible dans une population très déséquilibrée. C'est pourquoi
nous choisissons AP comme critère principal et montrons les deux courbes.

Sources : [AP](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.average_precision_score.html),
[ROC-AUC](https://scikit-learn.org/1.8/modules/generated/sklearn.metrics.roc_auc_score.html).

Le Brier est la moyenne de `(score - réponse)^2`. Plus il est faible, meilleur
est ce score probabiliste global. Il mélange calibration et discrimination ;
ce n'est pas un pur indice de calibration. La base est ici meilleure au Brier
que les deux classifieurs. Cela incite à ne pas prendre leurs scores pour des
probabilités médicales fiables.

## Lire les figures

| Fichier dans 05_figures | Ce qu'il faut regarder |
|---|---|
| `02_comparaison_cv.png` | La moyenne d'AP de chaque méthode et la variabilité entre plis. Scores de sélection, pas résultats finaux. |
| `02_courbes_test.png` | ROC à gauche, précision-rappel à droite ; l'AP des modèles reste proche de la référence. |
| `02_confusions_test.png` | Les faux négatifs au seuil OOF, sans changer ce seuil après observation du test. |
| `02_calibration_test.png` | Concordance score/fréquence observée et répartition des scores ; seulement 14 positives. |
| `02_interpretation.png` | Coefficients et importances fragiles, à relier à la faible discrimination. |

Les points de calibration regroupent les scores en cinq groupes de taille voisine,
sauf égalités de score. Chaque point met en relation score moyen et fraction de
biopsies positives. Les effectifs et nombres positifs figurent dans
`02_calibration_bins.csv`. Une courbe irrégulière sur si peu de cas n'établit
pas une calibration stable. Nous ne rajoutons pas une calibration isotone complexe
après avoir vu le test. Source :
[calibration](https://scikit-learn.org/1.8/modules/calibration.html).

## Pourquoi le meilleur modèle CV n'est-il pas le meilleur AP test ?

La forêt est choisie avant le test, avec AP CV = 0,2168 contre 0,1346 pour la
logistique. Sur le test, leurs AP sont 0,0816 et 0,0859. La différence est petite
et incertaine. Ce désaccord est un résultat de généralisation à expliquer,
pas une raison de changer rétrospectivement le choix annoncé.

Le seuil 0,5 donne zéro vrai positif pour les deux modèles. Au seuil F2 OOF,
la logistique produit 5 TP, 42 FP et 9 FN ; la forêt 2 TP, 28 FP et 12 FN.
Les résultats ne justifient aucun usage de diagnostic. Le projet montre une
procédure honnête et les limites du signal disponible.
