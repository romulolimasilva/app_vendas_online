import flet as ft
# Supondo que a função de login do vendedor esteja no mesmo módulo 'db'
from db import User
from db import login_vendedor 

def LoginView(page: ft.Page):

    def show_snackbar(message, color):
        """Exibe uma notificação na parte inferior da página."""
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def login_click(e):
        """Função chamada ao clicar no botão de login."""
        if not email_field.value or not password_field.value:
            show_snackbar("Por favor, preencha o e-mail e a senha.", ft.Colors.ORANGE)
            return

        # Tenta logar como vendedor primeiro
        user_data = login_vendedor(
            email=email_field.value,
            password=password_field.value
        )

        # Se não for vendedor, tenta logar como comprador
        if not user_data:
            user_data = User().login_user(
                email=email_field.value,
                password=password_field.value
            )

        if user_data:
            # Limpa a sessão antiga e armazena os novos dados do usuário
            page.session.clear()
            page.session.set("user_name", user_data["name"])
            page.session.set("user_id", user_data["id"]) # <-- ADICIONADO
            page.session.set("user_type", user_data["type"])
            show_snackbar("Login realizado com sucesso!", ft.Colors.GREEN)
            page.go("/")
        else:
            show_snackbar("E-mail ou senha inválidos.", ft.Colors.RED)

    # --- CAMPOS DO FORMULÁRIO ---
    email_field = ft.TextField(
        label="E-mail",
        hint_text="Digite seu e-mail de vendedor",
        prefix_icon=ft.Icons.EMAIL,
        keyboard_type=ft.KeyboardType.EMAIL,
        autofocus=True
    )
    password_field = ft.TextField(
        label="Senha",
        hint_text="Digite sua senha",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True
    )

    return ft.View(
        '/login',
        [
            ft.Column(
                [
                    ft.Text("Acesse sua Conta", size=32, weight="bold"),
                    ft.Text("Bem-vindo de volta! Faça o login para continuar.", color=ft.Colors.GREY_600),
                    email_field,
                    password_field,
                    ft.FilledButton("Entrar", on_click=login_click, width=200, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.Button ("Home", on_click=lambda e: page.go("/"), width=200, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.TextButton("Ainda não tem uma conta? Cadastre-se", on_click=lambda e: page.go("/cadastro_vendedor")),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True, # Faz a coluna ocupar o espaço disponível
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=50,
    )