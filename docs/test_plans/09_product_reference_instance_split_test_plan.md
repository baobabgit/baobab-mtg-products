# Plan de test — 09_product_reference_instance_split — Séparation référence produit / instance physique

## Objectif de validation

Vérifier que le modèle et les flux respectent :

- la distinction **référence catalogue** (`ProductReference` + `ProductReferenceId`) et **exemplaire physique** (`ProductInstance` + identifiant interne unique obligatoire) ;
- le partage d’une même référence par **plusieurs instances** et la création d’une **nouvelle instance** lors d’un scan commercial résolvant une référence déjà persistée, **sans blocage** ;
- le rattachement d’une instance à une **référence résolue** dans les chemins métier livrés (pas d’instance sans `reference_id` dans le modèle actuel) ;
- la **cohérence consultation** : services qui joignent instance + référence et lèvent les **exceptions métier dédiées** si la référence attendue est absente du dépôt ;
- la **non-régression** des features dépendantes (enregistrement par scan, qualification, parent/enfant, ouverture, intégration collection, ports).

Tous les tests restent **déterministes**, avec **fakes / stubs de ports** (pas de base de données ni d’API externes).

## Règle V1 — code-barres commercial

En **V1** du produit :

- un **code-barres commercial** résout au plus **une** `ProductReference` via le dépôt (`find_by_commercial_barcode` → `Optional[ProductReference]`) ;
- le scénario **plusieurs références candidates** pour un même code-barres est **hors périmètre** de la feature 09 ;
- une **feature ultérieure** pourra introduire désambiguïsation catalogue ou enrichissement du contrat de persistance si le besoin métier apparaît.

Les tests de la 09 valident ce contrat **singleton** ; ils ne préparent pas de jeux « multi-références pour un même EAN ».

## Règle — dénormalisation `product_type` et `set_code` sur `ProductInstance`

Les champs **`product_type`** et **`set_code`** portés par `ProductInstance` (s’ils sont toujours présents sur l’agrégat) sont des **copies techniques dénormalisées** des attributs équivalents de la `ProductReference` liée par `reference_id`. Ils permettent aux règles métier existantes de s’exécuter sans joindre systématiquement la référence.

Les tests doivent vérifier l’alignement sur les **chemins métier supportés** :

1. **Création depuis référence** — ex. `RegistrationFromScanRunner._new_instance_for_existing_reference` : type et set de l’instance reflètent ceux de la référence au moment de la création.
2. **Qualification** — `QualifyScannedProductUseCase` : après exécution, la référence persistée et l’instance partagent les mêmes type et set choisis, et l’indicateur `requires_qualification` côté référence est cohérent avec le flux.
3. **Consultation** — services de requête qui chargent instance + référence : les informations lisibles de catalogue exposées proviennent bien de la `ProductReference` jointe ; l’instance reste utilisable pour les aspects structurels (parent, statut, identifiants).

Les écarts volontaires hors ces chemins (copies non resynchronisées) ne font pas partie du périmètre de test de la 09 sauf **régression** si un invariant existant est documenté ailleurs.

## Périmètre vs feature 10 — numéro de série / code de production

La **unicité du code de production**, les règles avancées autour de la **création d’instance physique** et les scénarios détaillés de **`serial_number`** / traçabilité fabricant relèvent principalement de la feature **`10_physical_instance_creation_and_production_code`**.

Pour la **09**, limiter les tests sur `serial_number` à :

- la **non-régression** : le champ peut toujours être passé à la création (ex. runner commercial avec référence existante) et est conservé sur l’instance comme aujourd’hui ;
- l’absence de régression sur les accesseurs / `derived_with` déjà couverts par les tests d’instance.

Ne pas développer ici une batterie dédiée à la collision, à la normalisation catalogue du numéro de série, ou à la politique de production.

## Matrice des règles métier à couvrir

| Règle | Tests nominaux | Tests d'erreur | Tests de non-régression |
|-------|----------------|----------------|-------------------------|
| Une `ProductReference` ne représente jamais un objet physique unique | Construction référence + plusieurs `ProductInstance` avec le même `reference_id` ; scan commercial avec référence déjà enregistrée → nouvelle instance | — | Ouverture, parent-enfant, provenance avec `reference_id` |
| Une `ProductInstance` a un `internal_id` unique | Identité domaine ; deux enregistrements → deux identifiants internes distincts (fake factory) | — | Port instance inchangé hormis rattachement `reference_id` |
| Plusieurs instances partagent une `ProductReference` | Deux appels `register_via_commercial` avec même résolution V1 barcode → même `reference_id`, `internal_id` différents | — | Tests runner « shared reference » |
| Code-barres commercial au niveau référence (V1 : au plus une ref par code) | Référence avec `commercial_barcode` ; lookup `find_by_commercial_barcode` avant nouvelle matérialisation | — | Distinction scan interne / commercial |
| Référence peut exister sans instance (modèle) | `ProductReference` persistée via fake sans créer d’instance — optionnel | — | Contrat port référence |
| Instance toujours liée à une référence dans le modèle livré | Construction `ProductInstance` avec `reference_id` obligatoire | `ProductReferenceNotFoundForWorkflowError` / `ProductReferenceNotFoundForQueryError` si dépôt sans ref | Pas de chemin métier public sans `reference_id` |
| Copies `product_type` / `set_code` alignées sur chemins supportés | Création depuis ref ; qualification ; snapshot / vue structurelle | Référence manquante en consultation | Règles qui ne lisent que l’instance inchangées |

