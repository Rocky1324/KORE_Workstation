# KORE-Workstation V6.5: Ultimate Engineering Hub 🚀🎓

**KORE-Workstation** est un assistant de travail personnel tout-en-un, conçu spécifiquement pour les étudiants en ingénierie et en sciences. Conçu avec Python et CustomTkinter, cet outil centralise vos révisions, vos logs de bugs, vos documents de cours et vos scripts personnalisés dans un environnement natif, moderne et "Dark Mode".

![KORE-Workstation](https://img.shields.io/badge/Status-V6.5_Ultimate-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-darkblue)
![SQLite](https://img.shields.io/badge/DB-SQLite-lightgrey)

---

## 🌟 Fonctionnalités Principales

### 1. Dashboard Cockpit (Responsive & Interactif)
Le centre névralgique de votre productivité.
- **KPIs Premium :** Visualisez vos **Cartes Dues**, votre **Streak d'Activité**, votre **Dernier Log** et votre **Status Git/Sync**.
- **Graphiques Dynamiques :** Suivez vos heures de focus Pomodoro et votre productivité journalière via Matplotlib.
- **Facteur d'Urgence :** Récapitulatif intelligent de vos devoirs les plus proches avec alertes critiques.

### 2. Bibliothèque / Garde-Document 📚
Votre lecteur intégré pour garder le flow.
- **Rendu PDF Fluide :** Affichez vos cours directement avec zoom et navigation.
- **Extraction Cognitive :** Extraire du texte vers le Journal, créer des cartes SRS ou convertir en LaTeX d'un clic droit.

### 3. Math-Physics Tracker & SRS SM-2
- **Algorithme SM-2 :** Calcul intelligent de la courbe d'oubli pour vos révisions.
- **PDF-Intelligence :** Scannez vos documents pour générer automatiquement des flashcards (Théorèmes/Lois).

### 4. KORE-Calc & Simulation Lab 🔬
- **Calcul Symbolique :** Résolution d'équations, intégrales et dérivées via SymPy.
- **Simulation Physique :** Solveur de circuits DC (MNA) et simulateur de systèmes dynamiques (RK4).
- **Data Lab :** Import CSV, régressions linéaires/polynomiales et graphiques interactifs.

### 5. Graphe de Connaissances Interactif 🕸️
- **Moteur Physique Natif :** Visualisez les liens entre vos journaux, projets et notions via les `#tags`.
- **Navigation Organique :** Manipulez vos bulles de connaissances pour explorer vos clusters de cours.

### 6. Pont Numérique (Digital Bridge) 📱
- **Sync Mobile :** Liez votre smartphone via QR Code pour capturer des notes ou consulter vos devoirs en déplacement.
- **Streaming Document :** Accédez à vos PDF depuis votre mobile via le serveur local sécurisé.

### 7. Éditeur LaTeX Avancé & OCR
- **Live Preview :** Rédigez vos rapports avec auto-complétion par snippets et templates professionnels.
- **Capture OCR :** Transformez n'importe quelle zone de l'écran en code LaTeX exploitable.

---

## ⌨️ Guide des Commandes (Slash Commands)

| Catégorie | Commande | Action |
| :--- | :--- | :--- |
| **Général** | `/help` | Menu interactif d'aide |
| **Nav** | `/dashboard`, `/journal`, `/tracker`, `/calc`, `/lab`, `/latex` | Navigation rapide |
| **Doc** | `/open [nom]`, `/scan --lib`, `/import` | Gestion de la bibliothèque |
| **Études** | `/add homework`, `/todo`, `/done`, `/tasks` | Pilotage de projet |
| **Science** | `/plot [expr]`, `/f [loi]`, `/const [c]`, `/capture` | Outils scientifiques |
| **Sync** | `/sync`, `/backup`, `/obsidian` | Sauvegarde et exportation |

---

## 🛠️ Maintenance & Stabilité

### Problèmes Connus (Known Issues)
- **Performance Graphe :** Ralentissement possible au-delà de 200 noeuds sur PC d'entrée de gamme.
- **Sync Mobile :** Nécessite que le PC et le mobile soient sur le même réseau local (souci mDNS possible).
- **LaTeX Preview :** Certaines macros complexes nécessitent une syntaxe LaTeX standard stricte.

### Roadmap 2026 🗺️
- [ ] **Tests Automatisés :** Couverture complète des moteurs (`LabEngine`, `DataEngine`).
- [ ] **Optimisation UI :** Passage à un rendu GPU pour les graphes de connaissances massifs.
- [ ] **Plugin System :** Permettre l'ajout de modules tiers par la communauté.

### Contribuer 👥
Les contributions sont les bienvenues !
1. Forkez le projet.
2. Créez votre branche (`git checkout -b feature/NewFeature`).
3. Commitez vos changements.
4. Ouvrez une Pull Request.

---
**KORE : Développé pour l'excellence technique et la productivité maximale.**
*Version 6.5 (Ultimate Engineering Edition)*
