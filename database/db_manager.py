import sqlite3
import os
from datetime import datetime, timedelta

class DBManager:
    def __init__(self, db_path="kore.db"):
        self.db_path = db_path
        self._conn = None
        self.init_db()

    def get_connection(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._conn

    def init_db(self):
        schema_path = os.path.join(os.path.dirname(__file__), "init_db.sql")
        if not os.path.exists(schema_path):
            print(f"Schema file not found at {schema_path}")
            return
            
        with self.get_connection() as conn:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            
            # Apply schema updates for existing databases
            cursor = conn.cursor()
            
            # Check if tasks has completed_at
            cursor.execute("PRAGMA table_info(tasks)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'completed_at' not in columns:
                cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at DATE")
            
            
            # Initialize default formulas
            cursor = conn.cursor()
            defaults = [
                ("maxwell", r"\nabla \cdot \mathbf{E} = \frac{\rho}{\varepsilon_0}", "Équation de Maxwell-Gauss"),
                ("newton", r"F = G \frac{m_1 m_2}{r^2}", "Loi universelle de la gravitation"),
                ("schrodinger", r"i \hbar \frac{\partial}{\partial t} \Psi = \hat{H} \Psi", "Équation de Schrödinger"),
                ("thermo", r"dS = \frac{\delta Q}{T}", "Deuxième principe de la thermodynamique"),
                ("euler", r"e^{i\pi} + 1 = 0", "Identité d'Euler"),
                ("fourier", r"\hat{f}(\xi) = \int_{-\infty}^{\infty} f(x) e^{-2\pi i x \xi} dx", "Transformée de Fourier"),
                ("taylor", r"f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!} (x-a)^n", "Série de Taylor"),
                ("gauss_int", r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}", "Intégrale de Gauss"),
                ("laplace", r"L\{f(t)\} = \int_{0}^{\infty} e^{-st} f(t) dt", "Transformée de Laplace"),
                ("bayes", r"P(A|B) = \frac{P(B|A)P(A)}{P(B)}", "Théorème de Bayes"),
                ("maxwell_faraday", r"\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}", "Loi de Faraday (Maxwell)"),
                ("lorentz", r"\mathbf{F} = q(\mathbf{E} + \mathbf{v} \times \mathbf{B})", "Force de Lorentz"),
                ("snell", r"n_1 \sin \theta_1 = n_2 \sin \theta_2", "Loi de Snell-Descartes"),
                ("poynting", r"\mathbf{S} = \frac{1}{\mu_0} \mathbf{E} \times \mathbf{B}", "Vecteur de Poynting"),
                ("coulomb", r"F = k_e \frac{|q_1 q_2|}{r^2}", "Loi de Coulomb"),
                ("einstein", r"E = mc^2", "Équivalence masse-énergie"),
                ("bernoulli", r"P + \frac{1}{2}\rho v^2 + \rho gh = \text{const}", "Équation de Bernoulli"),
                ("lagrange", r"\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_i}\right) - \frac{\partial L}{\partial q_i} = 0", "Équations de Euler-Lagrange"),
                ("heisenberg", r"\Delta x \Delta p \geq \frac{\hbar}{2}", "Principe d'incertitude d'Heisenberg"),
                ("kepler", r"\frac{T^2}{a^3} = \frac{4\pi^2}{GM}", "Troisième loi de Kepler"),
                ("gaz_parfaits", r"PV = nRT", "Loi des gaz parfaits"),
                ("boltzmann", r"S = k_B \ln W", "Formule de Boltzmann (Entropie)"),
                ("stefan", r"P = \sigma A T^4", "Loi de Stefan-Boltzmann"),
                ("navier_stokes", r"\rho \left(\frac{\partial \mathbf{v}}{\partial t} + \mathbf{v} \cdot \nabla \mathbf{v}\right) = -\nabla p + \mu \nabla^2 \mathbf{v} + \mathbf{f}", "Équations de Navier-Stokes"),
                ("planck", r"E = h \nu", "Relation de Planck-Einstein")
            ]
            cursor.executemany("INSERT OR IGNORE INTO formulas (name, latex_code, description) VALUES (?, ?, ?)", defaults)
            conn.commit()

    # --- Math-Physics Tracker Methods ---
    def add_topic(self, name, category):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO topics (name, category) VALUES (?, ?)", (name, category))
            topic_id = cursor.lastrowid
            
            # Initialize first review for today
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute('''INSERT INTO reviews 
                              (topic_id, next_review_date, interval, ease_factor) 
                              VALUES (?, ?, 1, 2.5)''', (topic_id, today))
            conn.commit()
            return topic_id

    def get_topics(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, category FROM topics")
            return cursor.fetchall()
            
    def get_due_reviews(self, date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT t.id, t.name, t.category, r.interval, r.ease_factor 
                              FROM topics t 
                              JOIN reviews r ON t.id = r.topic_id 
                              WHERE r.next_review_date <= ?''', (date,))
            return cursor.fetchall()
            
    def update_review(self, topic_id, next_date, new_interval, new_ease):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE reviews 
                              SET next_review_date = ?, interval = ?, ease_factor = ?
                              WHERE topic_id = ?''', 
                           (next_date, new_interval, new_ease, topic_id))
            conn.commit()
            self.log_study_session()

    def log_study_session(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check if entry exists for today
            cursor.execute("SELECT id, reviews_completed FROM study_sessions WHERE date = ?", (today,))
            result = cursor.fetchone()
            
            if result:
                # Increment
                new_count = result[1] + 1
                cursor.execute("UPDATE study_sessions SET reviews_completed = ? WHERE id = ?", (new_count, result[0]))
            else:
                # Create new
                cursor.execute("INSERT INTO study_sessions (date, reviews_completed) VALUES (?, 1)", (today,))
            conn.commit()

    def get_study_sessions(self, limit=14):
        # Fetch last 14 days of study data
        cursor = self.get_connection().cursor()
        cursor.execute("SELECT date, reviews_completed FROM study_sessions ORDER BY date ASC LIMIT ?", (limit,))
        return cursor.fetchall()

    def get_dashboard_data(self):
        """Batches multiple KPI queries into one set of results for performance."""
        today = datetime.now().strftime("%Y-%m-%d")
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Due Cards
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE next_review_date <= ?", (today,))
        due_cards = cursor.fetchone()[0]
        
        # 2. Latest Journal
        cursor.execute("SELECT title FROM journal ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        latest_log = row[0] if row else "Aucun log"
        
        # 3. Pending Tasks
        cursor.execute("SELECT text FROM tasks WHERE status != 'Fait' ORDER BY priority DESC, deadline ASC LIMIT 4")
        tasks = [t[0] for t in cursor.fetchall()]
        
        # 4. Homework Urgency
        limit_hw = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        cursor.execute('''SELECT subject, title, deadline FROM homework 
                          WHERE deadline <= ? AND status != 'Fait' 
                          ORDER BY deadline ASC''', (limit_hw,))
        homework = cursor.fetchall()
        
        # 5. Study Sessions (Activity Chart)
        cursor.execute("SELECT date, reviews_completed FROM study_sessions ORDER BY date DESC LIMIT 7")
        sessions = cursor.fetchall()

        # Pomodoro Sessions (Last 7 days)
        cursor.execute("SELECT date, SUM(duration_minutes) FROM pomodoro_sessions GROUP BY date ORDER BY date DESC LIMIT 7")
        pomodoro = cursor.fetchall()
        
        # Completed Tasks (Last 7 days)
        cursor.execute("SELECT completed_at, COUNT(*) FROM tasks WHERE status = 'Fait' AND completed_at IS NOT NULL GROUP BY completed_at ORDER BY completed_at DESC LIMIT 7")
        completed_tasks = cursor.fetchall()

        # 6. Git Status (Batched for performance)
        from core.git_sync import GitSyncManager
        sync_status = GitSyncManager().get_status()
        
        return {
            "due_cards": due_cards,
            "latest_log": latest_log,
            "tasks": tasks,
            "homework": homework,
            "sessions": dict(sessions),
            "pomodoro": dict(pomodoro),
            "completed_tasks": dict(completed_tasks),
            "streak": self.get_current_streak(),
            "sync_status": sync_status
        }
            
    def get_due_cards_count(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE next_review_date <= ?", (today,))
            return cursor.fetchone()[0]
            
    def get_current_streak(self):
        """Calculates consecutive days of study from today backwards."""
        today = datetime.now().date()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date FROM study_sessions ORDER BY date DESC")
            dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in cursor.fetchall()]
        
        if not dates: return 0
        
        streak = 0
        current_date = today
        
        # If they haven't studied today, but studied yesterday, the streak is still alive
        if dates[0] == today:
            streak = 1
            idx = 1
        elif dates[0] == today - timedelta(days=1):
            streak = 1
            current_date = dates[0]
            idx = 1
        else:
            return 0
            
        while idx < len(dates):
            expected_prev = current_date - timedelta(days=1)
            if dates[idx] == expected_prev:
                streak += 1
                current_date = dates[idx]
                idx += 1
            else:
                break
        return streak

    # --- Journal Methods ---
    def add_journal_entry(self, title, content, keywords=""):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO journal (date, title, content, keywords) 
                              VALUES (?, ?, ?, ?)''', (today, title, content, keywords))
            conn.commit()
            return cursor.lastrowid

    def get_journal_entries(self, limit=50):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, date, title, content, keywords FROM journal ORDER BY date DESC, id DESC LIMIT ?", (limit,))
            return cursor.fetchall()
            
    def get_latest_journal_title(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title FROM journal ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else "Aucun log"

    # --- Formula Methods ---
    def get_formula(self, name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT latex_code, description FROM formulas WHERE name = ?", (name.lower(),))
            return cursor.fetchone()
            
    def list_formulas(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, description FROM formulas ORDER BY name")
            return cursor.fetchall()

    # --- Citation Methods ---
    def add_citation(self, url, title, authors, pub_date, notes=""):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO citations 
                              (date_added, url, title, authors, pub_date, notes) 
                              VALUES (?, ?, ?, ?, ?, ?)''', 
                           (today, url, title, authors, pub_date, notes))
            conn.commit()
            return cursor.lastrowid
            
    def get_citations(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url, title, authors, pub_date FROM citations ORDER BY id DESC")
            return cursor.fetchall()

    # --- Setting Methods ---
    def set_setting(self, key, value):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def get_setting(self, key, default=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            return result[0] if result else default

    # --- Homework & Project Methods ---
    def add_homework(self, subject, title, deadline, priority=3):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO homework (subject, title, deadline, priority) 
                              VALUES (?, ?, ?, ?)''', (subject, title, deadline, priority))
            conn.commit()
            return cursor.lastrowid

    def get_upcoming_homework(self, days=7):
        limit_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT id, subject, title, deadline, priority, status 
                              FROM homework 
                              WHERE deadline <= ? AND status != 'Fait' 
                              ORDER BY deadline ASC''', (limit_date,))
            return cursor.fetchall()

    def add_project(self, name, description=""):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO projects (name, description, start_date) VALUES (?, ?, ?)", 
                           (name, description, today))
            conn.commit()
            return cursor.lastrowid

    def add_task(self, text, priority=3, deadline=None, project_id=None, parent_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO tasks (text, priority, deadline, project_id, parent_id) 
                              VALUES (?, ?, ?, ?, ?)''', (text, priority, deadline, project_id, parent_id))
            conn.commit()
            return cursor.lastrowid

    def update_task_status(self, task_id, status='Fait'):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status == 'Fait':
                cursor.execute("UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?", (status, today, task_id))
            else:
                cursor.execute("UPDATE tasks SET status = ?, completed_at = NULL WHERE id = ?", (status, task_id))
            
            # If task is part of a project, possibly log to journal
            cursor.execute("SELECT text, project_id FROM tasks WHERE id = ?", (task_id,))
            task = cursor.fetchone()
            if task and task[1] and status == 'Fait':
                cursor.execute("SELECT name FROM projects WHERE id = ?", (task[1],))
                proj_name = cursor.fetchone()[0]
                self.add_journal_entry(f"Tâche terminée: {task[0]}", 
                                       f"Projet: {proj_name}\nStatus: Complété via /done.", 
                                       "Auto-Task")
            conn.commit()

    def log_pomodoro_session(self, duration_minutes):
        today = datetime.now().strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO pomodoro_sessions (date, duration_minutes) 
                              VALUES (?, ?)''', (today, duration_minutes))
            conn.commit()

    def get_pending_tasks(self, limit=10):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT id, text, priority, deadline, project_id 
                              FROM tasks 
                              WHERE status != 'Fait' 
                              ORDER BY priority DESC, deadline ASC LIMIT ?''', (limit,))
            return cursor.fetchall()

    def get_projects(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description, status, start_date FROM projects ORDER BY start_date DESC")
            return cursor.fetchall()

    def get_project_tasks(self, project_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT id, text, status, priority, deadline 
                              FROM tasks 
                              WHERE project_id = ? 
                              ORDER BY status ASC, priority DESC''', (project_id,))
            return cursor.fetchall()

    def get_all_homework(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, subject, title, deadline, priority, status FROM homework ORDER BY deadline ASC")
            return cursor.fetchall()

    def delete_homework(self, hw_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM homework WHERE id = ?", (hw_id,))
            conn.commit()

    def delete_task(self, task_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

    def delete_project(self, project_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Delete tasks associated with project
            cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()

if __name__ == "__main__":
    db = DBManager()
    print("Database initialized successfully.")
