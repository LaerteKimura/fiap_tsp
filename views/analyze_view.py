import os
import pygame
import subprocess
import threading
import platform

from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN, KEYUP, K_DELETE,
    K_ESCAPE, K_BACKSPACE, K_RETURN, K_KP_ENTER, K_TAB, KMOD_CTRL
)
from typing import Optional, Callable

from config import WHITE, GRAY, BLACK, RED, GREEN, DARK_GRAY
from route_analyzer import RouteAnalyzer

from ui_resources.ui_renderer import render_screen_header

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Pastas para organizar arquivos
SOLUTIONS_DIR = "solutions"
REPORTS_DIR = "reports"

def _get_font(size: int, bold: bool = False):
    for name in ["Segoe UI Emoji", "Segoe UI Symbol", "Segoe UI"]:
        f = pygame.font.SysFont(name, size, bold=bold)
        if f:
            return f
    return pygame.font.Font(None, size)


def _open_pdf(pdf_path: str):
    """Abre o PDF no visualizador padrão do sistema."""
    try:
        # Garantir caminho absoluto
        abs_path = os.path.abspath(pdf_path)
        if not os.path.exists(abs_path):
            print(f"Arquivo não encontrado: {abs_path}")
            return False
        
        if platform.system() == 'Windows':
            os.startfile(abs_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', abs_path])
        else:  # Linux
            subprocess.run(['xdg-open', abs_path])
        return True
    except Exception as e:
        print(f"Erro ao abrir PDF: {e}")
        return False


def show_api_key_input(screen: pygame.Surface, clock: pygame.time.Clock) -> Optional[str]:
    WIDTH, HEIGHT = screen.get_size()

    # Fontes no padrão
    font_title = _get_font(28, bold=True)
    font_sub   = _get_font(16)
    font_label = _get_font(16, bold=True)
    font_input = _get_font(18)
    font_btn   = _get_font(16, bold=True)
    font_hint  = _get_font(14)

    # Logo (mesmo padrão das outras telas)
    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "..", "assets", "location_pin.png")
    logo = pygame.image.load(logo_path).convert_alpha()
    logo = pygame.transform.smoothscale(logo, (40, 40))

    api_key = ""
    active = True
    cursor_visible = True
    cursor_timer = 0

    # Clipboard
    try:
        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_TEXT)
    except:
        pass

    def get_clipboard_text() -> Optional[str]:
        text = None
        try:
            scrap_text = pygame.scrap.get(pygame.SCRAP_TEXT)
            if scrap_text:
                text = scrap_text.decode("utf-8", errors="ignore").strip()
        except:
            pass

        if not text:
            try:
                import pyperclip  # type: ignore
                text = (pyperclip.paste() or "").strip()
            except:
                pass

        if text:
            text = "".join(c for c in text if c.isprintable() or c in " \t")
            return text
        return None

    while True:
        # Layout do card (calcula ANTES de tratar eventos pra não usar variável não definida)
        card_w = int(WIDTH * 0.85)
        card_h = 340
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2

        input_rect = pygame.Rect(card_x + 40, card_y + 150, card_w - 80, 50)

        buttons_y = card_y + card_h - 78
        back_rect = pygame.Rect(card_x + 40, buttons_y, 170, 46)
        continue_rect = pygame.Rect(card_x + card_w - 230, buttons_y, 190, 46)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None

                # Ctrl+V
                if (pygame.key.get_mods() & KMOD_CTRL) and event.key in (ord("v"), ord("V")):
                    if active:
                        clip = get_clipboard_text()
                        if clip:
                            api_key = clip
                    continue

                if event.key == K_BACKSPACE:
                    if active:
                        api_key = api_key[:-1]

                elif event.key in (K_RETURN, K_KP_ENTER):
                    if api_key.strip():
                        return api_key.strip()

                elif event.key == K_TAB:
                    continue

                else:
                    if event.unicode and active:
                        api_key += event.unicode

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if input_rect.collidepoint(mx, my):
                    active = True

                elif back_rect.collidepoint(mx, my):
                    return None

                elif continue_rect.collidepoint(mx, my):
                    if api_key.strip():
                        return api_key.strip()

        # Cursor blink
        cursor_timer += clock.get_time()
        if cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        # Render
        screen.fill((245, 247, 250))

        pygame.draw.rect(screen, (210, 215, 220), (card_x + 5, card_y + 5, card_w, card_h), border_radius=18)
        pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=18)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=18)

        # Topo: logo + título
        logo_x = card_x + 40
        logo_y = card_y + 32
        screen.blit(logo, (logo_x, logo_y))

        title = font_title.render("Chave API do Gemini", True, (40, 45, 55))
        title_rect = title.get_rect(midleft=(logo_x + 60, logo_y + logo.get_height() // 2))
        screen.blit(title, title_rect)

        sub = font_sub.render("Cole sua chave para habilitar o chat e os relatórios via LLM", True, (90, 95, 105))
        screen.blit(sub, (card_x + 40, card_y + 92))

        # Label do input
        label = font_label.render("Chave API:", True, (60, 65, 75))
        screen.blit(label, (card_x + 40, card_y + 125))

        # Input
        border_color = (30, 90, 160) if active else (200, 205, 210)
        pygame.draw.rect(screen, GRAY, input_rect, border_radius=10)
        pygame.draw.rect(screen, border_color, input_rect, width=2, border_radius=10)

        display_text = "*" * len(api_key) if api_key else ""
        input_surface = font_input.render(display_text, True, BLACK)
        screen.blit(input_surface, (input_rect.x + 12, input_rect.centery - input_surface.get_height() // 2))

        if active and cursor_visible:
            cursor_x = input_rect.x + 12 + input_surface.get_width()
            pygame.draw.line(screen, BLACK, (cursor_x, input_rect.y + 12), (cursor_x, input_rect.y + input_rect.height - 12), 2)

        mx, my = pygame.mouse.get_pos()

        # Botão Voltar
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_btn.render("< Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        # Botão Continuar
        cont_hover = continue_rect.collidepoint(mx, my)
        cont_bg = (220, 235, 250) if cont_hover else (245, 247, 250)
        pygame.draw.rect(screen, cont_bg, continue_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 90, 160), continue_rect, width=1, border_radius=12)
        cont_txt = font_btn.render("Continuar >", True, (30, 90, 160))
        screen.blit(cont_txt, cont_txt.get_rect(center=continue_rect.center))

        # Hint
        hint = font_hint.render("Enter confirmar • Esc voltar • Ctrl+V colar", True, (120, 125, 135))
        screen.blit(hint, (card_x + 40, buttons_y + 54))

        pygame.display.flip()
        clock.tick(60)

def show_file_selection(screen: pygame.Surface, clock: pygame.time.Clock, json_files: list) -> Optional[str]:
    WIDTH, HEIGHT = screen.get_size()

    font_title = _get_font(28, bold=True)
    font_sub   = _get_font(16)
    font_item  = _get_font(16)
    font_btn   = _get_font(16, bold=True)
    font_hint  = _get_font(14)

    # Logo padrão
    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "..", "assets", "location_pin.png")
    logo = pygame.image.load(logo_path).convert_alpha()
    logo = pygame.transform.smoothscale(logo, (40, 40))

    selected = 0
    scroll_offset = 0
    items_per_page = 8

    # Card fixo (padrão analyze)
    card_w = 820
    card_h = 520

    item_h = 46
    item_gap = 10

    while True:
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2

        # Áreas
        list_y = card_y + 140
        list_h = card_h - 220
        list_rect = pygame.Rect(card_x + 40, list_y, card_w - 80, list_h)

        # Botões
        buttons_y = card_y + card_h - 78
        back_rect = pygame.Rect(card_x + 40, buttons_y, 170, 46)
        continue_rect = pygame.Rect(card_x + card_w - 230, buttons_y, 190, 46)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    selected = max(0, selected - 1)
                elif event.key == pygame.K_DOWN:
                    selected = min(len(json_files) - 1, selected + 1)
                elif event.key in (K_RETURN, K_KP_ENTER):
                    return json_files[selected]

            if event.type == pygame.MOUSEWHEEL:
                # scroll suave
                scroll_offset = max(
                    0,
                    min(
                        scroll_offset - event.y * 20,
                        max(0, len(json_files) - items_per_page) * (item_h + item_gap),
                    ),
                )

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Clique em item da lista
                item_total_h = item_h + item_gap
                for i in range(len(json_files)):
                    item_y = list_y + i * item_total_h - scroll_offset
                    if item_y < list_y or item_y > list_y + list_h:
                        continue

                    item_rect = pygame.Rect(card_x + 40, item_y, card_w - 80, item_h)
                    if item_rect.collidepoint(mx, my):
                        return json_files[i]

                # Botões
                if back_rect.collidepoint(mx, my):
                    return None
                if continue_rect.collidepoint(mx, my):
                    return json_files[selected]

        # Ajustar scroll baseado na seleção (sempre mantém selecionado visível)
        item_total_h = item_h + item_gap
        visible_start = scroll_offset // item_total_h
        if selected < visible_start:
            scroll_offset = selected * item_total_h
        elif selected >= visible_start + items_per_page:
            scroll_offset = (selected - items_per_page + 1) * item_total_h

        # Render
        screen.fill((245, 247, 250))

        # Card
        pygame.draw.rect(screen, (210, 215, 220), (card_x + 5, card_y + 5, card_w, card_h), border_radius=18)
        pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=18)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=18)

        # Topo: logo + título
        logo_x = card_x + 40
        logo_y = card_y + 32
        screen.blit(logo, (logo_x, logo_y))

        title = font_title.render("Selecionar Arquivo de Solução", True, (40, 45, 55))
        title_rect = title.get_rect(midleft=(logo_x + 60, logo_y + logo.get_height() // 2))
        screen.blit(title, title_rect)

        sub = font_sub.render("Escolha o JSON exportado para análise", True, (90, 95, 105))
        screen.blit(sub, (card_x + 40, card_y + 92))

        # Lista
        mx, my = pygame.mouse.get_pos()

        for i in range(len(json_files)):
            item_y = list_y + i * item_total_h - scroll_offset
            if item_y < list_y or item_y > list_y + list_h:
                continue

            item_rect = pygame.Rect(card_x + 40, item_y, card_w - 80, item_h)
            is_hover = item_rect.collidepoint(mx, my)
            if is_hover:
                selected = i

            is_selected = (i == selected)

            bg = (220, 235, 250) if is_selected else ((235, 240, 246) if is_hover else WHITE)
            pygame.draw.rect(screen, bg, item_rect, border_radius=10)

            if is_selected:
                pygame.draw.rect(screen, (30, 90, 160), item_rect, width=2, border_radius=10)
            else:
                pygame.draw.rect(screen, (200, 205, 210), item_rect, width=1, border_radius=10)

            file_name = os.path.basename(json_files[i])
            file_text = font_item.render(file_name, True, (40, 45, 55) if is_selected else (70, 75, 85))
            screen.blit(file_text, (item_rect.x + 14, item_rect.centery - file_text.get_height() // 2))

        # Botões
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_btn.render("< Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        cont_hover = continue_rect.collidepoint(mx, my)
        cont_bg = (220, 235, 250) if cont_hover else (245, 247, 250)
        pygame.draw.rect(screen, cont_bg, continue_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 90, 160), continue_rect, width=1, border_radius=12)
        cont_txt = font_btn.render("Continuar >", True, (30, 90, 160))
        screen.blit(cont_txt, cont_txt.get_rect(center=continue_rect.center))

        pygame.display.flip()
        clock.tick(60)

def show_analysis_choice(screen: pygame.Surface, clock: pygame.time.Clock) -> Optional[str]:
    """Permite escolher entre gerar relatório ou iniciar chat."""
    WIDTH, HEIGHT = screen.get_size()

    # Fonts (padrão visual)
    font_title = _get_font(34, bold=True)
    font_sub   = _get_font(16)

    # Esses dois precisam suportar emoji
    font_item  = _get_font(18, bold=True)
    font_hint  = _get_font(14)

    # Logo (mesmo padrão das outras telas)
    base_dir = os.path.dirname(__file__)
    logo_path = os.path.join(base_dir, "..", "assets", "location_pin.png")
    logo = pygame.image.load(logo_path).convert_alpha()
    logo = pygame.transform.smoothscale(logo, (36, 36))

    selected = 0  # 0 = report, 1 = chat

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                if event.key == pygame.K_UP:
                    selected = 0
                if event.key == pygame.K_DOWN:
                    selected = 1
                if event.key in (K_RETURN, K_KP_ENTER):
                    return "report" if selected == 0 else "chat"

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if report_rect.collidepoint(mx, my):
                    return "report"
                if chat_rect.collidepoint(mx, my):
                    return "chat"
                if back_rect.collidepoint(mx, my):
                    return None
                if continue_rect.collidepoint(mx, my):
                    return "report" if selected == 0 else "chat"

        # Render
        screen.fill((245, 247, 250))

        # Card
        card_w = int(WIDTH * 0.78)
        card_h = int(HEIGHT * 0.78)
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2

        pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)

        # Topo: logo + título + subtítulo
        logo_x = card_x + 30
        logo_y = card_y + 28
        screen.blit(logo, (logo_x, logo_y))

        title = font_title.render("Modo de análise", True, (40, 45, 55))
        title_rect = title.get_rect(midleft=(logo_x + 54, logo_y + logo.get_height() // 2))
        screen.blit(title, title_rect)

        sub = font_sub.render("Escolha como você quer explorar a solução", True, (90, 95, 105))
        screen.blit(sub, (card_x + 30, card_y + 78))

        mx, my = pygame.mouse.get_pos()

        # Opções (bloco central)
        option_w = card_w - 60
        option_h = 84
        option_gap = 16
        options_top = card_y + 130

        report_rect = pygame.Rect(card_x + 30, options_top, option_w, option_h)
        chat_rect   = pygame.Rect(card_x + 30, options_top + option_h + option_gap, option_w, option_h)

        # Hover seleciona
        if report_rect.collidepoint(mx, my):
            selected = 0
        if chat_rect.collidepoint(mx, my):
            selected = 1

        def draw_option(rect, is_selected, is_hover, title_text, desc_text):
            bg = (220, 235, 250) if is_selected else ((235, 240, 246) if is_hover else WHITE)
            border = (30, 90, 160) if is_selected else (200, 205, 210)
            border_w = 2 if is_selected else 1

            pygame.draw.rect(screen, bg, rect, border_radius=12)
            pygame.draw.rect(screen, border, rect, width=border_w, border_radius=12)

            t = font_item.render(title_text, True, (40, 45, 55))
            d = font_hint.render(desc_text, True, (120, 125, 135))
            screen.blit(t, (rect.x + 18, rect.y + 18))
            screen.blit(d, (rect.x + 18, rect.y + 48))

        # ÍCONES DE VOLTA 😄
        draw_option(
            report_rect,
            is_selected=(selected == 0),
            is_hover=report_rect.collidepoint(mx, my),
            title_text="📄  Gerar relatório PDF",
            desc_text="Análise completa com visualizações"
        )

        draw_option(
            chat_rect,
            is_selected=(selected == 1),
            is_hover=chat_rect.collidepoint(mx, my),
            title_text="💬  Iniciar chat com LLM",
            desc_text="Diálogo interativo sobre a solução"
        )

        # Rodapé: botões (mesma linha) + hint embaixo (com folga)
        buttons_y = card_y + card_h - 92
        back_rect = pygame.Rect(card_x + 30, buttons_y, 170, 46)
        continue_rect = pygame.Rect(card_x + card_w - 200, buttons_y, 170, 46)

        # Botão Voltar
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_item.render("< Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        # Botão Confirmar
        cont_hover = continue_rect.collidepoint(mx, my)
        cont_bg = (220, 235, 250) if cont_hover else (245, 247, 250)
        pygame.draw.rect(screen, cont_bg, continue_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 90, 160), continue_rect, width=1, border_radius=12)
        cont_txt = font_item.render("Confirmar >", True, (30, 90, 160))
        screen.blit(cont_txt, cont_txt.get_rect(center=continue_rect.center))

        # Hint (abaixo, não encostado)
        hint = font_hint.render("↑↓ ou mouse • Enter confirmar • Esc voltar", True, (120, 125, 135))
        screen.blit(hint, (card_x + 30, buttons_y + 56))

        pygame.display.flip()
        clock.tick(60)

def show_chat_interface(screen: pygame.Surface, clock: pygame.time.Clock, api_key: str, json_path: str):
    import textwrap
    import threading
    import pygame
    from pygame.locals import (
        QUIT, KEYDOWN, KEYUP, MOUSEWHEEL, MOUSEBUTTONDOWN, TEXTINPUT,
        K_ESCAPE, K_BACKSPACE, K_RETURN, K_KP_ENTER,
        K_LEFT, K_RIGHT, K_HOME, K_END, K_DELETE, KMOD_CTRL
    )

    try:
        import google.generativeai as genai
    except Exception:
        genai = None

    WIDTH, HEIGHT = screen.get_size()

    # ===== Layout (100% tela, estilo TSP) =====
    HEADER_H = 64
    PADDING = 16
    ACTION_H = 54
    INPUT_H = 48  # menor e mais alinhado
    FOOTER_H = ACTION_H + INPUT_H + 12

    SCROLLBAR_W = 8
    SCROLLBAR_GAP = 10

    BG = (245, 247, 250)
    WHITE = (255, 255, 255)

    # ===== Fonts (emoji-friendly quando disponível) =====
    def _get_font(size: int, bold: bool = False):
        for name in ["Segoe UI Emoji", "Segoe UI Symbol", "Segoe UI"]:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        return pygame.font.Font(None, size)

    font_msg = _get_font(16, bold=False)
    font_input = _get_font(18, bold=False)
    font_badge = _get_font(14, bold=True)
    font_btn = _get_font(16, bold=True)
    font_placeholder = _get_font(14, bold=False)

    from route_analyzer import RouteAnalyzer
    from ui_resources.ui_renderer import render_screen_header

    # ===== Clipboard (Ctrl+V) =====
    try:
        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_TEXT)
    except Exception:
        pass

    def _get_clipboard_text() -> str:
        txt = None
        try:
            scrap_text = pygame.scrap.get(pygame.SCRAP_TEXT)
            if scrap_text:
                txt = scrap_text.decode("utf-8", errors="ignore")
        except Exception:
            txt = None

        if not txt:
            try:
                import pyperclip  # type: ignore
                txt = pyperclip.paste()
            except Exception:
                txt = None

        if not txt:
            return ""

        txt = txt.replace("\r\n", "\n").replace("\r", "\n")
        txt = "".join(c for c in txt if c.isprintable() or c in "\n\t ")
        return txt

    def _clean_text(text: str) -> str:
        if not text:
            return ""
        text = text.replace("\x00", "")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = []
        for ch in text:
            code = ord(ch)
            if code >= 0x20 or ch in "\n\t":
                cleaned.append(ch)
            else:
                cleaned.append(" ")
        return "".join(cleaned)

    def _draw_status_badge(text: str, color: tuple[int, int, int]):
        pad_x, pad_y = 10, 6
        surf = font_badge.render(text, True, (255, 255, 255))
        w, h = surf.get_width() + pad_x * 2, surf.get_height() + pad_y * 2
        r = pygame.Rect(WIDTH - w - PADDING, (HEADER_H - h) // 2, w, h)
        pygame.draw.rect(screen, color, r, border_radius=12)
        screen.blit(surf, (r.x + pad_x, r.y + pad_y))

    def _wrap_text_to_lines(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        paragraphs = text.split("\n")
        lines: list[str] = []
        for para in paragraphs:
            if not para.strip():
                lines.append("")
                continue

            words = para.split(" ")
            current: list[str] = []
            current_w = 0

            for w in words:
                token = (w + " ")
                try:
                    w_w = font.size(token)[0]
                except Exception:
                    w_w = len(token) * 8

                if current and current_w + w_w > max_width:
                    lines.append(" ".join(current))
                    current = [w]
                    current_w = w_w
                else:
                    current.append(w)
                    current_w += w_w

            if current:
                lines.append(" ".join(current))
        return lines

    def _measure_message_height(text: str, font: pygame.font.Font, max_text_width: int) -> int:
        lines = _wrap_text_to_lines(text, font, max_text_width)
        line_h = 22
        pad_y = 20
        return len(lines) * line_h + pad_y

    def _draw_button(rect: pygame.Rect, label: str, hover: bool, primary: bool = False):
        if primary:
            bg = (220, 235, 250) if hover else (245, 247, 250)
            border = (30, 90, 160)
            fg = (30, 90, 160)
        else:
            bg = (235, 240, 246) if hover else (245, 247, 250)
            border = (200, 205, 210)
            fg = (70, 75, 85)

        pygame.draw.rect(screen, bg, rect, border_radius=12)
        pygame.draw.rect(screen, border, rect, width=1, border_radius=12)
        txt = font_btn.render(label, True, fg)
        screen.blit(txt, txt.get_rect(center=rect.center))

    def _render_loading_center(msg: str):
        screen.fill(BG)
        render_screen_header(
            screen,
            pygame.Rect(0, 0, WIDTH, HEADER_H),
            "Chat com LLM - Análise",
            "./assets/location_pin.png",
        )
        surf = _get_font(18, bold=True).render(msg, True, (70, 75, 85))
        screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT // 2 - surf.get_height() // 2))
        pygame.display.flip()

    def _caret_pixel_x(text: str, caret_index: int) -> int:
        try:
            return font_input.size(text[:caret_index])[0]
        except Exception:
            return len(text[:caret_index]) * 10

    # ===== Inicializar analyzer/embeddings =====
    analyzer = None
    df_embeddings = None
    current_status = "Carregando solução..."

    try:
        if genai is None:
            raise RuntimeError("Pacote google-generativeai não está instalado.")

        def update_status(msg: str):
            nonlocal current_status
            current_status = msg
            _render_loading_center(msg)
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    pygame.quit()
                    raise SystemExit

        update_status("Carregando solução...")
        analyzer = RouteAnalyzer(api_key, progress_callback=update_status)
        analyzer.load_solution(json_path)

        update_status("Criando chunks de texto...")
        chunks = analyzer.create_text_chunks()

        update_status("Gerando embeddings...")
        df_embeddings = analyzer.generate_embeddings(chunks)

        current_status = "Pronto para conversar"
    except Exception as e:
        current_status = f"Erro: {str(e)}"
        df_embeddings = None

    # ===== Estado do chat =====
    messages: list[tuple[str, str]] = []
    input_text = ""
    caret_pos = 0
    scroll_offset = 0
    waiting_response = False
    input_active = True

    # Worker thread para NÃO congelar o pygame
    worker_thread: threading.Thread | None = None
    worker_result = {"done": False, "text": "", "error": ""}

    # Evita problema "~" / teclas mortas: usar TEXTINPUT (não unicode do KEYDOWN)
    pygame.key.set_repeat(350, 28)

    # Text input / IME
    pygame.key.start_text_input()

    def _set_caret_by_mouse(inner_x: int, current_input_rect: pygame.Rect):
        nonlocal caret_pos
        if not input_text:
            caret_pos = 0
            return

        target_x = max(0, inner_x)
        best_i = 0
        best_dx = 10**9
        for i in range(len(input_text) + 1):
            w = _caret_pixel_x(input_text, i)
            dx = abs(w - target_x)
            if dx < best_dx:
                best_dx = dx
                best_i = i
        caret_pos = best_i

    def _start_llm_request(query: str):
        nonlocal worker_thread, worker_result

        if worker_thread and worker_thread.is_alive():
            return

        worker_result["done"] = False
        worker_result["text"] = ""
        worker_result["error"] = ""

        def _worker():
            try:
                context = analyzer.find_relevant_context(query, df_embeddings, top_k=7)

                basic_info_chunks = []
                for _, row in df_embeddings.iterrows():
                    chunk_title = row.get("title", "")
                    if ("Resumo Geral" in chunk_title) or ("Estatísticas Agregadas" in chunk_title) or ("Métricas Principais" in chunk_title):
                        if row["text"] not in context:
                            basic_info_chunks.append(f"### {chunk_title}\n{row['text']}")

                full_context = ("\n\n".join(basic_info_chunks) + "\n\n" + context) if basic_info_chunks else context
                full_context_clean = _clean_text(full_context)

                import json as _json
                try:
                    json_data = _json.dumps(analyzer.solution_data, indent=2, ensure_ascii=False)
                    json_data_clean = _clean_text(json_data)
                    if len(json_data_clean) > 50000:
                        solution_data_summary = {
                            "metadata": analyzer.solution_data.get("metadata", {}),
                            "solution": {
                                "aggregate_stats": analyzer.solution_data.get("solution", {}).get("aggregate_stats", {}),
                                "routes_count": len(analyzer.solution_data.get("solution", {}).get("routes", [])),
                                "routes": analyzer.solution_data.get("solution", {}).get("routes", [])[:5],
                            },
                        }
                        json_data_clean = _clean_text(_json.dumps(solution_data_summary, indent=2, ensure_ascii=False))
                except Exception as e:
                    json_data_clean = f"Erro ao serializar JSON: {str(e)}"

                model = genai.GenerativeModel(analyzer.generation_model)

                prompt = textwrap.dedent(f"""
                Você é um assistente especializado em análise de soluções de roteamento e logística.

                Use APENAS as informações fornecidas abaixo para responder à pergunta do usuário.

                CONTEXTO RELEVANTE (chunks mais importantes):
                {full_context_clean}

                DADOS COMPLETOS DA SOLUÇÃO (JSON):
                {json_data_clean}

                PERGUNTA DO USUÁRIO: {query}

                INSTRUÇÕES IMPORTANTES:
                - Responda APENAS com base nas informações fornecidas acima
                - Use os dados do JSON completo para informações detalhadas
                - Use o contexto relevante para informações resumidas
                - Se encontrar informações nos dados, responda com os valores EXATOS mencionados
                - Se não encontrar a informação, diga claramente "Não tenho essa informação disponível"
                - Responda em português de forma direta, clara e precisa
                - Use números e valores exatos dos dados, não invente ou assuma valores
                """).strip()

                prompt = _clean_text(prompt)
                response = model.generate_content(prompt)

                if response and getattr(response, "text", None):
                    worker_result["text"] = _clean_text(response.text)
                else:
                    worker_result["error"] = "❌ Resposta vazia recebida da API"

            except Exception as e:
                msg = str(e)
                if len(msg) > 240:
                    msg = msg[:240] + "..."
                worker_result["error"] = f"❌ Erro: {msg}"
            finally:
                worker_result["done"] = True

        worker_thread = threading.Thread(target=_worker, daemon=True)
        worker_thread.start()

    def _send_current_input():
        nonlocal input_text, caret_pos, waiting_response, scroll_offset

        if waiting_response:
            return
        if df_embeddings is None:
            return
        if not input_text.strip():
            return

        user_msg = input_text.strip()
        messages.append(("user", user_msg))
        messages.append(("assistant", "⏳ Gerando resposta…"))

        input_text = ""
        caret_pos = 0
        waiting_response = True

        _start_llm_request(user_msg)

        # scroll para o fim imediatamente (mostra a bolha "⏳")
        msg_area_y = HEADER_H + PADDING
        msg_area_h = HEIGHT - msg_area_y - FOOTER_H
        msg_area_w = WIDTH - (PADDING * 2) - (SCROLLBAR_W + SCROLLBAR_GAP)
        max_text_width = msg_area_w - 80

        total_h = 0
        for _, txt in messages:
            total_h += _measure_message_height(txt, font_msg, max_text_width) + 10
        scroll_offset = max(0, total_h - msg_area_h + 20)

    # ===== Loop =====
    while True:
        header_rect = pygame.Rect(0, 0, WIDTH, HEADER_H)

        msg_area_y = HEADER_H + PADDING
        msg_area_h = HEIGHT - msg_area_y - FOOTER_H
        msg_area_x = PADDING
        msg_area_w = WIDTH - (PADDING * 2) - (SCROLLBAR_W + SCROLLBAR_GAP)

        scrollbar_x = msg_area_x + msg_area_w + SCROLLBAR_GAP
        scrollbar_y = msg_area_y
        scrollbar_h = msg_area_h

        action_rect = pygame.Rect(PADDING, HEIGHT - ACTION_H - PADDING, WIDTH - PADDING * 2, ACTION_H)
        input_rect = pygame.Rect(PADDING, action_rect.y - INPUT_H - 10, WIDTH - PADDING * 2, INPUT_H)

        # informa ao pygame/IME onde está o campo de texto
        try:
            pygame.key.set_text_input_rect(input_rect)
        except Exception:
            pass

        btn_w, btn_h = 170, 46
        btn_y = action_rect.y + (ACTION_H - btn_h) // 2
        back_rect = pygame.Rect(action_rect.x, btn_y, btn_w, btn_h)
        send_rect = pygame.Rect(action_rect.right - btn_w, btn_y, btn_w, btn_h)

        # ===== Eventos =====
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == MOUSEWHEEL:
                scroll_offset = max(0, scroll_offset - event.y * 36)

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if back_rect.collidepoint(mx, my):
                    pygame.key.stop_text_input()
                    return

                if send_rect.collidepoint(mx, my):
                    _send_current_input()

                if input_rect.collidepoint(mx, my):
                    input_active = True
                    inner_x = mx - (input_rect.x + 14)
                    _set_caret_by_mouse(inner_x, input_rect)
                else:
                    input_active = True

            if event.type == KEYDOWN:
                mods = pygame.key.get_mods()
                is_ctrl = bool(mods & KMOD_CTRL)

                if event.key == K_ESCAPE:
                    pygame.key.stop_text_input()
                    return

                # Ctrl+V
                if is_ctrl and (event.key == ord("v") or event.key == ord("V")):
                    if input_active and not waiting_response:
                        clip = _get_clipboard_text()
                        if clip:
                            input_text = input_text[:caret_pos] + clip + input_text[caret_pos:]
                            caret_pos += len(clip)
                    continue

                if waiting_response:
                    continue

                if event.key == K_BACKSPACE:
                    if input_active and caret_pos > 0:
                        input_text = input_text[:caret_pos - 1] + input_text[caret_pos:]
                        caret_pos -= 1

                elif event.key == K_DELETE:
                    if input_active and caret_pos < len(input_text):
                        input_text = input_text[:caret_pos] + input_text[caret_pos + 1:]

                elif event.key in (K_RETURN, K_KP_ENTER):
                    _send_current_input()

                elif event.key == K_LEFT:
                    caret_pos = max(0, caret_pos - 1)

                elif event.key == K_RIGHT:
                    caret_pos = min(len(input_text), caret_pos + 1)

                elif event.key == K_HOME:
                    caret_pos = 0

                elif event.key == K_END:
                    caret_pos = len(input_text)

                # NÃO usa event.unicode aqui (evita "~" duplicado)
                # texto entra via TEXTINPUT

            if event.type == TEXTINPUT:
                if input_active and not waiting_response:
                    txt = event.text
                    if txt:
                        input_text = input_text[:caret_pos] + txt + input_text[caret_pos:]
                        caret_pos += len(txt)

            if event.type == KEYUP:
                pass

        # ===== Coletar resultado do worker (sem travar) =====
        if waiting_response and worker_result["done"]:
            final_text = worker_result["text"] or worker_result["error"] or "❌ Erro desconhecido"

            if messages and messages[-1][0] == "assistant" and "⏳" in messages[-1][1]:
                messages[-1] = ("assistant", final_text)
            else:
                messages.append(("assistant", final_text))

            waiting_response = False
            worker_result["done"] = False

            # scroll para o fim após resposta real
            max_text_width = msg_area_w - 80
            total_h = 0
            for _, txt in messages:
                total_h += _measure_message_height(txt, font_msg, max_text_width) + 10
            scroll_offset = max(0, total_h - msg_area_h + 20)

        # ===== Render =====
        screen.fill(BG)

        # Header
        render_screen_header(screen, header_rect, "Chat com LLM - Análise", "./assets/location_pin.png")

        # Badge no header
        if df_embeddings is None:
            _draw_status_badge("Erro ao carregar", (200, 60, 60))
        elif waiting_response:
            _draw_status_badge("Gerando resposta…", (200, 150, 0))
        else:
            _draw_status_badge("Pronto para conversar", (40, 160, 90))

        # Mensagens (com clipping)
        clip_prev = screen.get_clip()
        screen.set_clip(pygame.Rect(msg_area_x, msg_area_y, msg_area_w + SCROLLBAR_W + SCROLLBAR_GAP, msg_area_h))

        y = msg_area_y - scroll_offset
        max_text_width = msg_area_w - 80
        line_h = 22
        bubble_pad_x = 14
        bubble_pad_y = 10
        bubble_w = msg_area_w - 10

        for role, text in messages:
            if y > msg_area_y + msg_area_h:
                break

            is_user = (role == "user")
            bg_color = (220, 235, 250) if is_user else WHITE
            text_color = (40, 45, 55) if is_user else (70, 75, 85)

            lines = _wrap_text_to_lines(text, font_msg, max_text_width)
            msg_h = len(lines) * line_h + (bubble_pad_y * 2)

            msg_x = (msg_area_x + msg_area_w - bubble_w) if is_user else msg_area_x
            msg_rect = pygame.Rect(msg_x, y, bubble_w, msg_h)

            pygame.draw.rect(screen, bg_color, msg_rect, border_radius=12)
            pygame.draw.rect(screen, (200, 205, 210), msg_rect, width=1, border_radius=12)

            for i, line in enumerate(lines):
                if not line:
                    continue
                try:
                    surf = font_msg.render(line, True, text_color)
                except Exception:
                    safe = "".join(c for c in line if c.isprintable() or c in " \n\t")
                    surf = font_msg.render(safe, True, text_color)
                screen.blit(surf, (msg_rect.x + bubble_pad_x, msg_rect.y + bubble_pad_y + i * line_h))

            y += msg_h + 10

        screen.set_clip(clip_prev)

        # Scrollbar
        total_messages_height = 0
        for _, text in messages:
            total_messages_height += _measure_message_height(text, font_msg, max_text_width) + 10

        if total_messages_height > msg_area_h:
            pygame.draw.rect(screen, (220, 225, 230), (scrollbar_x, scrollbar_y, SCROLLBAR_W, scrollbar_h), border_radius=4)

            max_scroll = max(1, total_messages_height - msg_area_h)
            ratio = min(1.0, scroll_offset / max_scroll) if max_scroll > 0 else 0.0

            thumb_h = max(20, int(msg_area_h * (msg_area_h / total_messages_height)))
            thumb_y = scrollbar_y + int(ratio * (scrollbar_h - thumb_h))

            pygame.draw.rect(screen, (150, 160, 170), (scrollbar_x, thumb_y, SCROLLBAR_W, thumb_h), border_radius=4)

        # Input
        pygame.draw.rect(screen, WHITE, input_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), input_rect, width=1, border_radius=12)

        text_left = input_rect.x + 14

        # Y centralizado verticalmente
        if input_text:
            temp_surf = font_input.render(input_text, True, (40, 45, 55))
            text_top = input_rect.y + (input_rect.h - temp_surf.get_height()) // 2
        else:
            ph_surf = font_placeholder.render("Digite sua pergunta…", True, (150, 155, 165))
            text_top = input_rect.y + (input_rect.h - ph_surf.get_height()) // 2

        max_input_w = input_rect.w - 28
        caret_px = _caret_pixel_x(input_text, caret_pos)

        start_x = 0
        if caret_px > max_input_w:
            start_x = caret_px - max_input_w + 10

        clip_prev2 = screen.get_clip()
        screen.set_clip(input_rect.inflate(-14, -12))

        if input_text:
            try:
                surf = font_input.render(input_text, True, (40, 45, 55))
            except Exception:
                safe = "".join(c for c in input_text if c.isprintable() or c in " \n\t")
                surf = font_input.render(safe, True, (40, 45, 55))
            screen.blit(surf, (text_left - start_x, text_top))
        else:
            screen.blit(ph_surf, (text_left, text_top))

        # Caret visível (pisca)
        if input_active and not waiting_response:
            blink_on = (pygame.time.get_ticks() % 900) < 450
            if blink_on:
                cx = text_left - start_x + caret_px
                # caret também centralizado
                cy1 = input_rect.y + 10
                cy2 = input_rect.y + input_rect.h - 10
                pygame.draw.line(screen, (40, 45, 55), (cx, cy1), (cx, cy2), 2)

        screen.set_clip(clip_prev2)

        # Action bar (botões)
        mx, my = pygame.mouse.get_pos()
        pygame.draw.rect(screen, BG, action_rect, border_radius=12)
        _draw_button(back_rect, "◀ Voltar", back_rect.collidepoint(mx, my), primary=False)
        _draw_button(send_rect, "Enviar ▶", send_rect.collidepoint(mx, my), primary=True)

        pygame.display.flip()
        clock.tick(60)

def _render_status_screen(screen: pygame.Surface, status: str, font_title, font_status):
    """Renderiza tela de status."""
    WIDTH, HEIGHT = screen.get_size()
    screen.fill((245, 247, 250))
    
    card_w = 700
    card_h = 400
    card_x = (WIDTH - card_w) // 2
    card_y = (HEIGHT - card_h) // 2
    
    pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
    pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=16)
    pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)
    
    title = font_title.render("Gerando Relatório", True, (40, 45, 55))
    screen.blit(title, (card_x + 30, card_y + 30))
    
    status_text = font_status.render(status, True, (70, 75, 85))
    screen.blit(status_text, (card_x + 30, card_y + 120))
    
    pygame.display.flip()


def show_analysis_progress(screen: pygame.Surface, clock: pygame.time.Clock, 
                          status_callback: Callable[[str], None]) -> tuple[Optional[str], Optional[str]]:
    """Mostra progresso da análise e retorna (pdf_path, error)."""
    WIDTH, HEIGHT = screen.get_size()
    
    font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_status = pygame.font.SysFont("Segoe UI", 18)
    font_hint = pygame.font.SysFont("Segoe UI", 14)
    
    current_status = "Iniciando análise..."
    pdf_path = None
    error = None
    
    # Criar pasta solutions se não existir
    if not os.path.exists(SOLUTIONS_DIR):
        os.makedirs(SOLUTIONS_DIR)
    
    # Buscar arquivos JSON na pasta solutions
    json_files = []
    if os.path.exists(SOLUTIONS_DIR):
        json_files = [f for f in os.listdir(SOLUTIONS_DIR) if f.endswith('.json') and 
                     ('solution' in f.lower() or 'vrp' in f.lower() or 'tsp' in f.lower())]
        # Adicionar caminho completo
        json_files = [os.path.join(SOLUTIONS_DIR, f) for f in json_files]
    
    if not json_files:
        return None, f"Nenhum arquivo de solução encontrado na pasta {SOLUTIONS_DIR}"
    
    # Solicitar chave API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        api_key = show_api_key_input(screen, clock)
        if not api_key:
            return None, None  # Usuário cancelou
    
    # Selecionar arquivo
    json_path = show_file_selection(screen, clock, json_files)
    if not json_path:
        return None, None  # Usuário cancelou
    
    # Escolher entre gerar relatório ou iniciar chat
    choice = show_analysis_choice(screen, clock)
    if choice == "chat":
        # Iniciar chat
        show_chat_interface(screen, clock, api_key, json_path)
        return None, None  # Chat não gera PDF
    elif choice is None:
        return None, None  # Usuário cancelou
    # Se choice == "report", continua com o fluxo de relatório
    
    # Executar análise com atualização de status
    def update_status(msg: str):
        nonlocal current_status
        current_status = msg
        _render_status_screen(screen, current_status, font_title, font_status)
        
        # Processar eventos para manter responsividade
        for event in pygame.event.get():
            if event.type == QUIT:
                raise KeyboardInterrupt
    
    try:
        analyzer = RouteAnalyzer(api_key, progress_callback=update_status)
        
        update_status("Carregando solução...")
        analyzer.load_solution(json_path)
        
        update_status("Criando chunks de texto...")
        chunks = analyzer.create_text_chunks()
        
        update_status("Gerando embeddings...")
        df = analyzer.generate_embeddings(chunks)
        
        update_status("Gerando análises com Gemini...")
        analyses = analyzer.generate_analysis(df)
        
        update_status("Criando visualizações...")
        viz_files = analyzer.create_visualizations()
        
        update_status("Gerando relatório PDF...")
        pdf_path = analyzer.generate_pdf_report(analyses, viz_files)
        
        current_status = "✅ Análise concluída com sucesso!"
        
    except KeyboardInterrupt:
        return None, None
    except Exception as e:
        error = str(e)
        current_status = f"❌ Erro: {error}"
    
    # Tela final com resultado
    while True:
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return pdf_path, error
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return pdf_path, error
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if pdf_path and os.path.exists(pdf_path):
                    open_rect = pygame.Rect(card_x + 30, card_y + 200, card_w - 60, 50)
                    if open_rect.collidepoint(event.pos):
                        _open_pdf(pdf_path)
                        continue
                
                back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, card_w - 60, 50)
                if back_rect.collidepoint(event.pos):
                    return pdf_path, error
        
        # Render
        screen.fill((245, 247, 250))
        
        card_w = 700
        card_h = 400
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2
        
        pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)
        
        # Título
        title = font_title.render("Análise Concluída" if pdf_path else "Erro na Análise", 
                                 True, (40, 45, 55))
        screen.blit(title, (card_x + 30, card_y + 30))
        
        # Status
        status_color = GREEN if pdf_path else RED
        status_text = font_status.render(current_status, True, status_color)
        screen.blit(status_text, (card_x + 30, card_y + 100))
        
        if pdf_path:
            # Mostrar apenas o nome do arquivo, não o caminho completo
            pdf_filename = os.path.basename(pdf_path)
            pdf_info = font_status.render(f"Relatório: {pdf_filename}", True, (70, 75, 85))
            screen.blit(pdf_info, (card_x + 30, card_y + 140))
        
        # Botão Abrir PDF (se sucesso)
        if pdf_path and os.path.exists(pdf_path):
            open_rect = pygame.Rect(card_x + 30, card_y + 200, card_w - 60, 50)
            open_hover = open_rect.collidepoint(mx, my)
            open_bg = (220, 235, 250) if open_hover else (245, 247, 250)
            pygame.draw.rect(screen, open_bg, open_rect, border_radius=12)
            pygame.draw.rect(screen, (30, 90, 160), open_rect, width=1, border_radius=12)
            open_txt = font_status.render("📄 Abrir PDF", True, (30, 90, 160))
            screen.blit(open_txt, open_txt.get_rect(center=open_rect.center))
        
        # Botão Voltar
        back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, card_w - 60, 50)
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_status.render("Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))
        
        pygame.display.flip()
        clock.tick(60)


def run_analyze_mode():
    """Executa o modo de análise com interface gráfica."""
    pygame.init()
    
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Análise de Soluções - Gemini AI")
    clock = pygame.time.Clock()
    
    pdf_path, error = show_analysis_progress(screen, clock, lambda x: None)
    
    pygame.quit()
    return pdf_path, error
