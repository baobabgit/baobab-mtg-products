# Plan de test — 12_container_deconditioning_workflow — Déconditionnement de contenants

## Objectif de validation

Vérifier que le **déconditionnement** (ouverture d’un **contenant** — display, bundle, prerelease kit, etc. — pour extraire ou rattacher des **sous-produits scellés**) est **distinct** de l’**ouverture de booster** (révélation de cartes) : pas d’événements de traçabilité carte ; statut / événements métier dédiés si retenus ; enfants modélisés comme **`ProductInstance`** avec `parent_id` = contenant ; **pas de double parent** ; **anti-cycles** préservés ; **vue structurelle** et **timeline métier** reflètent l’opération ; scénario **display → 15 boosters** et **bundle → sous-produits** couverts.

Les tests sont **déterministes**, avec **fakes** des ports (`ProductRepositoryPort`, `ProductReferenceRepositoryPort`, fabriques d’ids, `ProductWorkflowEventRecorderPort`, ledger / query historique, `CollectionPort` optionnel).

## Matrice des règles métier à couvrir

| Règle | Tests nominaux | Tests d'erreur | Tests de non-régression |
|-------|----------------|----------------|-------------------------|
| Cible = instance physique contenant | `DeconditionContainerUseCase` sur instance `DISPLAY` / `BUNDLE` / `PRERELEASE_KIT` (ou liste déconditionnable figée) | Contenant introuvable → `ProductNotFoundForWorkflowError` | Consultation par `internal_id` inchangée hors flux |
| Enfants = `ProductInstance`, parent = contenant | Après exécution, `child.parent_id == container.internal_id` pour chaque enfant créé ou rattaché | — | `AttachChildProductToParentUseCase` / règles `ParentChildRelationshipRules` si réutilisées |
| Création d’enfants depuis références | Commande DTO : N entrées « nouvelle instance » avec `ProductReferenceId` + optionnel `internal_barcode` / `ProductionCode` | Ref absente → erreur métier dédiée ; doublon **internal_barcode** → `DuplicateInternalBarcodeError` si applicable | `CreateProductInstanceUseCase` / scan 11 inchangés |
| Rattachement d’enfants existants | DTO : ids enfants orphelins (`parent_id is None`) → mis sous le contenant | Enfant déjà avec parent → `ProductAlreadyHasParentError` ; enfant introuvable → `ProductNotFoundForWorkflowError` | Comportement attach existant |
| Un produit, un seul parent | Tenter le même enfant dans deux déconditionnements ou double inclusion dans une commande | `ProductAlreadyHasParentError` ou validation commande | — |
| Pas d’événement « ouverture cartes » | Après déconditionnement : **aucun** `record_card_revealed_from_opening`, **aucun** `record_opening_card_scan` | — | `OpenSealedProductUseCase` continue d’émettre `OPENED` + cartes séparément |
| Pas de confusion avec ouverture simple | Déconditionnement **ne** pose pas le contenant en `OPENED` **si** la spec distingue statut `DECONDITIONED` ; sinon documenter la transition autorisée (`SEALED` → `DECONDITIONED`) | — | Statuts existants `REGISTERED`, `QUALIFIED`, `SEALED`, `OPENED` |
| Types non déconditionnables | `PLAY_BOOSTER` / `COLLECTOR_BOOSTER` comme **contenant** de l’opération | `InvalidContainerDeconditioningError` (nom à figer) ou équivalent | — |
| Anti-cycle | Contenant ne peut pas devenir enfant de son descendant (réutiliser chaîne ancêtres) | `CircularProductParentageError` | `ProductAncestorChain` |
| Vue structurelle | `GetProductStructuralViewService` : enfants directs visibles, refs résolues | — | `MissingReferencedParentProductError` si parent cassé (hors scope déconditionnement) |
| Timeline | Entrée `CONTAINER_DECONDITIONED` (ou `record_container_deconditioned`) visible via `GetProductBusinessTimelineService` / ledger | — | Autres kinds inchangés |

## Tests unitaires à créer

- **`ProductStatus.DECONDITIONED`** (si ajouté) : valeur stable, compatibilité sérialisation.
- **`ProductBusinessEventKind.CONTAINER_DECONDITIONED`** (ou équivalent) : valeur stable.
- **DTO de commande** (ex. `DeconditionContainerCommand`, `DeconditionChildSpec`) : immutabilité ; discriminant « créer vs rattacher » ; validation liste non vide si spec l’exige.
- **Règle « type contenant déconditionnable »** : fonction ou enum dédié testé isolément (display, bundle, prerelease, `OTHER_SEALED` ? — selon spec finale).
- **Résultat du use case** (optionnel) : tuple ou agrégat décrivant contenant mis à jour + enfants affectés.

