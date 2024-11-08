import pygame

class Button:
    def __init__(self, x, y, width, height, fg, content, fontsize, image_path='assets\img\GenericButton.png', image_path_hover='assets\img\GenericButtonActive.png'):
        # Define a fonte e outras variáveis
        self.font = pygame.font.Font('assets/fonts/PixelifySans-Regular.ttf', fontsize)  # Fonte do texto
        self.content = content
        self.fg = fg
        self.image_path = image_path  # Caminho para a imagem normal
        self.image_path_hover = image_path_hover  # Caminho para a imagem de hover

        # Rect do botão
        self.rect = pygame.Rect(x, y, width, height)

        # Carregar a imagem normal e a imagem de hover
        self.image = pygame.image.load(self.image_path)  # Carregar a imagem normal
        self.image = pygame.transform.scale(self.image, (width, height))  # Redimensionar a imagem para o tamanho do botão

        self.image_hover = pygame.image.load(self.image_path_hover)  # Carregar a imagem de hover
        self.image_hover = pygame.transform.scale(self.image_hover, (width, height))  # Redimensionar a imagem de hover

        self.current_image = self.image  # Inicializa com a imagem normal

    def draw(self, screen):
        # Desenhar o botão com a imagem selecionada
        screen.blit(self.current_image, self.rect.topleft)

        # Renderiza o texto centralizado no botão
        text = self.font.render(self.content, True, self.fg)
        text_rect = text.get_rect()  # Pega o retângulo do texto sem centralizar
        text_rect.centerx = self.rect.centerx  # Centraliza horizontalmente
        text_rect.centery = self.rect.centery - 5  # Centraliza verticalmente

        screen.blit(text, text_rect)


    def update(self, mouse_pos):
        # Altera a imagem do botão se o mouse estiver sobre ele
        if self.rect.collidepoint(mouse_pos):
            self.current_image = self.image_hover  # Muda para a imagem de hover
        else:
            self.current_image = self.image  # Muda para a imagem normal

    def is_pressed(self, pos, pressed):
        # Verifica se o botão foi clicado
        return self.rect.collidepoint(pos) and pressed[0]
    
class hub:
    def __init__(self, x, y, slot_size, max_slots, type_hub):
        self.x = x  # Posição horizontal do inventário
        self.y = y  # Posição vertical do inventário
        self.slot_size = slot_size  # Tamanho de cada slot no inventário
        self.max_slots = max_slots  # Número máximo de slots no inventário
        self.items = []  # Lista para armazenar os itens do inventário

        # Imagem do slot (pode ser um fundo para os itens)
        self.slot_image = pygame.image.load('assets/img/HotbarSkillBackground1.png')
        self.slot_image = pygame.transform.scale(self.slot_image, (slot_size, slot_size))

        # Define o layout ('horizontal' ou 'vertical')
        self.type_hub = type_hub

    def add_item(self, item_name, item_image_path, max_level=5):
        # Verifica se o item já está no inventário
        for item in self.items:
            if item['name'] == item_name:
                # Se o item já está no inventário, aumenta o nível até o limite
                if item['level'] < max_level:
                    item['level'] += 1
                return

        # Se o item não está no inventário e há espaço, adiciona
        if len(self.items) < self.max_slots:
            item_image = pygame.image.load(item_image_path)
            item_image = pygame.transform.scale(item_image, (self.slot_size - 10, self.slot_size - 10))
            self.items.append({'name': item_name, 'image': item_image, 'level': 1, 'max_level': max_level})

    def draw(self, screen):
        # Desenha cada slot do inventário
        for i in range(self.max_slots):
            # Ajusta o posicionamento dos slots com base no tipo de hub
            if self.type_hub == 'inventory':
                slot_x = self.x + i * (self.slot_size + 5)
                slot_y = self.y
            if self.type_hub == 'skills_hub':
                slot_x = self.x
                slot_y = self.y + i * (self.slot_size + 5)

            screen.blit(self.slot_image, (slot_x, slot_y))

            # Se houver um item neste slot, desenha ele e seu nível
            if i < len(self.items):
                item_x = slot_x + (self.slot_size - self.items[i]['image'].get_width()) // 2
                item_y = slot_y + (self.slot_size - self.items[i]['image'].get_height()) // 2
                screen.blit(self.items[i]['image'], (item_x, item_y))

                # Exibir o nível do item
                font = pygame.font.Font(None, 24)
                level_text = font.render(f"Nv. {self.items[i]['level']}", True, pygame.Color('white'))
                screen.blit(level_text, (item_x, item_y - 10))

            if self.type_hub == 'inventory':
                if i == self.selected_item_index:
                    pygame.draw.rect(screen, pygame.Color('yellow'), (slot_x, slot_y, self.slot_size, self.slot_size), 3)

class Inventory(hub):
    def __init__(self, x, y, slot_size, max_slots):
        super().__init__(x, y, slot_size, max_slots, type_hub="inventory")
        self.selected_item_index = 0

    def selection_event(self, event):
        # Verifica se uma tecla numérica foi pressionada
        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key <= pygame.K_9:
                slot_num = event.key - pygame.K_1  # Converte tecla para índice de slot
                if 0 <= slot_num < self.max_slots:
                    self.selected_item_index = slot_num if slot_num < len(self.items) else None

class Skills_hub(hub):
    def __init__(self, x, y, slot_size, max_slots):
        super().__init__(x, y, slot_size, max_slots, type_hub='skills_hub')