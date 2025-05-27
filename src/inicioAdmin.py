import flet as ft


def inicio_admin_screen(page: ft.Page) -> ft.View:
   
    def logout(_):
        page.user_data = {}
        page.go("/")


    appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.LOGOUT,
            tooltip="Cerrar sesión",
            on_click=logout,
        ),
        title=ft.Text("Agenda de tareas"),
        center_title=True,
        bgcolor=ft.Colors.WHITE,
    )

    def option_row(label: str, btn_text: str, on_click, danger=False):
        btn_color = ft.Colors.RED if danger else ft.Colors.BLUE
        return ft.Row(
            [
                ft.Text(label, expand=True),
                ft.ElevatedButton(
                    btn_text,
                    bgcolor=btn_color,
                    color=ft.Colors.WHITE,
                    on_click=on_click,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )

    
    content = ft.Column(
        [
            # Opciones de administración
            ft.Text("Opciones", size=22, weight=ft.FontWeight.BOLD),
            option_row(
                "Estadísticas de un usuario en específico",
                "Ver",
                lambda _: page.go("/taskStatisticsAdmin?type=single"),
            ),
            option_row(
                "Estadísticas de todos los usuarios",
                "Ver",
                lambda _: page.go("/taskStatisticsAdmin?type=all"),
            ),

            ft.Container(height=20),  

            # Area de peligro
            ft.Text("Área de peligro", size=22, weight=ft.FontWeight.BOLD),
            option_row(
                "Modificar contraseña de un usuario",
                "Abrir",
                lambda _: page.go("/ChangePassword"),
                danger=True,
            ),
        ],
        spacing=25,
        expand=True,
    )

    # Vista principal
    return ft.View(
        route="/inicioAdmin",
        appbar=appbar,
        controls=[content],
        padding=20,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        vertical_alignment=ft.MainAxisAlignment.START,
    )
