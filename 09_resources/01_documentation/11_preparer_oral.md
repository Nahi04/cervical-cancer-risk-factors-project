# Présenter le projet en dix minutes

Le support correspond à `06_report/presentation_orale.pdf`. La version PPTX est
modifiable. Les notes ci-dessous sont une aide à l'explication, à reformuler
avec tes propres mots après avoir compris le code. Les contributions de chacun
restent à renseigner selon le travail réellement effectué.

| Diapo | Temps | Message principal |
|---|---|---|
| 1. Question et méthodes | 0:00-0:40 | Prédire la positivité de Biopsy et explorer les profils. |
| 2. Données et déséquilibre | 0:40-1:30 | Seulement 55 biopsies positives parmi 858 dossiers. |
| 3. Prétraitement | 1:30-2:40 | Exclusions liées au scénario, imputation sans fuite. |
| 4. Validation | 2:40-3:40 | Profils groupés, développement 643, test 215. |
| 5. Modèles | 3:40-4:40 | Base, logistique L2, forêt limitée. |
| 6. Discrimination | 4:40-5:50 | Le classement des modèles en CV ne garantit pas leur test. |
| 7. Seuil et confusion | 5:50-6:55 | La forêt ne détecte que 2 des 14 positives. |
| 8. PCA | 6:55-7:55 | Deux axes gardent seulement 41,2 % de variance. |
| 9. Clustering évalué | 7:55-9:00 | Stabilité élevée, séparation modeste. |
| 10. Discussion | 9:00-10:00 | Signal fragile, profils descriptifs, validation externe nécessaire. |

## Diapo 1 : annoncer exactement la question

« Nous avons étudié des caractéristiques démographiques et médicales associées
à un résultat de biopsie. Notre objectif supervisé est de prédire la positivité
enregistrée de cette biopsie. Nous cherchons aussi des profils de patientes sans
utiliser le résultat pour construire les groupes. Nous avons volontairement retenu
deux classifieurs complémentaires et une seule méthode de clustering. »

## Diapo 2 : expliquer le piège de l'accuracy

« Le jeu comporte 858 dossiers et 36 colonnes, dont quatre résultats d'examens.
Notre cible contient 55 positives. Une réponse négative presque systématique
peut donc obtenir une accuracy élevée. C'est pourquoi nous évaluons surtout
le classement des positives avec l'average precision et la détection au seuil
retenu. Les données proviennent d'un recueil hospitalier à Caracas, et non d'un
échantillon représentatif de toutes les patientes. »

## Diapo 3 : défendre les choix de préparation

« Nous excluons les autres examens et les diagnostics Dx parce que leur disponibilité
avant la biopsie n'est pas garantie. Les deux délais d'IST ont plus de 91 % d'absences.
Deux âges au premier rapport sont incohérents et rendus manquants, sans inventer
la bonne valeur. Nous comparons moyenne et médiane sur les numériques transformés,
utilisons le mode pour les binaires et ajoutons des indicateurs d'absence. Tout
ce qui s'apprend sur des lignes reste dans les pipelines de validation. »

## Diapo 4 : expliquer les groupes et les cinq plis

« Les profils identiques restent du même côté d'un découpage. Nous ne savons pas
s'ils correspondent à des patientes différentes, donc nous les conservons sans
les disperser. Le développement contient 643 dossiers dont 41 positives. Le
test contient 215 dossiers dont 14 positives. Dans le développement, cinq plis
permettent de choisir les réglages. Chaque validation contient huit ou neuf
positives : l'incertitude reste importante. »

## Diapo 5 : expliquer ce que chaque modèle apporte

« La base ne connaît que la fréquence positive d'apprentissage. La logistique
L2 représente des effets additifs avec des coefficients pénalisés. La forêt
peut capter des seuils et interactions, mais nous limitons sa profondeur et
ses feuilles. Nous comparons aussi la pondération des classes. Il y a huit
configurations par famille, toutes sur les mêmes plis. La persistance ne serait
pas définie ici car il n'y a pas de suivi temporel des patientes. »

## Diapo 6 : présenter le résultat défavorable sans l'esquiver

« La forêt a l'AP moyenne la plus élevée en validation : 0,217. Elle est donc
choisie avant le test. Son AP test chute à 0,082, proche de 0,065 pour la base.
La légère différence forêt-base a un intervalle bootstrap incluant zéro.
Nous n'avons pas changé le découpage ou choisi un autre modèle après avoir
vu ce résultat. Il illustre la fragilité de la généralisation dans ce protocole. »

