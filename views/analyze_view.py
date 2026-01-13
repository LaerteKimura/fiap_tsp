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

# Pastas para organizar arquivos
SOLUTIONS_DIR = "solutions"
REPORTS_DIR = "reports"


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
    """Solicita chave API do Gemini em tela."""
    WIDTH, HEIGHT = screen.get_size()
    
    font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_label = pygame.font.SysFont("Segoe UI", 16)
    font_input = pygame.font.SysFont("Segoe UI", 18)
    font_hint = pygame.font.SysFont("Segoe UI", 14)
    
    api_key = ""
    active = True
    cursor_visible = True
    cursor_timer = 0
    
    # Inicializar scrap (clipboard) do pygame
    try:
        pygame.scrap.init()
        pygame.scrap.set_mode(pygame.SCRAP_TEXT)
    except:
        pass  # Scrap pode não estar disponível em todos os sistemas
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                elif event.key == K_BACKSPACE:
                    if active:
                        api_key = api_key[:-1]
                elif event.key in (K_RETURN, K_KP_ENTER):
                    if api_key.strip():
                        return api_key.strip()
                elif event.key == K_TAB:
                    continue
                elif event.key == ord('v') and (pygame.key.get_mods() & KMOD_CTRL):
                    # Ctrl+V para colar
                    if active:
                        clipboard_text = None
                        # Tentar usar pygame.scrap primeiro
                        try:
                            scrap_text = pygame.scrap.get(pygame.SCRAP_TEXT)
                            if scrap_text:
                                clipboard_text = scrap_text.decode('utf-8', errors='ignore').strip()
                        except:
                            pass
                        
                        # Fallback: tentar usar pyperclip se disponível
                        if not clipboard_text:
                            try:
                                import pyperclip  # type: ignore
                                clipboard_text = pyperclip.paste()
                                if clipboard_text:
                                    clipboard_text = clipboard_text.strip()
                            except ImportError:
                                pass
                        
                        if clipboard_text:
                            # Remove caracteres de controle, mantém apenas caracteres imprimíveis e espaços
                            clipboard_text = ''.join(c for c in clipboard_text if c.isprintable() or c == ' ')
                            api_key = clipboard_text
                else:
                    if event.unicode and active:
                        api_key += event.unicode
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                input_rect = pygame.Rect(card_x + 30, card_y + 120, card_w - 60, 50)
                continue_rect = pygame.Rect(card_x + card_w - 200, card_y + card_h - 70, 170, 46)
                back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, 170, 46)
                
                if input_rect.collidepoint(mx, my):
                    active = True
                elif continue_rect.collidepoint(mx, my):
                    if api_key.strip():
                        return api_key.strip()
                elif back_rect.collidepoint(mx, my):
                    return None
        
        # Toggle cursor
        cursor_timer += clock.get_time()
        if cursor_timer > 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        
        # Render
        screen.fill((245, 247, 250))
        
        # Card
        card_w = 700
        card_h = 300
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2
        
        pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)
        
        # Título
        title = font_title.render("Chave API do Gemini", True, (40, 45, 55))
        screen.blit(title, (card_x + 30, card_y + 30))
        
        # Label
        label = font_label.render("Digite sua chave API do Gemini:", True, (90, 95, 105))
        screen.blit(label, (card_x + 30, card_y + 90))
        
        # Input
        input_rect = pygame.Rect(card_x + 30, card_y + 120, card_w - 60, 50)
        border_color = (30, 90, 160) if active else (200, 205, 210)
        pygame.draw.rect(screen, GRAY, input_rect, border_radius=8)
        pygame.draw.rect(screen, border_color, input_rect, width=2, border_radius=8)
        
        # Texto do input (mascarado)
        display_text = "*" * len(api_key) if api_key else ""
        input_surface = font_input.render(display_text, True, BLACK)
        screen.blit(input_surface, (input_rect.x + 10, input_rect.centery - input_surface.get_height() // 2))
        
        # Cursor
        if active and cursor_visible:
            cursor_x = input_rect.x + 10 + input_surface.get_width()
            pygame.draw.line(screen, BLACK, (cursor_x, input_rect.y + 10), (cursor_x, input_rect.y + 40), 2)
        
        # Botões
        continue_rect = pygame.Rect(card_x + card_w - 200, card_y + card_h - 70, 170, 46)
        back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, 170, 46)
        
        mx, my = pygame.mouse.get_pos()
        
        # Botão Continuar
        continue_hover = continue_rect.collidepoint(mx, my)
        continue_bg = (220, 235, 250) if continue_hover else (245, 247, 250)
        pygame.draw.rect(screen, continue_bg, continue_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 90, 160), continue_rect, width=1, border_radius=12)
        continue_txt = font_label.render("Continuar >", True, (30, 90, 160))
        screen.blit(continue_txt, continue_txt.get_rect(center=continue_rect.center))
        
        # Botão Voltar
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_label.render("< Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))
        
        # Hint
        hint = font_hint.render("Digite a chave e pressione Enter ou clique em Continuar", True, (120, 125, 135))
        screen.blit(hint, (card_x + 30, card_y + card_h - 25))
        
        pygame.display.flip()
        clock.tick(60)


def show_file_selection(screen: pygame.Surface, clock: pygame.time.Clock, json_files: list) -> Optional[str]:
    """Mostra lista de arquivos JSON para seleção em tela."""
    WIDTH, HEIGHT = screen.get_size()
    
    font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_item = pygame.font.SysFont("Segoe UI", 16)
    font_hint = pygame.font.SysFont("Segoe UI", 14)
    
    selected = 0
    scroll_offset = 0
    items_per_page = 8
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            
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
                scroll_offset = max(0, min(scroll_offset - event.y * 20, 
                                         max(0, len(json_files) - items_per_page) * 50))
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                continue_rect = pygame.Rect(card_x + card_w - 200, card_y + card_h - 70, 170, 46)
                back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, 170, 46)
                
                if continue_rect.collidepoint(mx, my):
                    return json_files[selected]
                elif back_rect.collidepoint(mx, my):
                    return None
        
        # Render
        screen.fill((245, 247, 250))
        
        # Card
        card_w = 800
        card_h = 500
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2
        
        pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=16)
        pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)
        
        # Título
        title = font_title.render("Selecionar Arquivo de Solução", True, (40, 45, 55))
        screen.blit(title, (card_x + 30, card_y + 30))
        
        # Lista de arquivos
        list_y = card_y + 90
        list_h = card_h - 180
        list_rect = pygame.Rect(card_x + 30, list_y, card_w - 60, list_h)
        
        # Ajustar scroll baseado na seleção
        item_height = 50
        visible_start = scroll_offset // item_height
        if selected < visible_start:
            scroll_offset = selected * item_height
        elif selected >= visible_start + items_per_page:
            scroll_offset = (selected - items_per_page + 1) * item_height
        
        mx, my = pygame.mouse.get_pos()
        
        for i in range(len(json_files)):
            item_y = list_y + i * item_height - scroll_offset
            
            if item_y < list_y or item_y > list_y + list_h:
                continue
            
            item_rect = pygame.Rect(card_x + 30, item_y, card_w - 60, item_height - 5)
            is_selected = (i == selected)
            is_hover = item_rect.collidepoint(mx, my)
            
            if is_hover:
                selected = i
            
            bg_color = (220, 235, 250) if is_selected else ((235, 240, 246) if is_hover else WHITE)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=8)
            
            if is_selected:
                pygame.draw.rect(screen, (30, 90, 160), item_rect, width=2, border_radius=8)
            
            # Nome do arquivo
            file_text = font_item.render(json_files[i], True, (40, 45, 55) if is_selected else (70, 75, 85))
            screen.blit(file_text, (item_rect.x + 15, item_rect.centery - file_text.get_height() // 2))
        
        # Botões
        continue_rect = pygame.Rect(card_x + card_w - 200, card_y + card_h - 70, 170, 46)
        back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, 170, 46)
        
        # Botão Continuar
        continue_hover = continue_rect.collidepoint(mx, my)
        continue_bg = (220, 235, 250) if continue_hover else (245, 247, 250)
        pygame.draw.rect(screen, continue_bg, continue_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 90, 160), continue_rect, width=1, border_radius=12)
        continue_txt = font_item.render("Continuar >", True, (30, 90, 160))
        screen.blit(continue_txt, continue_txt.get_rect(center=continue_rect.center))
        
        # Botão Voltar
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_item.render("< Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))
        
        # Hint
        hint = font_hint.render("↑↓ ou mouse • Enter confirmar • Esc voltar", True, (120, 125, 135))
        screen.blit(hint, (card_x + 30, card_y + card_h - 25))
        
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
