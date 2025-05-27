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
    user_id = page.user_data.get("user_id")
    username = page.user_data.get("username", "Usuario")

    tasks_container = ft.Column(spacing=10)

    
    def load_completed():
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
                 WHERE user_id=%s AND completada=1
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
                for r in rows:
                    tasks_container.controls.append(build_completed_row(r))
        finally:
            cur.close(); conn.close(); page.update()

    # ---------- Des-marcar completada ----------------------------
    def undo_completed(task_id: int, task_box: ft.Container):
        def _done(_):
            conn = connect_db()
            if conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE tareas SET completada=0 WHERE id=%s AND user_id=%s",
                    (task_id, user_id),
                )
                conn.commit(); cur.close(); conn.close()
            load_completed()

        task_box.opacity = 0.0
        task_box.on_animation_end = _done
        task_box.update()

    
    def build_completed_row(task: dict) -> ft.Container:
        task_id  = task["id"]
        titulo   = task["titulo"]
        detalles = task["detalles"] or ""

        undo_btn = ft.IconButton(
            icon=ft.Icons.CHECK_CIRCLE,
            icon_color=ft.Colors.GREEN,
            tooltip="Deshacer completado",
            on_click=lambda _: undo_completed(task_id, box),
        )

        trash_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            tooltip="Eliminar definitivamente",
            # → AHORA solo navega a la pantalla de confirmación
            on_click=lambda _: page.go(f"/deleteTask?id={task_id}"),
        )

        text_col = ft.Column(
            [ft.Text(titulo, weight=ft.FontWeight.BOLD),
             ft.Text(detalles, size=12, color=ft.Colors.BLACK54)],
            expand=True,
            spacing=3,
        )

        box = ft.Container(
            content=ft.Row(
                [undo_btn, text_col, trash_btn],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.WHITE,
            padding=10,
            border_radius=8,
            animate_opacity=ft.Animation(300, "ease"),
        )
        return box

    
    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Volver",
            on_click=lambda _: page.go("/inicioUsuario"),
        ),
        title=ft.Text("Tareas completadas"),
        center_title=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
    )


    view = ft.View(
        "/completedTasks",
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
