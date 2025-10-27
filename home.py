import flet as ft
from create_user import create_user
from login import LoginView
from vendedor.cadastro_vendedor import CadastroVendedorView
from vendedor.cadastro_produto import CadastroProdutoView
from painel_adm.painel_adm import PainelAdmView
from lojas.lojas import LojasView
from vendedor.editar_produto import EditarProdutoView
from lojas.lojas_produtos import LojasProdutosView
from pedidos.carrinho_compras import CarrinhoComprasView
from pedidos.taxa_de_entrega import TaxaEntregaView
from db import init_db


def main(page: ft.Page):
    # Garante que o banco de dados e todas as tabelas estejam criados
    init_db()

    page.adaptive = True
    page.title = "Mercado Aberto"  # Nome mais convidativo
    page.theme_mode = ft.ThemeMode.LIGHT  # Ou DARK, para um visual mais moderno
    page.padding = 0  # Remover padding padrão da página para um layout mais "full-width"

    # Definir uma paleta de cores personalizada
    primary_color = ft.Colors.RED
    accent_color = ft.Colors.AMBER_400  # Uma cor de destaque
    background_color = ft.Colors.BLUE_GREY_50  # Fundo mais suave

    page.theme = ft.Theme(
        color_scheme_seed=primary_color,
        appbar_theme=ft.AppBarTheme(
            bgcolor=primary_color,
            title_text_style=ft.TextStyle(color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        ),
        navigation_drawer_theme=ft.NavigationDrawerTheme(
            bgcolor=background_color,
            indicator_color=ft.Colors.with_opacity(0.3, primary_color),
            label_text_style={
                ft.ControlState.SELECTED: ft.TextStyle(color=primary_color, weight=ft.FontWeight.BOLD),
                ft.ControlState.DEFAULT: ft.TextStyle(color=ft.Colors.BLUE_GREY_700),
            },
        )
    )

    # --- SIDEBAR (HAMBÚRGUER) ---
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Mercado Aberto", size=24, weight="bold", color=primary_color),
                        ft.Text("Sua plataforma de vendas", size=14, color=ft.Colors.GREY_600),
                    ]
                ),
                padding=ft.padding.all(20),
                alignment=ft.alignment.center_left,
                bgcolor=background_color,
            ),
            ft.Divider(height=1, color=ft.Colors.BLUE_GREY_200),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Home"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.STORE_OUTLINED, selected_icon=ft.Icons.STORE, label="Lojas"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.LOGIN, selected_icon=ft.Icons.PERSON, label="Login"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.PERSON_ADD, selected_icon=ft.Icons.PERSON_ADD_ALT_1, label="Criar Usuário"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.PERSON, selected_icon=ft.Icons.PERSON_ADD_ALT_1_ROUNDED, label="Cadastro de Vendedor"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.DASHBOARD, selected_icon=ft.Icons.DASHBOARD_CUSTOMIZE, label="Painel do Vendedor"
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SHOPPING_CART_CHECKOUT, selected_icon=ft.Icons.SHOPPING_CART, label="Carrinho de Compras"
            ),
            ft.Divider(height=1, color=ft.Colors.BLUE_GREY_200),
            ft.NavigationDrawerDestination(icon=ft.Icons.SETTINGS_OUTLINED, label="Configurações"),

        ]
    )

    def open_drawer(e):
        page.drawer.open = True
        page.update()

    def logout_click(e):
        """Limpa a sessão e redireciona para a home, atualizando a AppBar."""
        page.session.clear()
        page.go("/")

    # --- APP BAR MODERNA COM BOTÃO HAMBÚRGUER ---
    page.appbar = ft.AppBar(
        leading=ft.IconButton(
            icon=ft.Icons.MENU_ROUNDED,
            tooltip="Abrir Menu",
            on_click=open_drawer,
            icon_color=ft.Colors.WHITE
        ),
        title=ft.Text("Mercado Aberto", weight="bold", color=ft.Colors.WHITE),
        center_title=True,
        bgcolor=primary_color,
        actions=[],
    )

    # --- HOME VIEW ---
    def HomeView(page: ft.Page):
        return ft.View(
            route="/",
            controls=[
                ft.Container(
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[primary_color, ft.Colors.BLUE_400],
                    ),
                    height=200,
                    content=ft.Column(
                        [
                            ft.Text(
                                "Descubra Produtos Incríveis",
                                size=36,
                                weight="bold",
                                color=ft.Colors.WHITE,
                                text_align="center",
                            ),
                            ft.Text(
                                "A plataforma para vendedores e compradores.",
                                size=18,
                                color=ft.Colors.BLUE_50,
                                text_align="center",
                            ),
                        ],
                        horizontal_alignment="center",
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Divider(height=20, color="transparent"),
                            ft.Text(
                                "Bem-vindo ao Mercado Aberto!",
                                size=28,
                                weight="bold",
                                text_align="center",
                                color=ft.Colors.BLUE_GREY_900,
                            ),
                            ft.Text(
                                "Explore uma vasta gama de produtos e conecte-se com vendedores de todo o país.",
                                size=16,
                                color=ft.Colors.GREY_700,
                                text_align="center",
                            ),
                            ft.Divider(height=30, color="transparent"),
                            ft.ResponsiveRow(
                                [
                                    ft.Card(
                                        content=ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Icon(ft.Icons.STORE, size=40, color=primary_color),
                                                    ft.Text("Vendedores", size=18, weight="bold"),
                                                    ft.Text("Crie sua loja e alcance novos clientes.", text_align="center"),
                                                    ft.ElevatedButton(
                                                        "Ver Lojas",
                                                        on_click=lambda e: page.go("/lojas"),
                                                        style=ft.ButtonStyle(bgcolor=primary_color, color=ft.Colors.WHITE),
                                                    ),
                                                ],
                                                horizontal_alignment="center",
                                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                spacing=10,
                                            ),
                                            padding=ft.padding.all(20),
                                            alignment=ft.alignment.center,
                                        ),
                                        col={"xs": 12, "sm": 6, "md": 4},
                                        elevation=10,
                                    ),
                                    ft.Card(
                                        content=ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Icon(ft.Icons.SHOPPING_BAG, size=40, color=accent_color),
                                                    ft.Text("Compradores", size=18, weight="bold"),
                                                    ft.Text("Encontre produtos únicos e faça suas compras.", text_align="center"),
                                                    ft.OutlinedButton(
                                                        "Explorar Produtos",
                                                        on_click=lambda e: page.go("/lojas"),
                                                        style=ft.ButtonStyle(color=primary_color),
                                                    ),
                                                ],
                                                horizontal_alignment="center",
                                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                spacing=10,
                                            ),
                                            padding=ft.padding.all(20),
                                            alignment=ft.alignment.center,
                                        ),
                                        col={"xs": 12, "sm": 6, "md": 4},
                                        elevation=10,
                                    ),
                                    ft.Card(
                                        content=ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Icon(ft.Icons.PERSON_ADD, size=40, color=ft.Colors.GREEN_600),
                                                    ft.Text("Novo Aqui?", size=18, weight="bold"),
                                                    ft.Text("Crie sua conta de forma rápida e segura.", text_align="center"),
                                                    ft.ElevatedButton(
                                                        "Criar Conta",
                                                        on_click=lambda e: page.go("/create_user"),
                                                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
                                                    ),
                                                ],
                                                horizontal_alignment="center",
                                                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                                spacing=10,
                                            ),
                                            padding=ft.padding.all(20),
                                            alignment=ft.alignment.center,
                                        ),
                                        col={"xs": 12, "sm": 6, "md": 4},
                                        elevation=10,
                                    ),
                                ],
                                spacing=20,
                                run_spacing=20,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        horizontal_alignment="center",
                        spacing=20,
                    ),
                    expand=True,
                    alignment=ft.alignment.top_center,
                    padding=30,
                    bgcolor=background_color,
                ),
            ],
            bgcolor=ft.Colors.BLUE_GREY_50,
            scroll=ft.ScrollMode.AUTO,
        )

    # --- ROTAS ---
    app_routes = {
        "/": HomeView,
        "/login": LoginView,
        "/lojas": LojasView,
        "/create_user": create_user,
        "/cadastro_vendedor": CadastroVendedorView,
        "/cadastro_produto": CadastroProdutoView,
        "/painel_adm": PainelAdmView,
        "/carrinho": CarrinhoComprasView,
    }

    def route_change(route):
        user_name = page.session.get("user_name")
        page.appbar.actions.clear()

        if user_name:
            page.appbar.actions.extend([
                ft.IconButton(
                    ft.Icons.SHOPPING_CART_OUTLINED,
                    tooltip="Carrinho",
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda e: page.go("/carrinho")
                ),
                ft.Text(f"Olá, {user_name.split(' ')[0]}!", color=ft.Colors.WHITE, weight="bold"),
                ft.IconButton(
                    ft.Icons.LOGOUT,
                    tooltip="Sair",
                    on_click=logout_click,
                    icon_color=ft.Colors.WHITE,
                ),
                ft.Container(width=10),
            ])
        else:
            page.appbar.actions.extend([
                ft.IconButton(ft.Icons.SEARCH, tooltip="Pesquisar", icon_color=ft.Colors.WHITE),
                ft.IconButton(
                    ft.Icons.SHOPPING_CART_OUTLINED, 
                    tooltip="Carrinho", 
                    icon_color=ft.Colors.WHITE,
                    on_click=lambda e: page.go("/carrinho")
                ),
                ft.IconButton(
                    ft.Icons.LOGIN,
                    tooltip="Login",
                    on_click=lambda e: page.go("/login"),
                    icon_color=ft.Colors.WHITE,
                ),
                ft.Container(width=10),
            ])

        # Limpa as views anteriores
        page.views.clear()

        # Lógica para rota de edição de produto
        if page.route.startswith("/editar_produto/"):
            try:
                produto_id = int(page.route.split("/")[-1])
                new_view = EditarProdutoView(page, produto_id)
            except (ValueError, IndexError):
                new_view = PainelAdmView(page) # Volta ao painel se o ID for inválido

        # Lógica para rotas dinâmicas de produtos da loja
        elif page.route.startswith("/lojas/"):
            # Pega o slug da URL, que é a parte depois de "/lojas/"
            slug = page.route.split("/")[-1]
            if slug:
                new_view = LojasProdutosView(page, slug)
            else:
                # Se a URL for apenas "/lojas/", redireciona para a lista de lojas
                new_view = LojasView(page)
        else:
            # Lógica para rotas estáticas
            view_builder = app_routes.get(page.route, HomeView)
            new_view = view_builder(page)

        # Adiciona a nova view à pilha de navegação
        new_view.appbar = page.appbar
        new_view.drawer = page.drawer
        page.views.append(new_view)
        page.update()

    # --- EVENTO DO DRAWER ---
    def drawer_change(e):
        if e.control.selected_index == 0:
            page.go("/")
        elif e.control.selected_index == 1:
            page.go("/lojas")
        elif e.control.selected_index == 2:
            page.go("/login")
        elif e.control.selected_index == 3:
            page.go("/create_user")
        elif e.control.selected_index == 4:
            page.go("/cadastro_vendedor")
        elif e.control.selected_index == 5:
            page.go("/painel_adm")
        elif e.control.selected_index == 6:
            page.go("/carrinho") # Corresponde ao novo item "Carrinho de Compras"

        page.drawer.open = False
        page.update()

    page.drawer.on_change = drawer_change
    page.on_route_change = route_change
    page.go(page.route)


ft.app(target=main, view=ft.WEB_BROWSER)
