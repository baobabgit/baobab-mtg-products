# Note d’architecture — Références, instances physiques et persistance

## 1. Pourquoi séparer référence et instance ?

Un code-barres commercial identifie généralement un produit vendu dans le commerce, pas l’exemplaire physique posé sur la table.

Exemple : deux displays identiques peuvent avoir :

- le même code-barres commercial ;
- le même nom ;
- le même set ;
- le même type ;
- le même code de production.

Elles restent pourtant deux objets physiques différents. La librairie doit donc séparer :

- `ProductReference` : ce qu’est le produit commercial ;
- `ProductInstance` : l’exemplaire physique effectivement acheté, découvert, rattaché ou ouvert.

## 2. Règle d’unicité

L’unicité d’un exemplaire physique repose uniquement sur `internal_id`.

Ne doivent pas être uniques au niveau des instances :

- `commercial_barcode` ;
- `production_code` ;
- couple `product_type + production_code` ;
- couple `reference_id + production_code`.

Peut être unique :

- `internal_barcode`, lorsqu’il est généré par l’application pour identifier un exemplaire physique précis.

## 3. Workflow recommandé de scan commercial

```text
scan code-barres commercial
        │
        ▼
résoudre ou créer ProductReference
        │
        ▼
créer une nouvelle ProductInstance
        │
        ▼
associer production_code non unique si disponible
        │
        ▼
rattacher à un parent si le produit provient d’un contenant
        │
        ▼
si contenant : déconditionner et reprendre la boucle sur les enfants
        │
        ▼
si produit ouvrable révélant des cartes : ouvrir et tracer les cartes
```

## 4. Déconditionnement versus ouverture

Le déconditionnement concerne les contenants :

- display vers boosters ;
- bundle vers sous-produits ;
- prerelease kit vers sous-produits.

L’ouverture concerne les produits révélant des cartes :

- booster ;
- produit scellé dont les cartes doivent être tracées.

Ces deux actions ne doivent pas être modélisées par le même cas d’usage.

## 5. Ports de persistance

La librairie ne doit pas imposer SQLite, PostgreSQL, SQLAlchemy ou Django ORM.

Elle doit fournir des ports, et l’application doit brancher son adaptateur concret.

Exemples de ports attendus :

- `ProductReferenceRepositoryPort` ;
- `ProductInstanceRepositoryPort` ;
- `ProductRelationshipRepositoryPort` ;
- `ProductWorkflowEventRecorderPort` ;
- `ProductBusinessHistoryQueryPort` ;
- `RevealedCardTraceRepositoryPort`.

## 6. Schéma SQL indicatif

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

## 7. Critères de validation pour l’IA de développement

L’agent de développement doit ajouter ou adapter des tests prouvant que :

- deux instances peuvent partager la même référence ;
- deux instances peuvent partager le même code-barres commercial via la référence ;
- deux instances peuvent partager le même code de production ;
- un scan commercial connu peut créer une nouvelle instance physique ;
- un scan interne retrouve une instance physique existante ;
- une display peut être déconditionnée en boosters ;
- un booster peut être ouvert et rattacher des cartes révélées ;
- les ports de persistance peuvent être implémentés sans dépendance imposée dans le cœur métier.
