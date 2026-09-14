# Glossaire pour lire le projet

| Mot | Explication |
|---|---|
| Échantillon | Une ligne utilisée dans l'analyse, ici un dossier de patiente. |
| Variable / feature | Une colonne d'information donnée au modèle. |
| Cible / y | La réponse à prédire, ici Biopsy. |
| Classification | Prédire une catégorie, ici négative ou positive. |
| Régression | Dans le nom « logistique », modèle de probabilité d'une classe ; la régression numérique ordinaire prédit une quantité continue. |
| Prétraitement | Préparer les entrées avant l'algorithme. |
| Imputation | Remplacer une absence pour permettre un calcul, sans la transformer en observation réelle. |
| Standardisation | Centrer et diviser par un écart-type appris. |
| Fuite de données | Une information indisponible au moment prévu, ou venant de l'évaluation, influence l'apprentissage. |
| Pipeline | Suite d'opérations qui s'apprennent ensemble sur le bon sous-ensemble. |
| Paramètre | Valeur apprise pendant fit, par exemple un coefficient. |
| Hyperparamètre | Réglage choisi avant fit, par exemple C ou profondeur. |
| Validation croisée | Répéter apprentissage/validation en changeant les lignes laissées de côté. |
| Pli / fold | Une partie de ce découpage. |
| OOF | Prédiction hors pli : le modèle qui prédit une ligne ne l'a pas utilisée pour fit. |
| Test réservé | Sous-ensemble consulté après les décisions de modélisation. |
| Surapprentissage | Le modèle s'adapte aux particularités de l'apprentissage qui se reproduisent mal ailleurs. |
| Régularisation | Contraindre la complexité des paramètres pour limiter le surapprentissage. |
| Prévalence observée | Fraction de positives dans l'échantillon considéré, pas forcément dans la population. |
| Seuil | Score minimal pour annoncer une classe positive. |
| Calibration | Concordance entre scores et fréquences réellement observées. |
| Bootstrap | Rééchantillonner avec remise pour explorer l'incertitude. |
| PCA / ACP | Construire des axes qui résument la variance des données. |
| Variance expliquée | Fraction de variation portée par un axe ou un groupe d'axes. |
| Clustering | Répartir les lignes selon leur similarité, sans fournir la cible. |
| Centroïde | Moyenne des coordonnées d'un groupe dans l'espace du clustering. |
| Inertie | Somme des distances au carré aux centres de groupes. |
| Silhouette | Évalue la proximité au groupe attribué par rapport aux groupes voisins. |
| ARI | Accord ajusté entre deux partitions, invariant au nom des groupes. |
| Association | Deux variables évoluent ensemble ; cela ne prouve pas que l'une cause l'autre. |
| Validation externe | Évaluer sur une source de données indépendante, par exemple un autre hôpital. |

Pour les métriques, consulter [le guide dédié](07_metriques_et_graphiques.md).
Référence : [glossaire scikit-learn](https://scikit-learn.org/1.8/glossary.html).
