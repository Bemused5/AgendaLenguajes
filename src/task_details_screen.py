import flet as ft
import mysql.connector
from urllib.parse import urlparse, parse_qs

def connect_db():
    """Tu misma función de conexión."""
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

def task_details_screen(page: ft.Page) -> ft.View:
    """
    Pantalla que muestra los detalles completos de una tarea.
    La ruta puede ser /taskDetails?id=XYZ
    """
    # 1. Parsear el ID de la tarea desde la ruta
    parsed_url = urlparse(page.route)
    query_params = parse_qs(parsed_url.query)
    task_id = None
    if "id" in query_params:
        task_id = query_params["id"][0]  # p.ej. '5' en string

    if task_id is None:
        # Si no hay ID, mostramos un error
        return ft.View(
            "/taskDetails",
            controls=[ft.Text("No se especificó la tarea.")]
        )

    # Convertir task_id a int (si la DB lo maneja como entero)
    task_id = int(task_id)

    # 2. Consultar la base de datos
    conn = connect_db()
    if conn is None:
        return ft.View(
            "/taskDetails",
            controls=[ft.Text("Error al conectar con la base de datos.")]
        )

    tarea = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT titulo, detalles, fecha_inicio, fecha_fin, categoria, completada
            FROM tareas
            WHERE id = %s
        """
        cursor.execute(query, (task_id,))
        tarea = cursor.fetchone()
    except mysql.connector.Error as err:
        return ft.View(
            "/taskDetails",
            controls=[ft.Text(f"Error en la base de datos: {err}")]
        )
    finally:
        cursor.close()
        conn.close()

    if not tarea:
        # Si la tarea no existe
        return ft.View(
            "/taskDetails",
            controls=[ft.Text("La tarea no existe o fue eliminada.")]
        )

    # 3. Crear variables con los datos de la tarea
    titulo = tarea["titulo"]
    detalles = tarea["detalles"]
    fecha_inicio = tarea["fecha_inicio"]
    fecha_fin = tarea["fecha_fin"]
    categoria = tarea["categoria"]
    completada = tarea["completada"]  # 0 o 1

    # Convertir fechas a string, si no lo son
    fecha_inicio_str = str(fecha_inicio) if fecha_inicio else "N/A"
    fecha_fin_str = str(fecha_fin) if fecha_fin else "N/A"

    # 4. Creamos el botón y la función para marcar/desmarcar completada
    def toggle_completed(e):
        nonlocal completada  # Para modificar la variable externa

        new_value = 0 if completada == 1 else 1
        conn2 = connect_db()
        if conn2 is None:
            # Podrías mostrar un error, un mensaje, etc.
            return

        try:
            c2 = conn2.cursor()
            update_query = "UPDATE tareas SET completada = %s WHERE id = %s"
            c2.execute(update_query, (new_value, task_id))
            conn2.commit()

            # Actualizar la variable local y el texto del botón
            completada = new_value
            if completada == 1:
                toggle_button.text = "Quitar completado"
            else:
                toggle_button.text = "Marcar tarea como completa"

            page.update()  # Refrescar la UI
        except mysql.connector.Error as err:
            print(f"Error al actualizar tarea: {err}")
        finally:
            c2.close()
            conn2.close()

    # 5. Creamos el botón con el texto inicial según el estado de la tarea
    if completada == 1:
        toggle_button = ft.ElevatedButton(
            text="Quitar completado",
            on_click=toggle_completed
        )
    else:
        toggle_button = ft.ElevatedButton(
            text="Marcar tarea como completa",
            on_click=toggle_completed
        )

    # 6. Botón de regreso
    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_size=24,
        tooltip="Regresar",
        on_click=lambda e: page.go("/inicioUsuario")
    )

    # 7. Creamos el AppBar
    appbar = ft.AppBar(
        automatically_imply_leading=False,
        leading=back_button,
        title=ft.Text("Detalles de la tarea"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
    )

    # 8. Contenido principal
    content_column = ft.Column(
        spacing=10,
        controls=[
            ft.Text(f"Título:\n{titulo}"),
            ft.Text(f"Detalles:\n{detalles}"),
            ft.Text("Fechas de la tarea"),
            ft.Text(f"Inicio: {fecha_inicio_str}\tFinal: {fecha_fin_str}"),
            ft.Text(f"Categoría: {categoria}"),
            toggle_button,
        ]
    )

    # 9. Devolvemos la View
    return ft.View(
        "/taskDetails",
        appbar=appbar,
        controls=[content_column],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )