# Les modèles supervisés et leur rôle

## La base naïve remplace ici la persistance

Un modèle de persistance utilise la dernière valeur observée pour prévoir la
suivante. Sans ordre temporel ni visites répétées identifiées, « la dernière
biopsie de cette patiente » n'existe pas dans les données disponibles.

`DummyClassifier(strategy="prior")` apprend uniquement la fréquence de la classe
positive dans l'apprentissage. Il donne ensuite le même score à tout le monde.
Au seuil 0,5, tous les dossiers sont classés négatifs. Cette base permet de vérifier
si les variables apportent une information au-delà de la seule fréquence des cas.
Source : [DummyClassifier](https://scikit-learn.org/1.8/modules/generated/sklearn.dummy.DummyClassifier.html).

```python
base = DummyClassifier(strategy="prior")
base.fit(xd, yd)
p_base = base.predict_proba(xt)[:, 1]
```

`fit` apprend la proportion ; `predict_proba` renvoie deux colonnes de scores,
pour les classes 0 et 1. `[:, 1]` conserve le score de la classe positive.

## Régression logistique L2

La cible est binaire : une régression linéaire, Ridge ou Lasso de régression
ne convient pas à cette définition du problème. Nous utilisons la logistique,
qui transforme une somme pondérée des variables en un score entre zéro et un.

Pour une patiente, le modèle calcule d'abord `z = b + w1*x1 + ... + wp*xp`,
puis `p = 1 / (1 + exp(-z))`. `b` est l'interception et `w` représente les
coefficients appris. La perte logistique pénalise particulièrement les prédictions
confiantes mais fausses. La régularisation L2 décourage les coefficients excessifs.
Dans scikit-learn, un petit `C` renforce la régularisation.

Pourquoi ce choix ? Le modèle fournit une référence interprétable, utilise peu
de réglages et convient aux petites tables. Sa limite est l'addition des effets
dans l'espace transformé : les interactions complexes ne sont pas automatiquement
représentées. Nous testons seulement `C=0.1` et `C=1.0`.

```python
pipe = Pipeline([
    ("pre", preprocessor(scale=True)),
    ("constant", VarianceThreshold()),
    ("model", LogisticRegression(C=1.0, max_iter=2000))
])
```

Le premier élément prépare les entrées. Le deuxième retire ce qui est constant
dans le pli. Le troisième ajuste la logistique. `max_iter=2000` est une limite
de calcul pour que l'optimisation ait le temps de converger, pas un nombre de
réglages testés. Le solveur par défaut est `lbfgs`, la pénalisation par défaut L2
dans la version 1.8.0 utilisée.

Source : [LogisticRegression 1.8](https://scikit-learn.org/1.8/modules/generated/sklearn.linear_model.LogisticRegression.html).

## Forêt aléatoire de classification

Un arbre pose successivement des questions comme « la durée dépasse-t-elle ce
seuil ? ». Les feuilles regroupent les lignes qui ont suivi les mêmes branches.
Une forêt ajuste de nombreux arbres sur des échantillons bootstrap et des
sous-ensembles de variables candidats aux divisions. La moyenne des scores des
arbres donne le score final. Elle peut représenter des interactions et des seuils
que la logistique additive ne représente pas facilement.

La forêt peut toutefois mémoriser les rares cas positifs. Nous fixons 200 arbres,
une profondeur maximale de 5 et comparons des feuilles d'au moins 5 ou 15 lignes.
Le nombre d'arbres stabilise le calcul ; il ne justifie pas une complexité illimitée
de chaque arbre. Les variables candidates par division suivent le défaut `sqrt`.

```python
model = RandomForestClassifier(
    n_estimators=200, max_depth=5, min_samples_leaf=5,
    random_state=42, n_jobs=1
)
```

`random_state` rend les tirages reproductibles. `n_jobs=1` donne un comportement
simple et évite les problèmes de processus imbriqués dans certains environnements.
Ce projet de 858 lignes s'exécute sans GPU.

Source : [RandomForestClassifier](https://scikit-learn.org/1.8/modules/generated/sklearn.ensemble.RandomForestClassifier.html).

## Déséquilibre : poids et seuil répondent à des questions différentes

`class_weight="balanced"` augmente le poids des erreurs sur la classe rare dans
l'apprentissage. Les poids sont recalculés sur les classes présentes dans chaque
apprentissage. Nous comparons cette option à l'absence de pondération.
Ce n'est pas obligatoire qu'elle améliore l'AP : elle est évaluée et non imposée.

Le seuil agit après le calcul du score. Un seuil plus bas classe davantage de
patientes comme positives, ce qui peut augmenter le rappel mais aussi les faux
positifs. Il ne change ni les scores ni leur classement, donc ni l'AP ni la ROC-AUC.
Le seuil F2 est une règle pédagogique choisie sur le développement.

Nous n'utilisons pas SMOTE : cela ajouterait des choix de distance et des données
synthétiques sur une table mixte. Une pondération et un seuil explicites suffisent
pour étudier deux mécanismes de prise en compte du déséquilibre. Aucun dossier
positif n'est copié entre apprentissage et test.

## Lire l'interprétation avec prudence

Un coefficient positif augmente le log-odds conditionnel quand les autres entrées
restent fixes. Une unité correspond à un écart-type pour les numériques standardisés,
et au passage 0 à 1 pour les binaires/indicateurs. Les tailles absolues des coefficients
ne sont donc pas toutes directement comparables. Ils sont pénalisés et corrélés :
ce ne sont pas des effets causaux ni des tests statistiques de facteurs de risque.

L'importance par permutation mélange une colonne du test et mesure la baisse d'AP.
Une forte baisse indiquerait que le modèle dépend de cette information. Les
colonnes corrélées peuvent se remplacer, et leur permutation peut produire des
combinaisons peu plausibles. L'écart-type des 15 permutations mesure une variabilité
de permutation, pas un intervalle de confiance biologique. Comme la performance
du modèle est faible ici, aucune importance n'établit un facteur prédictif robuste.
Source : [importance par permutation](https://scikit-learn.org/1.8/modules/permutation_importance.html).
