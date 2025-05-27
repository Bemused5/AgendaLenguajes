import flet as ft
import mysql.connector
import re


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
        print(f"Error de conexión a la base de datos: {err}")
        return None



def register_screen(page: ft.Page) -> ft.Control:
    #  COMPONENTES UI
    title = ft.Text(
        "Task Master",
        size=40,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    lbl_user = ft.Text("Nombre de usuario", weight=ft.FontWeight.BOLD)
    username_input = ft.TextField(hint_text="Gabriel")

    lbl_email = ft.Text("Correo", weight=ft.FontWeight.BOLD)
    email_input = ft.TextField(hint_text="ejemplo@gmail.com")

    lbl_pwd = ft.Text("Contraseña", weight=ft.FontWeight.BOLD)
    password_input = ft.TextField(hint_text="********", password=True)

    lbl_confirm = ft.Text("Confirmar contraseña", weight=ft.FontWeight.BOLD)
    confirm_password_input = ft.TextField(hint_text="********", password=True)

    terms_checkbox = ft.Checkbox(label="Acepto los términos y condiciones")

    create_btn = ft.ElevatedButton(
        "Crear cuenta", bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE
    )

    login_link = ft.TextButton("Iniciar sesión", on_click=lambda _: page.go("/"))

    msg = ft.Text(size=14, color=ft.Colors.RED)

    # FUNCIÓN CREAR CUENTA 
    def create_account(_):
        username = username_input.value.strip()
        email = email_input.value.strip()
        password = password_input.value.strip()
        confirm = confirm_password_input.value.strip()
        accepted = terms_checkbox.value

        # Validaciones
        if not all([username, email, password, confirm]):
            msg.value = "Todos los campos son obligatorios."
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg.value = "Ingresa un correo válido."
        elif password != confirm:
            msg.value = "Las contraseñas no coinciden."
        elif not accepted:
            msg.value = "Debes aceptar los términos y condiciones."
        else:
            conn = connect_db()
            if conn is None:
                msg.value = "Error al conectar con la base de datos."
            else:
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT email FROM usuarios WHERE email=%s", (email,))
                    if cur.fetchone():
                        msg.value = "Este correo ya está registrado."
                    else:
                        cur.execute(
                            """
                            INSERT INTO usuarios (nombre, email, contraseña)
                            VALUES (%s, %s, SHA2(%s,256))
                            """,
                            (username, email, password),
                        )
                        conn.commit()
                        cur.execute("SELECT LAST_INSERT_ID()")
                        user_id = cur.fetchone()[0]

                        page.user_data = {"user_id": user_id, "username": username}
                        msg.value = "Cuenta creada exitosamente."
                        msg.color = ft.Colors.GREEN
                        page.go("/inicioUsuario")
                except mysql.connector.Error as err:
                    msg.value = f"Error en la base de datos: {err}"
                finally:
                    cur.close()
                    conn.close()
        page.update()

    create_btn.on_click = create_account

    form_column = ft.Column(
        [
            lbl_user, username_input,
            lbl_email, email_input,
            lbl_pwd, password_input,
            lbl_confirm, confirm_password_input,
            terms_checkbox,
            create_btn,
            login_link,
            msg,
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    form_container = ft.Container(content=form_column)

    #AJUSTE RESPONSIVO (90 % ANCHO) 
    def resize(_=None):
        target = min(600, int(page.width * 0.9))
        for ctrl in (
            username_input,
            email_input,
            password_input,
            confirm_password_input,
            create_btn,
        ):
            ctrl.width = target
        form_container.width = target
        page.update()

    page.on_resize = resize
    resize()

    
    return ft.Column(
        [
            title,
            ft.Row([form_container],
                   alignment=ft.MainAxisAlignment.CENTER),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=40,
        expand=True,
    )
