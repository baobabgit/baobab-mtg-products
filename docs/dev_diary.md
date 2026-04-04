# Journal de développement — baobab-mtg-products

Les entrées sont classées par **date et heure décroissantes** (les plus récentes en premier).

## 2026-04-04

### Modifications

- Création de la branche `feature/project-bootstrap` et du socle `src/baobab_mtg_products/` avec sous-packages `exceptions`, `domain`, `ports`, `use_cases`.
- Ajout de `pyproject.toml` (setuptools, pytest, coverage avec `data_file` et rapports sous `docs/tests/coverage/`, black, pylint, mypy strict, flake8 via `flake8-pyproject`, bandit).
- Implémentation de `BaobabMtgProductsException`, `DomainEntity`, `CollectionPort`, `StatisticsPort`, `UseCase` et tests miroirs associés.
- Rédaction de `README.md`, `CHANGELOG.md`, `LICENSE`, `docs/tests/coverage/README.md` et mise à jour de `.gitignore` pour les artefacts de couverture.
- Ajout du marqueur `py.typed` pour indiquer un package typé.

### Buts

- Satisfaire la feature `00_project_bootstrap` : projet installable, outillage qualité vert, couverture ≥ 90 %, structure conforme au cahier des charges.

### Impact

- Base prête pour les features métier (produits, scans, relations, ouverture) sans couplage API / front / rules engine / deckbuilder.
