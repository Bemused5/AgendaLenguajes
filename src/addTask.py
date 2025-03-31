import flet as ft
import mysql.connector
import re  # Para validar datos si fuera necesario

def connect_db():
    """
    Conexión a la base de datos en Hostinger (o cualquier otro servidor).
    Ajusta host, user, password, database con tus credenciales reales.
    """
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

def add_task_screen(page: ft.Page) -> ft.View:
    """Pantalla para añadir una nueva tarea con DatePicker funcional y guardar en DB."""

    # Texto para mostrar mensajes de error o confirmación
    message_text = ft.Text("", color=ft.Colors.RED, size=14)

    # Función para actualizar la fecha en los campos
    def update_date_field(field, e):
        field.value = date_picker.value
        page.update()

    # Crear `DatePicker` y asignar evento `on_change`
    date_picker = ft.DatePicker(
        on_change=lambda e: update_date_field(selected_field, e)
    )

    # Variables para almacenar el campo seleccionado
    selected_field = None

    # Función para mostrar el `DatePicker`
    def show_date_picker(e, field):
        nonlocal selected_field
        selected_field = field  # Guardamos qué campo será actualizado
        page.dialog = date_picker
        date_picker.open = True
        page.update()

    # Campos del formulario
    title_label = ft.Text("Título", weight=ft.FontWeight.BOLD)
    title_field = ft.TextField(hint_text="Proyecto lenguajes", width=300)

    details_label = ft.Text("Ingresa detalles en caso de ser necesario:", weight=ft.FontWeight.BOLD)
    details_field = ft.TextField(hint_text="Proyecto lenguajes", multiline=True, width=300)

    start_date_label = ft.Text("Deseas asignarle un plazo a la tarea:", weight=ft.FontWeight.BOLD)
    start_date_field = ft.TextField(
        hint_text="Fecha de inicio", 
        width=140, 
        read_only=True, 
        on_click=lambda e: show_date_picker(e, start_date_field)
    )
    end_date_field = ft.TextField(
        hint_text="Fecha de fin", 
        width=140, 
        read_only=True, 
        on_click=lambda e: show_date_picker(e, end_date_field)
    )

    category_label = ft.Text("Selecciona una categoría que le quieres asignar a la tarea:", weight=ft.FontWeight.BOLD)
    category_dd = ft.Dropdown(
        width=300,
        options=[
            ft.dropdown.Option("Escuela"),
            ft.dropdown.Option("Trabajo"),
            ft.dropdown.Option("Salud y Bienestar"),
            ft.dropdown.Option("Hogar"),
            ft.dropdown.Option("Otros"),
        ]
    )

    # Función para guardar tarea en la DB y regresar a inicioUsuario
    def save_task(e):
        # Recuperar el ID del usuario que inició sesión
        user_id = page.user_data.get("user_id", None)
        if not user_id:
            # Si no hay user_id, el usuario no está logueado correctamente
            message_text.value = "Error: no se encontró el ID de usuario. Inicia sesión nuevamente."
            message_text.color = ft.Colors.RED
            page.update()
            return

        titulo = title_field.value.strip()
        detalles = details_field.value.strip()
        if start_date_field.value:
        # Convierte a cadena con el formato que quieras
            fecha_inicio = start_date_field.value.strftime("%Y-%m-%d")
        else:
            fecha_inicio = None  # o la cadena vacía

        if end_date_field.value:
            fecha_fin = end_date_field.value.strftime("%Y-%m-%d")
        else:
            fecha_fin = None

        categoria = category_dd.value  # Puede ser None si no elige nada

        # Validaciones mínimas (ej. que el título no esté vacío)
        if not titulo:
            message_text.value = "Debes ingresar al menos un título para la tarea."
            message_text.color = ft.Colors.RED
            page.update()
            return

        # Insertar en la base de datos
        conn = connect_db()
        if conn is None:
            message_text.value = "Error al conectar a la base de datos."
            message_text.color = ft.Colors.RED
            page.update()
            return

        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO tareas (user_id, titulo, detalles, fecha_inicio, fecha_fin, categoria)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, titulo, detalles, fecha_inicio, fecha_fin, categoria))
            conn.commit()

            # Mensaje de éxito y regresar
            message_text.value = "¡Tarea creada con éxito!"
            message_text.color = ft.Colors.GREEN
            page.update()

            # Regresar a la pantalla de inicio de usuario
            page.go("/inicioUsuario")

        except mysql.connector.Error as err:
            message_text.value = f"Error en la base de datos: {err}"
            message_text.color = ft.Colors.RED
        finally:
            cursor.close()
            conn.close()

        page.update()

    # Botón de regreso
    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_size=24,
        tooltip="Regresar",
        on_click=lambda e: page.go("/inicioUsuario")
    )

    # Botón de Crear Tarea con estilo similar a la imagen
    save_button = ft.ElevatedButton(
        text="Crear tarea",
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.WHITE,
        width=300,
        on_click=save_task
    )

    return ft.View(
        "/addTask",
        controls=[
            ft.Row([back_button, ft.Text("Añadir tarea", size=20, weight=ft.FontWeight.BOLD)], spacing=10),
            title_label,
            title_field,
            details_label,
            details_field,
            start_date_label,
            ft.Row([start_date_field, end_date_field], spacing=10),
            category_label,
            category_dd,
            save_button,
            message_text,   # Texto de retroalimentación
            date_picker     # Asegurar que el `DatePicker` esté presente en el layout
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )