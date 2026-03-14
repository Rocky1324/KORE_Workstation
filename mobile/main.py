import flet as ft
import asyncio
from api_client import KOREApiClient

# --- Constants & Colors (Neon & Glass) ---
NEON_RED = "#FF3131"
NEON_GREEN = "#39FF14"
NEON_BLUE = "#00F3FF"
GOLD = "#FFA500"
BG_DARK = "#050505"
GLASS_WHITE = "rgba(255, 255, 255, 0.08)"
GLASS_BORDER = "rgba(255, 255, 255, 0.15)"

async def main(page: ft.Page):
    # --- 1. SUPER PURGE ---
    page.controls.clear()
    page.overlay.clear()
    page.navigation_bar = None
    
    page.title = "KORE Premium"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = "#000000"
    page.window_width = 400
    page.window_height = 800
    
    api = KOREApiClient()
    
    # --- 2. COMPONENTS ---
    tasks_list = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True, spacing=12)
    content_area = ft.Container(expand=True, bgcolor=BG_DARK)
    
    # Connection components
    status_text = ft.Text("HORS LIGNE", size=12, weight="bold", color="#888888")
    status_dot = ft.Container(width=8, height=8, bgcolor=NEON_RED, border_radius=4)
    next_task_title = ft.Text("Aucun devoir urgent", size=18, weight="bold", color="#FFFFFF")
    next_task_subtitle = ft.Text("Connectez-vous pour synchroniser", size=12, color="#666666")
    sr_stats = ft.Text("0", size=24, weight="black", color=NEON_GREEN)

    # --- 3. UI GENERATORS ---
    def glass_card(title=None, content=None, height=None, expand=False, border_color=GLASS_BORDER, on_click=None):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=12, weight="bold", color="#888888") if title else ft.Container(),
                content if content else ft.Container()
            ], spacing=10) if title else content,
            bgcolor=GLASS_WHITE,
            border=ft.Border.all(1, border_color),
            border_radius=18,
            padding=20,
            height=height,
            expand=expand,
            blur=ft.Blur(10, 10),
            on_click=on_click
        )

    async def check_connection():
        status_text.value = "VERIFICATION..."
        status_dot.bgcolor = GOLD
        page.update()
        
        print(f"DEBUG: Test de connexion vers {api.base_url}")
        res = await api.check_status()
        
        if "error" in res:
            err_msg = str(res["error"])
            print(f"DEBUG CONNECTION ERROR: {err_msg}")
            if "Timeout" in err_msg: status_text.value = "ERREUR: Timeout"
            elif "Connection refused" in err_msg: status_text.value = "ERREUR: Refusee"
            else: status_text.value = f"ERREUR: {err_msg[:20]}"
            status_dot.bgcolor = NEON_RED
        else:
            status_text.value = "OPERATIONNEL"
            status_dot.bgcolor = NEON_GREEN
        page.update()

    async def refresh_tasks():
        tasks_list.controls.clear()
        page.update()
        
        res = await api.get_tasks()
        tasks_list.controls.clear()
        
        if isinstance(res, list) and len(res) > 0:
            for t in res:
                p_color = NEON_RED if t.get('priority') == 'Haute' else NEON_BLUE if t.get('priority') == 'Moyenne' else NEON_GREEN
                tasks_list.controls.append(
                    glass_card(
                        content=ft.Row([
                            ft.Container(width=4, height=35, bgcolor=p_color, border_radius=2),
                            ft.Column([
                                ft.Text(t.get('text', 'Sans titre'), size=15, weight="bold", color="#FFFFFF"),
                                ft.Text(str(t.get('priority', 'N/A')), size=11, color="#888888"),
                            ], expand=True, spacing=2),
                            ft.Text("[V]", size=14, color="#FFFFFF")
                        ], alignment="spaceBetween")
                    )
                )
            next_task_title.value = res[0].get('text', 'Devoir')
            next_task_subtitle.value = "Priorite: " + str(res[0].get('priority', 'N/A'))
        else:
            tasks_list.controls.append(ft.Text("Aucun devoir trouve", color="#888888"))
            
        page.update()

    async def handle_connect():
        raw_config = url_input.value
        print(f"\n[DEBUG] ENTREE BRUTE: [{raw_config}]")
        
        config = raw_config.strip()
        if "|" in config:
            url_part, key_part = config.split("|", 1)
            
            # Nettoyage "Nucleaire"
            clean_url = url_part.strip().replace(" ", "")
            while clean_url.startswith("http://"): clean_url = clean_url[7:]
            while clean_url.startswith("https://"): clean_url = clean_url[8:]
            clean_url = clean_url.split("/")[0]
            
            final_url = f"http://{clean_url}"
            print(f">>> FINAL CONNECTION URL: [{final_url}]")
            
            api.set_config(final_url, key_part.strip())
            await show_view(0)
        else:
            url_input.error_text = "Format requis: IP:PORT|CLE"
        page.update()

    # --- 4. VIEWS ---
    dashboard_view = ft.Container(
        expand=True, padding=20,
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("KORE", size=32, weight="black", color="#FFFFFF", italic=True),
                    ft.Row([status_dot, status_text], spacing=8)
                ]),
                ft.Container(
                    content=ft.Text("RECO", size=10, weight="bold"),
                    bgcolor=GLASS_WHITE, padding=10, border_radius=10,
                    on_click=lambda _: asyncio.create_task(check_connection())
                )
            ], alignment="spaceBetween"),
            ft.Container(height=20),
            glass_card(
                title="PROCHAIN DEVOIR",
                border_color=NEON_BLUE,
                content=ft.Column([
                    next_task_title,
                    next_task_subtitle,
                    ft.Container(height=5),
                    ft.Row([
                        ft.Container(bgcolor=NEON_BLUE, padding=ft.Padding.symmetric(vertical=6, horizontal=15), 
                                    border_radius=8, content=ft.Text("VOIR PLUS", size=10, weight="bold", color="#000000"),
                                    on_click=lambda _: asyncio.create_task(show_view(1))),
                        ft.Text("T: 14:00", size=10, color="#888888")
                    ], alignment="spaceBetween")
                ])
            ),
            ft.Row([
                glass_card(title="SRS", expand=True, content=ft.Column([sr_stats, ft.Text("CARTES", size=10, color="#666666")])),
                glass_card(title="SYNC", expand=True, content=ft.Column([ft.Text("AUTO", size=18, color=NEON_GREEN), ft.Text("ACTIF", size=10, color="#666666")]))
            ], spacing=15),
            ft.Container(height=10),
            ft.Text("FLUX RECENT", size=14, weight="bold", color="#FFFFFF"),
            glass_card(height=100, content=ft.Text("Saisissez une note rapide...", color="#444444", size=13),
                       on_click=lambda _: asyncio.create_task(show_view(2)))
        ], spacing=15)
    )

    tasks_view = ft.Container(
        expand=True, padding=20,
        content=ft.Column([
            ft.Text("DEVOIRS", size=28, weight="black", color="#FFFFFF"),
            ft.Container(height=10),
            tasks_list
        ], spacing=10)
    )

    # JOURNAl
    note_title = ft.TextField(label="Titre", bgcolor="#111111", border_color=GLASS_BORDER, text_size=14)
    note_content = ft.TextField(
        label="Contenu de la note...", 
        bgcolor="#111111", 
        border_color=GLASS_BORDER, 
        text_size=13, 
        multiline=True, 
        min_lines=10,
        max_lines=15
    )
    
    save_status = ft.Text("", size=12, weight="bold")

    async def save_note():
        if not note_title.value or not note_content.value:
            save_status.value = "ERREUR: Champs vides"
            save_status.color = NEON_RED
            page.update()
            return

        save_status.value = "SAUVEGARDE..."
        save_status.color = GOLD
        page.update()

        res = await api.send_journal_note(note_title.value, note_content.value)
        
        if "error" in res:
            save_status.value = f"ERREUR: {str(res['error'])[:20]}"
            save_status.color = NEON_RED
        else:
            save_status.value = "NOTE ENREGISTREE !"
            save_status.color = NEON_GREEN
            note_title.value = ""
            note_content.value = ""
        
        page.update()
        await asyncio.sleep(3)
        save_status.value = ""
        page.update()

    journal_view = ft.Container(
        expand=True, padding=20,
        content=ft.Column([
            ft.Text("JOURNAL", size=28, weight="black", color="#FFFFFF"),
            ft.Container(height=5),
            save_status,
            ft.Container(height=5),
            note_title,
            note_content,
            ft.Container(height=10),
            ft.Container(
                bgcolor=GOLD, height=60, border_radius=15, alignment=ft.Alignment(0,0),
                content=ft.Text("ENREGISTRER", color="#000000", weight="bold"),
                on_click=lambda _: asyncio.create_task(save_note())
            )
        ], spacing=10, scroll=ft.ScrollMode.ADAPTIVE)
    )

    url_input = ft.TextField(label="IP_PC:8000|CLE", bgcolor="#111111", border_color=GLASS_BORDER, text_size=13)
    setup_view = ft.Container(
        expand=True, padding=30, alignment=ft.Alignment(0,0),
        content=ft.Column([
            ft.Text("[ SETUP ]", size=60, color=GOLD, weight="bold"),
            ft.Text("CONFIGURATION", size=24, weight="bold", color="#FFFFFF"),
            url_input,
            ft.Container(height=20),
            ft.Container(bgcolor=GOLD, padding=ft.Padding.symmetric(vertical=15, horizontal=40), border_radius=12,
                        content=ft.Text("CONNECTER", color="#000000", weight="bold"),
                        on_click=lambda _: asyncio.create_task(handle_connect()))
        ], horizontal_alignment="center", spacing=20)
    )

    # --- 5. SHELL & NAVIGATION ---
    async def show_view(idx):
        views = [dashboard_view, tasks_view, journal_view, setup_view]
        content_area.content = views[idx]
        if idx == 0: await check_connection()
        elif idx == 1: await refresh_tasks()
        elif idx == 2: save_status.value = ""
        page.update()

    def nav_item(label, idx):
        return ft.Container(
            content=ft.Text(label, size=14, weight="bold", color="#FFFFFF"),
            on_click=lambda _: asyncio.create_task(show_view(idx)),
            padding=15, border_radius=12
        )

    bottom_bar = ft.Container(
        height=80, bgcolor="#0A0A0A",
        border=ft.Border(top=ft.BorderSide(1, "rgba(255,255,255,0.05)")),
        content=ft.Row([
            nav_item("HOME", 0),
            nav_item("TASKS", 1),
            nav_item("NOTE", 2),
            nav_item("CONF", 3),
        ], alignment="spaceEvenly"),
        blur=ft.Blur(15, 15)
    )

    content_area.content = setup_view
    page.add(ft.Column([content_area, bottom_bar], expand=True, spacing=0))
    page.update()

if __name__ == "__main__":
    ft.run(main)
