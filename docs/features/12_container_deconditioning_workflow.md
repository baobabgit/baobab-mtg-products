# 12_container_deconditioning_workflow — Déconditionnement de contenants

## Objectif

Ajouter un cas d’usage métier distinct de l’ouverture de booster pour gérer l’ouverture d’un contenant et la création ou le rattachement de ses sous-produits.

Une display ouverte pour sortir ses boosters est déconditionnée. Un booster ouvert pour révéler des cartes est ouvert. Ces deux actions ne doivent pas être confondues.

## Branche de développement

`feature/container-deconditioning-workflow`

## Dépendances

- 09_product_reference_instance_split
- 10_physical_instance_creation_and_production_code
- 11_commercial_and_internal_scan_workflow_refactor
- 03_parent_child_relationships
- 05_history_and_event_log

## Périmètre

- Créer `DeconditionContainerUseCase`.
- Créer les objets de commande ou DTO nécessaires pour décrire les enfants découverts.
- Définir les types de produits déconditionnables : display, bundle, prerelease kit ou autres contenants.
- Permettre de créer des instances enfants à partir de références existantes ou nouvellement qualifiées.
- Permettre de rattacher des instances enfants déjà créées.
- Émettre un événement `container_deconditioned` ou équivalent.
- Adapter `ProductStatus` si un statut dédié est nécessaire, par exemple `DECONDITIONED`.
- Préserver les règles anti-cycle et les règles parent/enfant existantes.
- Documenter la boucle d’enregistrement des enfants.

## Hors périmètre

- Révélation des cartes d’un booster.
- Calcul automatique du contenu garanti d’un produit Magic.
- Vérification exhaustive du nombre exact de boosters par produit commercial.
- Interface utilisateur de saisie.

## Règles métier

- Le déconditionnement concerne une instance physique de contenant.
- Les enfants créés ou rattachés sont des `ProductInstance`.
- Le parent d’un enfant est l’`internal_id` du contenant déconditionné.
- Un produit ne doit pas être rattaché à deux parents.
- Le déconditionnement ne doit pas créer d’événement d’ouverture de cartes.
- La boucle d’enregistrement doit pouvoir être reprise sur chaque enfant : scan, code de production, rattachement, déconditionnement éventuel, ouverture éventuelle.

## Livrables attendus

- `DeconditionContainerUseCase`.
- DTO de commande pour enfants créés ou rattachés.
- Événement métier de déconditionnement.
- Statut dédié si retenu.
- Tests unitaires et tests de workflow.
- Documentation du scénario display → 15 boosters.

## Critères d'acceptation

- Une display peut être déconditionnée en 15 boosters enfants.
- Un bundle peut être déconditionné en sous-produits.
- Un booster ne peut pas être déconditionné comme une display.
- Le déconditionnement ne déclenche pas la traçabilité des cartes révélées.
- Les enfants sont consultables dans la vue structurelle du parent.
- Les événements de déconditionnement sont visibles dans la timeline métier.

## Scénario display → 15 boosters (boucle d’enregistrement)

1. Enregistrer la display (scan commercial ou création d’instance) ; disposer des références catalogue pour la display et pour le play booster contenu.
2. Construire une :class:`~baobab_mtg_products.domain.deconditioning.decondition_container_command.DeconditionContainerCommand` avec l’identifiant interne de la display et **quinze** :class:`~baobab_mtg_products.domain.deconditioning.decondition_child_specification.DeconditionChildSpecification` en mode création (`reference_id` du booster), kind ``DISPLAY_CONTAINS_BOOSTER``, codes internes optionnels uniques par booster si déjà suivis en stock.
3. Exécuter :class:`~baobab_mtg_products.use_cases.deconditioning.decondition_container_use_case.DeconditionContainerUseCase` : pour chaque enfant, création d’instance puis rattachement sous la display ; le contenant passe en ``ProductStatus.DECONDITIONED`` ; un événement ``CONTAINER_DECONDITIONED`` est journalisé **une fois** avec le nombre d’enfants traités.
4. Pour **chaque** booster ainsi créé, la boucle métier habituelle peut ensuite reprendre indépendamment : scan interne, code de production, rattachement à un autre parent si besoin, éventuel autre déconditionnement, puis ouverture pour cartes (workflow distinct).

Ce flux ne réalise ni ouverture scellée pour cartes ni révélation ; il matérialise uniquement la sortie physique des sous-produits du contenant.
## Contraintes de développement à respecter

La feature doit impérativement respecter les règles suivantes :

- développement Python orienté objet ;
- une classe par fichier ;
- arborescence source sous `src/baobab_mtg_products/` ;
- arborescence des tests miroir sous `tests/` ;
- docstrings sur toutes les API publiques ;
- annotations de type complètes ;
- exceptions métier spécifiques héritant d'une exception racine du projet ;
- configuration centralisée dans `pyproject.toml` ;
- qualité obligatoire : `black`, `pylint`, `mypy`, `flake8`, `bandit` ;
- couverture minimale attendue : `95%` ;
- journal de développement dans `docs/dev_diary.md` ;
- évolution du `README.md` et du `CHANGELOG.md` si nécessaire ;
- commits au format Conventional Commits ;
- travail sur une branche dédiée ;
- à la fin : si tests, qualité et contraintes sont OK, ouvrir une Pull Request puis la merger sur `main`.
