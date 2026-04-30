# Cahier des charges — baobab-mtg-products

## Description courte

`baobab-mtg-products` gère les produits scellés Magic: The Gathering : références produits, instances physiques, scans, codes de production non uniques, relations parent/enfant, déconditionnement de contenants, ouverture de produits, traçabilité des cartes obtenues et contrats de persistance. La librairie doit relier l’achat réel, les produits physiques, leur provenance et les cartes révélées, sans gérer l’interface graphique, l’API HTTP, les règles du jeu ni le deckbuilding.

## 1. Objet

`baobab-mtg-products` est une librairie Python métier dédiée à la représentation et à la gestion des produits scellés Magic: The Gathering ainsi qu’à leur cycle de vie : création de références produits, création d’instances physiques, enregistrement par scan, qualification, rattachement, déconditionnement, ouverture et traçabilité des cartes obtenues.

La librairie doit servir de brique métier indépendante, centrée sur le scellé et non sur l’API, l’interface graphique, la possession globale ou les règles du jeu.

## 2. Objectifs

Objectif principal : fournir une librairie Python stable, testable et typée permettant de gérer la provenance produit et la traçabilité d’ouverture des produits scellés Magic: The Gathering.

Objectifs secondaires :

- modéliser les références de produits scellés, par exemple une display d’un set donné, avec son nom, son image et son code-barres commercial ;
- modéliser les instances physiques réelles, par exemple deux displays achetées ayant le même code-barres commercial et le même code de production ;
- permettre l’enregistrement de plusieurs exemplaires physiques d’un même produit commercial ;
- gérer un code de production non unique ;
- conserver les relations parent/enfant entre produits physiques ;
- distinguer le déconditionnement d’un contenant de l’ouverture d’un produit révélant des cartes ;
- gérer l’ouverture d’un produit et l’association des cartes révélées ;
- exposer des cas d’usage métier clairs plutôt qu’un simple CRUD technique ;
- rester indépendante de l’API, du front, du moteur de règles, du deckbuilder et des implémentations concrètes de base de données.

## 3. Périmètre fonctionnel

### 3.1 Inclus dans le périmètre

Sont inclus dans le périmètre :

- les types de produits scellés ;
- les références commerciales ou éditoriales de produits ;
- les instances physiques de produits achetés, scannés ou découverts dans un contenant ;
- les statuts métier d’un produit ;
- le code de production éventuel, explicitement non unique ;
- le set associé ;
- le code-barres commercial, explicitement non unique au niveau des instances ;
- le code-barres interne éventuel, unique lorsqu’il est généré par l’application ;
- l’image et le nom d’un produit au niveau de la référence produit ou d’une couche de présentation associée ;
- les relations parent/enfant entre instances physiques ;
- le déconditionnement d’un contenant pour accéder à ses sous-produits ;
- l’ouverture d’un produit scellé révélant des cartes ;
- le rattachement des cartes ouvertes à leur produit d’origine ;
- les historiques et événements liés au produit ;
- les ports de persistance permettant à une application d’insérer les données dans une base SQL, NoSQL ou autre ;
- les cas d’usage d’enregistrement, création d’instance, rattachement, qualification, déconditionnement, ouverture et traçabilité.

### 3.2 Exclus du périmètre

Sont exclus du périmètre :

- le référentiel complet des cartes à lui seul ;
- la possession globale d’un usager ;
- le rangement physique en boîte ;
- les règles d’une partie de Magic ;
- la construction de deck ;
- l’exposition HTTP ;
- l’interface graphique ;
- une implémentation obligatoire de base de données dans le cœur métier ;
- l’imposition d’un ORM ou d’un moteur SQL précis.

## 4. Positionnement dans l’architecture

`baobab-mtg-products` se positionne entre le catalogue, la collection et les briques de statistiques/probabilité. Elle doit pouvoir être consommée par `baobab-mtg-platform`, `baobab-mtg-api`, la collection et les briques statistiques, tout en restant découplée du moteur de règles et du deckbuilder.

