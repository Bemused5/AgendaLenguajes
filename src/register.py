import flet as ft
import mysql.connector
import re  # Para validar el correo

# Conexión a la base de datos en Hostinger
def connect_db():
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
    return mysql.connector.connect(
        
    )

def register_screen(page: ft.Page):
    """Retorna un contenedor con la pantalla de registro de usuario y lo guarda en MySQL."""

    title = ft.Text("Task Master", size=30, weight=ft.FontWeight.BOLD)

    username_input = ft.TextField(label="Nombre de usuario", hint_text="Gabriel", width=300)
    email_input = ft.TextField(label="Email", hint_text="ejemplo@gmail.com", width=300)
    password_input = ft.TextField(label="Contraseña", hint_text="********", password=True, width=300)
    confirm_password_input = ft.TextField(label="Confirmar contraseña", hint_text="********", password=True, width=300)
    terms_checkbox = ft.Checkbox(label="Acepto los términos y condiciones")

    message_text = ft.Text("", color=ft.Colors.RED, size=14)  # Mensaje de error

    # Función para validar datos e insertar en la base de datos
    def create_account(e):
        username = username_input.value.strip()
        email = email_input.value.strip()
        password = password_input.value.strip()
        confirm_password = confirm_password_input.value.strip()
        terms_accepted = terms_checkbox.value

        # Validaciones
        if not username or not email or not password or not confirm_password:
            message_text.value = "Todos los campos son obligatorios."
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message_text.value = "Ingresa un correo válido."
        elif password != confirm_password:
            message_text.value = "Las contraseñas no coinciden."
        elif not terms_accepted:
            message_text.value = "Debes aceptar los términos y condiciones."
        else:
            conn = connect_db()  # Intentar conectar a la base de datos
            if conn is None:
                message_text.value = "Error al conectar con la base de datos."
            else:
                try:
                    cursor = conn.cursor()
                    # Verificar si el correo ya está registrado
                    cursor.execute("SELECT email FROM usuarios WHERE email = %s", (email,))
                    if cursor.fetchone():
                        message_text.value = "Este correo ya está registrado."
                    else:
                        # Insertar usuario en la base de datos con la contraseña hasheada
                        query = """
                            INSERT INTO usuarios (nombre, email, contraseña)
                            VALUES (%s, %s, SHA2(%s, 256))
                        """
                        cursor.execute(query, (username, email, password))
                        conn.commit()

                        # Obtener el ID recién insertado
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        new_user_id = cursor.fetchone()[0]

                        # Guardar la información del usuario en page (id + nombre)
                        page.user_data = {
                            "user_id": new_user_id,
                            "username": username
                        }

                        message_text.value = "Cuenta creada exitosamente."
                        message_text.color = ft.Colors.GREEN
                        page.go("/inicioUsuario")  # Redirigir a la pantalla principal

                except mysql.connector.Error as err:
                    message_text.value = f"Error en la base de datos: {err}"
                finally:
                    cursor.close()
                    conn.close()

        page.update()  # Actualizar UI con el mensaje

    create_account_button = ft.ElevatedButton(
        text="Crear cuenta",
        width=300,
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.WHITE,
        on_click=create_account
    )

    login_link = ft.TextButton("Iniciar sesión", on_click=lambda e: page.go("/"))

    return ft.Container(
        width=350,
        padding=20,
        border_radius=20,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            [
                title,
                username_input,
                email_input,
                password_input,
                confirm_password_input,
                terms_checkbox,
                create_account_button,
                message_text,  # Muestra errores o éxito
                login_link,
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
    )