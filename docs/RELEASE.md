# Publication d’une release — baobab-mtg-products

Ce document résume les contrôles à effectuer avant de taguer une version (ex. `v1.0.0`).

## Avant la release

1. **Branche à jour** : fusionner le travail validé sur `main`.
2. **Version** : aligner `version` dans `pyproject.toml`, le repli dans `baobab_mtg_products.__init__` (bloc `except PackageNotFoundError`) et le test `tests/.../test_init.py`.
3. **Changelog** : ajouter une entrée datée dans `CHANGELOG.md` (Keep a Changelog + SemVer).
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

5. **Packaging** : vérifier la construction des artefacts :

   ```bash
   python -m pip install build
   python -m build
   ```

6. **Journal** : compléter `docs/dev_diary.md` si la release clôt une feature ou un lot de durcissement.

## Après la release

- Pousser le tag Git (`git tag -a vX.Y.Z -m "…"` puis `git push origin vX.Y.Z`).
- Si le package est publié sur un index PyPI (public ou privé), suivre la procédure d’organisation (tokens, projet `twine`, etc.).

## Hors périmètre de la lib

L’exposition HTTP, l’UI, le moteur de règles du jeu et le deckbuilding restent du ressort d’autres briques ; cette lib ne publie qu’un wheel / sdist métier typé.
