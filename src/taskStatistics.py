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
        print(f"Error de conexión a la BD: {err}")
        return None


def task_statistics_screen(page: ft.Page) -> ft.View:

    selection_container = ft.Container()
    selected_text = ft.Text("")


    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Regresar",
            on_click=lambda _: page.go("/inicioUsuario"),
        ),
        title=ft.Text("Estadísticas de las tareas"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
    )


    weekly_data_loaded, monthly_data_loaded = False, False
    weekly_view, monthly_view = None, None

    def show_loading(msg="Obteniendo información…"):
        selection_container.content = ft.Text(msg)
        page.update()

    # CATEGORÍA 
    def show_category_chart(_):
        show_loading("Obteniendo estadísticas por categoría…")
        conn = connect_db()
        if not conn:
            selection_container.content = ft.Text("Error al conectar con la BD.")
            page.update()
            return

        counts = {
            "Escuela": 0, "Trabajo": 0, "Salud y Bienestar": 0,
            "Hogar": 0, "Otros": 0
        }

        try:
            cur = conn.cursor(dictionary=True)
            user_id = page.user_data.get("user_id")
            if user_id:
                cur.execute(
                    """
                    SELECT categoria, COUNT(*) total
                      FROM tareas WHERE user_id=%s GROUP BY categoria
                    """,
                    (user_id,),
                )
            else:
                cur.execute(
                    "SELECT categoria, COUNT(*) total FROM tareas GROUP BY categoria"
                )
            for r in cur:
                if r["categoria"] in counts:
                    counts[r["categoria"]] = r["total"]
        finally:
            cur.close(); conn.close()

        max_count = max(counts.values()) or 1
        bars = []
        for cat, val in counts.items():
            bars.append(
                ft.Row(
                    [
                        ft.Text(cat, width=140),
                        ft.Container(
                            width=int((val / max_count) * 250),
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


    def show_date_options(_):
        selection_container.content = ft.Column(
            [
                ft.Text("Selecciona el rango de fechas:"),
                ft.Row(
                    [
                        ft.ElevatedButton("Semanal", on_click=show_weekly_stats),
                        ft.ElevatedButton("Mensual", on_click=show_monthly_stats),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=12,
        )
        selected_text.value = ""
        page.update()

    #Estadisticas Semanales
    def show_weekly_stats(_):
        nonlocal weekly_data_loaded, weekly_view
        if weekly_data_loaded:
            selection_container.content = weekly_view
            selected_text.value = "Estadísticas por fecha (Semanal):"
            page.update()
            return

        show_loading()
        user_id = page.user_data.get("user_id")
        if not user_id:
            selection_container.content = ft.Text("No se encontró ID de usuario.")
            page.update()
            return

        today = date.today()
        start_monday = today - timedelta(days=today.weekday())
        conn = connect_db()
        if not conn:
            selection_container.content = ft.Text("Error BD.")
            page.update()
            return

        weekly_rows = []
        try:
            cur = conn.cursor(dictionary=True)
            for i in range(5):
                ws = start_monday + timedelta(days=7 * i)
                we = ws + timedelta(days=6)
                label = f"{ws.strftime('%d %b')} - {we.strftime('%d %b')}"

                cur.execute(
                    """
                    SELECT COUNT(*) total
                      FROM tareas
                     WHERE user_id=%s
                       AND fecha_inicio>=%s
                       AND fecha_fin<=%s
                    """,
                    (user_id, ws, we),
                )
                in_cnt = cur.fetchone()["total"]

                cur.execute(
                    """
                    SELECT COUNT(*) total
                      FROM tareas
                     WHERE user_id=%s
                       AND fecha_inicio<=%s
                       AND fecha_fin>=%s
                    """,
                    (user_id, we, ws),
                )
                overlap = cur.fetchone()["total"] - in_cnt

                max_cnt = max(in_cnt, overlap, 1)
                bar1 = ft.Container(width=int(in_cnt / max_cnt * 220),
                                    height=20, bgcolor=ft.Colors.GREEN, border_radius=5)
                bar2 = ft.Container(width=int(overlap / max_cnt * 220),
                                    height=20, bgcolor=ft.Colors.BLUE, border_radius=5)

                weekly_rows.append(
                    ft.Column(
                        [
                            ft.Text(f"Semana {i+1}: {label}", weight=ft.FontWeight.BOLD),
                            ft.Row([ft.Text("Tareas de la semana:", width=160), bar1, ft.Text(str(in_cnt))]),
                            ft.Row([ft.Text("Tareas multi-semana:", width=160), bar2, ft.Text(str(overlap))]),
                        ],
                        spacing=4,
                    )
                )
        finally:
            cur.close(); conn.close()

        weekly_view = ft.Column(weekly_rows, spacing=15)
        weekly_data_loaded = True
        selection_container.content = weekly_view
        selected_text.value = "Estadísticas por fecha (Semanal):"
        page.update()

    # Estadisticas Mensuales
    def show_monthly_stats(_):
        nonlocal monthly_data_loaded, monthly_view
        if monthly_data_loaded:
            selection_container.content = monthly_view
            selected_text.value = "Estadísticas por fecha (Mensual):"
            page.update()
            return

        show_loading()
        user_id = page.user_data.get("user_id")
        year = date.today().year
        conn = connect_db()
        if not conn:
            selection_container.content = ft.Text("Error BD.")
            page.update()
            return

        month_cols = []
        try:
            cur = conn.cursor(dictionary=True)
            for m in range(1, 13):
                m_start = date(year, m, 1)
                m_end = date(year if m < 12 else year + 1, (m % 12) + 1, 1) - timedelta(days=1)
                lbl = m_start.strftime("%b %Y")

                cur.execute(
                    """
                    SELECT COUNT(*) total FROM tareas
                     WHERE user_id=%s AND fecha_inicio>=%s AND fecha_fin<=%s
                    """,
                    (user_id, m_start, m_end),
                )
                in_cnt = cur.fetchone()["total"]

                cur.execute(
                    """
                    SELECT COUNT(*) total FROM tareas
                     WHERE user_id=%s AND fecha_inicio<=%s AND fecha_fin>=%s
                    """,
                    (user_id, m_end, m_start),
                )
                overlap = cur.fetchone()["total"] - in_cnt

                max_cnt = max(in_cnt, overlap, 1)
                bar1 = ft.Container(width=int(in_cnt / max_cnt * 180),
                                    height=18, bgcolor=ft.Colors.GREEN, border_radius=5)
                bar2 = ft.Container(width=int(overlap / max_cnt * 180),
                                    height=18, bgcolor=ft.Colors.BLUE, border_radius=5)

                month_cols.append(
                    ft.Column(
                        [
                            ft.Text(lbl, weight=ft.FontWeight.BOLD),
                            ft.Row([ft.Text("Mes:", width=110), bar1, ft.Text(str(in_cnt))], spacing=4),
                            ft.Row([ft.Text("Multi-mes:", width=110), bar2, ft.Text(str(overlap))], spacing=4),
                        ],
                        spacing=3,
                        expand=True,
                    )
                )
        finally:
            cur.close(); conn.close()


        pairs = []
        for i in range(0, len(month_cols), 2):
            pairs.append(ft.Row([month_cols[i], month_cols[i+1] if i+1 < len(month_cols) else ft.Container()],
                                spacing=30))

        monthly_view = ft.Column(pairs, spacing=15, scroll=ft.ScrollMode.AUTO)
        monthly_data_loaded = True
        selection_container.content = monthly_view
        selected_text.value = "Estadísticas por fecha (Mensual):"
        page.update()


    btn_category = ft.ElevatedButton("Categoría", on_click=show_category_chart)
    btn_date = ft.ElevatedButton("Fecha", on_click=show_date_options)


    header_row = ft.Row(
        [
            ft.Text("Selecciona si deseas las estadísticas por categoría o por fecha",
                    expand=True),
            btn_category,
            btn_date,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        spacing=15,
    )


    def resize_header(_=None):
        header_row.width = min(1000, int(page.width * 0.95))
        page.update()

    page.on_resize = resize_header
    resize_header()


    return ft.View(
        route="/taskStatistics",
        appbar=appbar,
        controls=[header_row, selected_text, selection_container],
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START,
        padding=20,
    )
