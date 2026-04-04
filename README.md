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

Les sous-packages `domain.products`, `domain.registration`, `ports` et `use_cases` portent le **modèle**, les **DTO du flux scan**, les **contrats d’intégration** et les **cas d’usage** métier.

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
