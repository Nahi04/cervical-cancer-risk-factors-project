# Dictionnaire des 36 variables

Le nom technique est conservé exactement. Pour les binaires, 0/1 est le codage
enregistré ; un zéro ne prouve pas une absence clinique lorsque le protocole de
mesure n'est pas précisé. Les nombres d'absences décrivent le fichier brut, avant
la règle appliquée aux deux âges incohérents. Toutes les variables binaires sont
contrôlées sur les valeurs observées.

Sources : [UCI](https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors)
et inspection directe du CSV. Les unités/chronologies non documentées restent
signalées. `02_data/dictionary.csv` ajoute minimum, maximum, type et rôle en clustering.

| variable | definition | missing_n | role_supervise | choix |
| --- | --- | --- | --- | --- |
| Age | Âge déclaré (ans) | 0 | Prédicteur candidat | Numérique ; âge conservé |
| Number of sexual partners | Nombre déclaré de partenaires sexuels | 26 | Prédicteur candidat | Numérique ; log1p |
| First sexual intercourse | Âge déclaré au premier rapport (ans) | 7 | Prédicteur candidat | Numérique ; âge conservé |
| Num of pregnancies | Nombre de grossesses | 56 | Prédicteur candidat | Numérique ; log1p |
| Smokes | Indicateur de tabagisme | 13 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| Smokes (years) | Durée de tabagisme (ans) | 13 | Prédicteur candidat | Numérique ; log1p |
| Smokes (packs/year) | Mesure de consommation libellée packs/year ; ne pas assimiler sans preuve à des paquets-années | 13 | Prédicteur candidat | Numérique ; log1p |
| Hormonal Contraceptives | Indicateur de contraception hormonale | 108 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| Hormonal Contraceptives (years) | Durée de contraception hormonale (ans) | 108 | Prédicteur candidat | Numérique ; log1p |
| IUD | Indicateur de dispositif intra-utérin (DIU) | 117 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| IUD (years) | Durée d'utilisation du DIU (ans) | 117 | Prédicteur candidat | Numérique ; log1p |
| STDs | Indicateur d'infections sexuellement transmissibles (IST) | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs (number) | Nombre d'IST déclaré | 105 | Prédicteur candidat | Numérique ; log1p |
| STDs:condylomatosis | Indicateur de condylomatose | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:cervical condylomatosis | Indicateur de condylomatose cervicale | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:vaginal condylomatosis | Indicateur de condylomatose vaginale | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:vulvo-perineal condylomatosis | Indicateur de condylomatose vulvo-périnéale | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:syphilis | Indicateur de syphilis | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:pelvic inflammatory disease | Indicateur de maladie inflammatoire pelvienne | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:genital herpes | Indicateur d'herpès génital | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:molluscum contagiosum | Indicateur de molluscum contagiosum | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:AIDS | Indicateur de sida | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:HIV | Indicateur d'infection par le VIH | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:Hepatitis B | Indicateur d'hépatite B | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs:HPV | Indicateur d'HPV dans le bloc IST | 105 | Prédicteur candidat | Binaire ; mode ; constante retirée dans chaque apprentissage |
| STDs: Number of diagnosis | Nombre de diagnostics d'IST | 0 | Prédicteur candidat | Numérique ; log1p |
| STDs: Time since first diagnosis | Délai depuis le premier diagnostic d'IST ; unité non explicitée par la fiche | 787 | Exclue | Très incomplet ; sens ambigu sans diagnostic |
| STDs: Time since last diagnosis | Délai depuis le dernier diagnostic d'IST ; unité non explicitée par la fiche | 787 | Exclue | Très incomplet ; sens ambigu sans diagnostic |
| Dx:Cancer | Diagnostic de cancer enregistré ; chronologie insuffisamment documentée | 0 | Exclue | Chronologie du diagnostic non garantie |
| Dx:CIN | Diagnostic de néoplasie intraépithéliale cervicale enregistré ; stade non fourni | 0 | Exclue | Chronologie du diagnostic non garantie |
| Dx:HPV | Diagnostic d'HPV enregistré ; différent du champ HPV du bloc IST | 0 | Exclue | Chronologie du diagnostic non garantie |
| Dx | Indicateur de diagnostic dont la définition détaillée n'est pas fournie | 0 | Exclue | Chronologie du diagnostic non garantie |
| Hinselmann | Résultat binaire de l'examen de Hinselmann | 0 | Exclue | Autre résultat d'examen |
| Schiller | Résultat binaire de l'examen de Schiller | 0 | Exclue | Autre résultat d'examen |
| Citology | Résultat binaire de cytologie, orthographié Citology dans le CSV | 0 | Exclue | Autre résultat d'examen |
| Biopsy | Résultat binaire de biopsie ; détail histologique non fourni | 0 | Cible unique | Cible |
