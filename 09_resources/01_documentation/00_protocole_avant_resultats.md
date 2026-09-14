# Protocole arrêté avant de calculer les performances

Le code et ce protocole fixent les choix ci-dessous avant l'ouverture du test.
L'audit global a déjà servi à contrôler le format, les absences et les incohérences.
Il ne s'agit donc pas d'un protocole préenregistré avant l'accès aux données.

1. Cible unique : `Biopsy` (0/1), aucune cible fabriquée en combinant les examens.
2. Conserver les 858 lignes ; grouper les profils identiques pour les séparations.
3. Rendre manquant l'âge au premier rapport lorsqu'il dépasse l'âge déclaré.
   On ne sait pas lequel des deux âges est erroné ; cette convention sera signalée.
4. Exclure les trois autres résultats d'examen et les quatre variables de diagnostic
   `Dx`. Le moment de leur disponibilité n'est pas suffisamment documenté pour
   un modèle utilisable avant les examens. Ce n'est pas une preuve de fuite effective.
5. Exclure les deux délais depuis diagnostic d'IST : 787 absences sur 858,
   sens ambigu chez les personnes sans diagnostic. Ne jamais remplacer ces absences par zéro.
6. Conserver 26 prédicteurs candidats ; retirer les colonnes constantes dans chaque
   pipeline. Pas de sélection univariée sur la cible ; L2 régularise la logistique.
7. Appliquer `log1p` aux huit comptes/durées retenus ; les deux âges restent bruts.
8. Imputer les numériques par médiane ou moyenne **dans l'espace transformé**,
   et les binaires par le mode. Ajouter sept indicateurs d'absence par domaine.
9. Découpage par `StratifiedGroupKFold(4, shuffle=True, random_state=42)` :
   premier pli réservé (~25 %). Dans le développement, cinq plis par groupes,
   graine 43. Aucun groupe partagé entre apprentissage et validation/test.
10. Base : `DummyClassifier(strategy="prior")`, seuil 0,5.
11. Logistique L2 : C = 0,1 ou 1 ; forêt : 200 arbres, profondeur 5,
    feuilles minimales de 5 ou 15. Pour chacune : deux imputations, pondération
    absente ou `balanced`. Soit huit configurations par famille, pas huit algorithmes.
12. Critère principal : average precision (AP) moyenne en validation croisée.
    Choisir la famille entre les deux classifieurs avant d'évaluer le test.
    La base garde son rôle de référence, même si elle surpasse un classifieur.
13. Seuil de chaque classifieur : maximum du F2 sur les prédictions hors pli du
    développement, après sélection des réglages. Présenter aussi le seuil 0,5.
    F2 est un choix pédagogique donnant davantage de poids au rappel, pas un
    seuil recommandé pour une décision médicale. Ces scores OOF ne constituent
    pas une validation indépendante du réglage ni du seuil.
14. Test : AP, ROC-AUC, Brier, accuracy, balanced accuracy, rappel, spécificité,
    précision, F1, F2, MCC et matrice de confusion. Bootstrap par groupes 1 000 fois
    pour le classifieur choisi ; différences appariées d'AP avec les comparateurs.
15. Sensibilité descriptive : retirer les indicateurs d'absence en CV, sans
    nouvelle recherche ni changement du modèle choisi.
16. Non supervisé : huit mesures numériques fixées dans `CLUSTER`, log1p sur six,
    médiane et standardisation apprises sur le développement. Pas de cible dans X.
17. k-means sur les **huit dimensions**, 20 initialisations, k de 2 à 5.
    Choisir la meilleure silhouette parmi les solutions dont chaque groupe
    contient au moins 5 % du développement. Ce repère pragmatique évite les
    groupes minuscules ; ce n'est pas un seuil biologique. Arrêter si aucun k admissible.
18. Évaluer inertie, silhouette, Calinski-Harabasz, Davies-Bouldin, stabilité sur
    20 sous-échantillons de 80 % des groupes de profils, puis silhouette du test
    affecté aux centres appris. Sensibilités : moyenne et écrêtage aux quantiles
    1/99 %, uniquement pour examiner la dépendance du résultat au prétraitement.
19. PCA : variance expliquée, coefficients des axes, erreur de reconstruction 2D ;
    affichage des groupes dans les deux premiers axes. Aucune PCA supervisée.
20. Décrire après fixation des groupes les biopsies et absences par groupe.
    Ne jamais choisir k pour séparer les biopsies. Les groupes n'ont pas de labels
    vrais connus et ne sont pas des catégories médicales validées.

Sources méthodologiques : [bonnes pratiques](https://scikit-learn.org/1.8/common_pitfalls.html),
[validation par groupes](https://scikit-learn.org/1.8/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html),
[UCI](https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors).
