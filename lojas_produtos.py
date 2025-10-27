import flet as ft
import base64
from db import get_vendedor_by_slug, get_produtos_by_vendedor, get_produto_by_id

def LojasProdutosView(page: ft.Page, vendedor_slug: str):
    """
    Exibe os produtos de uma loja específica.
    """
    # Busca os dados da loja e dos produtos
    loja = get_vendedor_by_slug(vendedor_slug)
    
    if loja:
        produtos = get_produtos_by_vendedor(loja['id'])
    else:
        # Se a loja não for encontrada, exibe uma mensagem e não busca produtos
        produtos = []

    def add_to_cart(e):
        produto_id = e.control.data
        
        # Pega o carrinho da sessão ou cria um novo se não existir
        carrinho = page.session.get("cart") or {}
        
        # Busca os detalhes do produto para adicionar ao carrinho
        produto = get_produto_by_id(produto_id)
        if not produto:
            snack = ft.SnackBar(content=ft.Text("Produto não encontrado!"), bgcolor=ft.Colors.RED)
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return


        # Se o produto já está no carrinho, incrementa a quantidade
        if str(produto_id) in carrinho:
            carrinho[str(produto_id)]["quantity"] += 1
        else:
            # Senão, adiciona o produto ao carrinho
            carrinho[str(produto_id)] = {
                "name": produto["nome"],
                "price": produto["preco"],
                "quantity": 1,
                "img": base64.b64encode(produto['img']).decode('utf-8') if produto['img'] else None,
                "vendedor_id": produto["vendedor_id"] # Adiciona o ID do vendedor ao item do carrinho
            }
        
        page.session.set("cart", carrinho)
        snack = ft.SnackBar(content=ft.Text(f"'{produto['nome']}' adicionado ao carrinho!"), bgcolor=ft.Colors.GREEN)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # Cria os cards dos produtos
    cards_produtos = []
    if produtos:
        for produto in produtos:
            img_produto = ft.Image(
                src_base64=base64.b64encode(produto['img']).decode('utf-8') if produto['img'] else None,
                src="Icons/no-image.png" if not produto['img'] else None,
                height=120,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )

            cards_produtos.append(
                ft.Card(
                    col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                    elevation=4,
                    content=ft.Column(
                        [
                            img_produto,
                            ft.Container(
                                padding=10,
                                content=ft.Column(
                                    [
                                        ft.Text(produto['nome'], size=16, weight="bold"),
                                        ft.Text(f"R$ {produto['preco']:.2f}", size=20, color=ft.Colors.GREEN_700, weight="bold"),
                                        ft.Text(f"Em estoque: {produto['quantidade']}", size=12, color=ft.Colors.GREY_600),
                                        ft.Divider(height=5, color="transparent"),
                                        ft.FilledButton(
                                            "Adicionar ao Carrinho",
                                            icon=ft.Icons.ADD_SHOPPING_CART,
                                            on_click=add_to_cart,
                                            data=produto['id'],
                                        ),
                                    ],
                                    spacing=5,
                                )
                            )
                        ],
                        spacing=0,
                    )
                )
            )
    else:
        cards_produtos.append(ft.Text("Esta loja ainda não possui produtos cadastrados.", size=18, col=12, text_align="center"))

    # Monta a View
    return ft.View(
        f"/lojas/{vendedor_slug}",
        [
            ft.Text(f"Produtos da Loja: {loja['name'] if loja else 'Desconhecida'}", size=32, weight="bold"),
            ft.Text(f"Localização: {loja['cidade']}, {loja['estado']}" if loja else "", size=16, color=ft.Colors.GREY_700),
            ft.Divider(height=20),
            ft.ResponsiveRow(controls=cards_produtos, spacing=20, run_spacing=20)
        ],
        padding=30,
        scroll=ft.ScrollMode.AUTO,
    )