import flet as ft

def inicio_admin_screen(page: ft.Page) -> ft.View:
    """Pantalla de inicio para el administrador."""

    def logout(e):
        page.user_data = {}
        page.go("/")

    # AppBar (barra superior)
    appbar = ft.AppBar(
        automatically_imply_leading=False,
        leading_width=220,
        toolbar_height=60,
        leading=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            controls=[
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color=ft.Colors.WHITE,
                        tooltip="Cerrar sesión",
                        on_click=logout
                    ),
                    bgcolor=ft.Colors.GREEN_300,
                    padding=ft.padding.all(5),
                    border_radius=ft.border_radius.all(30),
                ),
            ],
        ),
        title=ft.Text("Agenda de tareas"),
        center_title=True,
        bgcolor=ft.Colors.BLUE_GREY_50,
        actions=[],
    )

    # Contenido principal
    content = ft.Column(
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
        controls=[
            ft.Text("Opciones", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                text="Estadísticas de un usuario en específico",
                on_click=lambda e: page.go("/taskStatisticsAdmin?type=single"),
                width=300
            ),
            ft.ElevatedButton(
                text="Estadísticas de todos los usuarios",
                on_click=lambda e: page.go("/taskStatisticsAdmin?type=all"),
                width=300
            ),
            ft.Text("Área de peligro", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                text="Modificar contraseña de un usuario",
                on_click=lambda e: page.go("/ChangePassword"),
                width=300
            ),
        ],
    )

    view = ft.View(
        "/inicioAdmin",
        appbar=appbar,
        controls=[content],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
    return view
