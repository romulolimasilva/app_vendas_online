import flet as ft
from home import HomeView
from login import LoginView
from create_user import create_user

def main(page: ft.Page):
    def route_chage(e):
        page.views.clear()
    
    if page.route == '/':
        page.views.append(HomeView(page))
    elif page.route == '/login':
        page.views.append(LoginView(page))
    elif page.route == '/create_user':
        page.views.append(create_user(page))    
    page.update()

    page.on_route_change = route_chage
    page.go(page.route)
    

ft.app(target=main, view=ft.WEB_BROWSER)