import flet as ft
import mysql.connector
import re
from datetime import date


# ---------------------- CONEXIÓN BD ------------------------------
def connect_db():
    try:
        return mysql.connector.connect(
            host="srv1281.hstgr.io",
            user="u543141245_LenguajesAdmin",
            password="123456789Upslp",
            database="u543141245_Lenguajes",
        )
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None


# ---------------------- PANTALLA “NUEVA TAREA” -------------------
def add_task_screen(page: ft.Page) -> ft.View:
    # -----------------------------------------------------------------
    # Manejo del DatePicker
    # -----------------------------------------------------------------
    selected_field: ft.TextField | None = None

    def show_date_picker(e, field):
        nonlocal selected_field
        selected_field = field
        date_picker.open = True
        page.update()

    def update_date_field(_):
        if selected_field and date_picker.value:
            selected_field.value = date_picker.value.strftime("%Y-%m-%d")
            page.update()

    date_picker = ft.DatePicker(on_change=update_date_field, first_date=date(2000, 1, 1))


    # Mensajes
    msg = ft.Text(size=14, color=ft.Colors.RED)

    # Título
    lbl_title = ft.Text("Título", weight=ft.FontWeight.BOLD)
    title_tf = ft.TextField(hint_text="Ej. Proyecto Lenguajes")

    # Detalles
    lbl_details = ft.Text("Detalles", weight=ft.FontWeight.BOLD)
    details_tf = ft.TextField(
        hint_text="Añade una descripción en caso de ser necesario",
        multiline=True,
        min_lines=3,
        max_lines=None,
        expand=True,  # se estira verticalmente si es necesario
    )

    # Fechas
    lbl_dates = ft.Text("Fechas (opcional)", weight=ft.FontWeight.BOLD)
    start_tf = ft.TextField(
        hint_text="Fecha de inicio",
        read_only=True,
        on_click=lambda e: show_date_picker(e, start_tf),
    )
    end_tf = ft.TextField(
        hint_text="Fecha de fin",
        read_only=True,
        on_click=lambda e: show_date_picker(e, end_tf),
    )

    # Categoría
    lbl_cat = ft.Text("Categoría", weight=ft.FontWeight.BOLD)
    cat_dd = ft.Dropdown(
        hint_text="Selecciona una categoría",
        options=[
            ft.dropdown.Option("Escuela"),
            ft.dropdown.Option("Trabajo"),
            ft.dropdown.Option("Salud y Bienestar"),
            ft.dropdown.Option("Hogar"),
            ft.dropdown.Option("Otros"),
        ],
    )

    # -----------------------------------------------------------------
    # Guardar en DB
    # -----------------------------------------------------------------
    def save_task(_):
        user_id = page.user_data.get("user_id")
        if not user_id:
            msg.value = "Error: sesión inválida."
            msg.color = ft.Colors.RED
            page.update()
            return

        titulo = title_tf.value.strip()
        detalles = details_tf.value.strip()
        fecha_ini = start_tf.value or None
        fecha_fin = end_tf.value or None
        categoria = cat_dd.value

        if not titulo:
            msg.value = "Debes ingresar un título."
            msg.color = ft.Colors.RED
            page.update()
            return

        conn = connect_db()
        if conn is None:
            msg.value = "Error al conectar a la base de datos."
            msg.color = ft.Colors.RED
            page.update()
            return

        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO tareas (user_id, titulo, detalles,
                                    fecha_inicio, fecha_fin, categoria)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, titulo, detalles, fecha_ini, fecha_fin, categoria),
            )
            conn.commit()
            msg.value, msg.color = "¡Tarea creada con éxito!", ft.Colors.GREEN
            page.update()
            page.go("/inicioUsuario")
        except mysql.connector.Error as err:
            msg.value = f"Error BD: {err}"
            msg.color = ft.Colors.RED
            page.update()
        finally:
            cur.close()
            conn.close()

    save_btn = ft.ElevatedButton(
        "Crear tarea",
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.WHITE,
        on_click=save_task,
    )


    form_column = ft.Column(
        [
            lbl_title,
            title_tf,
            lbl_details,
            details_tf,
            lbl_dates,
            ft.Row([start_tf, end_tf], spacing=15, expand=True),
            lbl_cat,
            cat_dd,
            msg,
        ],
        spacing=20,
        expand=True,
    )

    wrapper = ft.Container(content=form_column, alignment=ft.alignment.top_left)

    # Ajustar ancho al 90 % 
    def resize(_=None):
        wrapper.width = min(900, int(page.width * 0.9))
        title_tf.width = wrapper.width
        details_tf.width = wrapper.width
        cat_dd.width = wrapper.width
        for tf in (start_tf, end_tf):
            tf.width = (wrapper.width - 15) / 2  # mitad con espacio entre
        page.update()

    page.on_resize = resize
    resize()

    # -----------------------------------------------------------------
    # Barra superios con botón atrás y “Crear tarea” a la derecha
    # -----------------------------------------------------------------
    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Regresar",
            on_click=lambda _: page.go("/inicioUsuario"),
        ),
        title=ft.Text("Añadir tarea"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
        actions=[ft.Container(content=save_btn, margin=ft.margin.only(right=10))],
    )

    # -----------------------------------------------------------------
    # Vista final
    # -----------------------------------------------------------------
    return ft.View(
        route="/addTask",
        appbar=appbar,
        controls=[wrapper, date_picker],
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START,
    )
