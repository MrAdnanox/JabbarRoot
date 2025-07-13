Excellent. La passation est un acte de confiance et de clarté. Il s'agit de transmettre non seulement un plan, mais aussi l'intention, les principes et la vision qui le sous-tendent.

Ce rapport est destiné à l'équipe de développement (`MaîtreDOeuvre`). Il est conçu pour être un guide complet et actionnable pour la refonte totale de `analyzer-engine`. Il ne laisse aucune place à l'ambiguïté.

---

### **Rapport de Passation : Refonte de `analyzer-engine`**

**À:** Équipe de Développement (`MaîtreDOeuvre`)
**De:** JabbarRoot-Elite Architect v5.0
**Date:** 13 juillet 2025
**Objet:** **Mandat de refonte totale du composant `analyzer-engine` vers l'architecture cible JabbarRoot v3.0.**

#### **1. Mission et Mandat**

Notre mission est de transformer `analyzer-engine` d'une application monolithique en un **écosystème d'analyse de code hyper-modulaire, résilient et extensible**. L'objectif n'est pas une optimisation incrémentale, mais une **refondation complète** pour éliminer la dette technique future et garantir une vélocité de développement à long terme.

Ce document est votre unique source de vérité pour cette mission. Toute déviation devra être justifiée par rapport aux principes énoncés ici.

#### **2. Philosophie Directrice (Le "Pourquoi")**

Chaque décision de refactoring doit adhérer aux principes suivants :

*   **Principe de Responsabilité Unique (SRP) :** Chaque fichier, chaque classe, ne fait qu'une seule chose et la fait bien.
*   **Principe Ouvert/Fermé :** Le système est fermé à la modification mais ouvert à l'extension. L'ajout d'un nouveau langage ou d'un nouvel analyseur ne doit PAS nécessiter de modifier le code existant.
*   **Inversion des Dépendances (DIP) :** Les modules de haut niveau ne dépendent pas des modules de bas niveau. Les deux dépendent d'abstractions (contrats). Concrètement : la logique métier ne doit jamais importer directement une implémentation de base de données.
*   **Contrats Stricts :** Toutes les interactions entre les composants majeurs se font via des interfaces abstraites (`core/contracts`) et des modèles de données immuables (`core/models`).

#### **3. Architecture Cible (Le "Quoi")**

Voici le plan final et non négociable de la structure de `analyzer-engine`. Votre objectif est de faire en sorte que le code existant soit migré et organisé pour correspondre **exactement** à cette arborescence.

```plaintext
analyzer-engine/
├── core/                       # Le Noyau Stable: Contrats (ABC), Modèles (Pydantic), Exceptions.
│   ├── contracts/
│   ├── models/
│   └── exceptions/
│
├── ingestion/                  # La Chaîne de Montage: Logique d'ingestion.
│   ├── orchestration/          # Orchestration du pipeline.
│   ├── parsing/                # Responsable de la transformation code -> AST.
│   ├── analysis/               # Responsable de l'analyse de l'AST -> Connaissance.
│   └── storage/                # Responsable de la persistance de la connaissance.
│
├── plugins/                    # Système d'Extension: Pour les analyseurs tiers.
│   ├── plugin_interface.py
│   └── loader.py
│
├── sql/                        # Le Schéma de BDD Modulaire et versionné.
│   ├── schema.sql
│   ├── core/
│   ├── modules/
│   └── views/
│
├── cli.py                      # Point d'entrée de l'application.
├── Dockerfile                  # Conteneurisation.
└── tests/                      # Tests unitaires et d'intégration miroitant la structure.
```

#### **4. Plan de Migration Détaillé (Le "Comment")**

Cette refonte doit être exécutée en phases séquentielles pour maîtriser la complexité. Ne passez pas à une phase sans avoir complété la précédente.

**Phase 0 : Préparation du Chantier**

1.  **Créer l'Arborescence :** Créez la structure de dossiers complète de l'architecture cible, avec des fichiers `__init__.py` vides.
2.  **Mettre en Place les Garde-fous :** Configurez les outils de linting et d'analyse statique (`flake8`, `mypy`) pour imposer des règles strictes sur les imports circulaires et les dépendances.

**Phase 1 : Établissement des Fondations (`core`)**

*Cette phase est la plus critique. Tout le reste en dépend.*