Les dépendances naturelles autorisées sont notamment `baobab-mtg-catalog`, `baobab-barcode` et, si nécessaire, une brique de collection via interface.

La librairie ne doit pas dépendre directement d’une base de données. Elle doit définir des ports de persistance suffisamment explicites pour permettre à une application consommatrice d’implémenter un adaptateur SQLite, PostgreSQL, SQLAlchemy, Django ORM, MongoDB ou tout autre stockage.

## 5. Concepts métier structurants

### 5.1 ProductReference

Une `ProductReference` représente un produit commercial ou éditorial, indépendamment de l’exemplaire physique détenu par l’utilisateur.

Exemples :

- une display de 15 boosters d’un set donné ;
- un bundle d’un set donné ;
- un play booster d’un set donné.

Attributs minimaux attendus :

- `reference_id` : identifiant interne unique de la référence ;
- `name` : nom lisible du produit ;
- `image_uri` : image représentative du produit, URL ou chemin applicatif ;
- `product_type` : type de produit ;
- `set_code` : code du set Magic ;
- `commercial_barcode` : code-barres commercial éventuel ;
- métadonnées extensibles si nécessaire.

Règles importantes :

- une référence produit n’est pas un exemplaire physique ;
- le code-barres commercial sert à résoudre ou proposer une référence produit ;
- le code-barres commercial ne doit pas être utilisé comme identifiant unique d’une instance physique ;
- selon les besoins réels, plusieurs références peuvent être associées à des codes-barres différents, ou une référence peut être enrichie ultérieurement par plusieurs codes-barres commerciaux.

### 5.2 ProductInstance

Une `ProductInstance` représente un exemplaire physique réellement possédé, scanné, créé ou découvert dans l’application.

Attributs minimaux attendus :

- `internal_id` : identifiant interne unique de l’instance physique ;
- `reference_id` : lien vers la référence produit ;
- `product_type` : type redondant autorisé seulement si utile pour simplifier les règles métier ;
- `set_code` : set redondant autorisé seulement si utile pour simplifier les règles métier ;
- `production_code` : code de production éventuel, non unique ;
- `internal_barcode` : code interne éventuel, unique s’il existe ;
- `status` : statut métier ;
- `parent_id` : identifiant de l’instance parent éventuelle.

Règles importantes :

- `internal_id` est la seule clé métier unique obligatoire pour une instance physique ;
- plusieurs instances peuvent partager le même `commercial_barcode` via leur `ProductReference` ;
- plusieurs instances peuvent partager le même `production_code`, y compris pour un même type de produit ;
- `production_code` ne doit jamais être considéré comme un numéro de série unique ;
- `internal_barcode`, lorsqu’il est généré par l’application, peut être unique et servir à retrouver directement une instance physique.

### 5.3 ProductionCode

Le code de production est une information de traçabilité industrielle ou logistique.

Contraintes :

- il est optionnel ;
- il n’est pas unique ;
- il peut être identique pour plusieurs displays, bundles ou boosters ;
- il peut être identique au sein d’un même type de produit ;
- il doit être indexable pour recherche, mais sans contrainte d’unicité.

Le nom `SerialNumber` ne doit être conservé que si la documentation précise clairement qu’il ne s’agit pas d’un numéro de série unique. Le nom métier recommandé est `ProductionCode` ou `ProductProductionCode`.

### 5.4 Code-barres commercial

Le code-barres commercial, par exemple EAN ou UPC, identifie généralement une référence vendue dans le commerce. Il ne doit pas identifier un exemplaire physique unique.

Règles :

- scanner deux displays identiques avec le même EAN doit permettre de créer deux `ProductInstance` différentes ;
- un scan commercial doit résoudre une référence produit ou demander sa qualification ;
- un scan commercial ne doit pas retourner automatiquement une instance existante comme s’il s’agissait du même objet physique ;
- seul un code-barres interne généré par l’application peut être utilisé comme identifiant direct d’une instance.

