# Publication d’une release — baobab-mtg-products

Ce document décrit les contrôles à effectuer avant de taguer une version (ex. `v1.0.0`) et de publier sur PyPI.

## Intégration continue

Sur chaque **push** et chaque **pull_request** vers le dépôt, le workflow **GitHub Actions** `.github/workflows/ci.yml` exécute, pour Python **3.10** à **3.13** :

- installation en mode éditable avec les extras de développement (`pip install -e ".[dev]"`) ;
- `pytest` ;
- `coverage run -m pytest` puis `coverage report` (seuil minimal défini par `tool.coverage.report.fail_under` dans `pyproject.toml`) ;
- `black --check .` ;
- `pylint src tests` ;
- `mypy src` ;
- `flake8 src tests` ;
- `bandit -r src` ;
- construction des artefacts (`python -m build`) ;
- contrôle des métadonnées d’artefacts (`python -m twine check dist/*`).

Une PR ne remplace pas une relecture humaine, mais la CI doit être **verte** avant de merger vers `main` et de préparer une release.

## Avant la release (local ou reprise de la CI)

1. **Branche à jour** : fusionner le travail validé sur `main`.
2. **Version** : aligner `version` dans `pyproject.toml`, le repli dans `baobab_mtg_products.__init__` (bloc `except PackageNotFoundError`) et le test `tests/.../test_init.py`.
3. **Changelog** : ajouter ou compléter une entrée datée dans `CHANGELOG.md` (Keep a Changelog + SemVer).
4. **Qualité** (depuis la racine du dépôt, environnement dev installé) :

   ```bash
   python -m pip install -e ".[dev]"
   python -m pytest
   python -m coverage run -m pytest
   python -m coverage report
   python -m black --check .
   python -m pylint src tests
   python -m mypy src
   python -m flake8 src tests
   python -m bandit -r src
   ```

   Le seuil de couverture est défini dans `pyproject.toml` (`tool.coverage.report.fail_under`).

5. **Packaging** : construire les artefacts et valider avec Twine (les outils `build` et `twine` sont inclus dans l’extra `[dev]`) :

   ```bash
   rm -rf dist
   python -m build
   python -m twine check dist/*
   ```

6. **Journal** : compléter `docs/dev_diary.md` si la release clôt une feature ou un lot de durcissement.

## Après la release

- Pousser le tag Git (`git tag -a vX.Y.Z -m "…"` puis `git push origin vX.Y.Z`).
- Publication sur PyPI (ou index privé) : suivre la procédure d’organisation (tokens, projet `twine`, etc.).

## Hors périmètre de la lib

L’exposition HTTP, l’UI, le moteur de règles du jeu et le deckbuilding restent du ressort d’autres briques ; cette lib ne publie qu’un wheel / sdist métier typé.
