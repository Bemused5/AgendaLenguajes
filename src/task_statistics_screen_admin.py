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

def get_all_users():
    """Recupera todos los usuarios (id, nombre) de la tabla 'usuarios'."""
    conn = connect_db()
    if conn is None:
        return []
    users = []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM usuarios")
        rows = cursor.fetchall()
        for row in rows:
            users.append((row["id"], row["nombre"]))
    except mysql.connector.Error as err:
        print(f"Error al obtener usuarios: {err}")
    finally:
        if cursor:
            cursor.close()
        conn.close()
    return users

def task_statistics_screen_admin(page: ft.Page) -> ft.View:
    """
    Pantalla de estadísticas para el Administrador.
    - Puede ser "single" (un usuario en específico) o "all" (todos los usuarios),
      según el query param "type" en la ruta: /taskStatisticsAdmin?type=single
    """

    # --------------------------------------------------------------------
    # 1) Parseamos el parámetro de la URL para ver si es "single" o "all"
    # --------------------------------------------------------------------
    url = urlparse(page.route)  # page.route = "/taskStatisticsAdmin?type=single" (por ejemplo)
    qs = parse_qs(url.query)
    stat_type = qs.get("type", ["all"])[0]  # "single" o "all"

    # Variable para almacenar el user_id seleccionado (solo en modo "single")
    selected_user_id = None

    # --------------------------------------------------------------------
    # Elementos visuales iniciales
    # --------------------------------------------------------------------
    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_size=24,
        tooltip="Regresar",
        # Regresar a la pantalla de inicioAdmin
        on_click=lambda e: page.go("/inicioAdmin")
    )

    title_row = ft.Row(
        controls=[
            back_button,
            ft.Text("Estadísticas de las tareas (Administrador)", size=18, weight=ft.FontWeight.BOLD)
        ],
        spacing=10
    )

    # Texto que mostrará cuál tipo de estadística se seleccionó (Categoría o Fecha)
    selected_text = ft.Text("")

    # Contenedor donde se mostrará la parte central (gráficos, etc.)
    selection_container = ft.Container()

    # Texto descriptivo inicial (puede cambiar dependiendo del modo)
    if stat_type == "single":
        description = ft.Text(
            "Selecciona el usuario y el tipo de estadísticas que deseas ver",
            text_align=ft.TextAlign.CENTER
        )
    else:
        description = ft.Text(
            "Estadísticas para todos los usuarios",
            text_align=ft.TextAlign.CENTER
        )

    # --------------------------------------------------------------------
    # Botones (Categoría, Fecha), inicialmente podrían estar deshabilitados
    # si estamos en modo "single" y aún no se elige usuario
    # --------------------------------------------------------------------
    category_button = ft.ElevatedButton(
        "Categoría",
        width=120,
        on_click=lambda e: show_category_chart(),
        disabled=(stat_type == "single")  # Deshabilitado si es single y no se ha elegido usuario
    )
    date_button = ft.ElevatedButton(
        "Fecha",
        width=120,
        on_click=lambda e: show_date_options(),
        disabled=(stat_type == "single")  # Mismo razonamiento
    )

    # --------------------------------------------------------------------
    # Si es "single", creamos un Dropdown para elegir el usuario
    # --------------------------------------------------------------------
    dropdown_users = None
    if stat_type == "single":
        all_users = get_all_users()
        # Convertimos la lista (id, nombre) a opciones del Dropdown
        dropdown_options = [
            ft.dropdown.Option(str(u[0]), u[1]) for u in all_users
        ]

        dropdown_users = ft.Dropdown(
            label="Selecciona el usuario que deseas ver sus estadísticas",
            hint_text="Escoge un usuario",
            options=dropdown_options,
            on_change=lambda e: on_user_selected(e.control.value)
        )

    # --------------------------------------------------------------------
    # Funciones auxiliares
    # --------------------------------------------------------------------
    def on_user_selected(value):
        """
        Se llama cuando el administrador elige un usuario en el dropdown.
        'value' será el string con el id del usuario.
        """
        nonlocal selected_user_id
        selected_user_id = int(value) if value else None

        # Una vez elegido el usuario, habilitamos los botones
        category_button.disabled = False
        date_button.disabled = False
        page.update()

    def show_loading_message(message="Obteniendo información de la DB..."):
        selection_container.content = ft.Text(message)
        page.update()

    # --------------------------------------------------------------------
    # Funciones para mostrar estadísticas por Categoría
    # --------------------------------------------------------------------
    def show_category_chart():
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

            # Si es single y tenemos un usuario seleccionado, filtramos por user_id
            if stat_type == "single" and selected_user_id is not None:
                query = """
                    SELECT categoria, COUNT(*) AS total
                    FROM tareas
                    WHERE user_id = %s
                    GROUP BY categoria
                """
                cursor.execute(query, (selected_user_id,))
            else:
                # Modo "all": estadísticas de todos los usuarios
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

    # --------------------------------------------------------------------
    # Funciones para mostrar estadísticas por Fecha (Semanal/Mensual)
    # --------------------------------------------------------------------
    # Mostramos opciones (Semanal / Mensual)
    def show_date_options():
        selection_container.content = ft.Column([
            ft.Text("Selecciona el tipo de estadística por fecha:"),
            ft.Row([
                ft.ElevatedButton("Semanal", on_click=show_weekly_stats),
                ft.ElevatedButton("Mensual", on_click=show_monthly_stats)
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])
        page.update()

    # Semanal
    def show_weekly_stats(e=None):
        show_loading_message("Obteniendo estadísticas semanales...")

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
                if stat_type == "single" and selected_user_id is not None:
                    query_in = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE user_id = %s
                          AND fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio >= %s
                          AND fecha_fin <= %s
                    """
                    cursor.execute(query_in, (selected_user_id, week_start, week_end))
                else:
                    # Modo "all"
                    query_in = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio >= %s
                          AND fecha_fin <= %s
                    """
                    cursor.execute(query_in, (week_start, week_end))

                in_count = cursor.fetchone()["total"]

                # Tareas que se superponen en esa semana
                if stat_type == "single" and selected_user_id is not None:
                    query_overlap = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE user_id = %s
                          AND fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio <= %s
                          AND fecha_fin >= %s
                    """
                    cursor.execute(query_overlap, (selected_user_id, week_end, week_start))
                else:
                    query_overlap = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio <= %s
                          AND fecha_fin >= %s
                    """
                    cursor.execute(query_overlap, (week_end, week_start))

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
            selected_text.value = "Estadísticas por fecha (Semanal):"
            page.update()

        except mysql.connector.Error as err:
            selection_container.content = ft.Text(f"Error en la base de datos: {err}")
            page.update()
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    # Mensual
    def show_monthly_stats(e=None):
        show_loading_message("Obteniendo estadísticas mensuales...")

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
            row_blocks = []
            for month in range(1, 13):
                start_of_month = date(current_year, month, 1)
                if month == 12:
                    end_of_month = date(current_year+1, 1, 1) - timedelta(days=1)
                else:
                    end_of_month = date(current_year, month+1, 1) - timedelta(days=1)

                month_label = start_of_month.strftime("%b %Y")

                # Tareas dentro del mes
                if stat_type == "single" and selected_user_id is not None:
                    query_in = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE user_id = %s
                          AND fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio >= %s
                          AND fecha_fin <= %s
                    """
                    cursor.execute(query_in, (selected_user_id, start_of_month, end_of_month))
                else:
                    query_in = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio >= %s
                          AND fecha_fin <= %s
                    """
                    cursor.execute(query_in, (start_of_month, end_of_month))

                in_count = cursor.fetchone()["total"]

                # Tareas que se superponen
                if stat_type == "single" and selected_user_id is not None:
                    query_overlap = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE user_id = %s
                          AND fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio <= %s
                          AND fecha_fin >= %s
                    """
                    cursor.execute(query_overlap, (selected_user_id, end_of_month, start_of_month))
                else:
                    query_overlap = """
                        SELECT COUNT(*) as total
                        FROM tareas
                        WHERE fecha_inicio IS NOT NULL
                          AND fecha_fin IS NOT NULL
                          AND fecha_inicio <= %s
                          AND fecha_fin >= %s
                    """
                    cursor.execute(query_overlap, (end_of_month, start_of_month))

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

                row_blocks.append(month_block)

            # Agrupamos cada dos meses en una fila
            monthly_pairs = []
            for i in range(0, len(row_blocks), 2):
                col1 = row_blocks[i]
                col2 = row_blocks[i+1] if i+1 < len(row_blocks) else ft.Container()
                monthly_pairs.append(
                    ft.Row(
                        controls=[col1, col2],
                        spacing=20
                    )
                )

            monthly_view = ft.Column(
                controls=monthly_pairs,
                spacing=15,
                scroll=ft.ScrollMode.AUTO  # Permite scroll si es muy grande
            )

            selection_container.content = monthly_view
            selected_text.value = "Estadísticas por fecha (Mensual):"
            page.update()

        except mysql.connector.Error as err:
            selection_container.content = ft.Text(f"Error en la base de datos: {err}")
            page.update()
        finally:
            if cursor is not None:
                cursor.close()
            conn.close()

    # --------------------------------------------------------------------
    # Construimos la vista final
    # --------------------------------------------------------------------
    # Si es single, mostramos el dropdown antes de los botones
    if stat_type == "single" and dropdown_users is not None:
        controls_top = [
            title_row,
            description,
            dropdown_users,
            ft.Row([category_button, date_button], alignment=ft.MainAxisAlignment.CENTER),
            selection_container,
            selected_text
        ]
    else:
        # Modo "all": no hay dropdown
        controls_top = [
            title_row,
            description,
            ft.Row([category_button, date_button], alignment=ft.MainAxisAlignment.CENTER),
            selection_container,
            selected_text
        ]

    return ft.View(
        "/taskStatisticsAdmin",
        controls=controls_top,
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