### 5.5 Déconditionnement d’un contenant

Le déconditionnement correspond à l’action d’ouvrir un contenant pour accéder aux sous-produits qu’il contient, sans nécessairement révéler des cartes.

Exemples :

- ouvrir une display pour sortir ses 15 boosters ;
- ouvrir un bundle pour accéder à ses sous-produits ;
- ouvrir un prerelease kit pour créer les boosters ou accessoires qu’il contient.

Le déconditionnement doit être distingué de l’ouverture d’un booster révélant des cartes.

### 5.6 Ouverture d’un produit révélant des cartes

L’ouverture correspond à l’action de rompre le scellé d’un produit pour révéler des cartes ou contenus traçables.

Exemples :

- ouvrir un play booster ;
- ouvrir un collector booster ;
- ouvrir tout produit dont le contenu carte doit être rattaché à sa provenance.

## 6. Exigences fonctionnelles détaillées

### 6.1 Modélisation des types de produits

Le système doit proposer une représentation explicite des types de produits scellés au moyen d’une énumération ou d’une hiérarchie dédiée, couvrant au minimum : display, play booster, collector booster, draft booster, set booster, bundle, prerelease kit, commander deck et autres produits scellés retenus dans le périmètre.

### 6.2 Modélisation des références produits

La librairie doit permettre de représenter une référence produit avec au minimum : nom, image, type, set, code-barres commercial et identifiant interne de référence.

Cette référence doit pouvoir être créée manuellement par l’application lorsqu’un produit est inconnu, puis réutilisée pour créer plusieurs instances physiques.

### 6.3 Modélisation des instances physiques

La librairie doit permettre de représenter un produit réel avec, au minimum, les attributs suivants : identifiant interne unique, lien vers une référence produit, code de production éventuel non unique, code-barres interne éventuel, statut et parent éventuel.

Le modèle doit garantir que plusieurs instances physiques puissent partager :

- le même code-barres commercial ;
- la même référence produit ;
- le même type de produit ;
- le même code de set ;
- le même code de production.

### 6.4 Enregistrement d’une référence produit

La librairie doit fournir un cas d’usage permettant de créer ou qualifier une référence produit à partir des informations saisies par l’utilisateur : code-barres commercial, image, type, code du set et nom.

Ce cas d’usage doit permettre :

- de créer une nouvelle référence produit ;
- de compléter une référence inconnue ;
- de résoudre un code-barres commercial vers une référence ;
- de détecter les cas ambigus et de les signaler explicitement.

### 6.5 Création d’une instance physique

La librairie doit fournir un cas d’usage dédié, par exemple `CreateProductInstanceUseCase`, permettant de créer un nouvel exemplaire physique à partir d’une référence produit.

Ce cas d’usage doit permettre :

- de créer plusieurs instances pour une même référence ;
- d’associer un code de production non unique ;
- d’associer éventuellement un code-barres interne unique ;
- d’initialiser le statut métier ;
- d’émettre un événement d’enregistrement d’instance.

### 6.6 Enregistrement par scan commercial

La librairie doit fournir un workflow de scan commercial compatible avec la création de plusieurs exemplaires physiques d’un même produit.

Règle obligatoire : scanner un code-barres commercial déjà connu ne doit pas empêcher la création d’une nouvelle instance physique.

Le workflow recommandé est :

1. scanner le code-barres commercial ;
2. résoudre ou créer la `ProductReference` ;
3. demander les informations complémentaires si nécessaire ;
4. créer une nouvelle `ProductInstance` si l’utilisateur enregistre un nouvel exemplaire ;
5. associer le code de production éventuel ;
6. enregistrer les événements de scan et de création.

### 6.7 Enregistrement par scan interne

Le scan d’un code-barres interne doit permettre de retrouver directement une instance physique déjà créée, à condition que le code interne soit unique.

