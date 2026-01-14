import os
import pygame
import subprocess
import platform
from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN, KEYUP,
    K_ESCAPE, K_BACKSPACE, K_RETURN, K_KP_ENTER, K_TAB, KMOD_CTRL
)
from typing import Optional, Callable

from config import WHITE, GRAY, BLACK, RED, GREEN, DARK_GRAY
from route_analyzer import RouteAnalyzer

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
    """Interface de chat com LLM usando o JSON como contexto."""
    import textwrap
    
    WIDTH, HEIGHT = screen.get_size()
    
    font_title = pygame.font.SysFont("Segoe UI", 24, bold=True)
    font_msg = pygame.font.SysFont("Segoe UI", 16)
    font_input = pygame.font.SysFont("Segoe UI", 18)
    font_hint = pygame.font.SysFont("Segoe UI", 14)
    
    # Inicializar analyzer e gerar embeddings
    analyzer = None
    df_embeddings = None
    current_status = "Carregando solução..."
    
    try:
        def update_status(msg: str):
            nonlocal current_status
            current_status = msg
            screen.fill((245, 247, 250))
            status_text = font_title.render(msg, True, (70, 75, 85))
            screen.blit(status_text, (WIDTH // 2 - status_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == QUIT:
                    raise KeyboardInterrupt
        
        update_status("Carregando solução...")
        analyzer = RouteAnalyzer(api_key, progress_callback=update_status)
        analyzer.load_solution(json_path)
        
        update_status("Criando chunks de texto...")
        chunks = analyzer.create_text_chunks()
        
        update_status("Gerando embeddings...")
        df_embeddings = analyzer.generate_embeddings(chunks)
        
        current_status = "✅ Pronto para conversar!"
        
    except Exception as e:
        current_status = f"❌ Erro: {str(e)}"
        df_embeddings = None
    
    # Estado do chat
    messages = []  # Lista de (role, text) onde role é 'user' ou 'assistant'
    input_text = ""
    input_active = True
    scroll_offset = 0
    waiting_response = False
    pending_query = None  # Query pendente para processar
    ctrl_pressed = False  # Flag para rastrear se Ctrl está pressionado
    
    # Inicializar scrap para clipboard
    try:
        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_TEXT)
    except:
        pass
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit
            
            if event.type == KEYDOWN:
                # Verificar modificadores primeiro
                mods = pygame.key.get_mods()
                is_ctrl = bool(mods & KMOD_CTRL)
                
                # Verificar Ctrl+V PRIMEIRO, antes de qualquer outra coisa
                # Verificar se é Ctrl+V (tanto 'v' quanto 'V' minúsculo/maiúsculo)
                if is_ctrl and (event.key == ord('v') or event.key == ord('V')):
                    # Ctrl+V para colar - apenas se estiver no input
                    if input_active and not waiting_response:
                        clipboard_text = None
                        try:
                            scrap_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                            if scrap_text:
                                clipboard_text = scrap_text.decode('utf-8', errors='ignore').strip()
                        except:
                            pass
                        if not clipboard_text:
                            try:
                                import pyperclip
                                clipboard_text = pyperclip.paste()
                                if clipboard_text:
                                    clipboard_text = clipboard_text.strip()
                            except ImportError:
                                pass
                        if clipboard_text:
                            input_text += clipboard_text
                    # SEMPRE pular este evento quando Ctrl+V é detectado
                    # Não processar mais nada deste evento - pular para próximo evento
                    continue
                
                # Se Ctrl está pressionado, não processar outros eventos de tecla
                # (exceto ESC que será verificado abaixo)
                if is_ctrl and event.key != K_ESCAPE:
                    continue
                
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_BACKSPACE:
                    if input_active and not waiting_response:
                        input_text = input_text[:-1]
                elif event.key in (K_RETURN, K_KP_ENTER):
                    if input_active and input_text.strip() and not waiting_response and df_embeddings is not None:
                        # Enviar mensagem
                        user_msg = input_text.strip()
                        messages.append(('user', user_msg))
                        input_text = ""
                        waiting_response = True
                        pending_query = user_msg  # Marcar query para processar
                        # Scroll para a última mensagem
                        scroll_offset = max(0, len(messages) * 150 - (HEIGHT - 280))
                elif input_active and not waiting_response:
                    # Não processar unicode se Ctrl está pressionado
                    if event.unicode and not is_ctrl:
                        input_text += event.unicode
            
            # Ignorar KEYUP quando Ctrl está pressionado (evita problemas com Ctrl+V)
            if event.type == KEYUP:
                mods = pygame.key.get_mods()
                is_ctrl = bool(mods & KMOD_CTRL)
                if is_ctrl:
                    continue
            
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, scroll_offset - event.y * 30)
        
        # Processar query pendente (fora do loop de eventos)
        if pending_query and waiting_response and df_embeddings is not None:
            # Definir dimensões da área de mensagens (usadas no cálculo de scroll)
            msg_area_y_temp = 80
            msg_area_h_temp = HEIGHT - 200
            msg_area_w_temp = WIDTH - 60
            
            # Renderizar "buscando contexto" antes de começar
            screen.fill((245, 247, 250))
            title = font_title.render("Chat com LLM - Análise de Solução", True, (40, 45, 55))
            screen.blit(title, (20, 20))
            status_text = font_hint.render("⏳ Buscando contexto relevante...", True, (200, 150, 0))
            screen.blit(status_text, (20, 55))
            pygame.display.flip()
            
            try:
                # Buscar contexto relevante
                context = analyzer.find_relevant_context(pending_query, df_embeddings, top_k=7)
                
                # Sempre incluir informações básicas importantes
                basic_info_chunks = []
                mode = analyzer.solution_data.get('metadata', {}).get('mode', '')
                
                # Procurar chunks importantes que devem sempre estar presentes
                for idx, row in df_embeddings.iterrows():
                    chunk_title = row['title']  # Renomear para evitar conflito com variável 'title' (Surface)
                    # Sempre incluir resumo geral e estatísticas agregadas/métricas principais
                    if 'Resumo Geral' in chunk_title or 'Estatísticas Agregadas' in chunk_title or 'Métricas Principais' in chunk_title:
                        if row['text'] not in context:  # Evitar duplicação
                            basic_info_chunks.append(f"### {chunk_title}\n{row['text']}")
                
                # Combinar informações básicas com contexto relevante
                if basic_info_chunks:
                    full_context = "\n\n".join(basic_info_chunks) + "\n\n" + context
                else:
                    full_context = context
                
                # Renderizar "gerando resposta"
                screen.fill((245, 247, 250))
                screen.blit(title, (20, 20))
                status_text = font_hint.render("⏳ Gerando resposta com Gemini...", True, (200, 150, 0))
                screen.blit(status_text, (20, 55))
                pygame.display.flip()
                
                # Limpar caracteres nulos e outros caracteres problemáticos do contexto
                def clean_text(text):
                    """Remove apenas caracteres nulos e outros caracteres de controle problemáticos, preservando Unicode válido."""
                    if not text:
                        return ""
                    # Remover caracteres nulos (\x00)
                    text = text.replace('\x00', '')
                    # Normalizar quebras de linha primeiro
                    text = text.replace('\r\n', '\n').replace('\r', '\n')
                    # Remover apenas caracteres de controle problemáticos (0x00-0x1F), mas preservar:
                    # - \n (0x0A) - quebra de linha
                    # - \t (0x09) - tabulação
                    # - Todos os caracteres Unicode válidos (>= 0x20 ou caracteres especiais)
                    cleaned = []
                    for char in text:
                        code = ord(char)
                        # Manter caracteres imprimíveis (>= 0x20), quebras de linha, tabs
                        # E também caracteres Unicode válidos (incluindo acentos, emojis, etc.)
                        if code >= 0x20 or char in '\n\t':
                            cleaned.append(char)
                        # Substituir outros caracteres de controle por espaço (exceto \n e \t)
                        elif code < 0x20 and char not in '\n\t':
                            cleaned.append(' ')
                    return ''.join(cleaned)
                
                full_context_clean = clean_text(full_context)
                
                # Preparar JSON completo (como no relatório)
                import json
                try:
                    json_data = json.dumps(analyzer.solution_data, indent=2, ensure_ascii=False)
                    json_data_clean = clean_text(json_data)
                    # Limitar tamanho do JSON se muito grande (Gemini tem limite de tokens)
                    if len(json_data_clean) > 50000:  # ~50KB
                        # Manter apenas partes essenciais
                        solution_data_summary = {
                            'metadata': analyzer.solution_data.get('metadata', {}),
                            'solution': {
                                'aggregate_stats': analyzer.solution_data.get('solution', {}).get('aggregate_stats', {}),
                                'routes_count': len(analyzer.solution_data.get('solution', {}).get('routes', [])),
                                'routes': analyzer.solution_data.get('solution', {}).get('routes', [])[:5]  # Primeiras 5 rotas
                            }
                        }
                        json_data_clean = clean_text(json.dumps(solution_data_summary, indent=2, ensure_ascii=False))
                except Exception as e:
                    json_data_clean = f"Erro ao serializar JSON: {str(e)}"
                
                # Gerar resposta
                model = genai.GenerativeModel(analyzer.generation_model)
                
                prompt = textwrap.dedent(f"""
                Você é um assistente especializado em análise de soluções de roteamento e logística.
                
                Use APENAS as informações fornecidas abaixo para responder à pergunta do usuário.
                
                CONTEXTO RELEVANTE (chunks mais importantes):
                {full_context_clean}
                
                DADOS COMPLETOS DA SOLUÇÃO (JSON):
                {json_data_clean}
                
                PERGUNTA DO USUÁRIO: {pending_query}
                
                INSTRUÇÕES IMPORTANTES:
                - Responda APENAS com base nas informações fornecidas acima
                - Use os dados do JSON completo para informações detalhadas
                - Use o contexto relevante para informações resumidas
                - Se encontrar informações nos dados, responda com os valores EXATOS mencionados
                - Se não encontrar a informação, diga claramente "Não tenho essa informação disponível"
                - Responda em português de forma direta, clara e precisa
                - Use números e valores exatos dos dados, não invente ou assuma valores
                """).strip()
                
                # Limpar o prompt também (remover caracteres nulos)
                prompt = clean_text(prompt)
                
                response = model.generate_content(prompt)
                
                if response and response.text:
                    # Limpar apenas caracteres nulos da resposta, preservando formatação e caracteres especiais
                    response_text = response.text.replace('\x00', '')
                    # Normalizar quebras de linha
                    response_text = response_text.replace('\r\n', '\n').replace('\r', '\n')
                    messages.append(('assistant', response_text))
                else:
                    messages.append(('assistant', "❌ Resposta vazia recebida da API"))
                
            except Exception as e:
                error_msg = str(e)
                # Truncar mensagens de erro muito longas
                if len(error_msg) > 200:
                    error_msg = error_msg[:200] + "..."
                messages.append(('assistant', f"❌ Erro: {error_msg}"))
            
            pending_query = None
            waiting_response = False
            # Scroll para mostrar a última mensagem (calcular altura total real)
            total_height = 0
            for role, text in messages:
                # Calcular altura real da mensagem
                words = text.split(' ')
                lines = []
                current_line = []
                current_width = 0
                max_width = msg_area_w_temp - 100
                
                for word in words:
                    # Usar render temporário para calcular largura
                    word_surface = font_msg.render(word + ' ', True, (0, 0, 0))
                    word_width = word_surface.get_width()
                    if current_width + word_width > max_width and current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_width = word_width
                    else:
                        current_line.append(word)
                        current_width += word_width
                if current_line:
                    lines.append(' '.join(current_line))
                total_height += len(lines) * 25 + 30
            
            # Scroll para mostrar a última mensagem, mantendo um pouco de espaço no final
            scroll_offset = max(0, total_height - msg_area_h_temp + 20)
        
        # Render
        screen.fill((245, 247, 250))
        
        # Área de mensagens
        msg_area_y = 80
        msg_area_h = HEIGHT - 200
        msg_area_w = WIDTH - 60  # Deixar espaço para barra de rolagem
        
        # Título
        title = font_title.render("Chat com LLM - Análise de Solução", True, (40, 45, 55))
        screen.blit(title, (20, 20))
        
        # Status
        if df_embeddings is None:
            status_color = RED
        else:
            status_color = GREEN if not waiting_response else (200, 150, 0)
        status_text = font_hint.render(current_status, True, status_color)
        screen.blit(status_text, (20, 55))
        
        # Mensagens
        y = msg_area_y - scroll_offset
        for role, text in messages:
            if y > msg_area_y + msg_area_h:
                break
            if y < msg_area_y - 50:
                y += 100
                continue
            
            is_user = (role == 'user')
            bg_color = (220, 235, 250) if is_user else WHITE
            text_color = (40, 45, 55) if is_user else (70, 75, 85)
            
            # Quebrar texto em linhas, respeitando quebras de linha originais
            # Primeiro, dividir por quebras de linha explícitas
            paragraphs = text.split('\n')
            lines = []
            
            for para in paragraphs:
                if not para.strip():
                    # Linha vazia
                    lines.append('')
                    continue
                
                # Quebrar parágrafo em palavras
                words = para.split(' ')
                current_line = []
                current_width = 0
                max_width = msg_area_w - 100  # Largura máxima da mensagem
                
                for word in words:
                    # Renderizar palavra para calcular largura (usar encoding correto)
                    try:
                        word_surface = font_msg.render(word + ' ', True, text_color)
                        word_width = word_surface.get_width()
                    except Exception:
                        # Se falhar, usar largura estimada
                        word_width = len(word) * 8
                    
                    if current_width + word_width > max_width and current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_width = word_width
                    else:
                        current_line.append(word)
                        current_width += word_width
                
                if current_line:
                    lines.append(' '.join(current_line))
            
            # Renderizar mensagem
            msg_h = len(lines) * 25 + 20
            msg_w = max_width + 20
            
            # Posicionamento: usuário à direita, assistente à esquerda
            if is_user:
                # Mensagem do usuário alinhada à direita
                msg_x = WIDTH - 30 - msg_w
            else:
                # Mensagem do assistente alinhada à esquerda
                msg_x = 30
            
            msg_rect = pygame.Rect(msg_x, y, msg_w, msg_h)
            pygame.draw.rect(screen, bg_color, msg_rect, border_radius=12)
            pygame.draw.rect(screen, (200, 205, 210), msg_rect, width=1, border_radius=12)
            
            for i, line in enumerate(lines):
                if line:  # Só renderizar se não for linha vazia
                    try:
                        line_surface = font_msg.render(line, True, text_color)
                        screen.blit(line_surface, (msg_rect.x + 10, msg_rect.y + 10 + i * 25))
                    except Exception as e:
                        # Se falhar ao renderizar, tentar renderizar sem caracteres problemáticos
                        try:
                            # Remover caracteres que podem causar problemas
                            safe_line = ''.join(c for c in line if c.isprintable() or c in ' \n\t')
                            line_surface = font_msg.render(safe_line, True, text_color)
                            screen.blit(line_surface, (msg_rect.x + 10, msg_rect.y + 10 + i * 25))
                        except:
                            # Se ainda falhar, renderizar mensagem de erro
                            error_surface = font_msg.render(f"[Erro ao renderizar linha]", True, RED)
                            screen.blit(error_surface, (msg_rect.x + 10, msg_rect.y + 10 + i * 25))
            
            y += msg_h + 10
        
        # Calcular altura total das mensagens para barra de rolagem
        total_messages_height = 0
        for role, text in messages:
            # Usar a mesma lógica de quebra de texto que na renderização
            paragraphs = text.split('\n')
            lines = []
            
            for para in paragraphs:
                if not para.strip():
                    lines.append('')
                    continue
                
                words = para.split(' ')
                current_line = []
                current_width = 0
                max_width = msg_area_w - 100
                
                for word in words:
                    try:
                        word_surface = font_msg.render(word + ' ', True, (0, 0, 0))
                        word_width = word_surface.get_width()
                    except Exception:
                        word_width = len(word) * 8
                    
                    if current_width + word_width > max_width and current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_width = word_width
                    else:
                        current_line.append(word)
                        current_width += word_width
                
                if current_line:
                    lines.append(' '.join(current_line))
            
            total_messages_height += len(lines) * 25 + 30
        
        # Desenhar barra de rolagem se necessário
        if total_messages_height > msg_area_h:
            scrollbar_x = WIDTH - 18
            scrollbar_w = 8
            scrollbar_h = msg_area_h
            scrollbar_y = msg_area_y
            
            # Calcular posição do thumb
            max_scroll = max(1, total_messages_height - msg_area_h)
            scroll_ratio = min(1.0, scroll_offset / max_scroll) if max_scroll > 0 else 0
            thumb_height = max(20, int(msg_area_h * (msg_area_h / total_messages_height)))
            thumb_y = scrollbar_y + int(scroll_ratio * (scrollbar_h - thumb_height))
            
            # Desenhar trilha da barra
            pygame.draw.rect(screen, (220, 225, 230), 
                           (scrollbar_x, scrollbar_y, scrollbar_w, scrollbar_h), 
                           border_radius=4)
            # Desenhar thumb
            pygame.draw.rect(screen, (150, 160, 170), 
                           (scrollbar_x, thumb_y, scrollbar_w, thumb_height), 
                           border_radius=4)
        
        if waiting_response:
            # Mostrar indicador animado
            dots = "." * ((pygame.time.get_ticks() // 500) % 4)
            waiting_text = font_hint.render(f"⏳ Gerando resposta{dots}", True, (200, 150, 0))
            screen.blit(waiting_text, (30, y))
            y += 30
        
        # Input
        input_rect = pygame.Rect(20, HEIGHT - 100, WIDTH - 40, 60)
        pygame.draw.rect(screen, WHITE, input_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), input_rect, width=1, border_radius=12)
        
        if input_active:
            input_display = input_text + ("|" if pygame.time.get_ticks() % 1000 < 500 else "")
        else:
            input_display = input_text
        
        if input_display:
            input_surface = font_input.render(input_display, True, (40, 45, 55))
            screen.blit(input_surface, (input_rect.x + 15, input_rect.y + 15))
        else:
            placeholder = font_hint.render("Digite sua pergunta...", True, (150, 155, 165))
            screen.blit(placeholder, (input_rect.x + 15, input_rect.y + 20))
        
        # Hint
        hint_text = "Enter enviar • Esc sair • Ctrl+V colar" if not waiting_response else "Aguarde resposta..."
        hint = font_hint.render(hint_text, True, (120, 125, 135))
        screen.blit(hint, (20, HEIGHT - 30))
        
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
