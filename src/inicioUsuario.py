import flet as ft
import mysql.connector

def connect_db():
    """
    Ajusta estos datos a tu configuración de MySQL.
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

def inicio_usuario_screen(page: ft.Page) -> ft.View:
    # Recuperar datos de usuario (user_id y username)
    user_id = page.user_data.get("user_id", None) if hasattr(page, "user_data") else None
    username = page.user_data.get("username", "Usuario") if hasattr(page, "user_data") else "Usuario"

    # Contenedor de mensaje cuando no hay tareas
    no_tasks_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(f"Bienvenido {username}, aquí están las tareas que has añadido", size=20),
                ft.Text(
                    "No has añadido ninguna tarea, presiona el botón + para añadir una tarea",
                    text_align=ft.TextAlign.CENTER
                )
            ]
        ),
        padding=15,
        alignment=ft.alignment.center,
        border_radius=ft.border_radius.all(8),
        border=ft.border.all(1, ft.Colors.BLACK12),
        width=300
    )

    # Contenedor principal donde se listarán las tareas
    tasks_container = ft.Column(spacing=10)

    # -------------------------------------------
    # Funciones para manejar las tareas en DB
    # -------------------------------------------

    def load_tasks():
        """
        Carga las tareas desde la base de datos y actualiza el tasks_container.
        """
        tasks_container.controls.clear()  # Limpiar lista antes de volver a cargar

        if not user_id:
            # Si no hay user_id, mostrar error simple
            tasks_container.controls.append(
                ft.Text("Error: No se encontró ID de usuario. Inicia sesión de nuevo.")
            )
            page.update()
            return

        conn = connect_db()
        if conn is None:
            tasks_container.controls.append(
                ft.Text("Error al conectar con la base de datos.")
            )
            page.update()
            return

        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, titulo, detalles, fecha_inicio, fecha_fin, categoria, completada FROM tareas WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()

            if not rows:
                # No hay tareas, mostrar el contenedor de "no tasks"
                tasks_container.controls.append(no_tasks_container)
            else:
                # Construir UI para cada tarea
                for row in rows:
                    tasks_container.controls.append(
                        build_task_item(row)
                    )

        except mysql.connector.Error as err:
            tasks_container.controls.append(
                ft.Text(f"Error en la base de datos: {err}")
            )
        finally:
            cursor.close()
            conn.close()

        page.update()

    def toggle_completed(task_id, current_value):
        """
        Cambia el estado de completada en la DB (0->1 o 1->0) y recarga las tareas.
        """
        new_value = 0 if current_value == 1 else 1
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            update_query = "UPDATE tareas SET completada = %s WHERE id = %s AND user_id = %s"
            cursor.execute(update_query, (new_value, task_id, user_id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error al actualizar tarea: {err}")
        finally:
            cursor.close()
            conn.close()
        # Recargar la lista de tareas
        load_tasks()

    def delete_task(task_id):
        """
        Elimina la tarea de la DB y recarga la lista de tareas.
        """
        conn = connect_db()
        if conn is None:
            return
        try:
            cursor = conn.cursor()
            delete_query = "DELETE FROM tareas WHERE id = %s AND user_id = %s"
            cursor.execute(delete_query, (task_id, user_id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error al eliminar tarea: {err}")
        finally:
            cursor.close()
            conn.close()
        # Recargar la lista de tareas
        load_tasks()

    # -------------------------------------------
    # Construir el "row" visual de cada tarea
    # -------------------------------------------
    def build_task_item(task):
        """
        Crea el control visual para cada tarea:
        - Círculo para marcar completada (verde) o no (vacío)
        - Título en negrita
        - Detalles truncados a 20 caracteres
        - Botón de basura para eliminar
        """
        task_id = task["id"]
        titulo = task["titulo"]
        detalles = task["detalles"] or ""
        completada = task["completada"]  # 0 o 1

        # Truncar detalles a 20 caracteres
        max_len = 20
        if len(detalles) > max_len:
            detalles = detalles[:max_len] + "..."

        # Elegir ícono y color según si está completada o no
        if completada == 1:
            circle_icon = ft.Icons.RADIO_BUTTON_CHECKED
            circle_color = ft.Colors.GREEN
        else:
            circle_icon = ft.Icons.RADIO_BUTTON_UNCHECKED
            circle_color = ft.Colors.BLACK54

        # Ícono para marcar la tarea como completada / no completada
        complete_icon_button = ft.IconButton(
            icon=circle_icon,
            icon_color=circle_color,
            tooltip="Marcar como completada" if completada == 0 else "Desmarcar tarea",
            on_click=lambda e: toggle_completed(task_id, completada)
        )

        # Título en negritas, detalles en texto más pequeño
        title_text = ft.Text(titulo, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)
        details_text = ft.Text(detalles, size=12, color=ft.Colors.BLACK54)

        # Ícono de basura para eliminar
        trash_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            tooltip="Eliminar tarea",
            # on_click=lambda e: delete_task(task_id)  # <-- Ya no se llama directamente
            on_click=lambda e: page.go(f"/deleteTask?id={task_id}")  # <-- Navegamos a la pantalla de borrado
        )

        # Estructura final de la tarea
        return ft.Container(
            on_click=lambda e: page.go(f"/taskDetails?id={task_id}"),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border_radius=ft.border_radius.all(8),
            content=ft.Row(
                # `spacing` crea un espacio horizontal entre cada control del Row
                spacing=8,
                controls=[
                    complete_icon_button,
                    ft.Column(
                        [
                            title_text,
                            details_text
                        ],
                        spacing=5,
                    ),
                    trash_button
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )


    # -------------------------------------------
    # Función para cerrar sesión
    # -------------------------------------------
    def logout(e):
        page.user_data = {}
        page.go("/")

    # -------------------------------------------
    # AppBar
    # -------------------------------------------
    appbar = ft.AppBar(
        automatically_imply_leading=False,
        leading_width=220,
        toolbar_height=60,
        leading=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            controls=[
                # Botón para cerrar sesión
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Cerrar sesión",
                        on_click=logout
                    ),
                    bgcolor=ft.Colors.GREEN_300,
                    padding=ft.padding.all(5),
                    border_radius=ft.border_radius.all(30),
                ),
                # Botón para ver estadísticas
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.INSERT_CHART_OUTLINED,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Ver estadísticas",
                        on_click=lambda e: page.go("/taskStatistics")
                    ),
                    bgcolor=ft.Colors.GREEN_300,
                    padding=ft.padding.all(5),
                    border_radius=ft.border_radius.all(30),
                )
            ],
        ),
        title=ft.Text("Agenda de tareas"),
        center_title=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        actions=[
            # Botón "+" para agregar tarea
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.ADD,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Agregar tarea",
                    on_click=lambda e: page.go("/addTask")
                ),
                bgcolor=ft.Colors.GREEN_300,
                padding=ft.padding.all(5),
                border_radius=ft.border_radius.all(30),
                margin=ft.margin.only(right=10),
            )
        ],
    )

    # -------------------------------------------
    # Construimos la vista
    # -------------------------------------------
    view = ft.View(
        "/inicioUsuario",
        appbar=appbar,
        controls=[tasks_container],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # Cargar las tareas al entrar a esta pantalla
    load_tasks()

    return view