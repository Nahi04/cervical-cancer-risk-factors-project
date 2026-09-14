# Apprentissage, validation et test : trois rôles différents

## Le test est une épreuve finale

L'apprentissage ajuste les paramètres, comme les coefficients de la logistique.
La validation aide à choisir les réglages : force de régularisation, imputation,
pondération des classes ou taille minimale des feuilles. Le test mesure la
performance après ces choix. Utiliser le test pour choisir reviendrait à regarder
les réponses de l'épreuve pour préparer le modèle.

Le découpage fourni contient 643 lignes de développement dont 41 positives,
et 215 lignes de test dont 14 positives. Le fichier `02_data/processed/split.csv`
permet de retrouver chaque ligne et son rôle. `source_row` compte l'en-tête CSV
comme ligne 1 : ce n'est pas un identifiant clinique.

## Pourquoi ne pas utiliser un simple train_test_split ?

Ce serait suffisant pour des dossiers indépendants sans répétitions apparentes.
Ici, 27 lignes répètent un profil de prédicteurs déjà présent, au-delà des 23
répétitions exactes sur les 36 colonnes. Des résultats d'examens différents peuvent
partager les mêmes prédicteurs. Sans identifiant, nous ne savons pas s'il s'agit
de patientes distinctes ou de répétitions. Nous conservons tout et prenons une
précaution : les mêmes profils restent toujours du même côté d'un découpage.

Le hash de pandas transforme chaque profil en un nombre technique stable pour
cette exécution. Il ne contient pas la cible. `StratifiedGroupKFold` tente de
préserver les proportions de classes tout en gardant les groupes ensemble.
Les 831 profils ne sont donc pas 831 patientes uniques prouvées.

```python
groups = pd.util.hash_pandas_object(x, index=False).to_numpy()
outer = StratifiedGroupKFold(4, shuffle=True, random_state=42)
dev, test = next(outer.split(x, y, groups))
```

On prend le premier des quatre plis comme test, soit environ un quart des lignes.
Le premier pli est fixé : nous n'essayons pas les quatre pour sélectionner celui
qui donne le meilleur résultat. `random_state=42` fixe un tirage reproductible,
sans rendre l'évaluation statistiquement certaine.

Source : [StratifiedGroupKFold](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html).

## Les cinq plis internes

Les 643 lignes de développement sont à leur tour réparties en cinq plis. Pour
chaque réglage, on entraîne sur quatre plis et on évalue sur le cinquième, puis
on change de pli réservé. Chaque validation contient huit ou neuf biopsies
positives. C'est peu : les scores varieront même avec une procédure correcte.

L'AP moyenne sert à sélectionner les réglages. L'écart-type entre plis montre
leur variabilité ; ce n'est pas un intervalle de confiance. Les modèles entraînés
dans différents plis utilisent en partie les mêmes données.

`return_train_score=True` permet aussi d'observer l'écart entre score d'apprentissage
et score de validation. Un modèle peut bien mémoriser son apprentissage et mal
classer les nouvelles lignes. La forêt montre ici un écart conséquent.

## Prédictions OOF et seuil

OOF signifie « hors pli ». Le modèle retenu est réentraîné sur chaque sous-ensemble
d'apprentissage pour produire un score sur le pli laissé de côté. On obtient ainsi
un score pour chacune des 643 lignes sans avoir directement entraîné le modèle
qui la prédit sur elle-même.

Ces OOF servent à choisir le seuil F2. Les hyperparamètres ont toutefois été choisis
à l'aide de ces mêmes plis. Il reste donc un optimisme de sélection. On ne présente
pas le meilleur F2 OOF comme une performance finale. Une validation imbriquée serait
utile pour évaluer toute la sélection en CV, mais le test réservé remplit ici le
rôle d'évaluation finale. Il ne doit pas être réutilisé pour une nouvelle sélection.

## Incertitude du test

Nous rééchantillonnons 1 000 fois les groupes de profils du test avec remise et
recalculons les métriques du modèle choisi. Les quantiles 2,5 % et 97,5 % donnent
des intervalles bootstrap approximatifs. On utilise les mêmes tirages pour les
différences d'AP entre modèles, ce qui préserve le caractère apparié.

Ces intervalles reflètent la composition du test pour des modèles déjà ajustés.
Ils ne couvrent pas toute l'incertitude liée à l'apprentissage, à l'imputation,
au choix des hyperparamètres ou au recrutement hospitalier. Avec 14 positives,
un seul cas fait varier le rappel de 1/14, soit 7,14 points de pourcentage.
Un autre hôpital constituerait une validation externe bien plus informative.
