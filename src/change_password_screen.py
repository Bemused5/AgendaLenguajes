import flet as ft
import mysql.connector

# Ajusta con tus credenciales
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

def get_all_users():
    """Devuelve una lista de tuplas (id, nombre) con todos los usuarios en la tabla 'usuarios'."""
    conn = connect_db()
    if not conn:
        return []
    users = []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM usuarios")
        rows = cursor.fetchall()
        for row in rows:
            users.append((row["id"], row["nombre"]))
    except mysql.connector.Error as err:
        print(f"Error al obtener usuarios: {err}")
    finally:
        if cursor:
            cursor.close()
        conn.close()
    return users

def change_password_screen(page: ft.Page) -> ft.View:
    """
    Pantalla para que el administrador cambie la contraseña de un usuario.
    - Dropdown para seleccionar el usuario.
    - Campos para nueva contraseña y confirmación.
    - Botón que se habilita solo cuando ambas contraseñas coinciden y hay un usuario seleccionado.
    """

    # ----------------------------------------------------------------
    # 1) Controles y variables
    # ----------------------------------------------------------------
    user_dropdown = ft.Dropdown(
        label="Selecciona al usuario que le deseas cambiar la contraseña",
        hint_text="Escoge un usuario",
        width=300,
    )

    new_password_field = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=300
    )

    confirm_password_field = ft.TextField(
        label="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        width=300
    )

    message_text = ft.Text("", color=ft.Colors.RED, size=14)

    change_password_button = ft.ElevatedButton(
        text="Cambiar contraseña",
        width=300,
        disabled=True  # Arranca deshabilitado
    )

    # ----------------------------------------------------------------
    # 2) Cargar usuarios en el Dropdown
    # ----------------------------------------------------------------
    def load_users():
        users = get_all_users()
        if not users:
            # Si no se puede conectar o no hay usuarios
            user_dropdown.options = []
            return
        # Convertimos la lista (id, nombre) a ft.dropdown.Option
        user_dropdown.options = [
            ft.dropdown.Option(key=str(u[0]), text=u[1]) for u in users
        ]

    load_users()

    # ----------------------------------------------------------------
    # 3) Lógica para habilitar/deshabilitar el botón
    # ----------------------------------------------------------------
    def check_fields(*_):
        """
        Verifica si hay un usuario seleccionado y
        si las contraseñas no están vacías y coinciden.
        """
        selected_user = user_dropdown.value  # string con el id
        new_pass = new_password_field.value.strip()
        confirm_pass = confirm_password_field.value.strip()

        if selected_user and new_pass and confirm_pass and (new_pass == confirm_pass):
            change_password_button.disabled = False
            message_text.value = ""
        else:
            change_password_button.disabled = True
            # Si hay algo escrito y no coinciden, avisamos
            if new_pass and confirm_pass and (new_pass != confirm_pass):
                message_text.value = "Las contraseñas no coinciden."
            else:
                message_text.value = ""

        page.update()

    # Llamamos a check_fields cuando cambie cualquiera de los campos
    user_dropdown.on_change = check_fields
    new_password_field.on_change = check_fields
    confirm_password_field.on_change = check_fields

    # ----------------------------------------------------------------
    # 4) Función para cambiar la contraseña en la DB
    # ----------------------------------------------------------------
    def change_password(e):
        # Obtenemos los valores
        selected_user_id = user_dropdown.value  # string
        new_pass = new_password_field.value.strip()

        conn = connect_db()
        if not conn:
            message_text.value = "Error al conectar con la base de datos."
            page.update()
            return

        try:
            cursor = conn.cursor()
            update_query = """
                UPDATE usuarios
                SET contraseña = SHA2(%s, 256)
                WHERE id = %s
            """
            cursor.execute(update_query, (new_pass, selected_user_id))
            conn.commit()

            message_text.value = "Contraseña cambiada exitosamente."
            message_text.color = ft.Colors.GREEN
            # Limpiamos los campos
            new_password_field.value = ""
            confirm_password_field.value = ""
            change_password_button.disabled = True

        except mysql.connector.Error as err:
            message_text.value = f"Error en la base de datos: {err}"
            message_text.color = ft.Colors.RED
        finally:
            if cursor:
                cursor.close()
            conn.close()

        page.update()

    change_password_button.on_click = change_password

    # ----------------------------------------------------------------
    # 5) Botón de "Regresar" para volver a la pantalla admin (opcional)
    # ----------------------------------------------------------------
    back_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_size=24,
        tooltip="Regresar",
        on_click=lambda e: page.go("/inicioAdmin")
    )

    # ----------------------------------------------------------------
    # 6) Construcción de la vista
    # ----------------------------------------------------------------
    title_text = ft.Text("Modificar contraseña", size=20, weight=ft.FontWeight.BOLD)

    # Estructura visual en Column
    content = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
        controls=[
            title_text,
            user_dropdown,
            new_password_field,
            confirm_password_field,
            change_password_button,
            message_text
        ],
    )

    view = ft.View(
        "/changePassword",
        controls=[
            ft.Row(
                controls=[back_button],
                alignment=ft.MainAxisAlignment.START
            ),
            content
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    return view
