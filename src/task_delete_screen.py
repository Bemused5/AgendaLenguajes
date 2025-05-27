import flet as ft
import mysql.connector
from urllib.parse import urlparse, parse_qs


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


#PANTALLA CONFIRMAR ELIMINACIÓN 
def task_delete_screen(page: ft.Page) -> ft.View:

    qs = parse_qs(urlparse(page.route).query)
    task_id = int(qs.get("id", [0])[0]) if qs.get("id") else None
    if not task_id:
        return ft.View("/deleteTask", controls=[ft.Text("Tarea no especificada.")])

    # Buscar datos de la tarea 
    conn = connect_db()
    if not conn:
        return ft.View("/deleteTask", controls=[ft.Text("Error BD.")])

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT titulo, detalles, fecha_inicio, fecha_fin,
                   categoria, completada
              FROM tareas WHERE id=%s
            """,
            (task_id,),
        )
        tarea = cur.fetchone()
    finally:
        cur.close(); conn.close()

    if not tarea:
        return ft.View("/deleteTask", controls=[ft.Text("La tarea no existe.")])


    lbl_title = ft.Text("Eliminar tarea", size=26, weight=ft.FontWeight.BOLD)

    info_items = ft.Column(
        [
            ft.Text(f"Título: {tarea['titulo']}", weight=ft.FontWeight.BOLD),
            ft.Text(f"Detalles: {tarea['detalles'] or '-'}"),
            ft.Text(
                f"Inicio: {tarea['fecha_inicio'] or 'N/A'}   |   "
                f"Fin: {tarea['fecha_fin'] or 'N/A'}"
            ),
            ft.Text(f"Categoría: {tarea['categoria']}"),
            ft.Text(
                f"Estatus: {'Completada' if tarea['completada'] else 'No completada'}",
                color=ft.Colors.GREEN if tarea["completada"] else ft.Colors.RED,
            ),
        ],
        spacing=4,
    )

    confirm_msg = ft.Text(
        "Escribe CONFIRMAR para eliminar definitivamente la tarea.",
        size=14,
    )
    tf_confirm = ft.TextField(hint_text="CONFIRMAR", width=400)
    feedback = ft.Text(size=14)

    # Button
    btn_delete = ft.ElevatedButton("Eliminar tarea", disabled=True)

    # Validación del texto 
    def check_text(_=None):
        btn_delete.disabled = tf_confirm.value.strip().upper() != "CONFIRMAR"
        feedback.value = ""
        page.update()

    tf_confirm.on_change = check_text
    check_text()

    #  Acción de borrado 
    def do_delete(_):
        conn2 = connect_db()
        if not conn2:
            feedback.value, feedback.color = "Error BD.", ft.Colors.RED; page.update(); return
        try:
            cur2 = conn2.cursor()
            cur2.execute("DELETE FROM tareas WHERE id=%s", (task_id,))
            conn2.commit()
            feedback.value, feedback.color = "Tarea eliminada.", ft.Colors.GREEN
        except mysql.connector.Error as err:
            feedback.value, feedback.color = f"Error: {err}", ft.Colors.RED
        finally:
            cur2.close(); conn2.close(); page.update()
            page.go("/inicioUsuario")

    btn_delete.on_click = do_delete

 
    form = ft.Column(
        [lbl_title, info_items, confirm_msg, tf_confirm, btn_delete, feedback],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    wrapper = ft.Container(content=form)

    def resize(_=None):
        wrapper.width = min(600, int(page.width * 0.9))
        tf_confirm.width = btn_delete.width = wrapper.width
        page.update()

    page.on_resize = resize
    resize()


    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Volver",
            on_click=lambda _: page.go("/inicioUsuario"),
        ),
        title=ft.Text("Eliminar tarea"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
    )

 
    return ft.View(
        route="/deleteTask",
        appbar=appbar,
        controls=[wrapper],
        padding=20,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # centramos wrapper
        vertical_alignment=ft.MainAxisAlignment.START,
    )
