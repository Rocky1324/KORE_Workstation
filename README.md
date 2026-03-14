# KORE-Workstation V6.0: Ultimate Engineering Hub 🚀🎓

**KORE-Workstation** est un assistant de travail personnel tout-en-un, conçu spécifiquement pour les étudiants en ingénierie et en sciences (type EPFL). Conçu avec Python et CustomTkinter, cet outil centralise vos révisions, vos logs de bugs, vos documents de cours et vos scripts personnalisés dans un environnement natif, moderne et "Dark Mode".

![KORE-Workstation](https://img.shields.io/badge/Status-V6.0_Ultimate-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-darkblue)
![SQLite](https://img.shields.io/badge/DB-SQLite-lightgrey)

---

## 🌟 Fonctionnalités Principales

### 1. Dashboard Cockpit (Responsive & Interactif)
Le centre névralgique de votre productivité.
- **KPIs Premium :** Visualisez instantanément vos **Cartes Dues** (Rouge), votre **Streak** (Orange), votre **Dernier Log** (Vert) et votre **Status Git/Sync** (Violet).
- **Graphique d'Activité :** Suivez vos révisions des 7 derniers jours via une intégration Matplotlib parfaitement harmonisée en Dark Mode.
- **Facteur d'Urgence :** Un récapitulatif intelligent de vos devoirs les plus proches (< 48h) avec alertes critiques.
- **Layout Scrollable :** Une interface qui s'adapte à votre contenu, fini les éléments coupés.

### 2. Gestionnaire d'Études Pro (Nouvelle Végétation)
Une interface dédiée pour piloter vos projets complexes (ex: construction de MTU, simulations).
- **Tab Devoirs :** Suivi des dates limites avec indicateurs d'urgence.
- **Tab Projets :** Divisez vos projets en étapes (sous-tâches) avec journalisation automatique à la complétion.
- **Tab To-do :** Liste de tâches générales avecIDs pour une gestion rapide par commande.
- **Ajout Direct :** Formulaires intégrés pour ajouter des données sans quitter la vue.

### 3. Math-Physics Tracker (Intelligence SRS)
Fini les oublis avant les partiels !
- **Algorithme SM-2 :** Calcul automatique des intervalles de révision optimaux.
- **PDF-Intelligence :** Scannez vos cours via `/scan [PDF]` pour extraire automatiquement les **Théorèmes, Lois, Définitions et Démonstrations**.
- **Validation UI :** Révisez et éditez les cartes générées avant de les ajouter à votre base.

### 4. KORE-Calc & Lab de Simulation
Votre moteur mathématique et physique embarqué.
- **Calcul Symbolique :** Résolution d'équations, intégrales, dérivées et limites via SymPy.
- **Graphes 2D/3D :** Visualisation interactive de fonctions complexes (ex: `sin(x)*cos(y)`) avec zoom et rotation.
- **Simulation Lab :** Solveur de circuits DC (MNA) et simulateur de physique numérique (RK4) pour les systèmes masse-ressort ou trajectoires.

### 5. Vision OCR & LaTeX Premium
- **Capture OCR :** Utilisez `/capture` pour transformer n'importe quelle zone de votre écran en texte ou code LaTeX.
- **Live Preview :** Rédigez et visualisez vos rapports LaTeX en temps réel.
- **Formula-Quick :** Bibliothèque de plus de 30 formules fondamentales (Maxwell, Navier-Stokes, Heisenberg) prêtes à l'emploi.

### 6. Pont Numérique (KORE Digital Bridge) 📱🌐
Synchronisez votre travail entre votre PC et votre mobile.
- **Serveur Embarqué :** Démarrez un serveur FastAPI local en un clic.
- **Companion Mobile :** Scannez le QR Code pour lier votre application mobile (Flet).
- **Capture à Distance :** Envoyez des notes au journal ou consultez vos devoirs directement sur votre téléphone.
- **Accès Documents :** Téléchargez vos fichiers PDF depuis votre Workstation vers votre mobile en streaming.

### 7. Cahier de Laboratoire & Data Analysis 📊🔬
Un outil de traitement de données intégré pour vos travaux pratiques.
- **Data Engine :** Importez des fichiers CSV et gérez vos jeux de données.
- **Régression Avancée :** Tracez des courbes avec régressions linéaires ou polynomiales (jusqu'à l'ordre 5).
- **Statistiques :** Calcul automatique des équations $y=f(x)$ et du coefficient de détermination $R^2$.
- **Exportation Report-Ready :** Sauvegardez vos graphiques en haute résolution avec inversion de couleurs automatique pour l'impression.

### 8. Graphe de Connaissances Interactif 🕸️🧠
Visualisez les liens entre vos différentes notions et travaux.
- **Force-Directed Graph :** Une représentation physique (moteur 100% natif `tk.Canvas`) de votre savoir.
- **Auto-Tag Linking :** Le graphe scanne vos journaux, projets et SRS pour créer des noeuds basés sur les `#tags`.
- **Navigation Organique :** Zoomez, déplacez et manipulez vos bulles de connaissances pour explorer les clusters de vos cours.

### 9. Écosystème Connecté & LaTeX Avancé ✍️📐
- **Éditeur LaTeX Pro :** Système d'auto-complétion par snippets (pop-up flottant) pour les équations complexes.
- **Templates Scientifiques :** Bibliothèque de structures prêtes à l'emploi (Rapports de Labo, Fiches de Révision).
- **Logbook Technique :** Enregistrez vos bugs et solutions avec `/log [msg]`.
- **Obsidian Integration :** Exportez votre journal vers votre Vault Obsidian avec `/obsidian`.
- **Sync Git :** Synchronisez votre base `kore.db` sur GitHub via `/sync`.
- **Zotero-like Biblio :** Gérez vos sources et citations avec `/cite [URL]`.

---

## ️ Guide d'Installation

### 1. Prérequis
- Python 3.10 ou supérieur
- Tesseract OCR (optionnel, pour la capture d'écran)

### 2. Setup Rapide
```bash
git clone https://github.com/votre_pseudo/kore-workstation.git
cd kore-workstation
pip install -r requirements.txt
python main.py
```

---

## ⌨️ Aide-Mémoire des Commandes (Slash Commands)
Tapez `/help` dans l'application pour ouvrir le menu d'aide interactif.

| Catégorie | Commande | Action |
| :--- | :--- | :--- |
| **Général** | `/help` | Ouvre ce guide en interactif |
| **Études** | `/add homework [Matière] [Titre] [Date]` | Ajoute un devoir |
| **Tracker** | `/scan [PDF]` | Scanne un cours pour extraire des fiches |
| **Science** | `/plot [expr]` | Trace une fonction 2D ou 3D |
| **Simul** | `/lab` | Ouvre l'onglet de simulation physique |
| **Sync** | `/sync` | Synchronise avec GitHub |
| **Journal** | `/log [msg]` | Note rapide dans le journal |
| **Outils** | `/widget [t]` | Widget flottant (timer/const/note) |

---
**KORE : Développé pour l'excellence technique et la productivité maximale.**
*Version 6.0 (Ultimate Engineering Edition)*
