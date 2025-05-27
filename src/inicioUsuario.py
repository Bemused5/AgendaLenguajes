import flet as ft
import mysql.connector


# CONEXIÓN BD 
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


#  PANTALLA INICIO USUARIO 
def inicio_usuario_screen(page: ft.Page) -> ft.View:
    user_id = page.user_data.get("user_id")
    username = page.user_data.get("username", "Usuario")

    # Contenedor de tareas
    tasks_container = ft.Column(spacing=10)

    #  Botón “Ver completadas”
    completed_btn_row = ft.Row(
        [
            ft.ElevatedButton(
                "Ver mis tareas completadas",
                icon=ft.Icons.DONE_ALL,
                bgcolor=ft.Colors.GREEN_300,
                color=ft.Colors.WHITE,
                on_click=lambda _: page.go("/completedTasks"),
            )
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    # Mensaje si no hay tareas
    no_tasks_container = ft.Container(
        ft.Column(
            [
                ft.Text(
                    "No has añadido ninguna tarea aún, o puede que ya las hayas completado.\n\n"
                    "Presiona + para añadir tareas o usa “Ver mis tareas completadas”.",
                    text_align=ft.TextAlign.CENTER,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
        border_radius=8,
        border=ft.border.all(1, ft.Colors.BLACK12),
    )

    def resize_no_tasks():
        no_tasks_container.width = min(700, int(page.width * 0.9))

    #DB cargar tareas
    def load_tasks():
        tasks_container.controls.clear()
        conn = connect_db()
        if not conn:
            tasks_container.controls.append(
                ft.Text("Error al conectar con la base de datos.", color=ft.Colors.RED)
            )
            page.update()
            return

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, titulo, detalles
                  FROM tareas
                 WHERE user_id=%s AND completada=0
                 ORDER BY id DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            if not rows:
                resize_no_tasks()
                tasks_container.controls.append(no_tasks_container)
            else:
                for row in rows:
                    tasks_container.controls.append(build_task_item(row))
        finally:
            cur.close()
            conn.close()
        page.update()

    # Marcar como completada
    def toggle_completed(task_id: int, task_box: ft.Container):
        task_box.opacity = 0.0
        task_box.on_animation_end = lambda _: (
            update_status(task_id, 1),
            load_tasks(),
        )
        task_box.update()

    def update_status(task_id: int, completed: int):
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE tareas SET completada=%s WHERE id=%s AND user_id=%s",
                (completed, task_id, user_id),
            )
            conn.commit()
            cur.close()
            conn.close()

    # -------- Fila visual de cada tarea ---------------------------
    def build_task_item(task: dict) -> ft.Container:
        task_id = task["id"]
        titulo = task["titulo"]
        detalles = task["detalles"] or ""

        complete_btn = ft.IconButton(
            icon=ft.Icons.RADIO_BUTTON_UNCHECKED,
            icon_color=ft.Colors.BLACK54,
            tooltip="Marcar como completada",
            on_click=lambda _: toggle_completed(task_id, task_box),
        )

        trash_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            tooltip="Eliminar tarea",
            on_click=lambda _: page.go(f"/deleteTask?id={task_id}"),
        )

        text_column = ft.Column(
            [
                ft.Text(titulo, weight=ft.FontWeight.BOLD),
                ft.Text(
                    detalles,
                    size=12,
                    color=ft.Colors.BLACK54,
                    max_lines=2,
                    overflow="ellipsis",
                ),
            ],
            expand=True,
            spacing=3,
        )

        task_box = ft.Container(
            content=ft.Row(
                [complete_btn, text_column, trash_btn],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border_radius=8,
            animate_opacity=ft.Animation(300, "ease"),
        )

        task_box.on_click = lambda _: page.go(f"/taskDetails?id={task_id}")
        return task_box

    # -------- AppBar y acciones ----------------------------------
    def logout(_):
        page.user_data = {}
        page.go("/")

    appbar = ft.AppBar(
        leading=ft.Row(
            [
                # Logout
                ft.IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Cerrar sesión",
                    icon_color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN_300,
                    on_click=logout,
                ),
                #Estadísticas
                ft.IconButton(
                    icon=ft.Icons.INSERT_CHART_OUTLINED,
                    tooltip="Ver estadísticas",
                    icon_color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN_300,
                    on_click=lambda _: page.go("/taskStatistics"),
                ),
            ],
            spacing=10,
        ),
        title=ft.Text("Agenda de tareas"),
        center_title=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        actions=[
            ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="Agregar tarea",
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_300,
                on_click=lambda _: page.go("/addTask"),
            )
        ],
    )
    # -------- Vista final ------------------------------------------
    view = ft.View(
        "/inicioUsuario",
        appbar=appbar,
        controls=[completed_btn_row, tasks_container],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.on_resize = lambda _: resize_no_tasks()
    load_tasks()
    return view
