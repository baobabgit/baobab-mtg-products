# 03_parent_child_relationships — Relations parent/enfant entre produits

## Objectif

Implémenter la représentation et les cas d’usage de rattachement structurel entre produits scellés.

## Branche de développement

`feature/parent-child-relationships`

## Dépendances

- 01_product_reference_model
- 02_registration_and_scan_workflow

## Périmètre

- Créer `ProductRelationship` et les types de relation utiles.
- Permettre de rattacher un booster à une display ou un bundle à ses sous-produits.
- Gérer les règles empêchant les rattachements incohérents.
- Permettre de représenter un booster indépendant sans parent.
- Historiser les événements de rattachement ou de détachement si retenu.

## Hors périmètre

- Ouverture et traçabilité du contenu.
- Publication vers la collection ou les statistiques.

## Livrables attendus

- Modèle de relation métier.
- Cas d’usage de rattachement.
- Tests unitaires des règles d’intégrité.

## Critères d'acceptation

- Les relations valides sont créées correctement.
- Les rattachements invalides sont rejetés par exceptions dédiées.
- Le modèle distingue clairement parent, enfant et produit indépendant.

## Contraintes de développement à respecter

La feature doit impérativement respecter les règles suivantes :

- développement Python orienté objet ;
- une classe par fichier ;
- arborescence source sous `src/baobab_mtg_products/` ;
- arborescence des tests miroir sous `tests/` ;
- docstrings sur toutes les API publiques ;
- annotations de type complètes ;
- exceptions métier spécifiques héritant d'une exception racine du projet ;
- configuration centralisée dans `pyproject.toml` ;
- qualité obligatoire : `black`, `pylint`, `mypy`, `flake8`, `bandit` ;
- couverture minimale attendue : `90%` ;
- journal de développement dans `docs/dev_diary.md` ;
- évolution du `README.md` et du `CHANGELOG.md` si nécessaire ;
- commits au format Conventional Commits ;
- travail sur une branche dédiée ;
- à la fin : si tests, qualité et contraintes sont OK, ouvrir une Pull Request puis la merger sur `main`.
