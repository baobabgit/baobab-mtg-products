# 09_product_reference_instance_split — Séparation référence produit / instance physique

## Objectif

Refondre le modèle pour distinguer clairement ce qu’est un produit commercial (`ProductReference`) et l’exemplaire physique réellement possédé ou manipulé (`ProductInstance`).

Cette séparation est nécessaire parce que plusieurs produits physiques peuvent partager le même code-barres commercial, le même nom, le même set, le même type et le même code de production.

## Branche de développement

`feature/product-reference-instance-split`

## Dépendances

- 01_product_reference_model
- 02_registration_and_scan_workflow
- 07_query_services_and_public_api

## Périmètre

- Créer `ProductReference` avec identifiant de référence, nom, image, type, set et code-barres commercial éventuel.
- Créer le value object `ProductReferenceId`.
- Adapter `ProductInstance` pour référencer une `ProductReference` via `reference_id`.
- Conserver `internal_id` comme seul identifiant unique obligatoire de l’instance physique.
- Clarifier la place des informations redondantes éventuelles `product_type` et `set_code` dans `ProductInstance`.
- Adapter les exceptions produit existantes ou créer des exceptions dédiées aux références.
- Adapter les services de consultation pour retourner, si nécessaire, référence + instance.
- Mettre à jour les exports publics du package.
- Mettre à jour la documentation d’usage.

## Hors périmètre

- Implémentation concrète de base de données.
- Déconditionnement de contenant.
- Ouverture et traçabilité des cartes.
- Interface graphique de saisie des images ou noms.

## Règles métier

- Une `ProductReference` ne représente jamais un objet physique unique.
- Une `ProductInstance` doit toujours avoir un `internal_id` unique.
- Une `ProductInstance` doit pouvoir référencer une `ProductReference` partagée par plusieurs instances.
- Le code-barres commercial doit rester au niveau de la référence ou d’un mapping de référence, pas au niveau identifiant unique de l’instance.
- Une référence produit peut exister avant toute instance physique.
- Une instance physique ne doit pas être créée sans référence résolue, sauf si un état transitoire explicite est prévu.

## Livrables attendus

- `ProductReference`.
- `ProductReferenceId`.
- `ProductReferenceRepositoryPort` ou adaptation du port existant.
- Adaptation de `ProductInstance`.
- Exceptions dédiées.
- Tests unitaires du modèle.
- Documentation mise à jour.

## Critères d'acceptation

- Deux `ProductInstance` peuvent référencer la même `ProductReference`.
- Le même code-barres commercial peut conduire à une même référence sans bloquer la création d’une nouvelle instance.
- Les services de consultation permettent d’obtenir les informations lisibles de référence associées à une instance.
- Les tests existants sont adaptés sans masquer les régressions métier.
- Les exports publics restent cohérents et documentés.
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
- couverture minimale attendue : `95%` ;
- journal de développement dans `docs/dev_diary.md` ;
- évolution du `README.md` et du `CHANGELOG.md` si nécessaire ;
- commits au format Conventional Commits ;
- travail sur une branche dédiée ;
- à la fin : si tests, qualité et contraintes sont OK, ouvrir une Pull Request puis la merger sur `main`.
