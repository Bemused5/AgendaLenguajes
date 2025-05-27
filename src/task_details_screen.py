import flet as ft
import mysql.connector
from urllib.parse import urlparse, parse_qs


#  CONEXIÓN BD 
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


# PANTALLA DETALLES 
def task_details_screen(page: ft.Page) -> ft.View:

    parsed = urlparse(page.route)
    params = parse_qs(parsed.query)
    if "id" not in params:
        return ft.View("/", controls=[ft.Text("No se especificó la tarea.")])
    task_id = int(params["id"][0])

    #Datos de DB
    conn = connect_db()
    if conn is None:
        return ft.View("/", controls=[ft.Text("Error al conectar con la base de datos.")])

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT titulo, detalles, fecha_inicio, fecha_fin,
                   categoria, completada
              FROM tareas
             WHERE id=%s
            """,
            (task_id,),
        )
        row = cur.fetchone()
    finally:
        cur.close()
        conn.close()

    if not row:
        return ft.View("/", controls=[ft.Text("La tarea no existe o fue eliminada.")])

    #Variables
    titulo     = row["titulo"]
    detalles   = row["detalles"] or "—"
    fecha_ini  = str(row["fecha_inicio"]) if row["fecha_inicio"] else "N/A"
    fecha_fin  = str(row["fecha_fin"]) if row["fecha_fin"] else "N/A"
    categoria  = row["categoria"] or "Sin categoría"
    completada = row["completada"]      # 0/1


    toggle_btn = ft.ElevatedButton(
        text="Quitar completado" if completada else "Marcar tarea como completa",
        style=ft.ButtonStyle(padding=ft.Padding(10, 5, 10, 5)),
    )

    def toggle_completed(_):
        nonlocal completada
        new_val = 0 if completada else 1
        conn2 = connect_db()
        if conn2:
            try:
                c2 = conn2.cursor()
                c2.execute(
                    "UPDATE tareas SET completada=%s WHERE id=%s",
                    (new_val, task_id),
                )
                conn2.commit()
                completada = new_val
                toggle_btn.text = (
                    "Quitar completado" if completada else "Marcar tarea como completa"
                )
                page.update()
            finally:
                c2.close()
                conn2.close()

    toggle_btn.on_click = toggle_completed


    def info_row(label, value):
        return ft.Row(
            [
                ft.Text(f"{label}:", weight=ft.FontWeight.BOLD),
                ft.Text(value, expand=True, selectable=True),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            expand=True,
        )

    info_column = ft.Column(
        [
            info_row("Título", titulo),
            info_row("Detalles", detalles),
            info_row("Inicio", fecha_ini),
            info_row("Final",  fecha_fin),
            info_row("Categoría", categoria),
        ],
        spacing=20,
        expand=True,
    )


    wrapper = ft.Container(content=info_column, alignment=ft.alignment.top_left)

    def resize(_=None):
        wrapper.width = min(900, int(page.width * 0.9))
        page.update()

    page.on_resize = resize
    resize()

    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Regresar",
            on_click=lambda _: page.go("/inicioUsuario"),
        ),
        title=ft.Text("Detalles de la tarea"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
        actions=[
            ft.Container(
                content=toggle_btn,
                margin=ft.margin.only(right=10),
            )
        ],
    )

    return ft.View(
        route="/taskDetails",
        appbar=appbar,
        controls=[wrapper],
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START,
    )
