import customtkinter as ctk
from database.db_manager import DBManager
import subprocess
import os

class CommandBar(ctk.CTkFrame):
    def __init__(self, master, app_instance, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app_instance
        self.db = DBManager()

        self.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            self, 
            placeholder_text="Tapez une commande (/log <msg>, /rev, /run <cmd>) ou une recherche...", 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.entry.bind("<Return>", self._process_command)
        
        # Area for command feedback/output
        self.feedback_label = ctk.CTkLabel(self, text="", text_color="gray", height=20)
        self.feedback_label.grid(row=1, column=0, sticky="w", padx=10)

    def _show_feedback(self, text, is_error=False):
        color = "red" if is_error else "green"
        self.feedback_label.configure(text=text, text_color=color)
        # Clear feedback after 3 seconds
        self.after(3000, lambda: self.feedback_label.configure(text=""))

    def _get_active_library(self):
        for widget in self.app.content_frame.winfo_children():
            if type(widget).__name__ == "LibraryView":
                return widget
        return None

    def _process_command(self, event=None):
        cmd_text = self.entry.get().strip()
        if not cmd_text: return
        
        self.entry.delete(0, 'end')
        
        # Navigation Commands
        if cmd_text == '/home' or cmd_text == '/dashboard':
            self.app.show_dashboard()
            self._show_feedback("Navigation: Dashboard")
            
        elif cmd_text == '/rev' or cmd_text == '/tracker':
            self.app.show_tracker()
            self._show_feedback("Navigation: Tracker")
            
        elif cmd_text == '/journal':
            self.app.show_journal()
            self._show_feedback("Navigation: Journal")

        elif cmd_text == '/latex':
            self.app.show_latex()
            self._show_feedback("Navigation: LaTeX Preview")

        elif cmd_text == '/pomodoro':
            self.app.show_pomodoro()
            self._show_feedback("Navigation: Pomodoro Timer")

        elif cmd_text == '/calc':
            self.app.show_calculator()
            self._show_feedback("Navigation: KORE-Calc")

        elif cmd_text.startswith('/plot '):
            expr = cmd_text[6:].strip()
            self.app.show_calculator(expression=expr)
            self._show_feedback(f"Traçage de : {expr}")
            
        # Library Commands
        elif cmd_text == '/import --folder':
            lib = self._get_active_library()
            if lib:
                lib._import_folder()
            else:
                self.app.show_library()
                self.after(100, lambda: self._get_active_library()._import_folder())

        elif cmd_text == '/import --file':
            lib = self._get_active_library()
            if lib:
                lib._import_file()
            else:
                self.app.show_library()
                self.after(100, lambda: self._get_active_library()._import_file())

        elif cmd_text == '/scan --lib':
            lib = self._get_active_library()
            if lib:
                lib.refresh_library()
                self._show_feedback("Garde-Document rafraîchi.")
            else:
                self._show_feedback("Ouvrez le Garde-Document d'abord.", is_error=True)

        elif cmd_text.startswith('/open --name '):
            name = cmd_text[12:].strip().strip('"\'')
            if not name: return
            
            lib_path = os.path.join(os.getcwd(), 'kore_library')
            found = None
            if os.path.exists(lib_path):
                for f in os.listdir(lib_path):
                    if name.lower() in f.lower():
                        found = os.path.join(lib_path, f)
                        break
            
            if found:
                self.app.show_library()
                self.after(100, lambda f=found: self._get_active_library()._load_file(f))
                self._show_feedback(f"Ouverture de {os.path.basename(found)}")
            else:
                self._show_feedback(f"Aucun fichier trouvé pour '{name}'", is_error=True)

        elif cmd_text.startswith('/extract --page '):
            page_str = cmd_text[15:].strip()
            if page_str.isdigit():
                page_num = int(page_str) - 1 # 0-indexed
                lib = self._get_active_library()
                if lib and lib.current_pdf_doc:
                    try:
                        if 0 <= page_num < len(lib.current_pdf_doc):
                            page = lib.current_pdf_doc[page_num]
                            text = page.get_text()
                            if text:
                                title = f"Extrait: {os.path.basename(lib.current_pdf_doc.name)} (p.{page_num + 1})"
                                self.db.add_journal_entry(title=title, content=text, keywords="extrait_pdf, auto")
                                self._show_feedback(f"Page {page_num + 1} extraite vers le Journal !")
                            else:
                                self._show_feedback("Aucun texte trouvé sur cette page.", is_error=True)
                        else:
                            self._show_feedback(f"Page {page_num + 1} n'existe pas.", is_error=True)
                    except Exception as e:
                        self._show_feedback(f"Erreur extraction: {str(e)[:30]}", is_error=True)
                else:
                    self._show_feedback("Ouvrez d'abord un PDF dans le Garde-Document.", is_error=True)
            else:
                self._show_feedback("Usage: extract --page [numero]", is_error=True)

        elif cmd_text == '/latex --convert':
            lib = self._get_active_library()
            if lib:
                lib._force_update_selection()
                if lib.selected_text_cache.strip():
                    lib._ctx_to_latex()
                else:
                    self._show_feedback("Sélectionnez d'abord du texte.", is_error=True)
            else:
                self._show_feedback("Ouvrez le Garde-Document d'abord.", is_error=True)

        # Action Commands
        elif cmd_text.startswith('/log '):
            content = cmd_text[5:].strip()
            if content:
                # Add a quick entry to the journal
                self.db.add_journal_entry(title="Quick Log", content=content, keywords="quick-log")
                self._show_feedback("Log ajouté au journal.")
                if hasattr(self.app, 'current_view') and self.app.current_view == 'journal':
                    self.app.show_journal() # Refresh
            else:
                self._show_feedback("Erreur: Le log ne peut pas être vide.", is_error=True)
                
        elif cmd_text.startswith('/ask '):
            query = cmd_text[5:].strip()
            if query:
                self._show_feedback(f"Recherche dans les PDF: {query}...")
                self._run_pdf_search(query)
            else:
                self._show_feedback("Erreur: Spécifiez un sujet à rechercher.", is_error=True)
                
        elif cmd_text.startswith('/run '):
            process_cmd = cmd_text[5:].strip()
            if process_cmd:
                script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", process_cmd)
                
                # Check if user wants to run a python script from our scripts directory
                if os.path.exists(script_path):
                    self._run_script_with_output(["python", script_path], title=f"Script: {process_cmd}")
                    self._show_feedback(f"Script lancé: {process_cmd}")
                else:
                    self._run_script_with_output(process_cmd, shell=True, title=f"System: {process_cmd}")
                    self._show_feedback(f"Processus système lancé: {process_cmd}")
            else:
                self._show_feedback("Erreur: Specifiez une commande.", is_error=True)
                
        elif cmd_text == '/backup':
            from core.backup import BackupManager
            bm = BackupManager()
            result = bm.create_backup()
            if result["status"] == "success":
                self._show_feedback("Backup créé avec succès !")
            else:
                self._show_feedback(result["message"], is_error=True)
                
        elif cmd_text.startswith('/setbackup '):
            new_path = cmd_text[11:].strip()
            from core.backup import BackupManager
            bm = BackupManager()
            if bm.set_backup_folder(new_path):
                self._show_feedback(f"Dossier de backup mis à jour !")
            else:
                self._show_feedback(f"Erreur: Dossier {new_path} invalide", is_error=True)
                
        elif cmd_text.startswith('/f '):
            form_name = cmd_text[3:].strip()
            if not form_name:
                self._show_feedback("Erreur: Spécifiez un nom (ex: /f maxwell)", is_error=True)
            else:
                formula_data = self.db.get_formula(form_name)
                if formula_data:
                    self._render_formula(form_name, formula_data[0], formula_data[1])
                    self._show_feedback(f"Affichage de la formule: {form_name}")
                else:
                    self._show_feedback(f"Formule '{form_name}' introuvable.", is_error=True)

        elif cmd_text == '/f':
            # List available formulas
            formulas = self.db.list_formulas()
            if formulas:
                names = ", ".join([f[0] for f in formulas])
                self._show_feedback(f"Disponibles: {names}")
            else:
                self._show_feedback("Aucune formule disponible.", is_error=True)

        elif cmd_text.startswith('/cite '):
            url = cmd_text[6:].strip()
            if url:
                self._show_feedback(f"Extraction des métadonnées: {url}...")
                self._run_citation_scrape(url)
            else:
                self._show_feedback("Erreur: Spécifiez une URL.", is_error=True)

        elif cmd_text == '/biblio':
            self._show_bibliography()
            self._show_feedback("Ouverture de la bibliothèque.")

        elif cmd_text.startswith('/conv '):
            parts = cmd_text[6:].split()
            # Expected: /conv [float] [unit1] [unit2]
            if len(parts) == 3:
                try:
                    val = float(parts[0])
                    u1, u2 = parts[1], parts[2]
                    from core.physics import PhysicsEngine
                    pe = PhysicsEngine()
                    res = pe.convert(val, u1, u2)
                    if res["success"]:
                        self._show_feedback(f"{val} {u1} = {res['value']:.4e} {res['unit']}")
                    else:
                        self._show_feedback(f"Erreur unité: {res['error'][:30]}", is_error=True)
                except ValueError:
                    self._show_feedback("Erreur: La valeur doit être un nombre.", is_error=True)
            else:
                self._show_feedback("Usage: /conv [val] [de] [a]", is_error=True)

        elif cmd_text.startswith('/const'):
            parts = cmd_text.split()
            from core.physics import PhysicsEngine
            pe = PhysicsEngine()
            if len(parts) == 2:
                name = parts[1]
                res = pe.get_constant(name)
                if res["success"]:
                    self._show_constant_popup(name, res["value"], res["unit"], res["description"])
                    self._show_feedback(f"Affichage de la constante: {name}")
                else:
                    self._show_feedback(res["error"], is_error=True)
            else:
                names = ", ".join(pe.list_constants())
                self._show_feedback(f"Constantes: {names}")

        elif cmd_text == '/break':
            self._start_break()
            self._show_feedback("Pause santé lancée !")

        elif cmd_text.startswith('/export '):
            target = cmd_text[8:].strip().lower()
            if target == 'journal':
                content = self.app.exporter.generate_journal_latex()
                path = self.app.exporter.save_to_file(content, "journal_export.tex")
                self._show_feedback(f"Journal exporté : {os.path.basename(path)}")
            elif target == 'tracker':
                content = self.app.exporter.generate_tracker_latex()
                path = self.app.exporter.save_to_file(content, "tracker_export.tex")
                self._show_feedback(f"Tracker exporté : {os.path.basename(path)}")
            else:
                self._show_feedback("Usage : /export [journal|tracker]", is_error=True)

        elif cmd_text.startswith('/scan '):
            filename = cmd_text[6:].strip()
            if filename:
                # Search in docs/ or exports/
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                paths = [
                    os.path.join(base_dir, "docs", filename),
                    os.path.join(base_dir, "exports", filename)
                ]
                found = False
                for p in paths:
                    if os.path.exists(p):
                        self._show_feedback(f"Scan en cours : {filename}...")
                        self._run_srs_scan(p)
                        found = True
                        break
                if not found:
                    self._show_feedback(f"Fichier introuvable : {filename}", is_error=True)
            else:
                self._show_feedback("Usage : /scan [nom_fichier]", is_error=True)

        elif cmd_text.startswith('/github '):
            url = cmd_text[8:].strip()
            res = self.app.git_sync.initialize_repo(remote_url=url)
            if res["success"]:
                self._show_feedback(f"Remote Git configuré : {url}")
            else:
                self._show_feedback(res["stderr"], is_error=True)

        elif cmd_text.startswith('/widget '):
            from ui.widgets import PomodoroWidget, ConstantsWidget, NoteWidget
            wtype = cmd_text[8:].strip().lower()
            if wtype == 'timer':
                PomodoroWidget(self.app)
                self._show_feedback("Widget Timer lancé")
            elif wtype == 'const':
                ConstantsWidget(self.app)
                self._show_feedback("Widget Constantes lancé")
            elif wtype == 'note':
                NoteWidget(self.app)
                self._show_feedback("Widget Note lancé")
            else:
                self._show_feedback("Usage : /widget [timer|const|note]", is_error=True)

        elif cmd_text == '/capture':
            self._show_feedback("Capture d'écran en cours...")
            self._run_capture_ocr()

        elif cmd_text == '/sync':
            self._show_feedback("Synchronisation Git en cours...")
            self._run_git_sync()
        elif cmd_text == '/obsidian':
            self._show_feedback("Export vers Obsidian...")
            self._run_obsidian_sync()

        elif cmd_text.startswith('/setobsidian '):
            path = cmd_text[13:].strip()
            if os.path.exists(path):
                self.db.set_setting("obsidian_vault", path)
                self._show_feedback(f"Vault Obsidian configuré !")
            else:
                self._show_feedback(f"Erreur: Dossier {path} invalide", is_error=True)

        elif cmd_text.startswith('/add homework '):
            # Format: /add homework [Maths] [Série 1] [2026-03-01]
            try:
                parts = re.findall(r'\[(.*?)\]', cmd_text)
                if len(parts) >= 3:
                    sub, title, deadline = parts[0], parts[1], parts[2]
                    self.db.add_homework(sub, title, deadline)
                    self._show_feedback(f"Devoir ajouté : {title} ({sub})")
                else:
                    self._show_feedback("Usage : /add homework [Matière] [Titre] [AAAA-MM-JJ]", is_error=True)
            except Exception as e:
                self._show_feedback(f"Erreur format : {str(e)}", is_error=True)

        elif cmd_text.startswith('/todo '):
            text = cmd_text[6:].strip()
            if text:
                self.db.add_task(text)
                self._show_feedback(f"Tâche ajoutée : {text}")

        elif cmd_text.startswith('/done '):
            tid = cmd_text[6:].strip()
            if tid.isdigit():
                self.db.update_task_status(int(tid))
                self._show_feedback(f"Tâche {tid} terminée !")
            else:
                self._show_feedback("Usage : /done [ID]", is_error=True)

        elif cmd_text == '/tasks':
            tasks = self.db.get_pending_tasks(limit=5)
            if tasks:
                summary = "--- TÂCHES EN ATTENTE ---\n"
                for t in tasks:
                    summary += f"#{t[0]} {t[1]} (Prio: {t[2]})\n"
                self._show_feedback(summary)
            else:
                self._show_feedback("Aucune tâche en attente.")

        elif cmd_text == '/help':
            self._show_help_window()

        else:
            self._show_feedback(f"Commande inconnue : {cmd_text}", is_error=True)

    def _show_help_window(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title("Centre d'Aide KORE-Workstation")
        help_win.geometry("600x500")
        help_win.attributes("-topmost", True)
        
        # Scrollable frame for commands
        scroll = ctk.CTkScrollableFrame(help_win, fg_color="#1a1a1a")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(scroll, text="KORE COMMAND CENTER", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1f538d").pack(pady=(10, 20))
        
        categories = {
            "📝 JOURNAL & TRACKER": [
                ("/log [msg]", "Ajouter une entrée rapide au journal"),
                ("/rev [ID]", "Réviser une carte SRS spécifique"),
                ("/export [journal|tracker]", "Exporter vos données en LaTeX")
            ],
            "🧮 CALCUL & LAB": [
                ("/calc [expr]", "Lancer un calcul standard ou symbolique"),
                ("/plot [expr]", "Tracer une fonction 2D ou 3D"),
                ("/f [nom]", "Afficher une constante ou formule LaTeX")
            ],
            "📚 GESTION D'ÉTUDES": [
                ("/add homework [Matière] [Titre] [Date]", "Ajouter un devoir (AAAA-MM-JJ)"),
                ("/todo [texte]", "Ajouter une tâche rapide"),
                ("/done [ID]", "Marquer une tâche comme terminée"),
                ("/tasks", "Lister les tâches en attente")
            ],
            "📂 CONNECTIVITÉ & SYNC": [
                ("/github [URL]", "Configurer le repo distant pour kore.db"),
                ("/sync", "Synchroniser vos données via Git"),
                ("/obsidian", "Exporter le journal vers Obsidian"),
                ("/setobsidian [chemin]", "Configurer le dossier Obsidian Vault")
            ],
            "📚 GARDE-DOCUMENT": [
                ("/import --file", "Importer un fichier manuel"),
                ("/import --folder", "Importer tout un dossier"),
                ("/scan --lib", "Rafraîchir les fichiers"),
                ("/open --name [Nom]", "Ouvrir un fichier du garde-document"),
                ("/extract --page [X]", "Extraire le texte de la page X vers le Journal"),
                ("/latex --convert", "Convertir le texte sélectionné en LaTeX")
            ],
            "🛠️ OUTILS & VISION": [
                ("/capture", "Lancer la capture d'écran pour OCR/LaTeX"),
                ("/widget [timer|const|note]", "Lancer un widget flottant"),
                ("/cite [URL]", "Extraire et ajouter une citation bibliographique")
            ]
        }
        
        for cat, cmds in categories.items():
            ctk.CTkLabel(scroll, text=cat, font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(fill="x", pady=(15, 5))
            for cmd, desc in cmds:
                f = ctk.CTkFrame(scroll, fg_color="#242424")
                f.pack(fill="x", pady=2)
                ctk.CTkLabel(f, text=cmd, text_color="#ff9500", font=ctk.CTkFont(family="Consolas", size=12)).pack(side="left", padx=10, pady=5)
                ctk.CTkLabel(f, text=f"• {desc}", font=ctk.CTkFont(size=11)).pack(side="left", padx=5)

    def _run_capture_ocr(self):
        # Snipper must run in main thread because it's a UI element
        path = self.app.vision.capture_screen_area(master=self)
        
        if not path:
            self._show_feedback("Capture annulée")
            return

        import threading
        def do_vision():
            # Perform OCR on the captured path
            res = self.app.vision.extract_formula(path)
            if not res["success"]:
                # Use mock if real OCR fails and it's not a cancel error
                if "annulée" not in res.get("error", ""):
                    res = self.app.vision.mock_ocr(path)
                
            self.after(0, lambda: self._show_vision_result(res))
            
        threading.Thread(target=do_vision, daemon=True).start()

    def _show_vision_result(self, res):
        # Open a small window with the recognized text
        popup = ctk.CTkToplevel(self)
        popup.title("OCR Result")
        popup.geometry("400x200")
        popup.attributes("-topmost", True)
        
        textbox = ctk.CTkTextbox(popup, height=100)
        textbox.pack(fill="both", expand=True, padx=20, pady=20)
        textbox.insert("1.0", res["text"])
        
        if res.get("is_mock"):
            ctk.CTkLabel(popup, text="(Mode démo : Installez Tesseract pour le vrai OCR)", text_color="gray").pack()
            
        def copy():
            self.clipboard_clear()
            self.clipboard_append(res["text"])
            self._show_feedback("Texte reconnu copié !")
            popup.destroy()
            
        ctk.CTkButton(popup, text="Copier & Fermer", command=copy).pack(pady=10)

    def _run_git_sync(self):
        import threading
        def do_sync():
            res = self.app.git_sync.sync()
            if res["success"]:
                self.after(0, lambda: self._show_feedback(res["message"]))
            else:
                self.after(0, lambda: self._show_feedback(res["stderr"], is_error=True))
        
        threading.Thread(target=do_sync, daemon=True).start()

    def _run_obsidian_sync(self):
        vault_path = self.db.get_setting("obsidian_vault")
        if not vault_path:
            self._show_feedback("Configurez d'abord le Vault avec /setobsidian [chemin]", is_error=True)
            return
            
        import threading
        def do_obsidian():
            try:
                # Target: Export journal entries as markdown files in a 'KORE-Journal' folder
                target_dir = os.path.join(vault_path, "KORE-Journal")
                if not os.path.exists(target_dir): os.makedirs(target_dir)
                
                entries = self.db.get_journal_entries(limit=100)
                for e in entries:
                    # e: (id, date, title, content, keywords)
                    safe_title = "".join(x for x in e[2] if x.isalnum() or x in " -_").strip()
                    filename = f"{e[1].replace('-', '')}_{safe_title}.md"
                    filepath = os.path.join(target_dir, filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"# {e[2]}\n\n")
                        f.write(f"**Date:** {e[1]}\n")
                        f.write(f"**Keywords:** {e[4]}\n\n")
                        f.write(f"---\n\n")
                        f.write(e[3])
                
                self.after(0, lambda: self._show_feedback(f"Export Obsidian réussi ({len(entries)} fichiers) !"))
            except Exception as e:
                self.after(0, lambda: self._show_feedback(f"Erreur Obsidian: {str(e)[:30]}...", is_error=True))
                
        threading.Thread(target=do_obsidian, daemon=True).start()

    def _start_break(self, duration_min=5):
        # Full-screen break window
        break_win = ctk.CTkToplevel(self)
        break_win.title("PAUSE SANTÉ - KORE")
        break_win.attributes("-topmost", True)
        # On windows, we can try to make it almost full screen
        break_win.after(100, lambda: break_win.state('zoomed'))
        
        frame = ctk.CTkFrame(break_win, fg_color="#1a1a1a")
        frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="🛑 TEMPS DE PAUSE 🛑", font=ctk.CTkFont(size=40, weight="bold"), text_color="#ff5555").pack(pady=(100, 20))
        ctk.CTkLabel(frame, text="Lève-toi, étire-toi, et repose tes yeux pendant 5 minutes.", font=ctk.CTkFont(size=20)).pack(pady=10)
        
        timer_lbl = ctk.CTkLabel(frame, text="05:00", font=ctk.CTkFont(size=60, weight="bold"))
        timer_lbl.pack(pady=40)
        
        self.break_seconds = duration_min * 60
        
        def count_down():
            if self.break_seconds > 0:
                self.break_seconds -= 1
                mins, secs = divmod(self.break_seconds, 60)
                timer_lbl.configure(text=f"{mins:02d}:{secs:02d}")
                break_win.after(1000, count_down)
            else:
                ctk.CTkLabel(frame, text="C'est fini ! Tu peux reprendre le travail.", text_color="green", font=ctk.CTkFont(size=18)).pack(pady=20)
                # Add a close button
                ctk.CTkButton(frame, text="Retour au travail", command=break_win.destroy).pack(pady=10)

        count_down()

    def _run_citation_scrape(self, url):
        import threading
        from core.scraper import CitationScraper
        
        def do_scrape():
            scraper = CitationScraper()
            data = scraper.scrape_metadata(url)
            
            if "error" in data:
                self.after(0, lambda: self._show_feedback(f"Erreur scrap: {data['error'][:30]}...", is_error=True))
                return
            
            # Save to DB
            self.db.add_citation(
                url=data["url"],
                title=data["title"],
                authors=data["authors"],
                pub_date=data["pub_date"]
            )
            self.after(0, lambda: self._show_feedback(f"Cité: {data['title'][:30]}..."))

        threading.Thread(target=do_scrape, daemon=True).start()

    def _show_bibliography(self):
        # Create a popup to show existing citations
        popup = ctk.CTkToplevel(self)
        popup.title("Paper-Archive: Bibliographie")
        popup.geometry("800x500")
        
        textbox = ctk.CTkTextbox(popup, font=ctk.CTkFont(family="Consolas", size=12), wrap="word")
        textbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        citations = self.db.get_citations()
        if not citations:
            textbox.insert("end", "Aucune citation enregistrée pour le moment. Utilisez /cite [URL].")
        else:
            content = "--- MA BIBLIOGRAPHIE GÉNÉRÉE ---\n\n"
            for c in citations:
                # c = (id, url, title, authors, pub_date)
                content += f"Titre   : {c[2]}\n"
                content += f"Auteur  : {c[3]}\n"
                content += f"Source  : {c[1]}\n"
                content += f"Date    : {c[4]}\n"
                content += "-" * 40 + "\n\n"
            textbox.insert("end", content)
            
            # Add an export button
            def export_bib():
                export_dir = "exports"
                if not os.path.exists(export_dir): os.makedirs(export_dir)
                filepath = os.path.join(export_dir, "bibliographie.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                self._show_feedback(f"Exporté: {filepath}")
                popup.destroy()

            btn = ctk.CTkButton(popup, text="Exporter en .txt", command=export_bib)
            btn.pack(pady=(0, 20))

    def _show_constant_popup(self, name, value, unit, description):
        # Create popup
        popup = ctk.CTkToplevel(self)
        popup.title(f"Constante: {name}")
        popup.geometry("500x300")
        popup.resizable(False, False)
        popup.attributes("-topmost", True)
        
        # Details
        title_lbl = ctk.CTkLabel(popup, text=description, font=ctk.CTkFont(size=18, weight="bold"))
        title_lbl.pack(pady=(30, 10))
        
        # Display large value
        val_str = f"{value:.8e}"
        val_lbl = ctk.CTkLabel(popup, text=val_str, font=ctk.CTkFont(family="Consolas", size=32, weight="bold"), text_color="#1f538d")
        val_lbl.pack(pady=10)
        
        unit_lbl = ctk.CTkLabel(popup, text=unit, font=ctk.CTkFont(size=16))
        unit_lbl.pack(pady=(0, 20))
        
        # Copy button
        def copy_val():
            self.clipboard_clear()
            self.clipboard_append(str(value))
            self._show_feedback(f"Valeur de {name} copiée !")
            popup.destroy()

        copy_btn = ctk.CTkButton(popup, text="Copier la valeur", command=copy_val)
        copy_btn.pack(pady=10)

    def _render_formula(self, name, latex_code, description):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        # Create popup
        popup = ctk.CTkToplevel(self)
        popup.title(f"Formule: {name}")
        popup.geometry("500x300")
        popup.resizable(False, False)
        
        # Details
        desc_lbl = ctk.CTkLabel(popup, text=description, font=ctk.CTkFont(size=14, weight="bold"))
        desc_lbl.pack(pady=(20, 10))
        
        code_lbl = ctk.CTkLabel(popup, text=latex_code, font=ctk.CTkFont(family="Consolas", size=10), text_color="gray")
        code_lbl.pack(pady=(0, 10))
        
        # Render Frame
        render_frame = ctk.CTkFrame(popup, fg_color="transparent")
        render_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Matplotlib LaTeX Render
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(4, 1.5), dpi=100)
        fig.patch.set_facecolor('#2B2B2B')
        
        ax.text(0.5, 0.5, f"${latex_code}$", fontsize=20, color='white', ha='center', va='center')
        ax.axis('off')
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=render_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True)

    def _run_script_with_output(self, cmd, shell=False, title="Terminal Output"):
        import threading
        
        # Create a new top-level window for the output
        output_window = ctk.CTkToplevel(self)
        output_window.title(title)
        output_window.geometry("600x400")
        output_window.grid_columnconfigure(0, weight=1)
        output_window.grid_rowconfigure(0, weight=1)
        
        textbox = ctk.CTkTextbox(output_window, font=ctk.CTkFont(family="Consolas", size=12))
        textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        def run_proc():
            try:
                kwargs = {}
                import sys
                if sys.platform == "win32":
                    kwargs["creationflags"] = 0x08000000 # subprocess.CREATE_NO_WINDOW

                # Use Popen to read stdout/stderr in real-time
                process = subprocess.Popen(
                    cmd, 
                    shell=shell, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT, 
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    **kwargs
                )
                
                for line in process.stdout:
                    # Update textbox from the main thread safely
                    self.after(0, lambda l=line: [textbox.insert("end", l), textbox.see("end")])
                    
                process.wait()
                self.after(0, lambda: [textbox.insert("end", f"\n[Process exited with code {process.returncode}]\n"), textbox.see("end")])
                
            except Exception as e:
                self.after(0, lambda: textbox.insert("end", f"\n[Execution error: {str(e)}]\n"))
                
        # Run process in a separate thread so we don't block the UI
        threading.Thread(target=run_proc, daemon=True).start()

    def _run_pdf_search(self, query):
        import threading
        
        # Create a new top-level window for the search results
        results_window = ctk.CTkToplevel(self)
        results_window.title(f"Recherche PDF: {query}")
        results_window.geometry("700x500")
        results_window.grid_columnconfigure(0, weight=1)
        results_window.grid_rowconfigure(0, weight=1)
        
        textbox = ctk.CTkTextbox(results_window, font=ctk.CTkFont(family="Consolas", size=13), wrap="word")
        textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        textbox.insert("end", f"Recherche de '{query}' en cours dans le dossier docs/...\n\n")
        
        def do_search():
            try:
                from core.pdf_engine import PDFEngine
                engine = PDFEngine()
                results = engine.search_query(query)
                
                self.after(0, lambda: textbox.delete("1.0", "end"))
                
                if not results:
                    self.after(0, lambda: textbox.insert("end", f"Aucun résultat trouvé pour '{query}' dans vos PDF."))
                    return
                    
                if "error" in results[0]:
                    self.after(0, lambda: textbox.insert("end", results[0]["error"]))
                    return
                
                formatted_text = f"--- Résultats pour '{query}' ---\n\n"
                for i, res in enumerate(results, 1):
                    formatted_text += f"[{i}] {res['file']} (Page {res['page']})\n"
                    formatted_text += f"... {res['context']} ...\n"
                    formatted_text += "-" * 50 + "\n\n"
                    
                self.after(0, lambda: textbox.insert("end", formatted_text))
                
            except Exception as e:
                self.after(0, lambda: textbox.insert("end", f"\n[Erreur de recherche: {str(e)}]\n"))
                
        threading.Thread(target=do_search, daemon=True).start()

    def _run_srs_scan(self, path):
        import threading
        def do_scan():
            cards = self.app.srs_intel.scan_file(path)
            self.after(0, lambda: self.app._show_srs_validation(cards))
        
        threading.Thread(target=do_scan, daemon=True).start()

