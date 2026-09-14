# Comprendre les données avant de calculer

## Ce que représente le tableau

Une ligne représente un dossier de patiente. Une colonne décrit une information
recueillie ou un résultat d'examen. Le fichier contient 858 lignes et 36 colonnes.
Ces 36 colonnes ne sont pas 36 prédicteurs indépendants : quatre sont des résultats
d'examens. Le projet en choisit un seul, `Biopsy`, comme cible.

Les données proviennent du jeu UCI collecté à l'Hospital Universitario de Caracas,
au Venezuela. Ce n'est pas un échantillon représentatif de toutes les femmes ni
un suivi de la population française. UCI signale notamment des refus de réponse
liés à la confidentialité. Le fichier ne fournit ni date de visite ni identifiant
de patiente exploitable. On ne peut donc pas estimer un risque à cinq ans, faire
une prévision temporelle, ou contrôler des visites répétées par identifiant.

Source : [fiche UCI et citation du jeu](https://doi.org/10.24432/C5Z310).

## La question biologique et la question statistique

La question biologique est : les caractéristiques recueillies apportent-elles
une information permettant de distinguer les dossiers ayant une biopsie positive ?
La question statistique correspondante est une **classification binaire**.
`y = 0` correspond au codage négatif et `y = 1` au codage positif de `Biopsy`.
La granularité histologique n'est pas fournie : ne pas transformer automatiquement
« biopsie positive » en « cancer invasif confirmé ».

La source identifie quatre cibles : `Hinselmann`, `Schiller`, `Citology` et `Biopsy`.
Le CSV écrit bien `Citology` alors que la documentation écrit parfois `Cytology`.
Le projet conserve les noms du fichier pour éviter les erreurs de colonnes.
Leur positivité peut diverger. Nous ne les fusionnons pas et nous ne les utilisons
pas pour expliquer une biopsie dans le scénario avant examens retenu.

Le contexte biologique inclut le rôle d'une infection persistante par un HPV à haut
risque. Mais le champ `STDs:HPV` du CSV n'est pas une mesure longitudinale de cette
persistance, et son zéro ne démontre pas l'absence d'infection. Il faut distinguer
ce qu'établit la littérature et ce que contient réellement ce tableau.
Source : [OMS, papillomavirus et cancer](https://www.who.int/fr/news-room/fact-sheets/detail/human-papilloma-virus-and-cancer).

## Pourquoi les types comptent

`Age` et les durées sont numériques. Le nombre de grossesses et le nombre de
partenaires sont des comptes. `Smokes`, `IUD` et les champs d'IST spécifiques sont
des indicateurs binaires 0/1. Les valeurs manquantes, écrites `?`, ne sont ni des
zéros ni une troisième classe. Dans pandas, elles deviennent `NaN`.

Une colonne binaire peut apparaître en `float64` parce que `NaN` coexiste avec
0,0 et 1,0. Son sens reste binaire. Inversement, certaines annotations de types
UCI sont sommaires : les durées de tabagisme comportent effectivement des valeurs
numériques. C'est pourquoi notre dictionnaire distingue le sens de la variable
et son stockage informatique.

## Les constats exacts

- `Biopsy` : 55 positifs et 803 négatifs, soit 6,41 % de positifs.
- Deux délais depuis diagnostic d'IST : 787 absences chacun, soit 91,72 %.
- `STDs:cervical condylomatosis` et `STDs:AIDS` : uniquement des zéros observés,
  avec 105 absences chacun. « Constante observée » ne signifie pas absence prouvée chez toutes.
- 23 lignes sont des répétitions exactes de lignes précédentes sur les 36 colonnes.
- Deux incohérences : âge 23 avec premier rapport 27 ; âge 14 avec premier rapport 16.
- Supprimer toute ligne contenant une absence sur les 36 colonnes ne laisserait
  que 59 dossiers. Sur les 26 prédicteurs retenus après nettoyage, il en resterait 668.

Les valeurs ci-dessus viennent de `04_results/tables/01_*.csv`, pas d'une simulation.
Le dictionnaire complet est dans [02_dictionnaire_variables.md](02_dictionnaire_variables.md).

## Lire le code d'import

```python
raw = pd.read_csv("02_data/raw/cervical_cancer.csv", na_values="?")
clean = raw.copy()
impossible = clean["First sexual intercourse"] > clean["Age"]
clean.loc[impossible, "First sexual intercourse"] = np.nan
```

La première ligne lit le CSV et reconnaît les absences. La deuxième protège la
source. La troisième fabrique un masque vrai/faux pour les deux incohérences.
La dernière rend le premier âge sexuel indisponible pour ces lignes. Ce choix
ne prétend pas connaître la valeur correcte ni prouver que seul ce champ est faux.
Les numéros de lignes CSV, en-tête inclus, sont 314 et 814.

Le fichier brut reste identique octet pour octet à la pièce jointe. Le fichier
dans l'archive fournie était également identique au CSV joint. L'empreinte SHA-256
figure dans `02_data/README.md` et `01_audit.json` pour rendre cette vérification possible.
