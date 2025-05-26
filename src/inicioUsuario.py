import flet as ft
import mysql.connector


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


def inicio_usuario_screen(page: ft.Page) -> ft.View:
    user_id  = page.user_data.get("user_id")
    username = page.user_data.get("username", "Usuario")

    tasks_container = ft.Column(spacing=10)
    completed_btn = ft.ElevatedButton(
        "Ver mis tareas completadas",
        icon=ft.Icons.DONE_ALL,
        bgcolor=ft.Colors.GREEN_300,
        color=ft.Colors.WHITE,
        on_click=lambda e: page.go("/completedTasks"),
    )

    no_tasks_container = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    f"Bienvenido {username}, aquí están las tareas que has añadido",
                    size=20,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "No has añadido ninguna tarea, presiona el botón + para añadir una tarea",
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=20,
        border_radius=ft.border_radius.all(8),
        border=ft.border.all(1, ft.Colors.BLACK12),
        width=350,
    )

    # ---------------------------------------------------------- #
    #  BD -> sólo pendientes
    # ---------------------------------------------------------- #
    def load_tasks():
        tasks_container.controls.clear()
        conn = connect_db()
        if conn is None:
            tasks_container.controls.append(
                ft.Text("Error al conectar con la base de datos.", color=ft.Colors.RED)
            )
            page.update()
            return

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT id, titulo, detalles, completada
                  FROM tareas
                 WHERE user_id = %s AND completada = 0
                 ORDER BY id DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            if not rows:
                tasks_container.controls.append(no_tasks_container)
            else:
                for row in rows:
                    tasks_container.controls.append(build_task_item(row))
        except mysql.connector.Error as err:
            tasks_container.controls.append(
                ft.Text(f"Error en la base de datos: {err}", color=ft.Colors.RED)
            )
        finally:
            cur.close()
            conn.close()

        page.update()

    # ---------------------------------------------------------- #
    #  Marcar como completada  (sin asyncio / sin Timer)
    # ---------------------------------------------------------- #
    def toggle_completed(task_id: int, current_value: int, task_box: ft.Container):
        new_val = 0 if current_value == 1 else 1

        # callback cuando la animación termina
        def _after_fade(_):
            conn = connect_db()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE tareas SET completada = %s WHERE id = %s AND user_id = %s",
                        (new_val, task_id, user_id),
                    )
                    conn.commit()
                finally:
                    cur.close()
                    conn.close()
            load_tasks()

        task_box.on_animation_end = _after_fade
        task_box.opacity = 0.0
        task_box.update()

    # ---------------------------------------------------------- #
    #  Eliminar
    # ---------------------------------------------------------- #
    def delete_task(task_id: int):
        conn = connect_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM tareas WHERE id = %s AND user_id = %s",
                            (task_id, user_id))
                conn.commit()
            finally:
                cur.close()
                conn.close()
        load_tasks()

    # ---------------------------------------------------------- #
    #  “Row” visual
    # ---------------------------------------------------------- #
    def build_task_item(task: dict) -> ft.Container:
        task_id  = task["id"]
        titulo   = task["titulo"]
        detalles = (task["detalles"] or "")[:20] + "..." \
            if task["detalles"] and len(task["detalles"]) > 20 else (task["detalles"] or "")

        task_box = ft.Container(
            animate_opacity=ft.Animation(300, "ease"),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border_radius=ft.border_radius.all(8),
            opacity=1.0,
        )

        complete_btn = ft.IconButton(
            icon=ft.Icons.RADIO_BUTTON_UNCHECKED,
            icon_color=ft.Colors.BLACK54,
            tooltip="Marcar como completada",
            on_click=lambda e: toggle_completed(task_id, 0, task_box),
        )

        trash_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            tooltip="Eliminar tarea",
            on_click=lambda e: delete_task(task_id),
        )

        task_box.content = ft.Row(
            [
                complete_btn,
                ft.Column(
                    [ft.Text(titulo, weight=ft.FontWeight.BOLD),
                     ft.Text(detalles, size=12, color=ft.Colors.BLACK54)],
                    spacing=3,
                ),
                trash_btn,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
        )

        task_box.on_click = lambda e: page.go(f"/taskDetails?id={task_id}")
        return task_box

    # ---------------------------------------------------------- #
    #  Logout + AppBar
    # ---------------------------------------------------------- #
    def logout(_):
        page.user_data = {}
        page.go("/")

    appbar = ft.AppBar(
        automatically_imply_leading=False,
        leading_width=220,
        leading=ft.Row(
            [
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Cerrar sesión",
                        on_click=logout,
                    ),
                    bgcolor=ft.Colors.GREEN_300,
                    padding=5,
                    border_radius=30,
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.INSERT_CHART_OUTLINED,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Ver estadísticas",
                        on_click=lambda e: page.go("/taskStatistics"),
                    ),
                    bgcolor=ft.Colors.GREEN_300,
                    padding=5,
                    border_radius=30,
                ),
            ],
            spacing=10,
        ),
        title=ft.Text("Agenda de tareas"),
        center_title=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        actions=[
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.ADD,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Agregar tarea",
                    on_click=lambda e: page.go("/addTask"),
                ),
                bgcolor=ft.Colors.GREEN_300,
                padding=5,
                border_radius=30,
                margin=ft.margin.only(right=10),
            )
        ],
    )

    view = ft.View(
        route="/inicioUsuario",
        appbar=appbar,
        controls=[completed_btn, tasks_container],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    load_tasks()
    return view
