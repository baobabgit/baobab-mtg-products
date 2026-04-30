# Cahier des charges — baobab-mtg-products

## Description courte

baobab-mtg-products gère les produits scellés Magic: identification, enregistrement, relations parent/enfant, ouverture et traçabilité des cartes obtenues. Elle relie l’achat réel, le produit scellé, son ouverture et la provenance des cartes, sans gérer règles, deckbuilding ni exposition HTTP.

## 1. Objet

baobab-mtg-products est une librairie Python métier dédiée à la représentation et à la gestion des produits scellés Magic: The Gathering ainsi qu’à leur cycle de vie : enregistrement, qualification, rattachement, ouverture et traçabilité des cartes obtenues.

La librairie doit servir de brique métier indépendante, centrée sur le scellé et non sur l’API, l’interface graphique, la possession globale ou les règles du jeu.

## 2. Description courte du projet

baobab-mtg-products gère les produits scellés Magic: identification, enregistrement, relations parent/enfant, ouverture et traçabilité des cartes obtenues. Elle relie l’achat réel, le produit scellé, son ouverture et la provenance des cartes, sans gérer règles, deckbuilding ni exposition HTTP.

## 3. Objectifs

Objectif principal : fournir une librairie Python stable, testable et typée permettant de gérer la provenance produit et la traçabilité d’ouverture des produits scellés Magic: The Gathering.

Objectifs secondaires :

- Modéliser les types de produits scellés et leurs instances réelles.
- Gérer l’enregistrement d’un produit acheté ou scanné.
- Conserver les relations parent/enfant entre produits.
- Gérer l’ouverture d’un produit et l’association des cartes révélées.
- Exposer des cas d’usage métier clairs plutôt qu’un simple CRUD technique.
- Rester indépendante de l’API, du front, du moteur de règles et du deckbuilder.

## 4. Périmètre fonctionnel

Inclus dans le périmètre :

### Inclus dans le périmètre :

- les types de produits scellés ;
- les instances de produits achetés ou scannés ;
- les statuts métier d’un produit ;
- le numéro de série ;
- le set associé ;
- les relations parent/enfant entre produits ;
- le rattachement des cartes ouvertes à leur produit d’origine ;
- les historiques et événements liés au produit ;
- les cas d’usage d’enregistrement, rattachement, qualification, ouverture et traçabilité.

### Exclus du périmètre :

- le référentiel complet des cartes à elle seule ;
- la possession globale d’un usager ;
- le rangement physique en boîte ;
- les règles d’une partie de Magic ;
- la construction de deck ;
- l’exposition HTTP ;
- l’interface graphique.

## 5. Positionnement dans l’architecture

baobab-mtg-products se positionne entre le catalogue, la collection et les briques de statistiques/probabilité. Elle doit pouvoir être consommée par baobab-mtg-platform, baobab-mtg-api, la collection et les briques statistiques, tout en restant découplée du moteur de règles et du deckbuilder.

Les dépendances naturelles autorisées sont notamment baobab-mtg-catalog, baobab-barcode et, si nécessaire, une brique de collection via interface.

## 6. Exigences fonctionnelles détaillées

### 6.1 Modélisation des types de produits

- Le système doit proposer une représentation explicite des types de produits scellés au moyen d’une énumération ou d’une hiérarchie dédiée, couvrant au minimum : display, play booster, collector booster, bundle, prerelease kit et autres produits retenus dans le périmètre.

### 6.2 Modélisation d’une instance de produit

- Le système doit permettre de représenter un produit réel avec, au minimum, les attributs suivants : identifiant interne unique, type de produit, set associé, numéro de série éventuel, code-barres commercial, code-barres interne éventuel, statut et parent éventuel.

### 6.3 Enregistrement d’un produit

- La librairie doit fournir un cas d’usage permettant d’enregistrer un produit lorsqu’il est acheté ou scanné pour la première fois.
- Ce cas d’usage doit couvrir le scan du code-barres commercial ou interne, la détection d’un produit inconnu, la qualification du type de produit, l’association éventuelle à un set et l’enregistrement du numéro de série.

### 6.4 Gestion des relations entre produits

- La librairie doit être capable de représenter les relations structurantes entre produits, notamment : display vers boosters contenus, produit parent vers sous-produits, booster indépendant sans parent.

### 6.5 Gestion de l’ouverture

- La librairie doit exposer un cas d’usage d’ouverture permettant de marquer un produit ouvrable comme ouvert, d’enregistrer l’événement d’ouverture, de lier les cartes révélées au produit ouvert, de tracer les scans des cartes ouvertes et de transmettre les résultats à la collection et aux statistiques par des interfaces adaptées.

### 6.6 Traçabilité

- Le système doit conserver l’historique des événements métier relatifs à un produit, au minimum : produit enregistré, produit scanné, produit qualifié, produit rattaché à un parent, produit ouvert et cartes associées au contenu.

## 7. Concepts métier attendus

La conception doit intégrer des objets métier clairement identifiés, notamment ProductType, ProductInstance, ProductRelationship et ProductOpeningEvent.

Ces objets doivent être pensés pour refléter le domaine métier et non une simple persistance technique.

## 8. Cas d’usage minimum à couvrir

- enregistrer une display scannée pour la première fois ;
- rattacher des boosters à une display ;
- enregistrer un booster scanné hors display ;
- ouvrir un booster ;
- lier des cartes scannées au booster ouvert ;
- fournir l’information de provenance à la collection ;
- fournir les événements d’ouverture au moteur statistique.

