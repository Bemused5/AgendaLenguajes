import flet as ft
import mysql.connector
from datetime import date, timedelta
from urllib.parse import urlparse, parse_qs



def connect_db():
    try:
        return mysql.connector.connect(
            host="srv1281.hstgr.io",
            user="u543141245_LenguajesAdmin",
            password="123456789Upslp",
            database="u543141245_Lenguajes",
        )
    except mysql.connector.Error as err:
        print(f"Error BD: {err}")
        return None



def get_all_users():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nombre FROM usuarios")
    data = [(r["id"], r["nombre"]) for r in cur]
    cur.close(); conn.close()
    return data


def task_statistics_screen_admin(page: ft.Page) -> ft.View:

    qs = parse_qs(urlparse(page.route).query)
    stat_type = qs.get("type", ["all"])[0] 
    selected_user_id = None


    selection_container = ft.Container()
    selected_text = ft.Text("")


    btn_cat = ft.ElevatedButton("Categoría", width=110, disabled=(stat_type == "single"))
    btn_date = ft.ElevatedButton("Fecha", width=110, disabled=(stat_type == "single"))


    def loading(msg="Obteniendo datos…"):
        selection_container.content = ft.Text(msg)
        page.update()


    dd_users = None
    if stat_type == "single":
        dd_users = ft.Dropdown(
            hint_text="Selecciona un usuario",
            options=[ft.dropdown.Option(str(i), n) for i, n in get_all_users()],
        )

        def on_user_selected(e):
            nonlocal selected_user_id
            selected_user_id = int(e.control.value) if e.control.value else None
            btn_cat.disabled = btn_date.disabled = selected_user_id is None
            page.update()

        dd_users.on_change = on_user_selected


 
    def show_category(_=None):
        loading("Cargando estadísticas por categoría…")
        conn = connect_db()
        if not conn:
            selection_container.content = ft.Text("Error BD.")
            page.update(); return
        counts = {k: 0 for k in ["Escuela", "Trabajo", "Salud y Bienestar", "Hogar", "Otros"]}
        try:
            cur = conn.cursor(dictionary=True)
            if stat_type == "single":
                cur.execute(
                    """
                    SELECT categoria, COUNT(*) total
                      FROM tareas
                     WHERE user_id=%s
                     GROUP BY categoria
                    """,
                    (selected_user_id,),
                )
            else:
                cur.execute("SELECT categoria, COUNT(*) total FROM tareas GROUP BY categoria")
            for r in cur:
                if r["categoria"] in counts:
                    counts[r["categoria"]] = r["total"]
        finally:
            cur.close(); conn.close()

        max_cnt = max(counts.values()) or 1
        bars = []
        for cat, val in counts.items():
            bars.append(
                ft.Row(
                    [
                        ft.Text(cat, width=140),
                        ft.Container(
                            width=int(val / max_cnt * 250),
                            height=20,
                            bgcolor=ft.Colors.BLUE,
                            border_radius=5,
                        ),
                        ft.Text(str(val)),
                    ],
                    spacing=6,
                )
            )
        selection_container.content = ft.Column(bars, spacing=10)
        selected_text.value = "Estadísticas por categoría:"
        page.update()

    btn_cat.on_click = show_category


    def show_date_options(_=None):
        selection_container.content = ft.Column(
            [
                ft.Text("Selecciona el rango de fechas:"),
                ft.Row(
                    [
                        ft.ElevatedButton("Semanal", on_click=show_weekly),
                        ft.ElevatedButton("Mensual", on_click=show_monthly),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
        )
        selected_text.value = ""
        page.update()

    btn_date.on_click = show_date_options

    def show_weekly(_=None):
        loading()
        today = date.today()
        start_monday = today - timedelta(days=today.weekday())
        rows = []
        conn = connect_db(); cur = None
        if not conn:
            selection_container.content = ft.Text("Error BD."); page.update(); return
        try:
            cur = conn.cursor(dictionary=True)
            for i in range(5):
                ws = start_monday + timedelta(days=i * 7)
                we = ws + timedelta(days=6)
                label = f"{ws.strftime('%d %b')} - {we.strftime('%d %b')}"

                def count(q, params):
                    cur.execute(q, params)
                    return cur.fetchone()["total"]

                if stat_type == "single":
                    base_params = (selected_user_id, ws, we)
                    in_q = """SELECT COUNT(*) total FROM tareas
                               WHERE user_id=%s AND fecha_inicio>=%s AND fecha_fin<=%s"""
                    overlap_q = """SELECT COUNT(*) total FROM tareas
                                    WHERE user_id=%s AND fecha_inicio<=%s AND fecha_fin>=%s"""
                    in_cnt = count(in_q, base_params)
                    ov_cnt = count(overlap_q, (selected_user_id, we, ws)) - in_cnt
                else:
                    in_q = """SELECT COUNT(*) total FROM tareas
                               WHERE fecha_inicio>=%s AND fecha_fin<=%s"""
                    overlap_q = """SELECT COUNT(*) total FROM tareas
                                    WHERE fecha_inicio<=%s AND fecha_fin>=%s"""
                    in_cnt = count(in_q, (ws, we))
                    ov_cnt = count(overlap_q, (we, ws)) - in_cnt

                m = max(in_cnt, ov_cnt, 1)
                bar1 = ft.Container(width=int(in_cnt / m * 200), height=18,
                                    bgcolor=ft.Colors.GREEN, border_radius=5)
                bar2 = ft.Container(width=int(ov_cnt / m * 200), height=18,
                                    bgcolor=ft.Colors.BLUE, border_radius=5)

                rows.append(
                    ft.Column(
                        [
                            ft.Text(f"Semana {i+1}: {label}", weight=ft.FontWeight.BOLD),
                            ft.Row([ft.Text("Dentro semana", width=150), bar1, ft.Text(str(in_cnt))]),
                            ft.Row([ft.Text("Multi-semana", width=150), bar2, ft.Text(str(ov_cnt))]),
                        ],
                        spacing=4,
                    )
                )
        finally:
            if cur: cur.close(); conn.close()

        selection_container.content = ft.Column(rows, spacing=15)
        selected_text.value = "Estadísticas por fecha (Semanal):"
        page.update()


    def show_monthly(_=None):
        loading()
        year = date.today().year
        rows = []
        conn = connect_db(); cur = None
        if not conn:
            selection_container.content = ft.Text("Error BD."); page.update(); return
        try:
            cur = conn.cursor(dictionary=True)
            for m in range(1, 13):
                ms = date(year, m, 1)
                me = date(year if m < 12 else year + 1, (m % 12) + 1, 1) - timedelta(days=1)
                label = ms.strftime("%b")

                if stat_type == "single":
                    base_params = (selected_user_id, ms, me)
                    in_q = """SELECT COUNT(*) total FROM tareas
                               WHERE user_id=%s AND fecha_inicio>=%s AND fecha_fin<=%s"""
                    ov_q = """SELECT COUNT(*) total FROM tareas
                               WHERE user_id=%s AND fecha_inicio<=%s AND fecha_fin>=%s"""
                    in_cnt = cur.execute(in_q, base_params) or cur.fetchone()["total"]
                    in_cnt = count_val(cur)
                else:
                    in_q = """SELECT COUNT(*) total FROM tareas
                               WHERE fecha_inicio>=%s AND fecha_fin<=%s"""
                    ov_q = """SELECT COUNT(*) total FROM tareas
                               WHERE fecha_inicio<=%s AND fecha_fin>=%s"""
                    cur.execute(in_q, (ms, me)); in_cnt = cur.fetchone()["total"]

                cur.execute(ov_q, ((selected_user_id,) if stat_type == "single" else ()) + (me, ms))
                ov_cnt = cur.fetchone()["total"] - in_cnt

                mval = max(in_cnt, ov_cnt, 1)
                bar1 = ft.Container(width=int(in_cnt / mval * 180), height=18,
                                    bgcolor=ft.Colors.GREEN, border_radius=5)
                bar2 = ft.Container(width=int(ov_cnt / mval * 180), height=18,
                                    bgcolor=ft.Colors.BLUE, border_radius=5)

                rows.append(
                    ft.Column(
                        [
                            ft.Text(label, weight=ft.FontWeight.BOLD),
                            ft.Row([ft.Text("Mes:", width=110), bar1, ft.Text(str(in_cnt))]),
                            ft.Row([ft.Text("Multi-mes:", width=110), bar2, ft.Text(str(ov_cnt))]),
                        ],
                        spacing=3,
                    )
                )
        finally:
            if cur: cur.close(); conn.close()

        selection_container.content = ft.Column(rows, spacing=12, scroll=ft.ScrollMode.AUTO)
        selected_text.value = "Estadísticas por fecha (Mensual):"
        page.update()


    if stat_type == "single":
        row_user = ft.Row(
            [
                ft.Text("Selecciona un usuario para ver sus estadísticas", expand=True),
                dd_users,
            ],
            spacing=15,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    else:
        row_user = ft.Text("Estadísticas agregadas de todos los usuarios")

  
    row_btns = ft.Row(
        [
            ft.Text("Selecciona el tipo de estadísticas", expand=True),
            btn_cat,
            btn_date,
        ],
        spacing=15,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


    wrapper = ft.Column([row_user, row_btns, selected_text, selection_container], spacing=25)

    def resize(_=None):
        width = min(1000, int(page.width * 0.95))
        for r in (row_user, row_btns):
            r.width = width
        wrapper.width = width
        page.update()

    page.on_resize = resize
    resize()


    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Volver",
            on_click=lambda _: page.go("/inicioAdmin"),
        ),
        title=ft.Text("Estadísticas de las tareas (Admin)"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
    )


    return ft.View(
        route="/taskStatisticsAdmin",
        appbar=appbar,
        controls=[wrapper],
        scroll=ft.ScrollMode.AUTO,
        padding=20,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START,
    )
