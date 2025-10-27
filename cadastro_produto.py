import flet as ft


def CadastroProdutoView(page: ft.Page):
    page.title = "Cadastro de Produto"
    page.update()
    
    # Testar a pagina
    return ft.View(
        '/cadastro_produto',
        controls=[
            ft.Text("Cadastro de Produto")
        ]
    )



