# Nettoyer et choisir les variables sans fabriquer du signal

## Ordre des opérations

Il faut séparer les règles déterministes des paramètres appris. Lire `?` comme
manquant, appliquer une règle de cohérence par ligne, choisir des colonnes pour
un scénario donné et calculer `log(1+x)` ne nécessitent aucune information sur
la distribution des autres patientes. Ces opérations peuvent précéder le split.
Une médiane, une moyenne, un écart-type et la détection d'une constante dépendent
du sous-ensemble observé : le pipeline les réapprend dans chaque pli.

Les graphiques globaux servent à l'audit du fichier. Les corrélations, distributions
détaillées, choix de modèles et choix de k utilisent le développement seulement.
Le test sert à évaluer les procédures arrêtées. Source :
[scikit-learn, éviter les fuites](https://scikit-learn.org/1.8/common_pitfalls.html).

## Dix colonnes exclues du modèle supervisé

| Colonnes | Pourquoi |
|---|---|
| `Biopsy` | C'est la réponse à prédire. |
| `Hinselmann`, `Schiller`, `Citology` | Résultats d'autres examens, exclus du scénario avant examens. |
| `Dx:Cancer`, `Dx:CIN`, `Dx:HPV`, `Dx` | Le moment du diagnostic n'est pas assez documenté. Exclusion prudente. |
| Deux champs `Time since ... diagnosis` | Plus de 91 % d'absences et ambiguïté de sens sans diagnostic antérieur. |

Il reste 26 colonnes candidates : 10 numériques et 16 binaires. Le pipeline retire
ensuite les constantes observées dans l'apprentissage. Une constante ne peut pas
séparer les dossiers. Les variables rares mais non constantes restent candidates :
les exclure uniquement parce qu'elles sont rares pourrait éliminer un signal utile.
En contrepartie, leurs coefficients seront fragiles et ne permettront aucune
conclusion biologique autonome.

Les sept indicateurs d'absence portent sur partenaires, premier rapport, grossesses,
tabagisme, contraception hormonale, DIU et IST. Ils indiquent qu'une réponse manque.
On ne répète pas l'indicateur d'absence des multiples champs d'IST qui manquent
ensemble. `VarianceThreshold` s'applique aussi aux indicateurs.

## Pourquoi ne pas lancer une sélection de variables automatique ?

Le développement ne contient que 41 biopsies positives. Tester un grand nombre
de combinaisons de variables risquerait d'adapter le modèle au bruit. Nous préférons
une sélection par le scénario d'utilisation, suivie d'une régularisation L2 pour
la logistique et de limites de profondeur/taille de feuilles pour la forêt.
L2 réduit les coefficients ; elle ne met pas généralement les variables à zéro.
Ce projet ne prétend donc pas avoir trouvé le « meilleur sous-ensemble de gènes »
ou de facteurs. Il distingue inclusion motivée et importance après apprentissage.

## Valeurs extrêmes : observer avant de supprimer

Un âge de 84 ans ou 28 partenaires est inhabituel mais pas logiquement impossible.
Nous les conservons. Les seuils de boîte à moustaches, calculés avec 1,5 fois
l'écart interquartile, servent à compter les extrêmes dans le développement.
Ils ne définissent pas une erreur. Pour une durée souvent nulle, l'écart
interquartile peut être nul : toute durée positive peut alors être signalée.
La supprimer reviendrait à retirer les personnes exposées.

## Pourquoi log1p ?

Les durées et comptes sont asymétriques, avec beaucoup de zéros et quelques valeurs
élevées. `log1p(x)` calcule `ln(1+x)` : zéro reste zéro, les grandes valeurs sont
comprimées. Le code transforme huit colonnes de `NUM[2:]`. `Age` et l'âge au premier
rapport restent dans leurs unités initiales avant standardisation.

Pour la logistique, cela impose une relation additive dans l'espace transformé.
C'est une hypothèse pratique, pas la preuve d'une relation logarithmique biologique.
Pour k-means, cela réduit l'influence des grandes durées sur les distances.
La forêt en a moins besoin, car elle divise selon l'ordre des valeurs ; réutiliser
les mêmes entrées simplifie la comparaison. L'ordre est préservé par log1p.

```python
x = clean[FEATURES].copy()
x[LOG] = np.log1p(x[LOG])
```

La liste `LOG` ne contient aucun champ binaire. Il n'y a ni transformation de la
cible ni transformation estimée sur le test. La moyenne d'imputation est ensuite
une moyenne **des valeurs transformées**, pas la moyenne brute suivie d'un log.

## Standardiser selon la méthode

La standardisation calcule `(x - moyenne_apprentissage) / écart_type_apprentissage`.
Elle met les numériques sur une échelle comparable pour la pénalisation logistique
et pour les distances de k-means. Les binaires restent 0/1 en supervisé. Cela évite
qu'un indicateur très rare soit amplifié par division par un petit écart-type.
La forêt ne reçoit pas de standardisation, car ses coupures n'en ont pas besoin.

Le non supervisé utilise huit variables numériques. Retirer `Smokes (packs/year)`
et `STDs: Number of diagnosis` évite une partie de la répétition du tabagisme et
des IST. Les corrélations résiduelles, notamment âge/grossesses, restent visibles
et doivent limiter l'interprétation de la distance.
