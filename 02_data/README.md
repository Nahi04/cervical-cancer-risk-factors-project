# Données et provenance

`raw/cervical_cancer.csv` est une copie inchangée du fichier fourni :
`11_Cervical_Cancer_Risk_Factors.csv`. Le CSV contenu dans le ZIP joint était
identique octet pour octet à ce fichier. Aucun tableau clinique supplémentaire
n'a été ajouté. L'identité binaire avec un téléchargement UCI effectué aujourd'hui
n'est pas revendiquée : la provenance est celle du jeu documenté correspondant.

- Forme : 858 lignes, 36 colonnes.
- Valeur manquante d'origine : `?`.
- SHA-256 : `8df193ad5c9ff4288fb4c401eef70dcd2cbda404ce7f82ac74c68cfc960ab063`.
- Source : Fernandes, K., Cardoso, J., & Fernandes, J. (2017),
  [Cervical Cancer (Risk Factors)](https://doi.org/10.24432/C5Z310), UCI.
- Licence des données : [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
  annoncée sur la [fiche UCI](https://archive.ics.uci.edu/dataset/383/cervical+cancer+risk+factors).

`dictionary.csv` décrit les colonnes dans les termes permis par la documentation
et le contenu observé. Les champs insuffisamment décrits y sont signalés.

`processed/split.csv` indique la ligne d'origine, le groupe de profil, le rôle
développement/test et le pli interne. Il ne contient aucune imputation globale.
Le nettoyage est reproduit en mémoire par `load_data` ; les médianes/moyennes
doivent être réapprises dans chaque pli, d'où l'absence d'un unique CSV « totalement
prétraité » à utiliser directement en validation croisée.

La source ne contient pas d'identifiant permettant d'affirmer que deux profils
identiques sont la même patiente. Le groupement conservateur évite de placer ces
profils des deux côtés d'une séparation, sans effacer les dossiers.
