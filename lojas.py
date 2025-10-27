import flet as ft
from db import get_all_vendedores


def LojasView(page: ft.Page):
    
    def go_to_store(e):
        """Navega para a página de produtos da loja selecionada."""
        store_slug = e.control.data
        page.go(f"/lojas/{store_slug}")

    # Busca as lojas no banco de dados
    lojas = get_all_vendedores()

    # Cria um Card para cada loja
    cards_lojas = []
    if lojas:
        for loja in lojas:
            cards_lojas.append(
                ft.Card(
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    content=ft.Container(
                        padding=15,
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.STOREFRONT, size=40, color=ft.Colors.RED),
                                ft.Text(loja['name'], size=18, weight="bold", text_align="center"),
                                ft.Text(f"{loja['cidade']}, {loja['estado']}", color=ft.Colors.GREY_600),
                                ft.Divider(height=10, color="transparent"),
                                ft.FilledButton(
                                    "Visitar Loja",
                                    icon=ft.Icons.ARROW_FORWARD,
                                    on_click=go_to_store,
                                    data=loja['slug'], # Armazena o SLUG da loja no botão
                                    width=200,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                        )
                    )
                )
            )
    else:
        cards_lojas.append(ft.Text("Nenhuma loja encontrada no momento.", size=18, col=12, text_align="center"))

    return ft.View(
        "/lojas",
        [
            ft.Text("Nossas Lojas", size=32, weight="bold"),
            ft.Text("Encontre os melhores vendedores e produtos.", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=20),
            ft.ResponsiveRow(controls=cards_lojas, spacing=20, run_spacing=20)
        ],
        padding=30,
        scroll=ft.ScrollMode.AUTO,
    )