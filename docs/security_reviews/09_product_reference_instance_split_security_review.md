# Revue sécurité — 09_product_reference_instance_split — Séparation référence produit / instance physique

**Branche analysée :** `feature/product-reference-instance-split`  
**Date de revue :** 2026-05-01  
**Avis retenu (revue code) :** **GO avec réserves non bloquantes**  
**Avis documentation (post-intégration 2026-05-01) :** **GO documentation**

## Avis sécurité

Les changements restent une couche domaine et ports sans accès fichier, sans exécution de commandes et sans nouvelle dépendance runtime. Les critères de refus (exécution de commande, chemin non contrôlé, ambiguïté de scan sans signal explicite côté résolution catalogue) ne sont pas franchis dans ce dépôt, sous réserve que les implémentations des ports respectent les contrats documentés (unicité référence par code-barres commercial en V1, levée d’exceptions en cas d’ambiguïté, cohérence instance ↔ référence). Ces contrats sont désormais détaillés dans la section **Décisions sécurité et intégrité des données** et dans le `README.md`.

## Surface d'exposition analysée

- **Modèle :** `ProductReference`, `ProductReferenceId`, `ProductInstance` (champs dénormalisés `product_type` / `set_code`), `ResolvedFromScan` (`display_name`, `image_uri`), `SealedProductSnapshot`, `ProductStructuralView`.
- **Orchestration :** `RegistrationFromScanRunner` (scan commercial / interne, matérialisation référence + instance, événements `record_scan` / `record_registration`).
- **Consultation :** `GetProductStructuralViewService`, `GetSealedProductSnapshotService`.
- **Ports :** `ProductReferenceRepositoryPort`, `ProductReferenceIdFactoryPort`, `BarcodeResolutionPort` (contrat d’ambiguïté inchangé).
- **Intégration :** `ProductProvenanceForCollection` (champ `product_reference_id`).
- **Exceptions :** nouvelles erreurs métier (messages génériques).
- **Configuration :** `pyproject.toml` (version semver, dépendances runtime inchangées).
- **Analyse statique :** `bandit` sur `src/baobab_mtg_products`.

## Risques identifiés

| Risque | Gravité | Fichier / zone | Recommandation |
|--------|---------|----------------|----------------|
| `find_by_commercial_barcode` retourne une seule référence ; si la persistance autorise plusieurs références pour le même GTIN et que l’adaptateur en choisit une sans erreur, une instance peut être rattachée à une mauvaise référence. | Moyenne (métier / intégrité) | `ProductReferenceRepositoryPort`, adaptateurs | Voir décision 1 ci-dessous. |
| Champs dénormalisés sur `ProductInstance` peuvent diverger de `ProductReference` si la persistance est incorrecte. | Moyenne (confusion métier) | `ProductInstance`, adaptateurs | Voir décision 2 ci-dessous. |
| `image_uri` et noms catalogue sans borne stricte côté domaine : usages réseau ou UI. | Faible à moyenne selon contexte | `ProductReference`, `ResolvedFromScan`, runner d’enregistrement | Voir décision 3 ci-dessous. |
| Valeurs scannées passées à `record_scan` (journaux / SI tiers). | Faible (fuite contextuelle) | `RegistrationFromScanRunner`, `ProductWorkflowEventRecorderPort` | Voir décision 4 ci-dessous. |

## Validation des entrées

- **`ProductReferenceId` :** normalisation (`strip`), non vide, longueur maximale — cohérent avec `InternalProductId`.
- **`CommercialBarcode` :** chiffres uniquement, longueur bornée.
- **`InternalBarcode` :** longueur max et motif alphanumérique contrôlé.
- **`ProductReference` :** nom non vide après `strip` ; `image_uri` optionnelle normalisée sans validation de schéma URL au domaine (volontaire ; responsabilité applicative).
- **Ambiguïté catalogue :** `BarcodeResolutionPort` impose la levée de `AmbiguousBarcodeResolutionError` ; le runner ne l’absorbe pas.

## Gestion des erreurs et journaux

- Exceptions métier : messages fixes, sans concaténation d’identifiants arbitraires dans les libellés observés.
- Pas de module `logging` dans le package source analysé ; la sensibilité porte sur les données transmises aux ports d’événements.

## Dépendances et appels externes

- Aucune dépendance runtime ajoutée dans `pyproject.toml` pour cette feature.
- Les ports restent abstraits (`Protocol`), sans I/O imposée au cœur métier.

## Points à corriger avant merge

Aucun correctif sécurité bloquant identifié dans le code de la feature au sens des règles de décision initiales. Les réserves portent sur les implémentations futures des ports.

**Documentation** : les décisions ci-dessous sont intégrées dans le dépôt (`README.md`, `docs/features/09_product_reference_instance_split.md`, `docs/002_product_reference_instance_persistence_guidance.md`, section homonyme dans la présente revue).

## Points à surveiller avant release

- Comportement déterministe des adaptateurs de `ProductReferenceRepositoryPort`.
- Traitement applicatif sécurisé des champs descriptifs (`image_uri`, noms).
- Cohérence données lors des migrations ou imports de masse (instance ↔ référence).

## Bandit

Exécution sur `src/baobab_mtg_products` : **aucun problème signalé** (profil par défaut).

---

## Décisions sécurité et intégrité des données

Règles **normatives** pour les adaptateurs et les applications consommatrices. Le package domaine ne réalise pas d’E/S ni de choix de persistance.

- **Résolution par code-barres commercial (V1)** : un code-barres commercial doit résoudre au **maximum une seule** `ProductReference`.
- **`find_by_commercial_barcode`** : une implémentation de `ProductReferenceRepositoryPort.find_by_commercial_barcode` ne doit **jamais** choisir arbitrairement une référence en cas de doublon en base.
- **Ambiguïté ou corruption** : en présence de plusieurs références pour un même GTIN, ou de données incohérentes, l’adaptateur doit lever une **erreur métier explicite** plutôt que de poursuivre avec un choix silencieux.
- **Dénormalisation** : `product_type` et `set_code` sur `ProductInstance` sont des **copies techniques dénormalisées** issues de la `ProductReference` liée.
- **Cohérence persistance** : les adaptateurs doivent **préserver ou vérifier** l’alignement entre l’instance et sa référence (lectures, écritures, migrations).
- **`image_uri`** : ne pas l’utiliser pour un **fetch serveur** sans garde-fous (allowlist, validation de schéma, timeouts, quotas).
- **Risques applicatifs** : protection contre **SSRF**, **XSS** et ressources **externes non fiables** lorsque noms, URIs ou contenus catalogue sont exposés ou suivis.
- **`record_scan`** : les charges passées à `ProductWorkflowEventRecorderPort.record_scan` peuvent être **sensibles** ; chaque implémentation du port doit définir une **politique** de journalisation, **masquage**, **hachage** ou **rétention**.

Ces points ne bloquent pas le merge de la feature `09_product_reference_instance_split` au regard du code livré ; ils **contraignent** les implémentations des ports et la documentation utilisateur (désormais alignée dans le dépôt).

### Correspondance `SerialNumber` / `production_code`

Dans le domaine Python actuel, l’attribut le plus proche du « code de production » du cahier des charges est **`SerialNumber`**. La feature **`10_physical_instance_creation_and_production_code`** tranchera renommage ou introduction d’un value object dédié. Les colonnes SQL nommées `production_code` dans les notes d’architecture restent **indicatives** et se mappent vers **`SerialNumber`** tant que la feature 10 n’a pas clarifié le modèle.