Si le code interne est inconnu, la librairie doit pouvoir signaler le cas explicitement.

### 6.8 Gestion des relations entre produits

La librairie doit être capable de représenter les relations structurantes entre instances physiques, notamment :

- display vers boosters contenus ;
- bundle vers sous-produits ;
- prerelease kit vers sous-produits ;
- booster indépendant sans parent.

Les rattachements doivent toujours concerner des `ProductInstance`, jamais uniquement des `ProductReference`.

### 6.9 Déconditionnement d’un contenant

La librairie doit exposer un cas d’usage distinct, par exemple `DeconditionContainerUseCase`, pour gérer l’ouverture d’un contenant et la création ou le rattachement des produits enfants.

Ce cas d’usage doit permettre :

- de marquer un contenant comme déconditionné si un statut dédié est retenu ;
- de créer ou rattacher les produits enfants découverts ;
- de tracer l’événement de déconditionnement ;
- de reprendre la boucle d’enregistrement sur chaque produit enfant ;
- d’éviter de confondre cette action avec l’ouverture d’un booster révélant des cartes.

### 6.10 Ouverture et traçabilité des cartes

La librairie doit exposer un cas d’usage d’ouverture, par exemple `OpenSealedProductUseCase`, permettant de marquer un produit ouvrable comme ouvert, d’enregistrer l’événement d’ouverture, de lier les cartes révélées au produit ouvert, de tracer les scans des cartes ouvertes et de transmettre les résultats à la collection et aux statistiques par des interfaces adaptées.

Ce cas d’usage doit être réservé aux produits dont l’ouverture produit un contenu traçable, notamment des cartes.

### 6.11 Traçabilité

Le système doit conserver l’historique des événements métier relatifs à un produit, au minimum :

- référence créée ou qualifiée ;
- instance créée ;
- produit scanné ;
- instance qualifiée ;
- code de production associé ;
- produit rattaché à un parent ;
- produit détaché d’un parent ;
- contenant déconditionné ;
- produit ouvert ;
- cartes associées au contenu.

## 7. Cas d’usage minimum à couvrir

### 7.1 Achat de plusieurs produits scellés

Le système doit couvrir le scénario suivant :

- l’utilisateur achète deux displays de 15 boosters et un bundle ;
- pour chaque produit principal, il saisit ou scanne le code-barres commercial ;
- il associe une image, un type de produit, un code de set et un nom ;
- il enregistre le code de production du produit ;
- le code de production peut être identique entre plusieurs produits ;
- chaque display et chaque bundle devient une instance physique distincte ;
- l’utilisateur peut déconditionner une display ;
- les boosters découverts sont créés comme instances physiques enfants de la display ;
- le même workflow se répète pour chaque enfant ;
- si un booster est ouvert, les cartes révélées sont rattachées au booster ouvert.

### 7.2 Cas d’usage unitaires

La librairie doit couvrir au minimum :

- créer une référence produit à partir d’un code-barres commercial, d’un nom, d’une image, d’un type et d’un set ;
- créer deux instances physiques à partir d’une même référence ;
- associer le même code de production à plusieurs instances ;
- enregistrer une display scannée pour la première fois ;
- enregistrer une deuxième display ayant le même code-barres commercial que la première ;
- rattacher des boosters à une display ;
- enregistrer un booster scanné hors display ;
- déconditionner une display sans révéler directement de cartes ;
- ouvrir un booster ;
- lier des cartes scannées au booster ouvert ;
- fournir l’information de provenance à la collection ;
- fournir les événements d’ouverture au moteur statistique.

## 8. Persistance et insertion en base de données

### 8.1 Principe général

La librairie doit permettre l’insertion en base de données par architecture, via des ports de persistance, sans embarquer obligatoirement d’implémentation SQLite, PostgreSQL ou ORM dans le cœur métier.

Le cœur de la librairie doit définir des contrats, par exemple :

