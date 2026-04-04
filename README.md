# baobab-mtg-products

Librairie Python **métier** pour la gestion des produits scellés *Magic: The Gathering* : modélisation, enregistrement et qualification par scan, relations parent / enfant, ouverture et traçabilité des cartes révélées. Elle expose des **ports** vers la collection et les statistiques sans imposer d’HTTP, d’UI, de moteur de règles ni de deckbuilding.

## Prérequis

- Python 3.10 ou supérieur
- Un environnement virtuel recommandé

## Installation

Installation en mode éditable avec les outils de développement :

```bash
python -m pip install -e ".[dev]"
```

Construction d’une roue (wheel) :

```bash
python -m pip install build
python -m build
```

## Utilisation de base

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

```python
from baobab_mtg_products import BaobabMtgProductsException

raise BaobabMtgProductsException("exemple d'erreur métier")
```

### Enregistrement par scan (aperçu)

Les applications fournissent des implémentations des ports (`ProductRepositoryPort`, `BarcodeResolutionPort`, etc.), puis injectent un `RegistrationFromScanRunner` dans les cas d’usage :

```python
from baobab_mtg_products.domain.products import CommercialBarcode
from baobab_mtg_products.use_cases.registration import (
    RegisterProductByCommercialScanUseCase,
    RegistrationFromScanRunner,
)

# runner = RegistrationFromScanRunner(repo, resolution, id_factory, event_recorder)
# use_case = RegisterProductByCommercialScanUseCase(CommercialBarcode("12345678"), runner)
# result = use_case.execute()  # existing | new_known_from_catalog | new_pending_qualification
```

Les sous-packages `domain.products`, `domain.registration`, `domain.opening`, `domain.history`, `ports` et `use_cases` portent le **modèle**, les **DTO des flux scan, ouverture et historique**, les **contrats d’intégration** et les **cas d’usage** métier.

### Relations parent / enfant (aperçu)

Un booster peut rester sans `parent_id` ; pour le rattacher à une display ou placer un sous-produit sous un bundle, utiliser les cas d’usage dédiés (types compatibles selon `ProductRelationshipKind`, pas de cycle, enfant sans parent préalable) :

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

Les événements `record_product_attached_to_parent` / `record_product_detached_from_parent` complètent le journal déjà utilisé pour les scans.

### Ouverture et cartes révélées (aperçu)

Un produit **ouvrable** (tout type sauf `DISPLAY`) au statut `sealed` ou `qualified` peut être passé à `opened` une seule fois. Les cartes sont rattachées via `ExternalCardId` (opaque pour la lib) et persistées par un adaptateur de `RevealedCardTraceRepositoryPort` ; les scans bruts pendant la session passent par `OpeningCardScanPayload` et `record_opening_card_scan`.

```python
from baobab_mtg_products import (
    ExternalCardId,
    OpenSealedProductUseCase,
    RecordOpeningCardScanUseCase,
    RegisterRevealedCardFromOpeningUseCase,
    OpeningCardScanPayload,
)

# open_uc = OpenSealedProductUseCase(product_id, repo, events)
# outcome = open_uc.execute()  # statut opened + ProductOpeningEvent
# RegisterRevealedCardFromOpeningUseCase(pid, ExternalCardId("…"), repo, trace_repo, events).execute()
# RecordOpeningCardScanUseCase(pid, OpeningCardScanPayload("…"), repo, events).execute()
```

Le package `domain.opening` regroupe les value objects et règles ; `ports` expose `RevealedCardTraceRepositoryPort`.

### Historique métier et journal interne (aperçu)

`InMemoryProductBusinessEventLedger` implémente `ProductWorkflowEventRecorderPort` : chaque appel `record_*` produit une entrée typée (`ProductBusinessEventKind`) avec charge utile optionnelle. Le ledger refuse les doublons interdits (ex. second enregistrement, ouverture sans scan ni enregistrement préalable, carte sans ouverture journalisée, rattachement incohérent). La consultation passe par `ProductBusinessHistoryQueryPort` / `ListProductBusinessHistoryUseCase` (vue enfant + événements où le produit apparaît comme parent pour attach / detach).

```python
from baobab_mtg_products import InMemoryProductBusinessEventLedger, ListProductBusinessHistoryUseCase
from baobab_mtg_products.domain.products import InternalProductId

# ledger = InMemoryProductBusinessEventLedger()
# runner = RegistrationFromScanRunner(repo, resolution, id_factory, ledger)
# events = ListProductBusinessHistoryUseCase(InternalProductId("…"), ledger).execute()
```

## Qualité et tests

```bash
pytest
coverage run -m pytest
coverage report
coverage html
black --check .
pylint src tests
mypy src
flake8 src tests
bandit -r src
```

Les données et rapports de couverture sont écrits sous `docs/tests/coverage/` (voir ce dossier).

## Documentation

- Cahier des charges : `docs/001_specifications.md`
- Contraintes de développement : `docs/000_dev_constraints.md`
- Journal de développement : `docs/dev_diary.md`
- Journal des versions : `CHANGELOG.md`

## Contribution

1. Créer une branche depuis `main` (ex. `feature/...`).
2. Respecter **une classe par fichier**, tests miroirs, types stricts et exceptions héritant de `BaobabMtgProductsException`.
3. Messages de commit au format [Conventional Commits](https://www.conventionalcommits.org/).
4. Vérifier tests, couverture (≥ 90 %) et outils listés ci-dessus.

## Licence

Ce projet est sous licence MIT — voir le fichier `LICENSE`.
