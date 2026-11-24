"""
Componente de rodapé (Footer) do Backup Utility CiD.
Exibe 'Powered by', a logo e o link clicável para o portfólio.
"""

from pathlib import Path
import sys
import flet as ft
from frontend.styles.theme import (
    COLOR_BG_SECONDARY,
    COLOR_BORDER,
    COLOR_ACCENT,
    COLOR_TEXT_SECONDARY,
)

PORTFOLIO_URL = "https://leonascimentodev-sooty.vercel.app"


def _get_logo_path() -> str:
    """Resolve o caminho da logo tanto em execução normal quanto empacotada via PyInstaller."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_dir = Path(sys._MEIPASS) / "frontend" / "assets"
    else:
        base_dir = Path(__file__).resolve().parent.parent / "assets"
    return str(base_dir / "logo_powered_by.png")


def create_footer(page: ft.Page) -> ft.Container:
    """Cria o rodapé institucional com 'Powered by', logo e link do portfólio."""
    def open_portfolio(_):
        if hasattr(page, "launch_url"):
            page.launch_url(PORTFOLIO_URL)

    return ft.Container(
        bgcolor=COLOR_BG_SECONDARY,
        padding=ft.Padding.symmetric(horizontal=24, vertical=8),
        border=ft.Border.only(top=ft.BorderSide(1, COLOR_BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Text(
                    "Powered by",
                    size=12,
                    color=COLOR_TEXT_SECONDARY,
                ),
                ft.Container(
                    content=ft.Image(
                        src=_get_logo_path(),
                        height=38,
                    ),
                    on_click=open_portfolio,
                    tooltip=PORTFOLIO_URL,
                ),
            ],
        ),
    )