## Diapo 7 : traduire les scores en dossiers

« Le seuil de la forêt a été choisi en maximisant F2 sur des scores hors pli
du développement. Sur le test, elle repère deux positives, en manque douze et
produit vingt-huit fausses alertes. Au seuil 0,5, aucun classifieur ne détecte
de positive, malgré une accuracy de 93,5 %. Le choix du seuil change le compromis
entre erreurs, mais ne répare pas un classement des patientes peu informatif. »

## Diapo 8 : distinguer projection et clustering

« Nous avons choisi huit mesures numériques pour définir une distance compréhensible,
sans multiplier les binaires rares. La PCA est apprise sur le développement sans
Biopsy. Ses deux premiers axes ne résument que 41,2 % de variance. Le k-means est
calculé dans les huit dimensions, puis ses groupes colorent cette projection.
Nous ne déduisons pas la qualité du clustering du seul aspect visuel. »

## Diapo 9 : distinguer stabilité et séparation

« Nous comparons deux à cinq groupes et choisissons la silhouette maximale parmi
les solutions de taille minimale suffisante. Cinq est le meilleur dans cette
grille, mais se situe à sa borne. La silhouette atteint 0,247 en développement
et 0,232 sur le test : les groupes se chevauchent. L'ARI moyen de 0,954 indique
une partition stable autour des sous-échantillons testés. Les profils reflètent
notamment âge/grossesses, DIU, tabagisme et IST. Cela ne prouve pas l'existence
de classes de risque clinique. »

## Diapo 10 : conclure sur la question initiale

« Nous avons une procédure reproductible qui contrôle plusieurs sources de fuite
et rend visibles les erreurs. Les deux classifieurs ne démontrent pas une utilité
clinique dans cette évaluation. Les groupes restent descriptifs. Les priorités
seraient une meilleure définition histologique et temporelle, plus de cas positifs
et une validation indépendante. Ajouter un algorithme plus complexe ne remplace
pas ces informations. »

## Questions probables

| Question | Réponse à comprendre |
|---|---|
| Pourquoi pas Ridge ? | La cible est binaire ; la logistique est le modèle linéaire de classification choisi. |
| Pourquoi pas Dx:Cancer ? | La chronologie est insuffisamment documentée pour notre scénario avant examens. |
| Pourquoi garder les répétitions ? | Pas d'identifiant permettant d'affirmer que ce sont des doublons de patientes. Les profils restent groupés. |
| Pourquoi pas supprimer les absences ? | Sur les 36 colonnes, il ne resterait que 59 lignes, avec un risque de sélection. |
| Pourquoi pas automatiquement balanced ? | C'est un réglage à comparer ; il n'améliore pas le classement mesuré par AP dans nos plis. |
| Est-ce que F2 est un seuil médical ? | Non. C'est une préférence pédagogique pour le rappel, sans coûts cliniques estimés. |
| OOF est-il totalement indépendant ? | La ligne n'est pas utilisée pour fit du modèle qui la prédit, mais les réglages ont été sélectionnés avec ces plis. |
| Pourquoi pas changer de seed ? | Le test consulté ne doit pas servir à rechercher un tirage favorable. |
| Une silhouette de 0,247 est-elle suffisante ? | Elle traduit une séparation modeste dans cette géométrie ; aucun seuil universel ne la transforme en validation biologique. |
| Pourquoi cinq groupes ? | C'est le meilleur résultat parmi k=2 à 5, avec taille minimale de 5 % ; pas un nombre vrai prouvé. |
| Pourquoi des biopsies positives différentes par groupe ? | Association descriptive après fixation des groupes, avec de petits effectifs ; aucun usage pour choisir k. |
| Pourquoi ne pas annoncer un facteur de risque à partir des coefficients ? | Coefficients conditionnels, pénalisés et fragiles ; association et prédiction ne démontrent pas la causalité. |

Les sources sont détaillées dans [REFERENCES.md](../REFERENCES.md), notamment UCI,
OMS et la documentation scikit-learn. L'article de Fernandes et al. (2018) est
cité pour situer la question de prédiction de biopsie, sans prétendre reproduire
ses scores ni avoir utilisé un tableau de résultats non consulté.
