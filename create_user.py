import flet as ft
from db import User

def create_user(page: ft.Page):
    page.title = "Crie sua Conta"

    def show_snackbar(message, color):
        """Exibe uma notificação na parte inferior da página."""
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    name_field = ft.TextField(label="Nome Completo", hint_text="Digite seu nome", autofocus=True, prefix_icon=ft.Icons.PERSON)
    email_field = ft.TextField(label="E-mail", hint_text="Digite seu e-mail", keyboard_type=ft.KeyboardType.EMAIL, prefix_icon=ft.Icons.EMAIL)
    password_field = ft.TextField(label="Senha", hint_text="Crie uma senha forte", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)
    confirm_password_field = ft.TextField(label="Repita a Senha", hint_text="Confirme sua senha", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK)

    def create_user_click(e):
        # Validação dos campos
        if not all([name_field.value, email_field.value, password_field.value, confirm_password_field.value]):
            show_snackbar("Por favor, preencha todos os campos.", ft.Colors.ORANGE)
            return

        if password_field.value != confirm_password_field.value:
            show_snackbar("As senhas não coincidem. Tente novamente.", ft.Colors.RED)
            password_field.value = ""
            confirm_password_field.value = ""
            password_field.focus()
            page.update()
            return

        # Tenta criar o usuário no banco de dados
        success = User().create_user(
            name=name_field.value,
            email=email_field.value,
            password=password_field.value
        )

        if success:
            show_snackbar("Usuário criado com sucesso!", ft.Colors.GREEN)
            page.go("/login")
        else:
            show_snackbar("Erro ao criar usuário. O e-mail já pode estar em uso.", ft.Colors.RED)

    return ft.View(
        '/create_user',
        [
            ft.Column(
                [
                    ft.Text("Crie sua Conta de Comprador", size=32, weight="bold"),
                    ft.Text("É rápido e fácil!", color=ft.Colors.GREY_600),
                    name_field,
                    email_field,
                    password_field,
                    confirm_password_field,
                    ft.FilledButton("Criar Conta", on_click=create_user_click, width=200, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.Button ("Home", on_click=lambda e: page.go("/"), width=200, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))),
                    ft.TextButton("Já tem uma conta? Faça o login", on_click=lambda e: page.go("/login")),
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=50,
    )
