# Installer, lancer et publier

## Windows : installation simple

Extrais l'archive dans un dossier, par exemple `C:\\Users\\ton_nom\\Documents\\cervical-cancer-python`.
Ouvre un terminal dans ce dossier. Utilise Python 3.12. Si `python` est introuvable
mais que le lanceur Windows est installé, remplace `python` par `py -3.12`.
Un environnement séparé évite de changer les dépendances d'autres projets.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe 01_scripts/run_project.py
```

Il n'est pas nécessaire d'activer l'environnement avec PowerShell : appeler
directement son Python suffit. Sous Linux/macOS, l'exécutable correspondant est
`.venv/bin/python`. L'installation nécessite internet ; l'analyse, ensuite, lit
le fichier déjà présent dans `02_data/raw`.

## Avec Spyder

Spyder exécute le code avec un noyau Python précis. Installer des paquets dans
un autre Python ne les rend pas disponibles dans ce noyau. Pour vérifier lequel
est utilisé, exécute dans sa console `import sys; print(sys.executable)`.
Dans cette même console IPython, `%pip install -r requirements.txt` installe les
dépendances si le répertoire de travail est le dossier du projet. Redémarre le
noyau après une mise à jour des bibliothèques puis ouvre `01_scripts/run_project.py` et lance F5.
Si ton environnement existant est incompatible avec ces versions, préfère
l'environnement séparé ci-dessus et son terminal, plutôt que de forcer une mise à jour.

Le fichier `01_scripts/src/common.py` utilise l'emplacement du projet pour trouver les données.
N'exécute pas seulement une sélection de lignes de `01_scripts/run_project.py` : exécute le fichier entier.
Ne déplace pas `01_scripts/run_project.py` seul. Les fichiers de figures sont dans `05_figures`.

## Mettre ce projet sur GitHub

Le dépôt livré est un dossier prêt à versionner. Git conserve l'historique local,
et GitHub héberge une copie distante. Sur GitHub, crée un dépôt vide nommé
`cervical-cancer-python`, sans ajouter de README ni de licence, puisque ces fichiers
sont déjà inclus ici. Depuis le dossier extrait, dans Git Bash ou un terminal avec Git :

```bash
git init -b main
git add .
git commit -m "Analyse reproductible des facteurs de risque cervicaux"
git remote add origin https://github.com/TON_COMPTE/cervical-cancer-python.git
git push -u origin main
```

Remplace `TON_COMPTE` par le compte réel et authentifie-toi avec le mécanisme proposé
par GitHub. Le projet ne demande aucun mot de passe dans les scripts. Si Git demande
un nom ou une adresse pour le commit, renseigne ta véritable identité de contribution
ou l'adresse privée GitHub que tu utilises. Le `.gitignore` exclut l'environnement
virtuel et les caches, mais conserve les figures et résultats nécessaires à la lecture.

Source : [GitHub, importer un projet local](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github).

## Cloner la copie publiée

Après publication, toi et les membres de ton groupe pourrez créer une copie locale :

```bash
git clone https://github.com/TON_COMPTE/cervical-cancer-python.git
cd cervical-cancer-python
python -m pip install -r requirements.txt
python 01_scripts/run_project.py
```

Cloner signifie copier un dépôt distant vers son ordinateur. Pour envoyer le dossier
fourni vers GitHub, l'opération est `push`. Source :
[GitHub, cloner un dépôt](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

La vérification GitHub Actions prévue lance les analyses et les contrôles sous Python
3.12. Elle n'a pas été exécutée sur un compte GitHub lors de cette livraison : les
vérifications réalisées sont locales. Aucun badge de réussite distant n'est fabriqué.

## Répartition du travail

Une personne peut vérifier les données/prétraitements, une autre les modèles et
métriques, une autre le clustering et l'oral. C'est une proposition d'organisation,
pas une attribution de contributions déjà réalisées. Dans les commits et le rendu,
décrivez ce que chacun a réellement vérifié, compris ou modifié.