## Tests unitaires à créer ou maintenir

**Déjà présents dans le dépôt (à conserver)**  

- `ProductReferenceId` — normalisation, vide, longueur max.  
- `ProductReference` — nom vide, `image_uri` vide → `None`, `derived_with`, optionnels.  
- `ProductInstance` — invariants, parent, `derived_with` (y compris conservation optionnelle de `serial_number` sans scénarios « production » lourds).  
- `ResolvedFromScan` — `is_complete`.  
- Ports structurels `ProductReferenceRepositoryPort`, `ProductRepositoryPort`.  
- DTO domaine `ProductStructuralView`, `SealedProductSnapshot`.

**Renforts recommandés (légers)**  

- `ProductReference.derived_with` avec nom vide / espaces → `InvalidProductReferenceError`.  
- Alignement dénormalisé : test ciblé après `derived_with` sur ref + instance dans un même scénario fictif si utile pour documenter le contrat (sans dupliquer toute la suite qualification).  
- Exceptions dédiées — assertions de type exact (`pytest.raises(..., match=...)`) là où le message stabilise le contrat.

## Tests de workflow à créer ou maintenir

**Déjà couverts**  

- `RegistrationFromScanRunner` — commercial avec référence existante, outcomes, collection.  
- `QualifyScannedProductUseCase` — mise à jour ref + instance, erreurs.  
- `GetProductStructuralViewService`, `GetSealedProductSnapshotService` — jointure ref, erreur ref manquante.

**À renforcer si besoin**  

- Enchaînement **deux scans commerciaux** même barcode (V1) → deux instances, une ref ; vérifier outcomes (`NEW_INSTANCE_SHARED_REFERENCE` / `NEW_PENDING_QUALIFICATION`).  
- **Qualification** — ordre et contenu des `save` sur les deux dépôts (fake).  
- **Consultation** — parent + enfants avec références résolues ; ordre stable des enfants.

## Cas limites

- Nom de référence vide ou espaces ; `image_uri` blanc.  
- `ProductReferenceId` longueur frontière (256 vs 257).  
- Runner commercial avec référence existante : `serial_number` `None` vs valeur fournie (**non-régression** uniquement pour la 09).  
- Consultation : référence centrale absente ; référence parent absente alors que le parent instance existe.

## Tests de non-régression

- **02** — enregistrement scan, résultats typés, événements.  
- **07** — services de consultation et DTO publics.  
- Relations **parent-enfant**, **ouverture**, **collection** — instanciation avec `ProductReferenceId`.  
- Exports package `baobab_mtg_products` cohérents.

## Risques de couverture

| Risque | Mitigation |
|--------|------------|
| Couverture ≥ 95 % | Suivre le rapport `coverage` ; compléter les branches des exceptions ou des `derived_with` si besoin. |
| Dérive type/set hors chemins supportés | Hors périmètre 09 sauf bug régression documenté ; la 10 et les specs persistance pourront renforcer les invariants. |

## Données de test recommandées

| Élément | Exemples |
|---------|----------|
| `ProductReferenceId` | `ref-mh3-play-booster-fr`, `ref-shared-display-fdn` |
| `InternalProductId` | `p-2026-00042`, `p-2026-00043` (même ref) |
| `CommercialBarcode` | EAN-13 fictif cohérent avec les value objects du projet |
| `InternalBarcode` | code entrepôt distinct par exemplaire |
| `MtgSetCode` | `MH3`, `FDN`, `BIG` |
| `ProductType` | `PLAY_BOOSTER`, `COLLECTOR_BOOSTER`, `DISPLAY`, `BUNDLE` |
| `SerialNumber` | une valeur stable pour **smoke** non-régression (détail métier → feature 10) |
| Référence partagée | une `ProductReference` avec `commercial_barcode` ; deux instances, `internal_id` différents |

## Synthèse

Ce plan cible la **séparation référence / instance**, le **contrat V1 barcode → au plus une référence**, la **dénormalisation contrôlée** `product_type` / `set_code`, et les **integrations workflow + consultation**, tout en **évitant** d’anticiper la feature **10** sur le code de production et les règles fines de `serial_number`.
