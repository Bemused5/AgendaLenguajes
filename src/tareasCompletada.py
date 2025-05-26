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


def completed_tasks_screen(page: ft.Page) -> ft.View:
    user_id  = page.user_data.get("user_id")
    username = page.user_data.get("username", "Usuario")

    tasks_container = ft.Column(spacing=10)

    # ---------------------------------------------------------- #
    #  Cargar completadas
    # ---------------------------------------------------------- #
    def load_completed():
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
                SELECT id, titulo, detalles
                  FROM tareas
                 WHERE user_id = %s AND completada = 1
                 ORDER BY id DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            if not rows:
                tasks_container.controls.append(
                    ft.Text("Aún no tienes tareas completadas.", italic=True)
                )
            else:
                for row in rows:
                    tasks_container.controls.append(build_completed_row(row))
        except mysql.connector.Error as err:
            tasks_container.controls.append(
                ft.Text(f"Error en la base de datos: {err}", color=ft.Colors.RED)
            )
        finally:
            cur.close()
            conn.close()

        page.update()

    # ---------------------------------------------------------- #
    #  Des-marcar (volver a pendientes)
    # ---------------------------------------------------------- #
    def undo_completed(task_id: int, task_box: ft.Container):
        def _after_fade(_):
            conn = connect_db()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE tareas SET completada = 0 WHERE id = %s AND user_id = %s",
                        (task_id, user_id),
                    )
                    conn.commit()
                finally:
                    cur.close()
                    conn.close()
            load_completed()

        task_box.on_animation_end = _after_fade
        task_box.opacity = 0.0
        task_box.update()

    # ---------------------------------------------------------- #
    #  Eliminar definitivamente
    # ---------------------------------------------------------- #
    def delete_task(task_id: int, task_box: ft.Container):
        def _after_fade(_):
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
            load_completed()

        task_box.on_animation_end = _after_fade
        task_box.opacity = 0.0
        task_box.update()

    # ---------------------------------------------------------- #
    #  Row de cada completada
    # ---------------------------------------------------------- #
    def build_completed_row(task: dict) -> ft.Container:
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

        undo_btn = ft.IconButton(
            icon=ft.Icons.UNDO,
            icon_color=ft.Colors.GREEN,
            tooltip="Mover a pendientes",
            on_click=lambda e: undo_completed(task_id, task_box),
        )

        trash_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            tooltip="Eliminar definitivamente",
            on_click=lambda e: delete_task(task_id, task_box),
        )

        task_box.content = ft.Row(
            [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                ft.Column(
                    [ft.Text(titulo, weight=ft.FontWeight.BOLD),
                     ft.Text(detalles, size=12, color=ft.Colors.BLACK54)],
                    spacing=3,
                ),
                ft.Row([undo_btn, trash_btn], spacing=5),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
        )

        return task_box

    # ---------------------------------------------------------- #
    #  AppBar
    # ---------------------------------------------------------- #
    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Volver",
            on_click=lambda e: page.go("/inicioUsuario"),
        ),
        title=ft.Text("Tareas completadas"),
        center_title=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
    )

    view = ft.View(
        route="/completedTasks",
        appbar=appbar,
        controls=[
            ft.Text(f"¡Buen trabajo, {username}! Estas son tus tareas completadas:",
                    size=18),
            tasks_container,
        ],
        padding=15,
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    load_completed()
    return view
