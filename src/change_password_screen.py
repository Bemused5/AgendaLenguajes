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
        print(f"Error BD: {err}")
        return None


def get_all_users():
    conn = connect_db()
    if not conn:
        return []
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, nombre FROM usuarios")
    users = [(r["id"], r["nombre"]) for r in cur]
    cur.close(); conn.close()
    return users


def change_password_screen(page: ft.Page) -> ft.View:
    show_pass = False

    lbl_user, lbl_newpw, lbl_confpw = (
        ft.Text("Usuario", weight=ft.FontWeight.BOLD),
        ft.Text("Contraseña", weight=ft.FontWeight.BOLD),
        ft.Text("Confirmar contraseña", weight=ft.FontWeight.BOLD),
    )

    user_dd = ft.Dropdown(hint_text="Selecciona un usuario")
    new_pw = ft.TextField(password=True)
    confirm_pw = ft.TextField(password=True)

    eye_btn = ft.IconButton(icon=ft.Icons.VISIBILITY_OFF)
    def toggle(_):
        nonlocal show_pass
        show_pass = not show_pass
        new_pw.password = confirm_pw.password = not show_pass
        eye_btn.icon = ft.Icons.VISIBILITY if show_pass else ft.Icons.VISIBILITY_OFF
        page.update()
    new_pw.suffix = confirm_pw.suffix = eye_btn
    eye_btn.on_click = toggle

    msg = ft.Text(size=14, color=ft.Colors.RED)
    save_btn = ft.ElevatedButton("Cambiar contraseña", disabled=True)

    user_dd.options = [ft.dropdown.Option(str(i), n) for i, n in get_all_users()]

    def validate(_=None):
        ok = user_dd.value and new_pw.value.strip() and new_pw.value == confirm_pw.value
        save_btn.disabled = not ok
        msg.value = "" if ok else ("Las contraseñas no coinciden."
                    if new_pw.value and confirm_pw.value else "")
        page.update()
    for c in (user_dd, new_pw, confirm_pw):
        c.on_change = validate
    validate()

    def save(_):
        conn = connect_db()
        if not conn:
            msg.value, msg.color = "Error al conectar BD.", ft.Colors.RED; page.update(); return
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE usuarios SET contraseña=SHA2(%s,256) WHERE id=%s",
                (new_pw.value.strip(), user_dd.value),
            )
            conn.commit()
            msg.value, msg.color = "Contraseña cambiada.", ft.Colors.GREEN
            new_pw.value = confirm_pw.value = ""; save_btn.disabled = True
        except mysql.connector.Error as err:
            msg.value, msg.color = f"Error BD: {err}", ft.Colors.RED
        finally:
            cur.close(); conn.close(); page.update()
    save_btn.on_click = save

    form = ft.Column(
        [lbl_user, user_dd, lbl_newpw, new_pw, lbl_confpw, confirm_pw, save_btn, msg],
        spacing=16,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    wrapper = ft.Container(content=form) 

    def resize(_=None):
        wrapper.width = min(600, int(page.width * 0.9))
        for ctl in (user_dd, new_pw, confirm_pw, save_btn):
            ctl.width = wrapper.width
        page.update()
    page.on_resize = resize
    resize()

    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Regresar",
            on_click=lambda _: page.go("/inicioAdmin"),
        ),
        title=ft.Text("Modificar contraseña"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
    )

    return ft.View(
        route="/changePassword",
        appbar=appbar,
        controls=[wrapper],
        scroll=ft.ScrollMode.AUTO,
        padding=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  
        vertical_alignment=ft.MainAxisAlignment.START,
    )
