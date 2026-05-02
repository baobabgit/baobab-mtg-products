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

La librairie **ne fournit pas** d’adaptateur SQL ou MongoDB : uniquement des **protocoles** (`Protocol`) et la logique métier. L’application consommatrice implémente la persistance (SQLite, PostgreSQL, etc.) derrière ces ports.

Ports catalogue / exemplaires (v2.x) :

- `ProductReferenceRepositoryPort` — agrégats catalogue ; le **code-barres commercial** y est porté ; recherche par EAN au niveau **référence** uniquement ;
- `ProductRepositoryPort` — **instances physiques** uniquement (nom historique conservé ; pas de renommage en `ProductInstanceRepositoryPort` dans la série 2.x) ; **pas** de `find_by_commercial_barcode` sur ce port.

Relations parent / enfant entre exemplaires : champ `parent_id` sur `ProductInstance` + méthodes du dépôt instance (`list_direct_children_of_parent`). Pas de port dédié « relations » tant qu’aucune décision d’architecture n’extrait cette responsabilité.

Autres ports déjà présents dans le projet :

- `ProductWorkflowEventRecorderPort` ;
- `ProductBusinessHistoryQueryPort` ;
- `RevealedCardTraceRepositoryPort`.

Doubles mémoire de test conformes aux deux premiers ports : `tests/support/in_memory_product_repositories.py`.

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

Les scripts ci-dessus sont **indicatifs** : types SQL, contraintes nommées et index sont à adapter au SGBD et au schéma réel.

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

## 8. Sécurité et intégrité des futurs adaptateurs de persistance

Le package **ne fournit aucun adaptateur SQL** : le cœur métier s’appuie sur des **`Protocol`** ; l’implémentation concrète (SQLite, PostgreSQL, ORM, etc.) relève **exclusivement** de l’application consommatrice.

1. **Schémas** : les exemples SQL de cette note et de la feature **13** sont **non normatifs** ; ils illustrent une cartographie possible domaine ↔ colonnes.
2. **Requêtes paramétrées** : les adaptateurs SQL doivent utiliser des **requêtes paramétrées** (bind parameters), pas l’assemblage de chaînes SQL.
3. **Injection** : aucune valeur issue d’un **scan**, d’un **nom produit**, d’un **code interne**, d’un **code de production** ou d’un **code-barres commercial** ne doit être concaténée ou interpolée dans du SQL brut.
4. **`internal_barcode`** : lorsqu’il est renseigné, une implémentation saine impose l’**unicité** (contrainte `UNIQUE` ou équivalent applicatif), alignée sur le domaine.
5. **`find_by_internal_barcode`** : si la base contient **plusieurs** lignes pour un même code interne (données corrompues ou migration incomplète), l’adaptateur **ne doit pas** en choisir une silencieusement : lever une **erreur explicite** ou définir une stratégie de réparation documentée.
6. **Écriture** : en cas de tentative de doublon sur code interne, **rejeter** la transaction ou lever une erreur métier / d’intégrité explicite.
7. **`commercial_barcode` (EAN)** : si l’application applique la règle **« au plus une référence par EAN »**, elle doit l’**appliquer en persistance** (`UNIQUE` sur la colonne ou table de mapping dédiée, ou contrôle applicatif équivalent). Voir aussi la documentation sécurité feature **09** sur l’absence de choix arbitraire en cas de doublon.
8. **Données historiques** : les doublons déjà présents doivent être traités par **migration**, **nettoyage** ou **erreur d’intégrité** explicite avant de reprendre un flux nominal.
9. **`image_uri`** : donnée descriptive **non fiable** ; pas de **fetch serveur** sans garde-fous (**SSRF**, ressources externes non maîtrisées) — responsabilité applicative.
10. **Affichage** : les champs exposés en **UI** doivent être **échappés** ou rendus via des mécanismes sûrs côté application consommatrice.

Les doubles mémoire **`tests/support/in_memory_product_repositories.py`** illustrent des politiques strictes (ex. rejet de doublon EAN entre références, **`DuplicateInternalBarcodeError`** à l’enregistrement) ; un adaptateur SQL doit définir ses propres garanties équivalentes.
