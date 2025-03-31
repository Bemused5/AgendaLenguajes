import flet as ft
import mysql.connector
from datetime import date, timedelta
from urllib.parse import urlparse, parse_qs

def connect_db():
    """ Ajusta tu conexión a la DB """
    try:
        conn = mysql.connector.connect(
            host="srv1281.hstgr.io",
            user="u543141245_LenguajesAdmin",
            password="123456789Upslp",
            database="u543141245_Lenguajes"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

def task_statistics_screen(page: ft.Page) -> ft.View:
    """
    Retorna la vista de estadísticas de tareas con opciones de categoría o fecha.
    """

    selected_text = ft.Text("")
    selection_container = ft.Container()

    # Botón de regreso
    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_size=24,
        tooltip="Regresar",
        on_click=lambda e: page.go("/inicioUsuario")
    )

    title = ft.Row(
        controls=[
            back_button,
            ft.Text("Estadísticas de las tareas", size=18, weight=ft.FontWeight.BOLD)
        ],
        spacing=10
    )

    description = ft.Text(
        "Selecciona si deseas las estadísticas por categoría o por fecha",
        text_align=ft.TextAlign.CENTER
    )

    # -------------------------------------------------
    # Variables para cachear los resultados:
    # -------------------------------------------------
    weekly_data_loaded = False
    monthly_data_loaded = False
    weekly_view = None
    monthly_view = None

    # -------------------------------------------------
    # Función para mostrar un mensaje de "Cargando..."
    # -------------------------------------------------
    def show_loading_message(message="Obteniendo información de la DB..."):
        selection_container.content = ft.Text(message)
        page.update()

    # -------------------------------------------------
    # Función para mostrar las opciones de fecha
    # -------------------------------------------------
    def show_date_options(e):
        selection_container.content = ft.Column([
            ft.Text("Selecciona el tipo de estadística por fecha:"),
            ft.Row([
                ft.ElevatedButton("Semanal", on_click=show_weekly_stats),
                ft.ElevatedButton("Mensual", on_click=show_monthly_stats)
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])
        page.update()

    # -------------------------------------------------
    # Lógica Semanal
    # -------------------------------------------------
    def show_weekly_stats(e):
        nonlocal weekly_data_loaded, weekly_view
        if weekly_data_loaded and weekly_view:
            # Si ya cargamos los datos antes, solo mostramos la vista guardada
            selection_container.content = weekly_view
            selected_text.value = "Estadísticas por fecha (Semanal):"
            page.update()
            return

        show_loading_message()

        user_id = page.user_data.get("user_id", None)
        if not user_id:
            selection_container.content = ft.Text("No se encontró el ID de usuario.")
            page.update()
            return

        today = date.today()
        offset = today.weekday()  # Lunes=0, Domingo=6
        start_of_this_week = today - timedelta(days=offset)

        weekly_rows = []
        conn = connect_db()
        if conn is None:
            selection_container.content = ft.Text("Error al conectar con la base de datos.")
            page.update()
            return

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            for i in range(5):
                week_start = start_of_this_week + timedelta(days=7 * i)
                week_end = week_start + timedelta(days=6)
                week_label = f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b')}"

                # Tareas dentro de la semana
                query_in = """
                    SELECT COUNT(*) as total
                    FROM tareas
                    WHERE user_id = %s
                      AND fecha_inicio IS NOT NULL
                      AND fecha_fin IS NOT NULL
                      AND fecha_inicio >= %s
                      AND fecha_fin <= %s
                """
                cursor.execute(query_in, (user_id, week_start, week_end))
                in_count = cursor.fetchone()["total"]

                # Tareas que se superponen
                query_overlap = """
                    SELECT COUNT(*) as total
                    FROM tareas
                    WHERE user_id = %s
                      AND fecha_inicio IS NOT NULL
                      AND fecha_fin IS NOT NULL
                      AND fecha_inicio <= %s
                      AND fecha_fin >= %s
                """
                cursor.execute(query_overlap, (user_id, week_end, week_start))
                overlap_count = cursor.fetchone()["total"]

                multiweek_count = overlap_count - in_count

                max_for_scaling = max(in_count, multiweek_count, 1)
                bar1_width = int((in_count / max_for_scaling) * 200)
                bar1 = ft.Container(
                    width=bar1_width, height=20, bgcolor=ft.Colors.GREEN, border_radius=5
                )
                row1 = ft.Row(
                    controls=[
                        ft.Text("Tareas de la semana:", width=150),
                        bar1,
                        ft.Text(str(in_count))
                    ],
                    spacing=5
                )

                bar2_width = int((multiweek_count / max_for_scaling) * 200)
                bar2 = ft.Container(
                    width=bar2_width, height=20, bgcolor=ft.Colors.BLUE, border_radius=5
                )
                row2 = ft.Row(
                    controls=[
                        ft.Text("Tareas multi-semana:", width=150),
                        bar2,
                        ft.Text(str(multiweek_count))
                    ],
                    spacing=5
                )

                weekly_rows.append(
                    ft.Column(
                        controls=[
                            ft.Text(f"Semana {i+1}: {week_label}", weight=ft.FontWeight.BOLD),
                            row1,
                            row2
                        ],
                        spacing=5
                    )
                )

            weekly_view = ft.Column(controls=weekly_rows, spacing=15)
            selection_container.content = weekly_view
            weekly_data_loaded = True

            selected_text.value = "Estadísticas por fecha (Semanal):"
            page.update()

        except mysql.connector.Error as err:
            selection_container.content = ft.Text(f"Error en la base de datos: {err}")
            page.update()
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    # -------------------------------------------------
    # Lógica Mensual
    # -------------------------------------------------
    def show_monthly_stats(e):
        nonlocal monthly_data_loaded, monthly_view
        if monthly_data_loaded and monthly_view:
            # Ya cargamos los datos antes
            selection_container.content = monthly_view
            selected_text.value = "Estadísticas por fecha (Mensual):"
            page.update()
            return

        show_loading_message()

        user_id = page.user_data.get("user_id", None)
        if not user_id:
            selection_container.content = ft.Text("No se encontró el ID de usuario.")
            page.update()
            return

        current_year = date.today().year
        monthly_rows = []
        conn = connect_db()
        if conn is None:
            selection_container.content = ft.Text("Error al conectar con la base de datos.")
            page.update()
            return

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            for month in range(1, 13):
                start_of_month = date(current_year, month, 1)
                if month == 12:
                    end_of_month = date(current_year+1, 1, 1) - timedelta(days=1)
                else:
                    end_of_month = date(current_year, month+1, 1) - timedelta(days=1)

                month_label = start_of_month.strftime("%b %Y")

                # Tareas dentro del mes
                query_in = """
                    SELECT COUNT(*) as total
                    FROM tareas
                    WHERE user_id = %s
                    AND fecha_inicio IS NOT NULL
                    AND fecha_fin IS NOT NULL
                    AND fecha_inicio >= %s
                    AND fecha_fin <= %s
                """
                cursor.execute(query_in, (user_id, start_of_month, end_of_month))
                in_count = cursor.fetchone()["total"]

                # Tareas que se superponen
                query_overlap = """
                    SELECT COUNT(*) as total
                    FROM tareas
                    WHERE user_id = %s
                    AND fecha_inicio IS NOT NULL
                    AND fecha_fin IS NOT NULL
                    AND fecha_inicio <= %s
                    AND fecha_fin >= %s
                """
                cursor.execute(query_overlap, (user_id, end_of_month, start_of_month))
                overlap_count = cursor.fetchone()["total"]

                multi_month_count = overlap_count - in_count

                max_for_scaling = max(in_count, multi_month_count, 1)
                bar1_width = int((in_count / max_for_scaling) * 200)
                bar1 = ft.Container(
                    width=bar1_width, height=20, bgcolor=ft.Colors.GREEN, border_radius=5
                )
                row1 = ft.Row(
                    controls=[
                        ft.Text("Tareas del mes:", width=120),
                        bar1,
                        ft.Text(str(in_count))
                    ],
                    spacing=5
                )

                bar2_width = int((multi_month_count / max_for_scaling) * 200)
                bar2 = ft.Container(
                    width=bar2_width, height=20, bgcolor=ft.Colors.BLUE, border_radius=5
                )
                row2 = ft.Row(
                    controls=[
                        ft.Text("Tareas multi-mes:", width=120),
                        bar2,
                        ft.Text(str(multi_month_count))
                    ],
                    spacing=5
                )

                # Armamos un "bloque" para este mes
                month_block = ft.Column(
                    controls=[
                        ft.Text(f"Mes {month_label}", weight=ft.FontWeight.BOLD),
                        row1,
                        row2
                    ],
                    spacing=5
                )

                monthly_rows.append(month_block)

                # -----------------------------
                # Agrupar los 12 bloques en pares (2 columnas por fila)
                # -----------------------------
                monthly_pairs = []
                for i in range(0, len(monthly_rows), 2):
                    col1 = monthly_rows[i]
                    col2 = monthly_rows[i+1] if i+1 < len(monthly_rows) else ft.Container()  # vacío si no hay par
                    monthly_pairs.append(
                        ft.Row(
                            controls=[col1, col2],
                            spacing=20
                        )
                    )

                # Colocamos todo en una Column con scroll
                monthly_view = ft.Column(
                    controls=monthly_pairs,
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO  # <--- Permite hacer scroll vertical
                )

                selection_container.content = monthly_view
                monthly_data_loaded = True

                selected_text.value = "Estadísticas por fecha (Mensual):"
                page.update()

        except mysql.connector.Error as err:
            selection_container.content = ft.Text(f"Error en la base de datos: {err}")
            page.update()
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()


    # -------------------------------------------------
    # Mostrar gráfico de barras por categoría
    # -------------------------------------------------
    def show_category_chart(e):
        show_loading_message("Obteniendo estadísticas por categoría...")

        conn = connect_db()
        if conn is None:
            selection_container.content = ft.Text("Error al conectar con la base de datos.")
            page.update()
            return

        counts = {
            "Escuela": 0,
            "Trabajo": 0,
            "Salud y Bienestar": 0,
            "Hogar": 0,
            "Otros": 0
        }

        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            user_id = page.user_data.get("user_id", None)
            if user_id is not None:
                query = """
                    SELECT categoria, COUNT(*) AS total
                    FROM tareas
                    WHERE user_id = %s
                    GROUP BY categoria
                """
                cursor.execute(query, (user_id,))
            else:
                query = """
                    SELECT categoria, COUNT(*) AS total
                    FROM tareas
                    GROUP BY categoria
                """
                cursor.execute(query)

            rows = cursor.fetchall()
            for row in rows:
                cat = row["categoria"]
                total = row["total"]
                if cat in counts:
                    counts[cat] = total

        except mysql.connector.Error as err:
            selection_container.content = ft.Text(f"Error en la base de datos: {err}")
            page.update()
            return
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

        max_count = max(counts.values()) if counts else 1
        if max_count == 0:
            max_count = 1

        bars = []
        for cat, count in counts.items():
            bar_width = int((count / max_count) * 300)
            bar_container = ft.Container(
                width=bar_width,
                height=20,
                bgcolor=ft.Colors.BLUE,
                border_radius=5
            )
            row = ft.Row(
                controls=[
                    ft.Text(cat, width=100),
                    bar_container,
                    ft.Text(str(count))
                ],
                spacing=5
            )
            bars.append(row)

        selection_container.content = ft.Column(
            controls=bars,
            spacing=10
        )
        selected_text.value = "Estadísticas por categoría:"
        page.update()

    # -------------------------------------------------
    # Botones principales
    # -------------------------------------------------
    buttons = ft.Row(
        controls=[
            ft.ElevatedButton("Categoría", width=120, on_click=show_category_chart),
            ft.ElevatedButton("Fecha", width=120, on_click=show_date_options)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    return ft.View(
        "/taskStatistics",
        controls=[title, description, buttons, selection_container, selected_text],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
