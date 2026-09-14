# Traiter les valeurs manquantes

## Une absence n'est pas une réponse négative

Si `IUD` vaut zéro, le fichier indique une réponse négative. Si `IUD` est `NaN`,
la réponse est indisponible. Remplacer tous les `NaN` par zéro confondrait ces deux
situations. La source UCI mentionne des refus de réponse liés à la confidentialité.
Nous ne supposons donc pas que les absences soient complètement aléatoires.
Leur mécanisme exact ne peut pas être établi avec ce seul fichier.

Source : [description du recueil UCI](https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors).

## Deux stratégies simples et comparables

| Type de colonne | Stratégie A | Stratégie B |
|---|---|---|
| Numérique après log1p éventuel | Médiane apprise | Moyenne apprise |
| Binaire | Mode appris | Mode appris |
| Absence de réponse dans sept domaines | Indicateur 0/1 | Même indicateur 0/1 |

La médiane est la valeur centrale des réponses observées ; elle est moins
influencée par les extrêmes. La moyenne exploite toutes les valeurs observées
mais peut être déplacée par les extrêmes. La transformation préalable réduit
déjà une partie de cette asymétrie. La comparaison utilise exactement les mêmes
plis et les mêmes choix d'hyperparamètres. L'effet de l'imputation peut donc se
comparer à réglages identiques dans les fichiers de grille.

Pour un binaire, le mode produit encore 0 ou 1. Ce remplacement est un outil
mathématique pour calculer un score, pas une nouvelle observation clinique.
L'imputation univariée peut créer des combinaisons d'expositions imparfaitement
cohérentes. Le rapport conserve cette limite et les fichiers bruts ne sont
jamais remplacés par un tableau présenté comme complètement observé.

Le projet compare ces stratégies par leur effet sur la **prédiction**, pas par
une erreur d'imputation sur les vraies absences : leur valeur véritable est inconnue.
Nous n'affirmons donc pas que la médiane « retrouve mieux » les réponses manquantes.

## Ce que fait le pipeline

```python
numeric = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler())
])
```

`fit` calcule les médianes et l'échelle sur les lignes d'apprentissage.
`transform` réutilise ces nombres sur les lignes de validation ou de test.
`GridSearchCV` recrée ce fonctionnement dans chaque pli grâce au pipeline complet.
Une imputation globale, suivie d'une validation croisée du seul modèle, laisserait
les lignes de validation influencer le prétraitement.

Les colonnes `missingindicator_...` valent un si le champ d'origine était absent.
Elles permettent au modèle d'utiliser ce contexte. Elles peuvent aussi apprendre
une pratique locale de recueil, qui ne se reproduira pas ailleurs. Nous comparons
donc la forêt sélectionnée avec une version sans ces indicateurs, en développement.

Source : [documentation de l'imputation](https://scikit-learn.org/1.8/modules/impute.html).

## Pourquoi ne pas utiliser tout de suite KNN ou MICE ?

Il faudrait définir une distance pertinente entre variables mixtes pour KNN,
traiter le codage des binaires et vérifier la dépendance aux voisins. Une imputation
multiple demanderait aussi une stratégie de combinaison des analyses. Ces méthodes
peuvent être utiles, mais elles ne sont pas nécessaires à cette première comparaison
de deux classifieurs sur peu de cas positifs. Leur complexité n'est pas une garantie
de meilleur résultat. Elles figurent comme prolongements, pas comme étapes manquantes.

L'analyse en cas complets est décrite par ses effectifs, sans prétendre comparer
équitablement son score à celui d'une méthode évaluée sur d'autres patientes.
Un vrai comparatif de modèles en cas complets demanderait une population de
validation commune et l'examen du biais introduit par l'exclusion des dossiers.

## Lire les résultats

Les deux classifieurs ne choisissent pas nécessairement la même imputation.
Les tables `02_grille_Logistique.csv` et `02_grille_Foret.csv` donnent les huit
combinaisons par famille. Dans cette exécution, la logistique sélectionne la
moyenne et la forêt la médiane, avec des différences d'AP faibles entre imputations.
L'effet majeur est la chute entre validation et test, pas un avantage décisif
d'une imputation. Les statistiques effectivement apprises sont exportées dans
`02_imputation_*.csv`, dans l'espace utilisé par les modèles.
