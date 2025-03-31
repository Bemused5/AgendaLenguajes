import flet as ft
from login import login_screen
from register import register_screen
from inicioUsuario import inicio_usuario_screen
from taskStatistics import task_statistics_screen
from addTask import add_task_screen
from task_details_screen import task_details_screen
from task_delete_screen import task_delete_screen
from inicioAdmin import inicio_admin_screen
from task_statistics_screen_admin import task_statistics_screen_admin
from change_password_screen import change_password_screen

def main(page: ft.Page):
    page.title = "Task Master"
    page.bgcolor = ft.Colors.GREY_200
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def route_change(route):
        page.views.clear()

        if page.route == "/":
            page.views.append(ft.View("/", controls=[login_screen(page)]))
        elif page.route == "/register":
            page.views.append(ft.View("/register", controls=[register_screen(page)]))
        elif page.route == "/inicioUsuario":
            page.views.append(inicio_usuario_screen(page))
        elif page.route == "/taskStatistics":
            page.views.append(task_statistics_screen(page))
        elif page.route == "/addTask":
            page.views.append(add_task_screen(page)) 
        elif page.route.startswith("/taskDetails"):
            page.views.append(task_details_screen(page))
        elif page.route.startswith("/deleteTask"):
            page.views.append(task_delete_screen(page))
        elif page.route.startswith("/inicioAdmin"):
            page.views.append(inicio_admin_screen(page))
        elif page.route.startswith("/taskStatisticsAdmin"):
            page.views.append(task_statistics_screen_admin(page))
        elif page.route.startswith("/ChangePassword"):
            page.views.append(change_password_screen(page))
        else:
            page.views.append(ft.View(controls=[ft.Text("404: Ruta no encontrada")]))


        page.update()

    def view_pop(view):
        page.views.pop()
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)