## Tests de workflow à créer

- **`DeconditionContainerUseCase`** avec fake repo :
  - **Display → 15 play boosters** : références booster existantes ; 15 créations ou combinaison création/rattachement ; assert `list_direct_children_of_parent(container_id)` taille 15 ; ordre stable.
  - **Bundle → 2 sous-produits** : types compatibles avec les `ProductRelationshipKind` utilisés.
  - **Rattachement seul** : 3 instances existantes sans parent → liées en une passe.
  - **Création seule** : ids fabriqués, `save` appelé pour chaque enfant + mise à jour contenant.
  - **Événements** : mock / spy sur `ProductWorkflowEventRecorderPort.record_container_deconditioned` (ou ledger append avec kind attendu) **une fois** par opération cohérente avec la spec (vs un event par enfant — à trancher).
  - **Timeline** : après exécution, filtrage par kind sur l’historique du contenant (ou produits concernés).
- **Intégration légère avec `GetProductStructuralViewService`** : dépôt prérempli post-use case → enfants et références présents.
- **Non-appel ouverture** : vérifier que le use case **n’injecte pas** / n’appelle pas `OpenSealedProductUseCase` ni enregistrement carte.

## Cas limites

- Contenant **sans** enfants dans la commande : rejet ou no-op selon spec (à tester en conséquence).
- **Enfant partiel** : commande avec 5 boosters sur 15 permise (pas de contrainte de nombre exact).
- **Références encore `requires_qualification=True`** pour enfants créés : statut `REGISTERED` hérité des règles existantes.
- **Contenant `REGISTERED` vs `QUALIFIED` vs `SEALED`** : quels statuts autorisent le déconditionnement (à figer puis tester).
- **Idempotence** : double appel même commande → second échec (enfants déjà parents) ou protection métier.

## Tests de non-régression

- **`AttachChildProductToParentUseCase`** : inchangé si le déconditionnement le compose ; sinon règles dupliquées doivent rester alignées — préférer tests croisés sur types autorisés parent/enfant.
- **`OpenSealedProductUseCase`** : ouverture booster inchangée ; événements `OPENED` / cartes inchangés.
- **Features **09–11** : références, instances, codes production, scan — pas de régression sur constructions `ProductInstance`.
- **Ledger mémoire** : implémentation de toute nouvelle méthode `record_*` + kind enum.

## Risques de couverture

| Risque | Mitigation |
|--------|------------|
| Liste exacte des types « contenant » | Spec à figer ; tests paramétrés `@pytest.mark.parametrize` sur `ProductType` |
| Un event global vs N events enfants | Documenter le contrat dans le use case et assert précis |
| `OTHER_SEALED` ambigu | Test explicite accepté vs refusé comme contenant |
| Couverture ≥ 95 % | Couvrir branches validation DTO + exceptions |

## Données de test recommandées

| Rôle | Exemples |
|------|----------|
| Contenant display | `InternalProductId("disp-mh3-1")`, `ProductType.DISPLAY`, `MtgSetCode("MH3")`, statut `SEALED` ou `DECONDITIONED` selon spec |
| Références enfants | `ProductReferenceId("ref-mh3-play")` pour play booster |
| 15 boosters | `InternalProductId("pb-01")` … `pb-15`, `InternalBarcode("INT-PB-01")` … uniques |
| Bundle | `InternalProductId("bdl-fdn-1")`, enfants types variés (`SET_BOOSTER`, `COMMANDER_DECK`, …) selon kind |
| Booster invalide comme contenant | Instance `PLAY_BOOSTER` comme cible du use case → erreur |
| production_code | Même `ProductionCode("LOT-X")` sur plusieurs enfants (non unique) pour valider 10 |

## Ambiguïtés de spécification à clarifier pour des tests définitifs

1. **Transition de statut du contenant** : `SEALED` → `DECONDITIONED` uniquement, ou aussi `QUALIFIED` ? Refus si déjà `OPENED` ?
2. **Événement unique vs multiple** : un seul `CONTAINER_DECONDITIONED` avec payload (nombre d’enfants) ou réutilisation de `ATTACHED_TO_PARENT` × N ?
3. **`OTHER_SEALED`** : déconditionnable ou non ?
4. **Relation `ProductRelationshipKind`** : le déconditionnement impose-t-il un kind unique (`DISPLAY_WITH_BOOSTERS`) pour tous les enfants ?
5. **Collection / provenance** : publication événement collection obligatoire ou optionnelle comme pour attach ?

---

## Voir aussi

- Découpage en **tickets et fichiers de tests** (placeholders `pytest.mark.skip`) : [`12_container_deconditioning_test_tickets.md`](12_container_deconditioning_test_tickets.md).
