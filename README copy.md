# KORE-Workstation V6.5: Ultimate Engineering Hub 🚀🎓

**KORE-Workstation** est un assistant de travail personnel tout-en-un, conçu spécifiquement pour les étudiants en ingénierie et en sciences (type EPFL). Conçu avec Python et CustomTkinter, cet outil centralise vos révisions, vos logs de bugs, vos documents de cours et vos scripts personnalisés dans un environnement natif, moderne et "Dark Mode".

![KORE-Workstation](https://img.shields.io/badge/Status-V6.5_Ultimate-success)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-darkblue)
![SQLite](https://img.shields.io/badge/DB-SQLite-lightgrey)

---

## 🌟 Fonctionnalités Principales

### 1. Dashboard Cockpit (Responsive & Interactif)
Le centre névralgique de votre productivité.
- **KPIs Premium :** Visualisez instantanément vos **Cartes Dues** (Rouge), votre **Streak d'Activité** (Orange - basé sur le SRS et les Tâches accomplies), votre **Dernier Log** (Vert) et votre **Status Git/Sync** (Violet).
- **Graphiques Doubles :**
  - **Temps de Focus :** Suivez vos heures de productivité réalisées via le minuteur Pomodoro.
  - **Productivité Multimodale :** Un graphe empilé récapitulatif de vos tâches terminées ET de vos sessions d'apprentissage SRS.
- **Facteur d'Urgence :** Un récapitulatif intelligent de vos devoirs les plus proches avec alertes critiques.

### 2. Bibliothèque / Garde-Document 📚
Votre lecteur intégré pour garder le flow.
- **Explorateur Automatique :** Naviguez dans le dossier `kore_library` en temps réel. Supporte PDF, TXT, PY, MD, JSON.
- **Rendu PDF Fluide :** Affichez vos cours PDF directement dans l'application avec zoom, pagination et défilement libre.
- **Menu d'Extraction Cognitif (Le Clic Droit) :** Extraire vers le *Journal*, créer une *Notion SRS*, *Convertir en LaTeX* ou l'envoyer au *LabEngine*.

### 3. Gestionnaire d'Études Pro & Tracker SRS
- **Projets & Tâches :** Divisez vos projets, suivez vos échéances et validez vos tâches pour enrichir votre de Streak de Productivité quotidienne.
- **Algorithme SM-2 :** Calcul intelligent de la courbe d'oubli pour vos fiches d'ingénierie.
- **PDF-Intelligence :** Scannez vos cours via la commande `/scan` pour en extraire des flashcards automatiques (Théorèmes et Démonstrations).

### 4. Pomodoro Logique & Widget Flottant 🍅
- **Cycle Complet Automatique :** 25min (Focus) -> 5min (Pause Courte) -> 15min (Pause Longue après 4 cycles).
- **Log Automatique :** Chaque session de Focus réussie alimente le graphe du Dashboard.
- **Widget Flottant :** Gardez le minuteur visible au-dessus de tout avec `/widget timer`.

### 5. KORE-Calc & Lab de Simulation
- **Calcul Symbolique :** Résolution d'équations, inéquations, intégrales, dérivées et limites.
- **Graphes :** Graphes 2D standards, tracés de **courbes implicites en 2D** (ex: cercle, cœur), et de **surfaces 3D** paramétrables.
- **Simulation Lab :** Solveur de circuits (MNA) et simulateur de physique temporelle (RK4).

### 6. Journal, OCR & Écosystème Connecté
- **Exportation Obsidian :** Synchronisez tout votre journal technique avec votre Vault.
- **Backups Locaux & Git :** Commandes de sauvegarde intégrées `/backup` et synchronisation `/sync` avec Github.
- **Capture OCR :** Transformez des formules à l'écran en LaTeX copiable.

---

## ⌨️ La KORE Command Bar (Liste Complète)
Le hub central pour piloter l'application. Tapez `/help` dans KORE pour le menu interactif.

### Navigation Rapide
| Commande | Action |
| :--- | :--- |
| `/dashboard` ou `/home` | Retour au Cockpit principal |
| `/journal` | Ouvrir le Journal / Logbook |
| `/tracker` ou `/rev` | Lancer le Tracker SRS SM-2 |
| `/calc` | Ouvrir le KORE-Calc |
| `/pomodoro` | Ouvrir l'onglet Pomodoro |
| `/latex` | Ouvrir la prévisualisation Live LaTeX |

### Garde-Document (Bibliothèque)
| Commande | Action |
| :--- | :--- |
| `/import --file` | Ouvre une pop-up pour importer un document précis |
| `/import --folder` | Importe tout un dossier de cours d'un clic |
| `/scan --lib` | Force le rafraîchissement des fichiers du dossier |
| `/open --name "Doc"` | Cherche et ouvre le document contenant "Doc" |
| `/extract --page X` | Copie le texte de la page X du PDF vers le Journal |
| `/latex --convert` | Transforme la sélection de texte courante en LaTeX |

### Productivité (Gestion & Tracker)
| Commande | Action |
| :--- | :--- |
| `/add homework [Matière] [Titre] [AAAA-MM-JJ]` | Ajoute une échéance de devoir |
| `/todo [txt]` | Ajoute une tâche à votre Action List |
| `/done [ID]` | Valide la tâche #ID et augmente votre Streak ! |
| `/tasks` | Résumé des tâches en attente dans la barre de feedback |
| `/scan [Nom du Fichier]` | Analyse le document pour générer des SRS Cards automatiques |

### Mathématiques, Physique & Outils
| Commande | Action |
| :--- | :--- |
| `/plot [expr]` | Trace directement une équation (2D/3D selon l'expression) |
| `/calc [expr]` | Identique à /plot, s'ouvre dans le calculateur |
| `/f [maxwell]` | Affiche/Rend la formule physique spécifiée (`/f` seul liste les formules) |
| `/const [c]` | Récupère la valeur d'une constante scientifique (`/const` seul les liste) |
| `/conv [val] [u1] [u2]` | Convertit une valeur physique (ex: `/conv 10 m cm`) |
| `/capture` | Lance l'outil de capture OCR d'écran |

### Journal, Système & Connectivité
| Commande | Action |
| :--- | :--- |
| `/log [msg]` | Enregistre une entrée rapide dans le Journal de bord |
| `/run [cmd/script.py]` | Exécute un programme ou script système avec affichage du terminal |
| `/cite [URL]` | Extrait les métadonnées de l'URL pour la bibliographie |
| `/biblio` | Affiche votre bibliographie complète |
| `/widget [timer\|const\|note]` | Ouvre le widget flottant correspondant en "Always on Top" |
| `/break` | Force une fenêtre plein écran de pause santé (5 min) |

### Sauvegarde & Exportation
| Commande | Action |
| :--- | :--- |
| `/backup` | Crée une copie de sécurité locale de `kore.db` |
| `/setbackup [chemin]` | Configure le dossier des backups locaux |
| `/github [URL]` | Initialise le repo Git distant de l'application |
| `/sync` | Pousse votre base de données vers GitHub (Commit automatique) |
| `/obsidian` | Exporte votre Journal au format Markdown dans votre Vault |
| `/setobsidian [chemin]` | Indique quel est le dossier racine de votre Vault |
| `/export [journal\|tracker]`| Exporte les données choisies sous format LaTeX `.tex` |

---

## 🛠️ Guide d'Installation

### 1. Prérequis
- Python 3.10 ou supérieur
- Bibliothèques scientifiques : `sympy`, `numpy`, `matplotlib`, `scipy`
- Moteur PDF & OCR : `PyMuPDF` (`fitz`), Tesseract-OCR (Optionnel)

### 2. Setup Rapide
```bash
git clone https://github.com/votre_pseudo/kore-workstation.git
cd kore-workstation
pip install -r requirements.txt
python main.py
```

---
**KORE : Développé pour l'excellence technique et la productivité maximale.**
*Version 6.5 (Ultimate Engineering Edition)*
