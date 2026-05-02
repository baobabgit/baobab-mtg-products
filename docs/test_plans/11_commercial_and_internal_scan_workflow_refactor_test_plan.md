# Plan de test — 11_commercial_and_internal_scan_workflow_refactor — Refonte des workflows de scan commercial et interne

## Objectif de validation

Vérifier que le **scan commercial** (EAN) résout une **`ProductReference`** et matérialise une **nouvelle `ProductInstance`** à chaque enregistrement d’exemplaire, sans jamais traiter l’EAN comme clé d’unicité d’exemplaire ; que le **scan interne** retrouve l’**instance exacte** ou signale explicitement l’**inconnu** sans création implicite ; que les **ambiguïtés** catalogue remontent via **`AmbiguousBarcodeResolutionError`** ; que **`resolved_reference`** et **`CommercialReferenceResolutionResult`** exposent la résolution référence aux consommateurs ; que le scénario **« 2 displays + 15 boosters + 1 bundle »** reste représentable.

Les tests s’appuient sur des **doubles de ports** en mémoire (pas de DB, pas de matériel).

## Matrice des règles métier à couvrir

| Règle | Tests nominaux | Tests d'erreur | Tests de non-régression |
|-------|----------------|----------------|-------------------------|
| EAN connu ne bloque pas une nouvelle instance | `test_two_commercial_scans_same_ean_two_instances` ; `test_commercial_shared_reference_creates_new_instance` | — | `resolved_reference` renseigné |
| EAN ne résout pas « un seul exemplaire » implicite | Assertions sur `list_by_reference_id` (≥ 2) ; pas de lookup instance par EAN | — | Consultation / provenance inchangées |
| Scan interne → instance exacte | `test_internal_existing_records_scan_only` ; inventaire `test_inventory_two_displays_fifteen_boosters_one_bundle` | — | Événements : scan sans `record_registration` |
| Interne inconnu → pas de matérialisation | `test_internal_unknown_barcode_does_not_materialize` | — | `INTERNAL_BARCODE_UNKNOWN`, `product is None` |
| Interne invalide (format VO) | Construction `InternalBarcode` avant use case | `InvalidInternalBarcodeError` (`test_internal_barcode.py`, `test_register_product_by_internal_scan_use_case`) | Jamais d’appel runner si le VO lève à la construction |

Pour le scan interne, un code invalide est rejeté lors de la construction du value object `InternalBarcode`.
Le use case reçoit donc un `InternalBarcode` déjà valide.
Un code interne valide mais inconnu produit un résultat métier explicite `INTERNAL_BARCODE_UNKNOWN`.
| Ambiguïté visible | `test_ambiguous_resolution_propagates` (runner) ; `test_ambiguous_catalog_raises` (resolve use case) | — | Exception métier exacte |
| Résolution référence seule (sans instance) | `ResolveProductReferenceFromCommercialBarcodeUseCase` : persistant / catalogue | — | `CommercialReferenceResolutionResult` |

## Tests unitaires à créer

- **`RegistrationScanOutcome`** : présence de `INTERNAL_BARCODE_UNKNOWN` ; valeurs stables.
- **`RegistrationScanResult`** : `resolved_reference` optionnel ; `product` optionnel.
- **`CommercialReferenceResolutionResult`** : `has_persistent_reference` ; branches mutuellement exclusives.
- **`ResolveProductReferenceFromCommercialBarcodeUseCase`** : EAN en dépôt ; EAN catalogue seul ; ambiguïté (voir ci-dessus).

## Tests de workflow à créer

- **`RegistrationFromScanRunner`** : branches commercial (shared ref, new catalog, pending, overrides, serial) ; interne (existant, inconnu) ; ambiguïté ; collection.
- **`RegisterProductByCommercialScanUseCase` / `RegisterProductByInternalScanUseCase`** : délégation au runner (smoke si besoin).
- **Inventaire** : `test_inventory_two_displays_fifteen_boosters_one_bundle` (deux scans EAN display, 15 instances booster + bundle, scan interne ciblé).

## Cas limites

- Référence `requires_qualification=True` + EAN connu → instance `REGISTERED`.
- Overrides partiels (set sans type) → pending.
- `resolved_reference` `None` si référence orpheline en théorie (tests défensifs si le runner évolue).

## Tests de non-régression

- Qualification, création d’instance hors scan (feature 10), vues consultation (07).
- Fakes de tests : implémenter toutes les méthodes du **`ProductRepositoryPort`** (y compris `list_by_*`).

## Risques de couverture

| Risque | Mitigation |
|--------|------------|
| Événements « dédiés » vs `record_scan(channel=…)` | Le port unique avec canal typé suffit si la spec produit le valide ; sinon ajouter méthodes dédiées + tests. |
| Ambiguïté **dépôt** (plusieurs refs pour un EAN) | Hors contrat V1 du dépôt référence ; tests catalogue uniquement tant que `find_by_commercial_barcode` reste `Optional`. |

## Données de test recommandées

| Élément | Exemples |
|---------|----------|
| EAN display | `4006381333930` (normalisé côté `CommercialBarcode`) |
| Codes internes boosters | `INT-MH3-PB-01` … `INT-MH3-PB-15` |
| Identifiants internes | `disp-1`, `disp-2`, `boost-1` … `boost-15`, `bundle-1` |
| Références | `ref-mh3-display`, `ref-mh3-play`, `ref-fdn-bundle` |
