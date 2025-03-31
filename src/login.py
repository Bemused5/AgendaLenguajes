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
        print("Conexión a la base de datos establecida.")
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

def login_screen(page: ft.Page):
    """Retorna un contenedor con la pantalla de login y la funcionalidad para iniciar sesión."""

    title = ft.Text(
        "Task Master",
        size=30,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )

    email_input = ft.TextField(
        label="Email",
        hint_text="Gabriel@gmail.com",
        width=300
    )
    password_input = ft.TextField(
        label="Contraseña",
        hint_text="********",
        password=True,
        width=300
    )

    # Texto para mostrar mensajes de error o confirmación
    message_text = ft.Text("", color=ft.Colors.RED, size=14)

    def login(e):
        email = email_input.value.strip()
        password = password_input.value.strip()

        print(f"Intentando iniciar sesión con email: {email}")

        # Validaciones básicas
        if not email or not password:
            message_text.value = "Todos los campos son obligatorios."
            print("Validación fallida: Campos vacíos.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            message_text.value = "Ingresa un correo válido."
            print("Validación fallida: Correo inválido.")
        else:
            conn = connect_db()  # Intentar conectar a la base de datos
            if conn is None:
                message_text.value = "Error al conectar a la base de datos."
                print("No se pudo conectar a la base de datos.")
            else:
                try:
                    cursor = conn.cursor()
                    # Consulta para validar credenciales y obtener id, nombre y perfil
                    query = """
                        SELECT id, nombre, perfil
                        FROM usuarios
                        WHERE email = %s AND contraseña = SHA2(%s,256)
                    """
                    cursor.execute(query, (email, password))
                    result = cursor.fetchone()
                    print(f"Resultado de la consulta: {result}")
                    if result:
                        user_id, username, perfil = result
                        # Convertir perfil a entero si es posible
                        try:
                            perfil = int(perfil)
                        except ValueError:
                            print(f"Error al convertir perfil a entero: {perfil}")
                            perfil = None

                        page.user_data = {
                            "user_id": user_id,
                            "username": username,
                            "perfil": perfil
                        }
                        message_text.value = "Inicio de sesión exitoso."
                        message_text.color = ft.Colors.GREEN
                        # Redirige según el perfil del usuario
                        if perfil == 1:
                            print("Usuario con perfil 1. Redirigiendo a /inicioUsuario")
                            page.go("/inicioUsuario")
                        elif perfil == 2:
                            print("Usuario con perfil 2. Redirigiendo a /inicioAdmin")
                            page.go("/inicioAdmin")
                        else:
                            message_text.value = "Perfil no reconocido."
                            print(f"Perfil desconocido: {perfil}")

                    else:
                        message_text.value = "Credenciales inválidas. Intenta nuevamente."
                        print("Credenciales inválidas, no se encontró el usuario.")
                except mysql.connector.Error as err:
                    message_text.value = f"Error en la base de datos: {err}"
                    print(f"Error durante la consulta a la base de datos: {err}")
                finally:
                    cursor.close()
                    conn.close()
                    print("Conexión a la base de datos cerrada.")

        page.update()  # Actualizar la UI con el mensaje

    login_button = ft.ElevatedButton(
        text="Log In",
        width=300,
        bgcolor=ft.Colors.BLACK,
        color=ft.Colors.WHITE,
        on_click=login
    )

    create_account_link = ft.TextButton(
        "Crear una nueva cuenta",
        on_click=lambda e: page.go("/register")
    )

    return ft.Container(
        width=350,
        padding=20,
        border_radius=20,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            [
                title,
                email_input,
                password_input,
                login_button,
                message_text,  # Muestra mensajes de error o confirmación
                create_account_link,
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
    )