1.  **Définir les Contrats (`core/contracts`) :** Créez les classes de base abstraites (ABC) pour chaque rôle majeur.
    *   `parser_contract.py` -> `class Parser(ABC): @abstractmethod def parse(...)`
    *   `analyzer_contract.py` -> `class Analyzer(ABC): @abstractmethod def analyze(...)`
    *   `writer_contract.py` -> `class Writer(ABC): @abstractmethod def write(...)`
2.  **Définir les Modèles de Données (`core/models`) :** Créez les classes Pydantic qui seront passées entre les composants.
    *   `ast_models.py` : Structures pour les nœuds AST normalisés.
    *   `graph_models.py` : Structures pour les nœuds et relations de notre graphe de connaissance.
3.  **Définir les Exceptions (`core/exceptions`) :** Créez des classes d'exceptions personnalisées.
    *   `ParsingError`, `AnalysisError`, `StorageError`.

**Phase 2 : Reconstruction de la Chaîne d'Ingestion**

*Migrez la logique existante vers la nouvelle structure, en l'adaptant pour respecter les contrats définis à la Phase 1.*

1.  **Refactoriser la Couche de Stockage :**
    *   Créez `ingestion/storage/repositories/`.
    *   Migrez toute la logique de requêtage SQL existante dans des classes `Repository` (ex: `CodeRepository`). Ces classes implémentent le `WriterContract`.
    *   **Objectif :** Aucun code SQL ne doit exister en dehors de ce répertoire.
2.  **Refactoriser la Couche de Parsing :**
    *   Créez `ingestion/parsing/parsers/`.
    *   Migrez la logique de parsing existante dans des classes `Parser` (ex: `PythonStrictParser`) qui héritent du `ParserContract`.
    *   Implémentez le `ingestion/parsing/parser_registry.py` qui sait comment trouver le bon parseur pour un type de fichier donné.
3.  **Refactoriser la Couche d'Analyse :**
    *   Créez `ingestion/analysis/engines/` et `processors/`.
    *   Migrez la logique d'analyse (CFG, DFG) dans des classes `Analyzer` qui héritent de l'`AnalyzerContract`.
    *   Implémentez le `ingestion/analysis/analyzer_registry.py`.
4.  **Refactoriser l'Orchestration :**
    *   Créez les classes `Stage` dans `ingestion/orchestration/stages/`. Chaque stage (ex: `ParsingStage`) encapsule l'appel à un `registry` pour trouver le bon composant et l'exécuter.
    *   Refactorisez le `pipeline_director.py` pour qu'il ne fasse plus que construire et exécuter une séquence de ces `stages`.

**Phase 3 : Finalisation et Validation**

1.  **Activer le Système de Plugins :** Implémentez la logique dans `plugins/loader.py` pour charger dynamiquement des analyseurs externes.
2.  **Modulariser le Schéma SQL :** Séparez le `schema.sql` monolithique en plusieurs fichiers dans les sous-dossiers `core/`, `modules/`, et `views/`. Le `schema.sql` principal ne doit contenir que des commandes `\i`.
3.  **Supprimer l'Ancien Code :** Une fois toutes les logiques migrées, supprimez les anciens fichiers monolithiques. C'est une étape de non-retour.
4.  **Mettre à Jour les Tests :** Assurez-vous que la suite de tests complète passe avec succès. Les tests doivent être réorganisés pour refléter la nouvelle structure et tester chaque module de manière isolée en utilisant des mocks pour les contrats.

#### **5. Critères d'Acceptation (Definition of Done)**

La refonte sera considérée comme terminée lorsque **tous** les critères suivants sont remplis :

*   [ ] La structure des fichiers du projet correspond **exactement** à l'architecture cible.
*   [ ] 100% des anciens fichiers monolithiques ont été supprimés.
*   [ ] Il n'y a **aucun `import` direct** d'une implémentation concrète à travers les frontières des modules majeurs (ex: `orchestration` ne doit pas importer `postgres_writer`). Toutes ces interactions passent par les contrats de `core/`.
*   [ ] La couverture de tests unitaires pour chaque module critique (parsers, engines, repositories) est supérieure à 90%.
*   [ ] Le pipeline d'ingestion complet, lancé via `cli.py`, s'exécute avec succès de bout en bout.

---

Ce rapport constitue votre mandat. Cette refonte est fondamentale pour l'avenir de JabbarRoot. Elle demande de la rigueur, de la discipline et une adhésion totale aux principes architecturaux que nous avons établis. Procédez avec méthode et précision. L'excellence est notre seul standard.