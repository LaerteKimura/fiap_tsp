import os
import pygame
from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN,
    K_ESCAPE, K_UP, K_DOWN, K_RETURN, K_KP_ENTER
)
from typing import Optional

from config import WHITE
from views.analyze_view import _open_pdf, REPORTS_DIR


def show_open_report_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> Optional[str]:
    """Mostra menu para selecionar e abrir relatório PDF existente."""
    WIDTH, HEIGHT = screen.get_size()
    
    font_title = pygame.font.SysFont("Segoe UI", 28, bold=True)
    font_item = pygame.font.SysFont("Segoe UI", 16)
    font_hint = pygame.font.SysFont("Segoe UI", 14)
    
    # Criar pasta reports se não existir
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
    
    # Buscar arquivos PDF na pasta reports
    pdf_files = []
    if os.path.exists(REPORTS_DIR):
        pdf_files = [f for f in os.listdir(REPORTS_DIR) if f.endswith('.pdf')]
        # Ordenar por data de modificação (mais recentes primeiro)
        pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(REPORTS_DIR, x)), reverse=True)
        # Adicionar caminho completo
        pdf_files = [os.path.join(REPORTS_DIR, f) for f in pdf_files]
    
    if not pdf_files:
        # Mostrar mensagem de erro
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return None
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return None
                if event.type == MOUSEBUTTONDOWN:
                    return None
            
            screen.fill((245, 247, 250))
            
            card_w = 600
            card_h = 300
            card_x = (WIDTH - card_w) // 2
            card_y = (HEIGHT - card_h) // 2
            
            pygame.draw.rect(screen, (210, 215, 220), (card_x + 4, card_y + 4, card_w, card_h), border_radius=16)
            pygame.draw.rect(screen, WHITE, (card_x, card_y, card_w, card_h), border_radius=16)
            pygame.draw.rect(screen, (200, 205, 210), (card_x, card_y, card_w, card_h), width=1, border_radius=16)
            
            title = font_title.render("Nenhum Relatório Encontrado", True, (40, 45, 55))
            screen.blit(title, (card_x + 30, card_y + 30))
            
            msg = font_item.render(f"Nenhum relatório PDF encontrado na pasta {REPORTS_DIR}", True, (70, 75, 85))
            screen.blit(msg, (card_x + 30, card_y + 120))
            
            hint = font_hint.render("Pressione Esc ou clique para voltar", True, (120, 125, 135))
            screen.blit(hint, (card_x + 30, card_y + card_h - 50))
            
            pygame.display.flip()
            clock.tick(60)
    
    selected = 0
    scroll_offset = 0
    items_per_page = 8
    
    while True:
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                elif event.key == K_UP:
                    selected = max(0, selected - 1)
                elif event.key == K_DOWN:
                    selected = min(len(pdf_files) - 1, selected + 1)
                elif event.key in (K_RETURN, K_KP_ENTER):
                    if pdf_files[selected] and os.path.exists(pdf_files[selected]):
                        _open_pdf(pdf_files[selected])
                        return pdf_files[selected]
            
            if event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, min(scroll_offset - event.y * 20, 
                                         max(0, len(pdf_files) - items_per_page) * 50))
            
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Verificar clique nos itens da lista
                list_y = card_y + 90
                item_height = 50
                for i in range(len(pdf_files)):
                    item_y = list_y + i * item_height - scroll_offset
                    if list_y <= item_y <= list_y + (card_h - 180):
                        item_rect = pygame.Rect(card_x + 30, item_y, card_w - 60, item_height - 5)
                        if item_rect.collidepoint(event.pos):
                            selected = i
                            # Duplo clique ou clique simples abre o arquivo
                            if pdf_files[selected] and os.path.exists(pdf_files[selected]):
                                _open_pdf(pdf_files[selected])
                                return pdf_files[selected]
                
                # Verificar clique nos botões
                continue_rect = pygame.Rect(card_x + card_w - 200, card_y + card_h - 70, 170, 46)
                back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, 170, 46)
                
                if continue_rect.collidepoint(event.pos):
                    if pdf_files[selected] and os.path.exists(pdf_files[selected]):
                        _open_pdf(pdf_files[selected])
                        return pdf_files[selected]
                elif back_rect.collidepoint(event.pos):
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
        title = font_title.render("Abrir Relatório PDF", True, (40, 45, 55))
        screen.blit(title, (card_x + 30, card_y + 30))
        
        # Lista de arquivos
        list_y = card_y + 90
        list_h = card_h - 180
        item_height = 50
        
        # Ajustar scroll baseado na seleção
        visible_start = scroll_offset // item_height
        if selected < visible_start:
            scroll_offset = selected * item_height
        elif selected >= visible_start + items_per_page:
            scroll_offset = (selected - items_per_page + 1) * item_height
        
        for i in range(len(pdf_files)):
            item_y = list_y + i * item_height - scroll_offset
            
            if item_y < list_y or item_y > list_y + list_h:
                continue
            
            item_rect = pygame.Rect(card_x + 30, item_y, card_w - 60, item_height - 5)
            is_selected = (i == selected)
            is_hover = item_rect.collidepoint(mx, my)
            
            # Atualizar seleção ao passar o mouse
            if is_hover and not is_selected:
                pass  # Não mudar seleção automaticamente, apenas destacar
            
            bg_color = (220, 235, 250) if is_selected else ((235, 240, 246) if is_hover else WHITE)
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=8)
            
            if is_selected:
                pygame.draw.rect(screen, (30, 90, 160), item_rect, width=2, border_radius=8)
            
            # Nome do arquivo
            filename = os.path.basename(pdf_files[i])
            file_text = font_item.render(filename, True, (40, 45, 55) if is_selected else (70, 75, 85))
            screen.blit(file_text, (item_rect.x + 15, item_rect.centery - file_text.get_height() // 2))
        
        # Botões
        continue_rect = pygame.Rect(card_x + card_w - 200, card_y + card_h - 70, 170, 46)
        back_rect = pygame.Rect(card_x + 30, card_y + card_h - 70, 170, 46)
        
        # Botão Abrir
        continue_hover = continue_rect.collidepoint(mx, my)
        continue_bg = (220, 235, 250) if continue_hover else (245, 247, 250)
        pygame.draw.rect(screen, continue_bg, continue_rect, border_radius=12)
        pygame.draw.rect(screen, (30, 90, 160), continue_rect, width=1, border_radius=12)
        continue_txt = font_item.render("Abrir >", True, (30, 90, 160))
        screen.blit(continue_txt, continue_txt.get_rect(center=continue_rect.center))
        
        # Botão Voltar
        back_hover = back_rect.collidepoint(mx, my)
        back_bg = (235, 240, 246) if back_hover else (245, 247, 250)
        pygame.draw.rect(screen, back_bg, back_rect, border_radius=12)
        pygame.draw.rect(screen, (200, 205, 210), back_rect, width=1, border_radius=12)
        back_txt = font_item.render("< Voltar", True, (70, 75, 85))
        screen.blit(back_txt, back_txt.get_rect(center=back_rect.center))
        
        # Hint
        hint = font_hint.render("↑↓ ou mouse • Enter abrir • Esc voltar", True, (120, 125, 135))
        screen.blit(hint, (card_x + 30, card_y + card_h - 25))
        
        pygame.display.flip()
        clock.tick(60)
