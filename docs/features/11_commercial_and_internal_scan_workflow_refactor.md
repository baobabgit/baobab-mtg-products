# 11_commercial_and_internal_scan_workflow_refactor — Refonte des workflows de scan commercial et interne

## Objectif

Corriger le workflow de scan pour que le code-barres commercial résolve une référence produit, tandis que le code-barres interne retrouve une instance physique précise.

Le scan commercial ne doit plus considérer qu’un produit déjà connu avec le même EAN correspond automatiquement au même exemplaire physique.

## Branche de développement

`feature/scan-workflow-reference-instance-refactor`

## Dépendances

- 09_product_reference_instance_split
- 10_physical_instance_creation_and_production_code
- 02_registration_and_scan_workflow
- 05_history_and_event_log

## Périmètre

- Adapter `RegisterProductByCommercialScanUseCase`.
- Adapter `RegisterProductByInternalScanUseCase`.
- Créer ou adapter `ResolveProductReferenceFromCommercialBarcodeUseCase`.
- Définir clairement les résultats possibles d’un scan commercial : référence connue, référence inconnue, référence ambiguë, nouvelle instance créée.
- Définir clairement les résultats possibles d’un scan interne : instance trouvée, code inconnu, code invalide.
- Adapter `BarcodeResolutionPort` si nécessaire.
- Adapter `RegistrationScanResult` et `RegistrationScanOutcome` si nécessaire.
- Ajouter les événements de scan commercial et de scan interne.
- Mettre à jour les tests de non-régression pour le cas des deux displays identiques.

## Hors périmètre

- Saisie graphique du produit.
- Déconditionnement de contenant.
- Ouverture de produit révélant des cartes.
- Implémentation de scanner matériel.

## Workflow attendu — scan commercial

```text
scanner commercial_barcode
        │
        ▼
résoudre ProductReference
        │
        ├── référence inconnue → résultat à qualifier
        ├── référence ambiguë → exception ou résultat ambigu explicite
        └── référence connue
                │
                ▼
        créer une nouvelle ProductInstance si l’utilisateur enregistre un nouvel exemplaire
```

## Workflow attendu — scan interne

```text
scanner internal_barcode
        │
        ▼
retrouver ProductInstance
        │
        ├── inconnue → résultat explicite ou exception métier
        └── connue → retourner l’instance physique exacte
```

## Règles métier

- Un code-barres commercial connu ne bloque jamais la création d’une nouvelle instance.
- Un code-barres commercial ne doit pas servir de clé d’unicité d’instance.
- Un code-barres interne peut servir de clé directe vers une instance physique.
- Les ambiguïtés de référence doivent être visibles par l’application consommatrice.

## Livrables attendus

- Workflows de scan refactorés.
- Résultats de scan adaptés.
- Ports adaptés.
- Tests de scan commercial et interne.
- Documentation d’exemples.

## Critères d'acceptation

- Scanner deux fois le même EAN peut créer deux instances différentes.
- Scanner un EAN connu retourne ou résout une référence, pas une instance unique supposée.
- Scanner un code interne connu retourne l’instance exacte.
- Les cas inconnus et ambigus sont couverts par exceptions ou résultats métiers explicites.
- Le scénario “2 displays 15 boosters + 1 bundle” est représentable sans contournement.
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
