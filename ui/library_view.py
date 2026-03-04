import os
import shutil
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog
import fitz  # PyMuPDF
from PIL import Image, ImageTk

class LibraryView(ctk.CTkFrame):
    def __init__(self, master, app_instance=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance
        self.doc_path = os.path.join(os.getcwd(), 'kore_library')
        
        if not os.path.exists(self.doc_path):
            os.makedirs(self.doc_path)
            
        self.current_extension = ""
        self.current_pdf_doc = None
        self.current_page = 0
        self.pdf_image = None
        
        # Grid Layout: Left is Treeview (30%), Right is Viewer (70%)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # --- Panneau Latéral (Treeview) ---
        self.sidebar = ctk.CTkFrame(self, corner_radius=0, width=250)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.sidebar.grid_rowconfigure(1, weight=1)
        
        header_f = ctk.CTkFrame(self.sidebar, fg_color="#1E1E1E")
        header_f.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(header_f, text="📚 GARDE-DOCUMENT", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # Subframe for Treeview + Scrollbar
        tree_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        self.tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        
        btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(btn_frame, text="Importer", command=self._import_file, fg_color="#2db34a", hover_color="#238f3a").grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(btn_frame, text="Rafraîchir", command=self.refresh_library).grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # --- Lecteur (Viewer) ---

        self.viewer_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1a1a")
        self.viewer_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self.viewer_frame.grid_rowconfigure(1, weight=1)
        self.viewer_frame.grid_columnconfigure(0, weight=1)
        
        # Top toolbar (for PDF pagination)
        self.toolbar_f = ctk.CTkFrame(self.viewer_frame, height=40, fg_color="#333333")
        self.toolbar_f.grid(row=0, column=0, sticky="ew")
        
        self.page_lbl = ctk.CTkLabel(self.toolbar_f, text="")
        self.page_lbl.pack(side="left", padx=10)
        
        self.btn_prev = ctk.CTkButton(self.toolbar_f, text="◀", width=30, command=self._prev_page, state="disabled")
        self.btn_prev.pack(side="left", padx=5)
        self.btn_next = ctk.CTkButton(self.toolbar_f, text="▶", width=30, command=self._next_page, state="disabled")
        self.btn_next.pack(side="left", padx=5)
        
        # 1. Text Viewer (For raw files)
        self.text_viewer = ctk.CTkTextbox(self.viewer_frame, font=ctk.CTkFont(family="Consolas", size=14), wrap="word")
        
        # 2. PDF Viewer Container
        self.pdf_container = ctk.CTkScrollableFrame(self.viewer_frame, fg_color="#1a1a1a")
        
        # Inside Container: The Canvas for the actual page rendering
        self.pdf_canvas = tk.Canvas(self.pdf_container, bg="#1a1a1a", highlightthickness=0)
        self.pdf_canvas.pack(fill="x", pady=(0, 10))
        
        # Inside Container: The text box for selectable content
        self.pdf_text_overlay = ctk.CTkTextbox(self.pdf_container, font=ctk.CTkFont(size=14), wrap="word", fg_color="transparent", text_color="#d0d0d0")
        self.pdf_text_overlay.pack(fill="both", expand=True)
        
        # Context Menu for text selection
        self.context_menu = tk.Menu(self, tearoff=0, bg="#2d2d2d", fg="#ffffff", activebackground="#007aff", activeforeground="#ffffff")
        self.context_menu.add_command(label="📝 Ajouter au Journal", command=self._ctx_add_journal)
        self.context_menu.add_command(label="🧠 Nouvelle Notion (SRS)", command=self._ctx_add_srs)
        self.context_menu.add_command(label="📐 Convertir en LaTeX", command=self._ctx_to_latex)
        self.context_menu.add_command(label="⚡ Calculer via LabEngine", command=self._ctx_calc_lab)
        
        self.text_viewer.bind("<Button-3>", self._show_context_menu)
        self.pdf_text_overlay.bind("<Button-3>", self._show_context_menu_pdf)
        
        # The currently selected text from context menu
        self.selected_text_cache = ""

        # Populate tree
        self.refresh_library()

    def refresh_library(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        root_node = self.tree.insert("", "end", text="kore_library", open=True)
        self._populate_tree(root_node, self.doc_path)
        
    def _import_file(self):
        file_path = filedialog.askopenfilename(
            title="Importer un document", 
            filetypes=[("Documents Supportés", "*.pdf;*.txt;*.py;*.md;*.json"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            try:
                dest_path = os.path.join(self.doc_path, os.path.basename(file_path))
                if os.path.exists(dest_path):
                    if hasattr(self.app_instance, 'cmd_bar'):
                        self.app_instance.cmd_bar._show_feedback("Ce fichier existe déjà.", is_error=True)
                    return
                shutil.copy2(file_path, dest_path)
                self.refresh_library()
                if hasattr(self.app_instance, 'cmd_bar'):
                    self.app_instance.cmd_bar._show_feedback("Document importé avec succès !")
            except Exception as e:
                if hasattr(self.app_instance, 'cmd_bar'):
                    self.app_instance.cmd_bar._show_feedback(f"Erreur d'import : {e}", is_error=True)

    def _import_folder(self):
        folder_path = filedialog.askdirectory(title="Importer un dossier de cours")
        if folder_path:
            try:
                count = 0
                for root, _, files in os.walk(folder_path):
                    for f in files:
                        ext = f.split('.')[-1].lower() if '.' in f else ""
                        if ext in ['pdf', 'txt', 'py', 'md', 'json']:
                            dest = os.path.join(self.doc_path, f)
                            if not os.path.exists(dest):
                                shutil.copy2(os.path.join(root, f), dest)
                                count += 1
                if count > 0:
                    self.refresh_library()
                    if hasattr(self.app_instance, 'cmd_bar'):
                        self.app_instance.cmd_bar._show_feedback(f"{count} documents importés !")
                else:
                    if hasattr(self.app_instance, 'cmd_bar'):
                        self.app_instance.cmd_bar._show_feedback("Aucun nouveau document trouvé.")
            except Exception as e:
                if hasattr(self.app_instance, 'cmd_bar'):
                    self.app_instance.cmd_bar._show_feedback(f"Erreur d'import : {e}", is_error=True)

    def _populate_tree(self, parent, path):
        try:
            for item in sorted(os.listdir(path)):
                p = os.path.join(path, item)
                if os.path.isdir(p):
                    node = self.tree.insert(parent, "end", text="📁 " + item, open=False)
                    self._populate_tree(node, p)
                else:
                    ext = item.split('.')[-1].lower() if '.' in item else ""
                    if ext in ['txt', 'py', 'md', 'json', 'pdf']:
                        icon = "📄"
                        if ext == 'pdf': icon = "📕"
                        elif ext == 'py': icon = "🐍"
                        self.tree.insert(parent, "end", text=f"{icon} {item}", values=(p,))
        except Exception as e:
            pass

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        if 'values' in item and item['values']:
            path = item['values'][0]
            if os.path.isfile(path):
                self._load_file(path)

    def _load_file(self, path):
        self.current_extension = path.split('.')[-1].lower()
        
        # Close old PDF
        if self.current_pdf_doc:
            self.current_pdf_doc.close()
            self.current_pdf_doc = None
            
        if self.current_extension == 'pdf':
            self.text_viewer.grid_forget()
            self.pdf_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            
            try:
                self.current_pdf_doc = fitz.open(path)
                self.current_page = 0
                self.btn_prev.configure(state="normal")
                self.btn_next.configure(state="normal")
                self._render_pdf_page()
            except Exception as e:
                self.page_lbl.configure(text="Err chargement PDF")
                print("PDF Error:", e)
        else:
            # Text file
            self.pdf_container.grid_forget()
            self.text_viewer.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            self.page_lbl.configure(text=f"Fichier : {os.path.basename(path)}")
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_viewer.delete("1.0", tk.END)
                    self.text_viewer.insert("1.0", content)
            except Exception as e:
                self.text_viewer.delete("1.0", tk.END)
                self.text_viewer.insert("1.0", f"Erreur de lecture: {e}")

    # --- PDF Navigation ---
    def _render_pdf_page(self):
        if not self.current_pdf_doc: return
        try:
            page = self.current_pdf_doc[self.current_page]
            self.page_lbl.configure(text=f"Page {self.current_page + 1} / {len(self.current_pdf_doc)}")
            
            # Zoom factor for better quality (1.5x)
            mat = fitz.Matrix(1.5, 1.5)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            
            self.pdf_image = ImageTk.PhotoImage(img) # Keep ref
            
            self.pdf_canvas.configure(width=pix.width, height=pix.height)
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_image(0, 0, image=self.pdf_image, anchor="nw")
            self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))
            
            # Extract Text for the overlay box
            text_content = page.get_text()
            self.pdf_text_overlay.delete("1.0", tk.END)
            # Add a divider to show this is the extracted text
            self.pdf_text_overlay.insert("1.0", "--- Texte Extrait (Sélectionnable) ---\n\n" + text_content)
            
            # Scroll to top
            self.pdf_container._parent_canvas.yview_moveto(0)

        except Exception as e:
            print("Render error:", e)

    def _next_page(self):
        if self.current_pdf_doc and self.current_page < len(self.current_pdf_doc) - 1:
            self.current_page += 1
            self._render_pdf_page()

    def _prev_page(self):
        if self.current_pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self._render_pdf_page()

    # --- Context Menu Logic ---
    def _show_context_menu(self, event):
        try:
            self.selected_text_cache = self.text_viewer.selection_get()
            if self.selected_text_cache.strip():
                self.context_menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            pass
        finally:
            self.context_menu.grab_release()

    def _show_context_menu_pdf(self, event):
        try:
            self.selected_text_cache = self.pdf_text_overlay.selection_get()
            if self.selected_text_cache.strip():
                self.context_menu.tk_popup(event.x_root, event.y_root)
        except tk.TclError:
            pass
        finally:
            self.context_menu.grab_release()

    def _force_update_selection(self):
        try:
            if self.current_extension == 'pdf':
                self.selected_text_cache = self.pdf_text_overlay.selection_get()
            else:
                self.selected_text_cache = self.text_viewer.selection_get()
        except tk.TclError:
            self.selected_text_cache = ""

    def _ctx_add_journal(self):
        if not self.selected_text_cache: return
        dialog = ctk.CTkInputDialog(text=f"Extrait :\n{self.selected_text_cache[:50]}...\n\nTitre de l'entrée :", title="Ajouter au Journal")
        title = dialog.get_input()
        if title:
            self.app_instance.db.add_journal_entry(title=title, content=self.selected_text_cache, keywords="extrait, library")
            if hasattr(self.app_instance, 'cmd_bar'):
                self.app_instance.cmd_bar._show_feedback(f"Extrait sauvé : {title}", is_error=False)

    def _ctx_add_srs(self):
        if not self.selected_text_cache: return
        dialog = ctk.CTkInputDialog(text=f"Notion: {self.selected_text_cache[:40]}...\n\nCatégorie (ex: Physique, Elect):", title="Nouvelle Notion SRS")
        cat = dialog.get_input()
        if cat:
            self.app_instance.db.add_topic(self.selected_text_cache, cat)
            if hasattr(self.app_instance, 'cmd_bar'):
                self.app_instance.cmd_bar._show_feedback(f"Notion SRS ajoutée dans [{cat}]", is_error=False)

    def _ctx_to_latex(self):
        if not self.selected_text_cache: return
        # Simple heuristic or placeholder: wrap in \[ \]
        # In a full app, this might call an API to translate `x^2/y` to `\frac{x^2}{y}`
        latex_str = f"\\[\n{self.selected_text_cache}\n\\]"
        self.clipboard_clear()
        self.clipboard_append(latex_str)
        if hasattr(self.app_instance, 'cmd_bar'):
            self.app_instance.cmd_bar._show_feedback("Formule LaTeX copiée dans le presse-papier !")

    def _ctx_calc_lab(self):
        if not self.selected_text_cache: return
        if self.app_instance:
            self.app_instance.show_calculator(expression=self.selected_text_cache)
            if hasattr(self.app_instance, 'cmd_bar'):
                self.app_instance.cmd_bar._show_feedback("Formule envoyée à la calculatrice KORE-Calc.")
