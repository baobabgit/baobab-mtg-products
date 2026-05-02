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

**Inclus** (voir `docs/001_specifications.md`) : références produits, instances physiques, statuts, codes-barres commerciaux non uniques au niveau instance, codes de production non uniques, codes internes uniques si générés, relations parent-enfant, déconditionnement de contenants, ouverture, traces carte ↔ produit ouvert, historique métier, intégration collection/statistiques via ports, consultation structurée et contrats de persistance.

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
    ProductReferenceId,
    ProductStatus,
    ProductType,
)

instance = ProductInstance(
    internal_id=InternalProductId("uuid-ou-id-interne"),
    reference_id=ProductReferenceId("ref-catalogue-partage"),
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

Les applications implémentent les ports (`ProductRepositoryPort`, `ProductReferenceRepositoryPort`, `BarcodeResolutionPort`, fabriques d’identifiants, etc.), puis injectent un `RegistrationFromScanRunner` :

```python
from baobab_mtg_products.domain.products import CommercialBarcode
from baobab_mtg_products.use_cases.registration import (
    RegisterProductByCommercialScanUseCase,
    RegisterProductByInternalScanUseCase,
    RegistrationFromScanRunner,
)

# runner = RegistrationFromScanRunner(
#     repo, ref_repo, resolution, id_factory, ref_id_factory, event_recorder, collection=…
# )
# use_case = RegisterProductByCommercialScanUseCase(CommercialBarcode("12345678"), runner)
# result = use_case.execute()
# # outcomes (commercial) : new_known_from_catalog, new_pending_qualification,
# #           new_instance_shared_reference (nouvel exemplaire, même référence catalogue)
# # outcomes (interne) : existing_product (instance trouvée), internal_barcode_unknown
```

Un même **code-barres commercial** peut désigner une **`ProductReference`** déjà persistée : le flux crée alors une **nouvelle** `ProductInstance` sans bloquer sur un doublon commercial (voir `RegistrationScanOutcome.NEW_INSTANCE_SHARED_REFERENCE`). Le code-barres commercial et les métadonnées descriptives (nom, visuel) vivent sur **`ProductReference`** ; l’instance porte `reference_id` et une copie dénormalisée de type / set pour les règles métier existantes. Le résultat d’enregistrement expose **`resolved_reference`** (référence alignée) ; l’EAN **ne** correspond **jamais** à un exemplaire unique implicite. Une **ambiguïté** catalogue sur l’EAN se traduit par une levée d’**`AmbiguousBarcodeResolutionError`**. Pour une **résolution référence seule** (sans persister d’instance), utiliser **`ResolveProductReferenceFromCommercialBarcodeUseCase`** avec **`CommercialReferenceResolutionResult`**.

**Scan interne** : pour le scan interne, un code **invalide** est rejeté lors de la construction du value object **`InternalBarcode`** (`InvalidInternalBarcodeError`). Le cas d’usage **`RegisterProductByInternalScanUseCase`** reçoit donc un **`InternalBarcode`** déjà valide. Un code interne **valide mais inconnu** produit l’issue **`INTERNAL_BARCODE_UNKNOWN`** avec `product is None`. Un code **connu** retrouve l’instance exacte (`EXISTING_PRODUCT`). Les cas d’usage d’enregistrement par scan ne sont pas réexportés à la racine du package : importer depuis **`baobab_mtg_products.use_cases.registration`** (voir aussi `docs/features/11_commercial_and_internal_scan_workflow_refactor.md`).

### Création explicite d’instance et code de production

En dehors du scan, une application peut matérialiser un exemplaire avec **`CreateProductInstanceUseCase`** (référence catalogue obligatoire, **`ProductionCode`** optionnel et **non unique**, code-barres interne optionnel mais **unique** dans le dépôt). Le **`SerialNumber`** reste un VO distinct (souvent pensé comme piste qualité unitaire) ; il ne doit pas être confondu avec le lot **`ProductionCode`**. Une saisie différée du lot utilise **`AssignProductionCodeToProductInstanceUseCase`**. Les dépôts exposent **`list_by_reference_id`** et **`list_by_production_code`** : la recherche par code de production retourne **toujours** une séquence (plusieurs résultats possibles), jamais une hypothèse d’unicité implicite.

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

### Déconditionnement de contenants

Sortir les sous-produits physiques d’une **display**, d’un **bundle**, d’un **prerelease kit**, etc. sans passer par l’ouverture pour cartes : **`DeconditionContainerUseCase`** avec **`DeconditionContainerCommand`** et une liste de **`DeconditionChildSpecification`** (création depuis une **`ProductReferenceId`** ou rattachement d’une instance orpheline existante). Le contenant passe en **`ProductStatus.DECONDITIONED`** ; le journal enregistre **`CONTAINER_DECONDITIONED`** une fois par opération. Les kinds **`ProductRelationshipKind`** existants (ex. **`DISPLAY_CONTAINS_BOOSTER`**, **`BUNDLE_CONTAINS_SUBPRODUCT`**) contrôlent la compatibilité des types. Voir **`docs/features/12_container_deconditioning_workflow.md`**.

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

# snapshot = GetSealedProductSnapshotService(InternalProductId("…"), repo, ref_repo).load()
# # snapshot.product, snapshot.reference (nom, image_uri, code-barres commercial…)
# struct = GetProductStructuralViewService(InternalProductId("…"), repo, ref_repo).load()
# # struct.product, struct.product_reference, struct.parent, struct.parent_reference,
# # struct.direct_children, struct.child_references
```

Les dépôts doivent implémenter `list_direct_children_of_parent`, `list_by_reference_id` et `list_by_production_code` sur `ProductRepositoryPort`, ainsi que les méthodes du `ProductReferenceRepositoryPort` pour résoudre les références associées aux instances.

### Historique métier

`InMemoryProductBusinessEventLedger` implémente `ProductWorkflowEventRecorderPort` et peut servir de journal avec garde-fous. Lecture via `GetProductBusinessTimelineService` ou `ListProductBusinessHistoryUseCase` (`use_cases.history`).

```python
from baobab_mtg_products import GetProductBusinessTimelineService, InMemoryProductBusinessEventLedger
from baobab_mtg_products.domain.products import InternalProductId

# ledger = InMemoryProductBusinessEventLedger()
# timeline = GetProductBusinessTimelineService(InternalProductId("…"), ledger).load()
```

## Qualité, couverture et release

La **2.0.0** introduit la séparation **`ProductReference`** / **`ProductInstance`** (voir `CHANGELOG.md`). Les versions **1.x** restent documentées dans l’historique du changelog ; consulter `docs/RELEASE.md` avant publication.

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
- Note d’architecture références / instances / persistance : `docs/002_product_reference_instance_persistence_guidance.md`
- Nouvelles features post-1.0.1 : `docs/features/09_product_reference_instance_split.md` à `docs/features/13_persistence_contracts_database_insertion.md`
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