- `ProductReferenceRepositoryPort` ;
- `ProductInstanceRepositoryPort` ou `ProductRepositoryPort` enrichi ;
- `ProductRelationshipRepositoryPort` si les relations sont séparées ;
- `ProductBusinessHistoryRepositoryPort` ou port de journalisation ;
- `RevealedCardTraceRepositoryPort`.

Une application consommatrice doit pouvoir fournir ses adaptateurs concrets.

### 8.2 Contraintes de persistance

Les contraintes minimales recommandées sont :

- `product_reference.reference_id` unique ;
- `product_instance.internal_id` unique ;
- `product_instance.internal_barcode` unique lorsqu’il est renseigné ;
- `product_reference.commercial_barcode` indexable, mais pas utilisé comme clé unique d’instance ;
- `product_instance.production_code` indexable, mais jamais unique ;
- `product_instance.parent_id` indexable ;
- les liens parent/enfant doivent référencer des instances physiques.

### 8.3 Exemple conceptuel de schéma SQL

Ce schéma est indicatif et ne doit pas imposer une dépendance SQL à la librairie.

```sql
CREATE TABLE mtg_product_references (
    reference_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    image_uri TEXT NULL,
    product_type TEXT NOT NULL,
    set_code TEXT NOT NULL,
    commercial_barcode TEXT NULL
);

CREATE INDEX idx_product_references_commercial_barcode
    ON mtg_product_references(commercial_barcode);

CREATE TABLE mtg_product_instances (
    internal_id TEXT PRIMARY KEY,
    reference_id TEXT NOT NULL,
    status TEXT NOT NULL,
    production_code TEXT NULL,
    internal_barcode TEXT NULL UNIQUE,
    parent_id TEXT NULL,

    FOREIGN KEY(reference_id)
        REFERENCES mtg_product_references(reference_id),

    FOREIGN KEY(parent_id)
        REFERENCES mtg_product_instances(internal_id)
);

CREATE INDEX idx_product_instances_reference_id
    ON mtg_product_instances(reference_id);

CREATE INDEX idx_product_instances_production_code
    ON mtg_product_instances(production_code);

CREATE INDEX idx_product_instances_parent_id
    ON mtg_product_instances(parent_id);
```

Rappel : aucune contrainte `UNIQUE` ne doit être posée sur `production_code`.

## 9. Nouvelles features de développement

Les nouveaux éléments de la discussion doivent être traités comme des features additionnelles, indépendantes des features déjà livrées.

Les nouvelles features documentées dans `docs/features/` sont :

- `09_product_reference_instance_split.md` : séparation `ProductReference` / `ProductInstance` ;
- `10_physical_instance_creation_and_production_code.md` : création d’instances physiques et code de production non unique ;
- `11_commercial_and_internal_scan_workflow_refactor.md` : refonte des workflows de scan commercial et interne ;
- `12_container_deconditioning_workflow.md` : déconditionnement de contenants ;
- `13_persistence_contracts_database_insertion.md` : contrats de persistance pour insertion en base.

## 10. Exigences non fonctionnelles

### 10.1 Structure du projet

- Code source dans `src/baobab_mtg_products` ; tests dans `tests/` ; documentation dans `docs/`.
- L’arborescence des tests doit refléter celle du code source.
- Chaque classe doit être définie dans son propre fichier.

### 10.2 Style de développement

- Le projet doit adopter une programmation orientée objet.
- Les noms doivent respecter les conventions PEP 8 : classes en PascalCase ; fonctions, méthodes, variables et modules en snake_case ; constantes en UPPER_SNAKE_CASE.

### 10.3 Typage

- Toutes les fonctions et méthodes doivent être annotées, y compris les types de retour.
- Les attributs de classe et d’instance doivent être typés.
- La configuration mypy doit être stricte et tout le projet doit passer sans erreur.

### 10.4 Documentation

