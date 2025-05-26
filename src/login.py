import flet as ft
import mysql.connector
import re


# --------------- CONEXIÓN BD ------------------------------------
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="srv1281.hstgr.io",
            user="u543141245_LenguajesAdmin",
            password="123456789Upslp",
            database="u543141245_Lenguajes",
        )
        print("✔ Conexión a la base de datos establecida.")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Error de conexión a la base de datos: {err}")
        return None


# --------------- PANTALLA LOGIN ---------------------------------
def login_screen(page: ft.Page) -> ft.Control:
    # ----------- Widgets ----------------------------------------
    title = ft.Text(
        "Task Master",
        size=40,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    lbl_email = ft.Text("Correo", weight=ft.FontWeight.BOLD)
    email_input = ft.TextField(hint_text="usuario@ejemplo.com")

    lbl_pwd = ft.Text("Contraseña", weight=ft.FontWeight.BOLD)
    password_input = ft.TextField(hint_text="********", password=True)

    login_btn = ft.ElevatedButton(
        "Log In",
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.WHITE,
    )

    create_link = ft.TextButton(
        "Crear una nueva cuenta", on_click=lambda _: page.go("/register")
    )

    msg = ft.Text(size=14, color=ft.Colors.RED)

    # ----------- Lógica de autenticación ------------------------
    def do_login(_):
        email = email_input.value.strip()
        password = password_input.value.strip()

        print(f"➡ Intento de login con: {email}")

        # Validaciones
        if not email or not password:
            msg.value = "Todos los campos son obligatorios."
            print("✋ Validación fallida: campos vacíos.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg.value = "Ingresa un correo válido."
            print("✋ Validación fallida: correo inválido.")
        else:
            conn = connect_db()
            if conn is None:
                msg.value = "Error al conectar a la base de datos."
            else:
                try:
                    cur = conn.cursor()
                    query = """
                        SELECT id, nombre, perfil
                          FROM usuarios
                         WHERE email = %s
                           AND contraseña = SHA2(%s,256)
                    """
                    cur.execute(query, (email, password))
                    result = cur.fetchone()
                    print(f"ℹ Resultado consulta: {result}")
                    if result:
                        user_id, username, perfil = result
                        try:
                            perfil_int = int(perfil)
                        except (ValueError, TypeError):
                            print(f"⚠ Perfil no convertible a int: {perfil}")
                            perfil_int = None

                        page.user_data = {
                            "user_id": user_id,
                            "username": username,
                            "perfil": perfil_int,
                        }
                        msg.value = "Inicio de sesión exitoso."
                        msg.color = ft.Colors.GREEN
                        print(f"✅ Login OK – perfil {perfil_int}")

                        # Redirección
                        if perfil_int == 1:
                            page.go("/inicioUsuario")
                        elif perfil_int == 2:
                            page.go("/inicioAdmin")
                        else:
                            msg.value = "Perfil no reconocido."
                            print("⚠ Perfil no reconocido.")
                    else:
                        msg.value = "Credenciales inválidas."
                        print("❌ Credenciales inválidas.")
                except mysql.connector.Error as err:
                    msg.value = f"Error en la base de datos: {err}"
                    print(f"❌ Error consulta BD: {err}")
                finally:
                    cur.close()
                    conn.close()
                    print("🔌 Conexión BD cerrada.")

        page.update()

    login_btn.on_click = do_login

    # ----------- Formulario y centrado --------------------------
    form_column = ft.Column(
        [
            lbl_email, email_input,
            lbl_pwd, password_input,
            login_btn, create_link,
            msg,
        ],
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    form_container = ft.Container(content=form_column)

    def resize(_=None):
        target = min(600, int(page.width * 0.9))
        for ctrl in (email_input, password_input, login_btn):
            ctrl.width = target
        form_container.width = target
        page.update()

    page.on_resize = resize
    resize()

    # ----------- Layout final -----------------------------------
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
