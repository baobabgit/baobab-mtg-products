# Couverture de tests

La configuration **coverage** du projet est définie dans `pyproject.toml` (`[tool.coverage.*]`).

## Emplacement des fichiers

- Fichier de données SQLite : `docs/tests/coverage/.coverage`
- Rapport HTML : `docs/tests/coverage/html/`
- Rapport XML : `docs/tests/coverage/coverage.xml`

Ces chemins respectent la contrainte projet : artefacts de couverture regroupés sous `docs/tests/coverage/`.

## Commandes usuelles

```bash
coverage run -m pytest
coverage report
coverage html
coverage xml
```

Le seuil minimal de couverture est fixé à **90 %** (`fail_under` dans `pyproject.toml`).

Les fichiers générés sont ignorés par Git (voir `.gitignore`).