- Toutes les classes, méthodes et fonctions publiques doivent posséder des docstrings.
- Un `README.md` doit exister à la racine avec description, installation, usage, exemples, contribution et licence.
- Un `CHANGELOG.md` doit être maintenu.
- La documentation de développement doit être tenue dans `docs/`.

### 10.5 Journal de développement

- Un journal de développement doit être maintenu dans `docs/dev_diary.md`, avec des entrées triées par date décroissante et contenant les modifications, buts et impacts.

### 10.6 Gestion des exceptions

- Le projet doit définir une exception racine propre à la librairie, par exemple `BaobabMtgProductsException`, dans un module `exceptions`.
- Toutes les exceptions spécifiques doivent hériter de cette base et être organisées de manière hiérarchique par domaine métier.
- Les erreurs spécifiques au projet doivent faire l’objet d’exceptions spécifiques et explicites.

### 10.7 Qualité du code

- Le code doit passer sans erreur `black`, `pylint`, `mypy`, `flake8` et `bandit`.
- La longueur maximale des lignes doit être fixée à 100 caractères.
- Toute la configuration des outils doit être centralisée dans `pyproject.toml`.

### 10.8 Tests

- Chaque classe doit avoir son fichier de tests correspondant.
- Les tests doivent être organisés en classes de test.
- Les classes abstraites doivent être testées via des implémentations concrètes dédiées aux tests.
- La couverture minimale attendue est de 95 %, avec génération des rapports dans `docs/tests/coverage`.
- Les tests doivent couvrir explicitement les cas suivants :
  - deux instances avec le même code-barres commercial ;
  - deux instances avec le même code de production ;
  - création d’une nouvelle instance à partir d’une référence déjà connue ;
  - scan commercial connu créant une nouvelle instance physique ;
  - scan interne retrouvant une instance physique existante ;
  - déconditionnement d’une display sans ouverture de cartes ;
  - ouverture d’un booster avec traçabilité des cartes.

### 10.9 Dépendances

- Les dépendances doivent être séparées entre production et développement dans `pyproject.toml`.
- Les versions doivent être contraintes de manière précise avec une stratégie du type `>=x.y.z,<next_major`.
- Les dépendances runtime doivent rester limitées au strict nécessaire.
- Aucune dépendance de base de données ne doit être imposée au cœur métier.

### 10.10 Versioning

- Le projet doit suivre strictement le versioning sémantique `MAJOR.MINOR.PATCH`.
- La version doit être portée dans `pyproject.toml`.
- Chaque release doit être taguée avec le format `vMAJOR.MINOR.PATCH`.
- Les nouvelles features postérieures à `1.0.1` doivent donner lieu à une version mineure ou majeure selon la compatibilité de l’API publique.

## 11. Exigences d’architecture

### 11.1 Indépendance

La librairie doit rester indépendante de l’API, du front, du moteur de règles, du deckbuilder et des implémentations concrètes de persistance.

### 11.2 Orientée cas d’usage

L’API interne de la librairie doit exposer des services ou cas d’usage métier explicites, et non un simple CRUD générique.

Cas d’usage attendus ou recommandés :

- `CreateProductReferenceUseCase` ;
- `ResolveProductReferenceFromCommercialBarcodeUseCase` ;
- `CreateProductInstanceUseCase` ;
- `AssignProductionCodeToProductInstanceUseCase` si le code de production est saisi après création ;
- `RegisterProductByCommercialScanUseCase`, corrigé pour ne pas confondre référence et instance ;
- `RegisterProductByInternalScanUseCase` ;
- `AttachChildProductToParentUseCase` ;
- `DetachChildProductFromParentUseCase` ;
- `DeconditionContainerUseCase` ;
- `OpenSealedProductUseCase` ;
- `RegisterRevealedCardFromOpeningUseCase` ;
- `RecordOpeningCardScanUseCase`.

### 11.3 Pilotage par scan

La conception doit être compatible avec un fonctionnement piloté par scan de code-barres.

Elle doit permettre de distinguer clairement :

- code-barres commercial connu ;
- code-barres commercial inconnu ;
- référence produit connue ;
- référence produit à qualifier ;
- nouvelle instance physique à créer ;
- instance physique connue par code interne ;
- produit rattaché ;
- contenant déconditionné ;
- produit ouvert.

### 11.4 Identifiants

Chaque entité métier principale doit disposer d’un identifiant interne unique, stable et exploitable.

Règle centrale : l’unicité d’une instance physique repose sur `internal_id`, pas sur le code-barres commercial ni sur le code de production.

### 11.5 Compatibilité base de données

Les ports doivent être conçus pour être implémentables simplement par un adaptateur de base de données.

La librairie peut fournir des exemples ou adaptateurs mémoire pour tests, mais ne doit pas imposer de moteur de stockage.

## 12. Proposition de structure logique

Une structure cible cohérente pourrait être la suivante :

- `src/baobab_mtg_products/domain/references/`
- `src/baobab_mtg_products/domain/products/`
- `src/baobab_mtg_products/domain/production/`
- `src/baobab_mtg_products/domain/products/relationships/`
- `src/baobab_mtg_products/domain/deconditioning/`
- `src/baobab_mtg_products/domain/opening/`
- `src/baobab_mtg_products/domain/history/`
- `src/baobab_mtg_products/use_cases/references/`
- `src/baobab_mtg_products/use_cases/instances/`
- `src/baobab_mtg_products/use_cases/registration/`
- `src/baobab_mtg_products/use_cases/parent_child/`
- `src/baobab_mtg_products/use_cases/deconditioning/`
- `src/baobab_mtg_products/use_cases/opening/`
- `src/baobab_mtg_products/services/query/`
- `src/baobab_mtg_products/ports/`
- `src/baobab_mtg_products/exceptions/`

## 13. Livrables attendus

- le code source de la librairie ;
- les objets métier `ProductReference` et `ProductInstance` ;
- les cas d’usage de référence, instance, scan, rattachement, déconditionnement et ouverture ;
- les ports de persistance ;
- les tests unitaires ;
- le `pyproject.toml` configuré ;
- le `README.md` ;
- le `CHANGELOG.md` ;
- le journal `docs/dev_diary.md` ;
- la documentation technique utile ;
- les rapports de couverture dans `docs/tests/coverage`.

## 14. Workflow de développement attendu

Le développement doit être mené avec une branche dédiée par fonctionnalité.

Les messages de commit doivent suivre les Conventional Commits.

Toute fonctionnalité doit être accompagnée de ses tests, de sa documentation utile, et d’une entrée dans le journal de développement.

Les nouvelles features doivent être développées après analyse d’impact sur l’API publique existante. Si elles cassent volontairement la compatibilité du modèle `ProductInstance`, la montée de version doit être majeure.

## 15. Critères de validation globale

Le projet est considéré conforme lorsque :

- tous les tests passent ;
- la couverture minimale est atteinte ;
- `black`, `pylint`, `mypy`, `flake8` et `bandit` passent sans erreur ;
- le package est installable ;
- les cas d’usage métier minimum sont couverts ;
- les erreurs métier sont explicites ;
- la librairie reste indépendante des interfaces externes ;
- plusieurs instances physiques d’une même référence peuvent être créées ;
- le même code de production peut être associé à plusieurs instances ;
- le scan commercial ne confond plus référence produit et instance physique ;
- l’insertion en base de données est possible via des ports de persistance ;
- le déconditionnement d’un contenant est distingué de l’ouverture d’un booster ou produit révélant des cartes.

## 16. Valeur attendue

La librairie doit devenir la brique métier qui relie de manière fiable un achat réel, une référence commerciale, un produit scellé réel, sa provenance physique, son éventuel déconditionnement, son ouverture réelle et les cartes réellement obtenues.

C’est cette traçabilité qui doit permettre l’intégration cohérente avec la collection, les statistiques d’ouverture et les applications utilisatrices.
