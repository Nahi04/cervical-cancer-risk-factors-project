# PCA et clustering : explorer sans confondre groupes et diagnostic

## Pourquoi séparer cette question du supervisé ?

En supervisé, on connaît la cible et on cherche à la prédire. En non supervisé,
on cherche des ressemblances entre les lignes à partir des variables seulement.
`Biopsy` n'entre ni dans l'imputation du clustering, ni dans la PCA, ni dans
k-means, ni dans la sélection de k. Les résultats de biopsie ne sont examinés
par groupe qu'après avoir arrêté la partition.

## Un espace de huit mesures numériques

Les huit colonnes sont âge, âge au premier rapport, nombre de partenaires,
nombre de grossesses, années de tabagisme, années de contraception hormonale,
années de DIU et nombre d'IST. Elles couvrent des dimensions complémentaires du
profil. Les comptes et durées subissent log1p ; les deux âges restent bruts.
Une médiane et une standardisation sont apprises sur le développement.

Les binaires rares ne sont pas inclus dans la distance. Standardiser une colonne
avec une seule valeur 1 pourrait lui donner une très grande influence. Répéter
plusieurs descriptions d'un même domaine compterait ce domaine plusieurs fois.
Cette sélection numérique rend k-means plus facile à défendre, mais elle ne
représente pas l'intégralité du dossier médical. Il ne faut pas l'appeler
« clustering optimal de toutes les données mixtes ».

## PCA : changer de repère

La PCA construit des axes, chacun étant une combinaison des huit entrées.
PC1 capte la plus grande variance possible ; PC2 en capte une autre, orthogonale
à PC1. La PCA cherche la variance, pas la séparation entre biopsies et pas
nécessairement la pertinence biologique.

```python
pca = PCA().fit(zd)
pc_dev = pca.transform(zd)
pc_test = pca.transform(zt)
```

`zd` est la matrice de développement après prétraitement. Le test `zt` est
transformé avec les mêmes paramètres. Ici PC1 explique 24,05 % et PC2 17,15 %,
soit 41,19 % ensemble. Il faut sept composantes pour dépasser 90 %.
La vue 2D laisse donc de côté beaucoup de variabilité.

La table `03_pca_axes.csv` contient les coefficients des axes, ou directions
principales, pas des corrélations variable/axe déjà normalisées. Pour reconstruire
les données avec deux axes, on projette en sens inverse et mesure l'erreur moyenne
dans l'espace standardisé. Le résultat est dans `03_pca_reconstruction.csv`.
La PCA n'a ni accuracy ni rappel puisqu'elle ne prédit pas une classe.

Source : [PCA](https://scikit-learn.org/1.8/modules/decomposition.html#pca).

## K-means : attribuer les lignes à des centres

K-means alterne l'affectation de chaque patiente au centre le plus proche et le
recalcul des centres. Il minimise la somme des distances euclidiennes au carré
aux centres, appelée inertie. Nous l'appliquons sur **les huit dimensions**, et
nous colorons ensuite la PCA avec ses groupes. Le clustering ne se fait pas
sur les deux axes qui ne gardent que 41,19 % de variance.

```python
model = KMeans(n_clusters=5, n_init=20, random_state=42)
labels = model.fit_predict(zd)
test_labels = model.predict(zt)
```

Ce court exemple illustre la solution retenue. Le script réel compare d'abord
k=2, 3, 4 et 5. `n_init=20` essaye vingt initialisations des centres pour réduire
la dépendance à un mauvais départ. `predict` affecte le test aux centres existants,
sans déplacer ces centres.

## Comment choisir k sans vraie étiquette de groupe ?

La silhouette compare, pour chaque ligne, sa distance moyenne aux membres de son
groupe et celle au groupe voisin le plus proche. Elle se situe entre -1 et 1.
Une valeur voisine de zéro signale un chevauchement. Nous retenons la silhouette
maximale parmi les k dont le plus petit groupe représente au moins 5 % du
développement. Le seuil de taille est pragmatique, pas biologique.

Nous montrons aussi l'inertie, Calinski-Harabasz (plus élevé : meilleure séparation
relative) et Davies-Bouldin (plus faible : meilleure séparation relative).
Ces indices ne sont pas des preuves d'existence de catégories naturelles.
L'inertie diminue mécaniquement lorsqu'on ajoute des groupes. Ici la silhouette
augmente de k=2 à k=5 : le maximum se situe à la borne de la grille. Nous disons
donc « meilleur k parmi 2 à 5 », pas « le nombre vrai est cinq ».

Source : [évaluation du clustering](https://scikit-learn.org/1.8/modules/clustering.html#clustering-performance-evaluation).

## Évaluer la stabilité et le transfert

Nous réapprenons imputation, échelle et k-means sur vingt sous-échantillons
contenant 80 % des groupes de profils du développement. Chaque nouvelle procédure
réaffecte toutes les lignes de développement. L'ARI compare ces affectations
à la partition de référence en ignorant les numéros arbitraires des groupes.
ARI=1 signifie même partition ; ARI proche de 0, accord proche d'un repère aléatoire.
Il ne compare pas les groupes à `Biopsy`.

L'ARI moyen est 0,9536. C'est une stabilité autour de ces données, pas une
validation indépendante : les sous-échantillons se recouvrent et la référence
utilise tout le développement. La silhouette du test affecté est 0,2318,
contre 0,2475 en développement. Elle montre que la séparation reste modeste.
Nous ne comparons pas directement les valeurs brutes de Calinski-Harabasz entre
développement et test car leurs tailles diffèrent.

Changer la médiane en moyenne donne un ARI de 0,9353 ; écrêter les valeurs aux
quantiles 1/99 % donne 0,9506. Ces vérifications indiquent une partition relativement
stable au prétraitement testé. Elles n'autorisent pas à effacer les extrêmes de
l'analyse principale ni à parler de sous-types de cancer.

## Décrire les groupes

Les médianes observées permettent de reconnaître des profils d'âge/grossesses,
de DIU, de tabagisme et d'IST. Les numéros n'ont aucun ordre de gravité. Une médiane
se calcule ici sur les réponses disponibles, avec son effectif observé exporté.
Les centres de la heatmap sont, eux, des moyennes dans l'espace transformé et
imputé. Ce ne sont pas les mêmes objets.

Les fractions de biopsies positives par groupe sont descriptives. Le groupe 5
compte 8/46 positives en développement mais 2/25 dans le test. Ces faibles
effectifs et cette variation empêchent de lui attribuer une classe de risque
clinique validée. Des pratiques de recueil et les valeurs manquantes peuvent aussi
contribuer aux groupes ; leurs taux d'absence sont exportés séparément.
