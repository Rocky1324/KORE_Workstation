# KORE-Workstation: Ultimate Engineering Hub 🚀🎓

**KORE-Workstation** est un assistant de travail personnel tout-en-un, conçu spécifiquement pour les étudiants en ingénierie et en sciences. Conçu avec Python et CustomTkinter, cet outil centralise vos révisions, vos logs de bugs, vos documents de cours et vos scripts personnalisés dans un environnement natif, moderne et "Dark Mode".

![Version](https://img.shields.io/badge/Version-6.7-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-darkblue)

---

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.10+
- Tesseract OCR (Optional, for screen capture)

### ⚙️ Installation
```bash
git clone https://github.com/Rocky1324/KORE_Workstation.git
cd KORE_Workstation
pip install -r requirements.txt
python main.py
```
---

## 🌟 Fonctionnalités Principales

### 1. Dashboard Cockpit (Responsive & Interactif)
Le centre névralgique de votre productivité.
- **KPIs Premium :** Visualisez vos **Cartes Dues**, votre **Streak d'Activité**, votre **Dernier Log** et votre **Status Git/Sync**.
- **Graphiques Dynamiques :** Suivez vos heures de focus Pomodoro et votre productivité journalière via Matplotlib.
- **Facteur d'Urgence :** Récapitulatif intelligent de vos devoirs les plus proches avec alertes critiques.

### 2. Document Library & Reader 📚
Votre lecteur intégré pour garder le flow.
- **Rendu PDF Fluide :** Affichez vos cours directement avec zoom et navigation.
- **Smart Text Extraction :** Extraire du texte vers le Journal, créer des cartes SRS ou convertir en LaTeX d'un clic droit.

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

### 🐛 Troubleshooting
**Q: Graph is slow with many cards**  
A: This is a known limitation on older hardware. Consider archiving old cards or upgrading to GPU acceleration in future versions.

**Q: Mobile sync not working?**  
A: Ensure both devices are on the same WiFi network. Check if the PC server is running and accessible.

**Q: LaTeX preview shows errors?**  
A: Use standard LaTeX syntax. Custom macros may not render correctly in the live preview.

### Roadmap 2026 🗺️
- [ ] **Tests Automatisés** (High Priority, Q2 2026) : Couverture complète des moteurs.
- [ ] **Optimisation UI** (Medium Priority, Q3 2026) : Passage à un rendu GPU pour les graphes massifs.
- [ ] **Plugin System** (Future, Post-2026) : Architecture modulaire pour extensions tierces.

### 🤝 Contributing
We welcome contributions!
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes.
4. Open a Pull Request.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 📍 Links
- **Issues & Features:** [GitHub Issues](https://github.com/Rocky1324/KORE_Workstation/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Rocky1324/KORE_Workstation/discussions)
- **Wiki & Docs:** [Documentation](https://github.com/Rocky1324/KORE_Workstation/wiki)

---
**KORE : Développé pour l'excellence technique et la productivité maximale.**
*Version 6.7 (Ultimate Engineering Edition)*
