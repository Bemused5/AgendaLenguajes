import flet as ft

def show_add_task_dialog(page: ft.Page):
    """Muestra un modal tipo pop-up desde abajo con un fondo oscurecido."""

    print("Intentando abrir el modal...")  # Log para verificar la ejecución

    page.snack_bar = ft.SnackBar(ft.Text("Abriendo modal..."))
    page.snack_bar.open = True
    page.update()

    # Campos del formulario
    title_field = ft.TextField(label="Título", hint_text="Proyecto lenguajes", width=300)
    details_field = ft.TextField(label="Detalles", hint_text="Proyecto lenguajes", multiline=True, width=300)
    start_date_field = ft.TextField(label="Fecha de inicio", hint_text="Fecha de inicio", width=140)
    end_date_field = ft.TextField(label="Fecha de fin", hint_text="Fecha de fin", width=140)

    category_dd = ft.Dropdown(
        label="Selecciona una categoría:",
        width=300,
        options=[
            ft.dropdown.Option("Escuela"),
            ft.dropdown.Option("Trabajo"),
            ft.dropdown.Option("Salud y Bienestar"),
            ft.dropdown.Option("Hogar"),
            ft.dropdown.Option("Otros"),
        ]
    )

    # Función para cerrar el modal
    def close_modal(e):
        print("Cerrando modal...")
        page.bottom_sheet.open = False
        page.update()

    # Función que maneja la creación de la tarea
    def create_task(e):
        print(f"Tarea creada: {title_field.value}, {category_dd.value}")
        close_modal(e)

    # Crear el modal (BottomSheet)
    page.bottom_sheet = ft.BottomSheet(
        content=ft.Container(
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.only(top_left=16, top_right=16),
            content=ft.Column([
                ft.Text("Añadir tarea", size=20, weight=ft.FontWeight.BOLD),
                title_field,
                details_field,
                ft.Text("¿Asignar un plazo?"),
                ft.Row([start_date_field, end_date_field], spacing=10),
                category_dd,
                ft.Row([
                    ft.ElevatedButton("Cancelar", on_click=close_modal),
                    ft.ElevatedButton("Crear tarea", on_click=create_task),
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=10)
        ),
        open=True
    )

    print("Modal debería estar abierto ahora.")  # Log adicional
    page.update()
