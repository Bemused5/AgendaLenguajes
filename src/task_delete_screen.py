import flet as ft
import mysql.connector
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

def task_delete_screen(page: ft.Page) -> ft.View:
    """
    Pantalla para confirmar y eliminar una tarea.
    Ruta: /deleteTask?id=XYZ
    El usuario debe escribir 'CONFIRMAR' para eliminar.
    """

    # 1. Obtener el ID de la tarea desde la URL
    parsed_url = urlparse(page.route)  # e.g. "/deleteTask?id=5"
    query_params = parse_qs(parsed_url.query)
    task_id = None
    if "id" in query_params:
        task_id = query_params["id"][0]  # '5'
    if not task_id:
        return ft.View(
            "/deleteTask",
            controls=[ft.Text("No se especificó la tarea.")]
        )
    
    # Convertir a int si corresponde
    task_id = int(task_id)

    # 2. Consultar la DB para obtener datos de la tarea
    conn = connect_db()
    if conn is None:
        return ft.View(
            "/deleteTask",
            controls=[ft.Text("Error al conectar con la base de datos.")]
        )

    tarea = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, titulo, detalles, fecha_inicio, fecha_fin, categoria, completada
            FROM tareas
            WHERE id = %s
        """
        cursor.execute(query, (task_id,))
        tarea = cursor.fetchone()
    except mysql.connector.Error as err:
        return ft.View(
            "/deleteTask",
            controls=[ft.Text(f"Error en la base de datos: {err}")]
        )
    finally:
        cursor.close()
        conn.close()

    if not tarea:
        # Tarea no encontrada
        return ft.View(
            "/deleteTask",
            controls=[ft.Text("La tarea no existe o fue eliminada.")]
        )

    # Extraer campos
    titulo = tarea["titulo"]
    detalles = tarea["detalles"]
    fecha_inicio = tarea["fecha_inicio"]
    fecha_fin = tarea["fecha_fin"]
    categoria = tarea["categoria"]
    completada = tarea["completada"]

    # Convertir fechas a string si es necesario
    fecha_inicio_str = str(fecha_inicio) if fecha_inicio else "N/A"
    fecha_fin_str = str(fecha_fin) if fecha_fin else "N/A"

    # Determinar estatus
    status_str = "Completada" if completada == 1 else "No completada"

    # Texto y Título
    title_text = ft.Text("Eliminar tarea", size=24, weight=ft.FontWeight.BOLD)
    confirm_text = ft.Text(
        "Estas seguro de que deseas eliminar la tarea, escribe CONFIRMAR para eliminarla",
        size=14
    )

    # Mostramos los datos de la tarea
    tarea_text = ft.Text(f"Título: {titulo}", weight=ft.FontWeight.BOLD)
    detalles_text = ft.Text(f"Detalles: {detalles}")
    fechas_text = ft.Text(f"Inicio: {fecha_inicio_str}      |    Final: {fecha_fin_str}")
    categoria_text = ft.Text(f"Categoría: {categoria}")
    status_text = ft.Text(f"Status de la tarea: {status_str}")

    # 3. Campo para que el usuario escriba "CONFIRMAR"
    confirm_input = ft.TextField(
        hint_text="CONFIRMAR",
        width=300
    )

    message_text = ft.Text("", color=ft.Colors.RED)

    # 4. Función para eliminar la tarea si el usuario escribió CONFIRMAR
    def delete_task_confirm(e):
        if confirm_input.value.strip().upper() == "CONFIRMAR":
            # Eliminar de la DB
            conn2 = connect_db()
            if conn2 is None:
                message_text.value = "Error al conectar con la base de datos."
                page.update()
                return
            try:
                c2 = conn2.cursor()
                delete_query = "DELETE FROM tareas WHERE id = %s"
                c2.execute(delete_query, (task_id,))
                conn2.commit()
                message_text.value = "Tarea eliminada exitosamente."
                message_text.color = ft.Colors.GREEN
                page.update()
            except mysql.connector.Error as err:
                message_text.value = f"Error al eliminar tarea: {err}"
                message_text.color = ft.Colors.RED
            finally:
                c2.close()
                conn2.close()

            # Regresar a inicioUsuario
            page.go("/inicioUsuario")
        else:
            message_text.value = "No se escribió CONFIRMAR correctamente."
            message_text.color = ft.Colors.RED
            page.update()

    # Botón para eliminar
    delete_button = ft.ElevatedButton(
        text="Eliminar tarea",
        width=300,
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.WHITE,
        on_click=delete_task_confirm
    )

    # Botón de regreso
    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_size=24,
        tooltip="Regresar",
        on_click=lambda e: page.go("/inicioUsuario")
    )

    # AppBar
    appbar = ft.AppBar(
        automatically_imply_leading=False,
        leading=back_button,
        title=ft.Text("Eliminar tarea"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
    )

    # Contenido principal
    content_column = ft.Column(
        spacing=10,
        controls=[
            title_text,
            confirm_text,
            tarea_text,
            detalles_text,
            fechas_text,
            categoria_text,
            status_text,           # <-- Aquí mostramos el estatus
            confirm_input,
            delete_button,
            message_text
        ]
    )

    return ft.View(
        "/deleteTask",
        appbar=appbar,
        controls=[content_column],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