## 9. Exigences non fonctionnelles

### 9.1 Structure du projet

- Code source dans src/baobab_mtg_products ; tests dans tests/ ; documentation dans docs/.
- L’arborescence des tests doit refléter celle du code source. Chaque classe doit être définie dans son propre fichier.

### 9.2 Style de développement

- Le projet doit adopter une programmation orientée objet.
- Les noms doivent respecter les conventions PEP 8 : classes en PascalCase ; fonctions, méthodes, variables et modules en snake_case ; constantes en UPPER_SNAKE_CASE.

### 9.3 Typage

- Toutes les fonctions et méthodes doivent être annotées, y compris les types de retour.
- Les attributs de classe et d’instance doivent être typés.
- La configuration mypy doit être stricte et tout le projet doit passer sans erreur.

### 9.4 Documentation

- Toutes les classes, méthodes et fonctions publiques doivent posséder des docstrings.
- Un README.md doit exister à la racine avec description, installation, usage, exemples, contribution et licence.
- Un CHANGELOG.md doit être maintenu. La documentation de développement doit être tenue dans docs/.

### 9.5 Journal de développement

- Un journal de développement doit être maintenu dans docs/dev_diary.md, avec des entrées triées par date décroissante et contenant les modifications, buts et impacts.

### 9.6 Gestion des exceptions

- Le projet doit définir une exception racine propre à la librairie, par exemple BaobabMtgProductsException, dans un module exceptions.
- Toutes les exceptions spécifiques doivent hériter de cette base et être organisées de manière hiérarchique par domaine métier.
- Les erreurs spécifiques au projet doivent faire l’objet d’exceptions spécifiques et explicites.

### 9.7 Qualité du code

- Le code doit passer sans erreur black, pylint, mypy, flake8 et bandit.
- La longueur maximale des lignes doit être fixée à 100 caractères.
- Toute la configuration des outils doit être centralisée dans pyproject.toml.

### 9.8 Tests

- Chaque classe doit avoir son fichier de tests correspondant.
- Les tests doivent être organisés en classes de test.
- Les classes abstraites doivent être testées via des implémentations concrètes dédiées aux tests.
- La couverture minimale attendue est de 95 %, avec génération des rapports dans docs/tests/coverage.

### 9.9 Dépendances

- Les dépendances doivent être séparées entre production et développement dans pyproject.toml.
- Les versions doivent être contraintes de manière précise avec une stratégie du type >=x.y.z,<next_major.
- Les dépendances doivent rester limitées au strict nécessaire.

### 9.10 Versioning

- Le projet doit suivre strictement le versioning sémantique MAJOR.MINOR.PATCH.
- La version doit être portée dans pyproject.toml.
- Chaque release doit être taguée avec le format vMAJOR.MINOR.PATCH.

## 10. Exigences d’architecture

### 10.1 Indépendance

- La librairie doit rester indépendante de l’API, du front, du moteur de règles et du deckbuilder.

### 10.2 Orientée cas d’usage

- L’API interne de la librairie doit exposer des services ou cas d’usage métier explicites, et non un simple CRUD générique.

### 10.3 Pilotage par scan

- La conception doit être compatible avec un fonctionnement piloté par scan de code-barres.
- Elle doit permettre de distinguer clairement produit connu, produit inconnu à qualifier, produit rattaché et produit ouvert.

### 10.4 Identifiants

- Chaque entité métier principale doit disposer d’un identifiant interne unique, stable et exploitable.

## 11. Proposition de structure logique

Une structure cible cohérente pourrait être la suivante :

- src/baobab_mtg_products/product_types/
- src/baobab_mtg_products/products/
- src/baobab_mtg_products/relationships/
- src/baobab_mtg_products/openings/
- src/baobab_mtg_products/use_cases/
- src/baobab_mtg_products/exceptions/
- src/baobab_mtg_products/interfaces/
- src/baobab_mtg_products/events/

## 12. Livrables attendus

- le code source de la librairie ;
- les tests unitaires ;
- le pyproject.toml configuré ;
- le README.md ;
- le CHANGELOG.md ;
- le journal docs/dev_diary.md ;
- la documentation technique utile ;
- les rapports de couverture dans docs/tests/coverage.

## 13. Workflow de développement attendu

Le développement doit être mené avec une branche dédiée par fonctionnalité.

Les messages de commit doivent suivre les Conventional Commits.

Toute fonctionnalité doit être intégrée via Pull Request après validation des tests, de la couverture et des outils qualité.

## 14. Critères d’acceptation

- le périmètre métier défini est couvert ;
- les cas d’usage minimum sont implémentés ;
- l’architecture reste indépendante des couches hors périmètre ; 
- les exceptions sont hiérarchisées et spécifiques ;
- les tests atteignent au moins 95 % de couverture ;
- black, pylint, mypy, flake8 et bandit passent sans erreur ;
- la documentation et le journal de développement sont présents ;
- la structure du projet respecte les contraintes définies.

## 15. Valeur attendue

La librairie doit devenir la brique métier qui relie de manière fiable un achat réel, un produit scellé réel, son ouverture réelle et les cartes réellement obtenues.

C’est cette traçabilité qui doit permettre l’intégration cohérente avec la collection et l’analyse statistique des ouvertures.
