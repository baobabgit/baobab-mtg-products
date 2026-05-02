# Tickets de tests — 12_container_deconditioning_workflow

Découpage du plan [`12_container_deconditioning_workflow_test_plan.md`](12_container_deconditioning_workflow_test_plan.md) en **fichiers** et **méthodes de test** prévues. Les fichiers correspondants existent sous `tests/` avec `pytest.mark.skip` jusqu’à livraison du use case et des DTO.

## Légende

| Priorité | Signification |
|----------|----------------|
| P0 | Critère d’acceptation bloquant |
| P1 | Règle métier / erreur explicite |
| P2 | Cas limite / non-régression étendue |

---

## Lot A — Domaine & valeur métier

| ID | Priorité | Fichier de test | Méthode (nom cible) | Comportement à vérifier |
|----|----------|-----------------|---------------------|-------------------------|
| A1 | P1 | `tests/baobab_mtg_products/domain/deconditioning/test_product_status_deconditioned.py` | `test_deconditioned_value_stable` | Si `ProductStatus.DECONDITIONED` existe : valeur chaîne stable |
| A2 | P1 | `tests/baobab_mtg_products/domain/history/test_product_business_event_kind_deconditioning.py` | `test_container_deconditioned_kind_stable` | Si `ProductBusinessEventKind.CONTAINER_DECONDITIONED` : valeur stable |
| A3 | P1 | `tests/baobab_mtg_products/domain/deconditioning/test_decondition_container_command.py` | `test_command_rejects_empty_children_when_required` | DTO/commande : liste enfants vide → erreur si spec impose au moins un enfant |
| A4 | P2 | `tests/baobab_mtg_products/domain/deconditioning/test_decondition_container_command.py` | `test_child_spec_create_vs_attach_discriminant` | Entrées création (reference_id) vs rattachement (child_internal_id) mutuellement exclusives |
| A5 | P1 | `tests/baobab_mtg_products/domain/deconditioning/test_deconditionable_container_types.py` | `test_play_booster_not_deconditionable_container` | Prédicat types : booster comme **contenant** → faux ou erreur |

---

## Lot B — Use case `DeconditionContainerUseCase`

| ID | Priorité | Fichier de test | Méthode (nom cible) | Comportement à vérifier |
|----|----------|-----------------|---------------------|-------------------------|
| B1 | P0 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_display_deconditions_into_fifteen_play_boosters` | 15 enfants, `parent_id` = display, `list_direct_children_of_parent` taille 15, ordre stable |
| B2 | P0 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_bundle_deconditions_into_subproducts` | Bundle + 2 sous-produits (types/kinds conformes) |
| B3 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_attach_only_orphans_under_container` | 3 instances sans parent → rattachées ; pas de `save` création ref nouvelle si rattachement pur |
| B4 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_create_children_from_references_saves_each` | `repository.save` pour chaque enfant créé + contenant mis à jour si applicable |
| B5 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_container_not_found_raises` | `ProductNotFoundForWorkflowError` |
| B6 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_booster_as_container_target_rejected` | Erreur métier dédiée (nom à figer dans l’implémentation) |
| B7 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_child_already_has_parent_rejected` | `ProductAlreadyHasParentError` |
| B8 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_cycle_prevention_uses_ancestor_rules` | `CircularProductParentageError` si tentative invalide |
| B9 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_missing_reference_when_creating_child_raises` | Erreur métier dédiée si ref absente |
| B10 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_duplicate_internal_barcode_on_create_raises` | `DuplicateInternalBarcodeError` si applicable |
| B11 | P0 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_no_card_reveal_events_emitted` | Aucun appel `record_card_revealed_from_opening` / `record_opening_card_scan` sur le spy événements |
| B12 | P1 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_container_decondition_event_recorded` | `record_container_deconditioned` ou entrée ledger kind dédié (contrat à figer) |
| B13 | P2 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_partial_children_allowed_five_of_fifteen` | Pas d’erreur pour commande partielle si spec OK |
| B14 | P2 | `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | `test_idempotent_second_call_fails_or_noop` | Selon spec : enfants déjà liés → erreur |

---

## Lot C — Consultation & historique

| ID | Priorité | Fichier de test | Méthode (nom cible) | Comportement à vérifier |
|----|----------|-----------------|---------------------|-------------------------|
| C1 | P0 | `tests/baobab_mtg_products/services/query/test_structural_view_after_deconditioning.py` | `test_parent_lists_all_deconditioned_children` | `GetProductStructuralViewService` : `direct_children` + `child_references` alignés |
| C2 | P0 | `tests/baobab_mtg_products/use_cases/history/test_timeline_includes_container_deconditioned.py` | `test_timeline_lists_decondition_event_for_container` | `GetProductBusinessTimelineService` / ledger : kind déconditionnement présent |

---

## Lot D — Non-régression croisée

| ID | Priorité | Fichier de test | Méthode (nom cible) | Comportement à vérifier |
|----|----------|-----------------|---------------------|-------------------------|
| D1 | P1 | `tests/baobab_mtg_products/use_cases/opening/test_open_sealed_product_use_case.py` | *(existant + 1 cas si besoin)* | Ouverture booster inchangée ; pas de régression après ajout statuts |
| D2 | P1 | `tests/baobab_mtg_products/use_cases/parent_child/test_attach_child_product_to_parent_use_case.py` | *(existant)* | Règles attach toujours valides si déconditionnement réutilise les mêmes garde-fous |

---

## Ordre d’implémentation recommandé

1. Statuts / kinds / port événement + ledger (débloque A1, A2, B12, C2).  
2. DTO commande (A3, A4).  
3. `DeconditionContainerUseCase` + fakes (B*).  
4. Services query / timeline (C*).  
5. Retirer `pytest.mark.skip` sur les fichiers placeholder et implémenter les corps.

## Fichiers placeholder (skip global)

| Fichier | Statut |
|---------|--------|
| `tests/baobab_mtg_products/use_cases/deconditioning/test_decondition_container_use_case.py` | Skip module jusqu’à feature 12 |
| `tests/baobab_mtg_products/domain/deconditioning/test_product_status_deconditioned.py` | Skip si enum pas encore étendu |
| `tests/baobab_mtg_products/domain/history/test_product_business_event_kind_deconditioning.py` | Skip si kind pas encore ajouté |
| `tests/baobab_mtg_products/domain/deconditioning/test_decondition_container_command.py` | Skip si DTO absent |
| `tests/baobab_mtg_products/domain/deconditioning/test_deconditionable_container_types.py` | Skip si module règles absent |
| `tests/baobab_mtg_products/services/query/test_structural_view_after_deconditioning.py` | Skip jusqu’à use case |
| `tests/baobab_mtg_products/use_cases/history/test_timeline_includes_container_deconditioned.py` | Skip jusqu’à événement |

---

_Lors de l’implémentation, remplacer les `skip` par les assertions réelles et ajuster noms d’exceptions / méthodes port au code livré._
