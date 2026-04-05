# baobab-mtg-products

Librairie Python **métier** et **typée** (`py.typed`) pour la gestion des produits scellés *Magic: The Gathering* : modélisation, enregistrement et qualification par scan, relations parent / enfant, ouverture, traçabilité des cartes révélées, journal d’événements, ports vers la collection et les statistiques, et services de consultation. **Aucune** exposition HTTP, interface graphique, moteur de règles du jeu ni deckbuilding.

## Table des matières

- [Périmètre](#périmètre)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Organisation du package](#organisation-du-package)
- [Scénarios métier (aperçus)](#scénarios-métier-aperçus)
- [Qualité, couverture et release](#qualité-couverture-et-release)
- [Documentation](#documentation)
- [Contribution](#contribution)
- [Licence](#licence)

## Périmètre

**Inclus** (voir `docs/001_specifications.md`) : types et instances de produits scellés, statuts, codes-barres, série, set, relations parent-enfant, ouverture, traces carte ↔ produit ouvert, historique métier, intégration collection/statistiques via ports, consultation structurée.

**Exclus** : règles de jeu, deckbuilding, possession globale utilisateur, API REST/GraphQL, UI.

## Prérequis

- Python **3.10** à **3.13**
- Environnement virtuel recommandé pour le développement

## Installation

### Depuis PyPI (après publication)

Lorsque le paquet est disponible sur l’index PyPI public :

```bash
python -m pip install baobab-mtg-products
```

Le nom du projet sur PyPI est `baobab-mtg-products` ; le module Python importable est `baobab_mtg_products`.

### Utilisateur (runtime)

Depuis une roue ou un sdist produit localement ou par votre pipeline :

```bash
python -m pip install /chemin/vers/baobab_mtg_products-*.whl
```

Ou, à partir du dépôt cloné (sans les outils de dev) :

```bash
python -m pip install .
```

Aucune dépendance runtime tierce n’est requise (`dependencies = []` dans `pyproject.toml`).

### Contributeur (développement)

```bash
python -m pip install -e ".[dev]"
```

Construction et contrôle des artefacts (avec l’extra `[dev]`, `build` et `twine` sont déjà installés) :

```bash
rm -rf dist
python -m build
python -m twine check dist/*
```

Les roues et le sdist sont générés sous `dist/`.

## Démarrage rapide

```python
from baobab_mtg_products import (
    BaobabMtgProductsException,
    InternalProductId,
    MtgSetCode,
    ProductInstance,
    ProductStatus,
    ProductType,
)

instance = ProductInstance(
    internal_id=InternalProductId("uuid-ou-id-interne"),
    product_type=ProductType.PLAY_BOOSTER,
    set_code=MtgSetCode("mh3"),
    status=ProductStatus.REGISTERED,
)
assert instance.domain_identity() == "uuid-ou-id-interne"
```

Les erreurs métier héritent de `BaobabMtgProductsException` :

```python
from baobab_mtg_products import BaobabMtgProductsException

raise BaobabMtgProductsException("exemple d'erreur métier")
```

**Version** : `import baobab_mtg_products as pkg; print(pkg.__version__)`.

## Organisation du package

| Zone | Rôle |
|------|------|
| `baobab_mtg_products` (racine) | Exports publics stables (modèle, services de lecture, cas d’usage courants, ports d’intégration clés). |
| `domain.*` | Entités, value objects, règles, DTO d’intégration et de consultation. |
| `use_cases.*` | Workflows commande (scan, qualification, rattachement, ouverture, …). |
| `ports` | Contrats (`Protocol`) pour persistance, catalogue, journal, collection, statistiques, etc. |
| `services.query` | Consultation : snapshot produit, vue structurelle, frise historique. |
| `exceptions` | Exceptions spécifiques (réexportées au niveau racine pour les plus usuelles). |

La liste exacte des symboles exportés par la racine est donnée par `baobab_mtg_products.__all__`.

## Scénarios métier (aperçus)

### Enregistrement par scan

Les applications implémentent les ports (`ProductRepositoryPort`, `BarcodeResolutionPort`, etc.), puis injectent un `RegistrationFromScanRunner` :

```python
from baobab_mtg_products.domain.products import CommercialBarcode
from baobab_mtg_products.use_cases.registration import (
    RegisterProductByCommercialScanUseCase,
    RegistrationFromScanRunner,
)

# runner = RegistrationFromScanRunner(repo, resolution, id_factory, event_recorder, collection=…)
# use_case = RegisterProductByCommercialScanUseCase(CommercialBarcode("12345678"), runner)
# result = use_case.execute()  # existing | new_known_from_catalog | new_pending_qualification
```

Les adaptateurs **collection** et **statistiques** implémentent `CollectionPort` et `StatisticsPort` ; les cas d’usage concernés acceptent une injection **optionnelle** et publient des DTO stables après succès.

### Relations parent / enfant

```python
from baobab_mtg_products import (
    AttachChildProductToParentUseCase,
    DetachChildProductFromParentUseCase,
    InternalProductId,
    ProductRelationshipKind,
)
from baobab_mtg_products.domain.products import ProductRelationship

# attach = AttachChildProductToParentUseCase(
#     parent_id, child_id, ProductRelationshipKind.DISPLAY_CONTAINS_BOOSTER, repo, events
# )
# link: ProductRelationship = attach.execute()
# DetachChildProductFromParentUseCase(child_id, repo, events).execute()
```

### Ouverture et cartes révélées

```python
from baobab_mtg_products import (
    ExternalCardId,
    OpenSealedProductUseCase,
    RecordOpeningCardScanUseCase,
    RegisterRevealedCardFromOpeningUseCase,
    OpeningCardScanPayload,
)

# open_uc = OpenSealedProductUseCase(product_id, repo, events, collection=…, statistics=…)
# outcome = open_uc.execute()
# RegisterRevealedCardFromOpeningUseCase(pid, ExternalCardId("…"), repo, trace_repo, events).execute()
# RecordOpeningCardScanUseCase(pid, OpeningCardScanPayload("…"), repo, events).execute()
```

### Consultation (produit, structure, historique)

```python
from baobab_mtg_products import (
    GetProductBusinessTimelineService,
    GetProductStructuralViewService,
    GetSealedProductSnapshotService,
    InternalProductId,
)

# snapshot = GetSealedProductSnapshotService(InternalProductId("…"), repo).load()
# struct = GetProductStructuralViewService(InternalProductId("…"), repo).load()
# # struct.product, struct.parent, struct.direct_children
```

Le dépôt doit implémenter `list_direct_children_of_parent` sur `ProductRepositoryPort`.

### Historique métier

`InMemoryProductBusinessEventLedger` implémente `ProductWorkflowEventRecorderPort` et peut servir de journal avec garde-fous. Lecture via `GetProductBusinessTimelineService` ou `ListProductBusinessHistoryUseCase` (`use_cases.history`).

```python
from baobab_mtg_products import GetProductBusinessTimelineService, InMemoryProductBusinessEventLedger
from baobab_mtg_products.domain.products import InternalProductId

# ledger = InMemoryProductBusinessEventLedger()
# timeline = GetProductBusinessTimelineService(InternalProductId("…"), ledger).load()
```

## Qualité, couverture et release

Après le tag public **`v1.0.0`**, les correctifs de chaîne release (packaging, métadonnées, extras `[dev]`) sont portés en **1.0.1** et suivants selon **SemVer** ; consulter `CHANGELOG.md` et `docs/RELEASE.md` avant publication.

Une chaîne équivalente aux commandes ci-dessous est exécutée sur **push** et **pull_request** via **GitHub Actions** (`.github/workflows/ci.yml`), pour les versions de Python annoncées dans `pyproject.toml`.

```bash
python -m pytest
python -m coverage run -m pytest
python -m coverage report
coverage html
python -m black --check .
python -m pylint src tests
python -m mypy src
python -m flake8 src tests
python -m bandit -r src
```

Les données de couverture sont configurées dans `pyproject.toml` (seuil minimal, chemins sous `docs/tests/coverage/`). La procédure de publication (build, `twine check`, tag) est détaillée dans **`docs/RELEASE.md`**.

## Documentation

- Cahier des charges : `docs/001_specifications.md`
- Contraintes de développement : `docs/000_dev_constraints.md`
- Journal de développement : `docs/dev_diary.md`
- Journal des versions : `CHANGELOG.md`
- Publication : `docs/RELEASE.md`

## Contribution

1. Créer une branche depuis `main` (ex. `feature/...`).
2. Respecter **une classe par fichier**, tests miroirs, types stricts et exceptions héritant de `BaobabMtgProductsException`.
3. Messages de commit au format [Conventional Commits](https://www.conventionalcommits.org/).
4. Exécuter les tests, la couverture (seuil minimal dans `[tool.coverage.report] fail_under`) et les outils listés ci-dessus.

## Licence

Ce projet est sous licence MIT — voir le fichier `LICENSE`.
