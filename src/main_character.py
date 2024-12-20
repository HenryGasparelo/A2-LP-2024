"""Módulo que define a classe Player, representando o personagem principal do jogo."""

import pygame
import math
import random
import config
import repositorio_sprites as rs
from items_abilities import *

class Player(pygame.sprite.Sprite):
    """
    Representa o personagem principal do jogo, e todos os seus métodos
    """
    def __init__(self, game, x, y):
        """
        Inicializa uma nova instância da classe `Player`.
        
        Args:
        game (object): Referência à instância do jogo que contém informações sobre o estado do jogo e gerencia os elementos do mundo.
        x (int): Coordenada x de posição inicial do jogador.
        y (int): Coordenada y de posição inicial do jogador.
        """
        # Define propriedades do jogador, como camada e grupo de sprites
        self.game= game
        self._layer = config.layers["player_layer"]
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        
        # Define propriedades que serão essencias para o jogador
        self.speed = config.player_speed
        self.health = config.max_health["player"]
        self.max_health = config.max_health["player"]
        self.low_life = False
        self.heart_beating = False
        self.level = 1
        self.xp = 0
        self.enemies = []
        self.damage = False
        self.damage_time = 0
        self.damage_index = 0
        self.damage_sound = False
        self.death = False
        self.death_time = 0
        self.death_index = 0
        self.game_over_sound = False
        self.attacking = False
        self.attack_time = 0

        # Define tamanho e posicao do jogador
        self.x = x * config.tilesize
        self.y = y * config.tilesize
        self.width = config.tilesize
        self.height = config.tilesize

        # Define a variacao da posicao do jogador nos eixos, inicial igual a 0
        self.x_change = 0
        self.y_change = 0

        # Define para onde ele olha e o estado da animacao, inicial igual para baixo e 1, respectivamente
        self.facing = "down"
        self.animation_loop = 1

        # Define a imagem inicial do jogador e ajusta o tamanho dele com a tela
        self.image = self.game.sprites.warrior_animations["walk_animations"]["walk_down_animations"][0]
        # Define posicoes do retangulo do jogador
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        

    # Atualiza todas as propriedades do jogador, como movimento, animacao, mudanca de posicao e colisao
    def update(self):
        """Atualiza o estado do jogador a cada ciclo do jogo."""

        # Se tiver morto ou receber dano, ativa as animações
        if self.death:
            self.death_animation()
        elif self.damage:
            self.damage_animation()
            
        else:
            # Atualiza a velocidade do jogador com os buffs
            self.speed = config.player_speed * (1 + self.game.buffs["speed"])
            # Atualiza o deslocamento do jogador e a câmera
            self.movement()
            # Atualiza as animações do jogador
            self.animate()
            # Verifica colisão com inimigos e ataques de inimigos
            self.collide_enemy()
            self.collide_enemy_attacks()
            
            # Atualiza a posição do jogador e colisão
            self.rect.x += self.x_change
            self.collide_blocks("x")
            self.rect.y += self.y_change
            self.collide_blocks("y")
            
            self.x_change = 0
            self.y_change = 0
            
            # Verifica se o jogador está com pouca vida ou se subiu de nível
            self.check_xp_level()
            self.check_low_life()
            
            # Atualiza a vida máxima do jogador
            self.max_health = config.max_health["player"] * (1 + self.game.buffs["life"])

    # Cria o movimento do jogador
    def movement(self):
        """Gerencia a movimentação do jogador com base nas entradas de controle."""

        # Para cada tecla que ele pressiona, define para onde o personagem vai olhar e a variacao da posicao, além de mover tudo na direção oposta para criar a câmera
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            for sprite in self.game.all_sprites:
                sprite.rect.x += self.speed
            self.x_change -= self.speed
            self.facing = "left"
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= self.speed
            self.x_change += self.speed
            self.facing = "right"
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            for sprite in self.game.all_sprites:
                sprite.rect.y += self.speed
            self.y_change -= self.speed
            self.facing = "up"
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            for sprite in self.game.all_sprites:
                sprite.rect.y -= self.speed
            self.y_change += self.speed
            self.facing = "down"
        
        #Caso for implementar o controle, uma base para a movimentação
        """
        # Inicializa o joystick (caso ainda não tenha sido iniciado)
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            # Obtém os valores dos eixos do joystick
            x_axis = joystick.get_axis(0)  # Eixo horizontal (esquerda/direita)
            y_axis = joystick.get_axis(1)  # Eixo vertical (cima/baixo)

            # Movimento do jogador com base no eixo analógico (ajuste o limiar de sensibilidade conforme necessário) DAVI
            if abs(x_axis) > 0.1:
                for sprite in self.game.all_sprites:
                    sprite.rect.x += x_axis * config_mod.player_speed
                self.x_change += x_axis * config_mod.player_speed
                self.facing = "left" if x_axis < 0 else "right"

            if abs(y_axis) > 0.1:
                for sprite in self.game.all_sprites:
                    sprite.rect.y += y_axis * config_mod.player_speed
                self.y_change += y_axis * config_mod.player_speed
                self.facing = "up" if y_axis < 0 else "down"
           """     

    # Ajusta a colisao
    def collide_blocks(self, direction):
        """
        Verifica colisões do jogador com blocos em uma direção específica.

        Args:
        direction (str): A direção em que a colisão deve ser verificada. Pode ser 'up', 'down', 'left' ou 'right', correspondendo às direções de movimento.
        """
        # Para cada direcao, se o personagem colide com o cenario, entao ajusta a posicao do jogador para fora do objeto colidido
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.collidable_sprites, False)
            if hits:
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                    # Ajusta a camera para nao ser modificada na colisao
                    for sprite in self.game.all_sprites:
                        sprite.rect.x += self.speed
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
                    # Ajusta a camera para nao ser modificada na colisao
                    for sprite in self.game.all_sprites:
                        sprite.rect.x -= self.speed
        
        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.collidable_sprites, False)
            if hits:
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                    # Ajusta a camera para nao ser modificada na colisao
                    for sprite in self.game.all_sprites:
                        sprite.rect.y += self.speed
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom
                    # Ajusta a camera para nao ser modificada na colisao
                    for sprite in self.game.all_sprites:
                        sprite.rect.y -= self.speed
        
                    
    def animate(self):
         """Atualiza a animação do jogador com base no estado atual do movimento."""

        # Colecao de todas as imagens de animacao do personagem principal
         [walk_down_animations, walk_up_animations, walk_right_animations, walk_left_animations] = self.game.sprites.warrior_animations["walk_animations"].values()

        # Para cada direcao que o personagem olha, ajusta a animacao correspondente e o tamanho da imagem
         if self.facing == "down":
             if self.y_change == 0:
                 self.image = walk_down_animations[0]
             else:
                 # Cria o loop de animacao
                 self.image = walk_down_animations[math.floor(self.animation_loop)]
                 # Ajusta a velocidade com que o loop ocorre nessa direcao
                 self.animation_loop += 0.2
                 if self.animation_loop >= (len(walk_down_animations) - 1):
                     self.animation_loop = 1
            
         if self.facing == "up":
             if self.y_change == 0:
                 self.image = walk_up_animations[0]
             else:
                 # Cria o loop de animacao
                 self.image = walk_up_animations[math.floor(self.animation_loop)]
                 # Ajusta a velocidade com que o loop ocorre nessa direcao
                 self.animation_loop += 0.2
                 if self.animation_loop >= (len(walk_up_animations) - 1):
                     self.animation_loop = 1
                     
         if self.facing == "right":
             if self.x_change == 0:
                 self.image = walk_right_animations[0]
             else:
                 # Cria o loop de animacao
                 self.image = walk_right_animations[math.floor(self.animation_loop)]
                 # Ajusta a velocidade com que o loop ocorre nessa direcao
                 self.animation_loop += 0.2
                 if self.animation_loop >= (len(walk_right_animations) - 1):
                     self.animation_loop = 1
                     
         if self.facing == "left":
             if self.x_change == 0:
                 self.image = walk_left_animations[0]
             else:
                 # Cria o loop de animacao
                 self.image = walk_left_animations[math.floor(self.animation_loop)]
                 # Ajusta a velocidade com que o loop ocorre nessa direcao
                 self.animation_loop += 0.2
                 if self.animation_loop >= (len(walk_left_animations) - 1):
                     self.animation_loop = 1
            
    def collide_enemy(self):
        """Verifica e trata colisões do jogador com inimigos.
        
         Este método interage com os sprites de inimigos no jogo para determinar se houve uma colisão e causar o dano no jogador.
        """

        # Verifica se o personagem colidiu com um inimigo
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            current_time = pygame.time.get_ticks()
            # Aplica um delay entre os danos
            if current_time - self.damage_time > config.damage_delay:
                # Ativa o dano e coleta as informações necessárias para contabilizar o dano
                self.damage = True
                self.damage_sound = True
                self.damage_index = 0
                self.damage_time = pygame.time.get_ticks()
                self.enemies = list(hits)
                
    def collide_enemy_attacks(self):
        """
        Verifica e trata colisões do jogador com ataques de inimigos.
        
        Este método interage com os sprites de ataques inimigos no jogo para determinar se houve uma colisão e causar o dano no jogador.
        """

        # Verifica se o personagem colidiu com um ataque inimigo
        hits = pygame.sprite.spritecollide(self, self.game.enemy_attacks, False)
        if hits:
            current_time = pygame.time.get_ticks()
            # Aplica um delay entre os danos
            if current_time - self.damage_time > config.damage_delay:
                # Ativa o dano e coleta as informações necessárias para contabilizar o dano
                self.damage = True
                self.damage_sound = True
                self.damage_index = 0
                self.damage_time = pygame.time.get_ticks()
                self.enemies = list(hits)
                
    def damage_animation(self):
        """
        Executa a animação de dano do jogador.
        
        Este método deve ser chamado quando o jogador colide com um inimigo ou um ataque inimigo, como uma forma de fornecer feedback visual sobre a vida do jogador.
        """
        # Para cada inimigo ou ataque colidido, remove da vida do jogador o dano do ataque, considerando os buffs
        for enemy in self.enemies:
            if enemy.class_ == "EnemyAttack":
                self.health -= config.damage["enemies_attack"][enemy.kind] * (1 - self.game.buffs["defense"]) * self.game.difficulty_ratio
                enemy.kill()
            elif enemy.class_ == "Enemy":
                self.health -= config.damage["enemies"][enemy.kind] * (1 - self.game.buffs["defense"]) * self.game.difficulty_ratio
        # Aplica o som de dano
        self.game.play_sound("warrior_hurt_sound", self.damage_sound)
        self.damage_sound = False
        # Aplica a animação de dano, considerando delay e direção do jogador
        [self.hurt_down_animations, self.hurt_up_animations, self.hurt_right_animations, self.hurt_left_animations] = self.game.sprites.warrior_animations["hurt_animations"].values()
        if self.facing == "down":
            current_time = pygame.time.get_ticks()
            if current_time - self.damage_time > 50:  # Troca de frame a cada 50ms
                self.damage_time = current_time
                self.damage_index = (self.damage_index + 1)
                if self.damage_index < len(self.hurt_down_animations):
                    self.image = self.hurt_down_animations[self.damage_index]
                else:
                    self.damage = False
                

        if self.facing == "up":
            current_time = pygame.time.get_ticks()
            if current_time - self.damage_time > 50:  # Troca de frame a cada 50ms
                self.damage_time = current_time
                self.damage_index = (self.damage_index + 1)
                if self.damage_index < len(self.hurt_up_animations):
                    self.image = self.hurt_up_animations[self.damage_index]
                else:
                    self.damage = False
               
        if self.facing == "right":
            current_time = pygame.time.get_ticks()
            if current_time - self.damage_time > 50:  # Troca de frame a cada 50ms
                self.damage_time = current_time
                self.damage_index = (self.damage_index + 1)
                if self.damage_index < len(self.hurt_right_animations):
                    self.image = self.hurt_right_animations[self.damage_index]
                else:
                    self.damage = False
                
        if self.facing == "left":
            current_time = pygame.time.get_ticks()
            if current_time - self.damage_time > 50:  # Troca de frame a cada 50ms
                self.damage_time = current_time
                self.damage_index = (self.damage_index + 1)
                if self.damage_index < len(self.hurt_left_animations):
                    self.image = self.hurt_left_animations[self.damage_index]
                else:
                    self.damage = False

    def death_animation(self):
        """
        Executa a animação de morte do jogador.
        
        Este método é chamado para fornecer um feedback visual claro de que o jogador morreu, antes de iniciar o processo de reinício ou exibição de uma tela de game over.
        """

        # Aplica o som de morte
        self.game.play_sound("game_over_sound", self.game_over_sound)
        self.game_over_sound = False
        
        # Aplica a animação de morte
        [self.death_down_animations, self.death_up_animations, self.death_right_animations, self.death_left_animations] = self.game.sprites.warrior_animations["death_animations"].values()
        if self.facing == "down":
            current_time = pygame.time.get_ticks()
            if current_time - self.death_time > 100: # Troca de frame a cada 100ms
                self.death_time = current_time
                self.death_index = (self.death_index + 1)
                if self.death_index < len(self.death_down_animations):
                    self.image = self.death_down_animations[self.death_index]  
                else:
                    # Mostra a tela de game over
                    self.game.draw()
                    self.game.game_over()

        if self.facing == "up":
            current_time = pygame.time.get_ticks()
            if current_time - self.death_time > 100:  # Troca de frame a cada 100ms
                self.death_time = current_time
                self.death_index = (self.death_index + 1)
                if self.death_index < len(self.death_up_animations):
                    self.image = self.death_up_animations[self.death_index]
                else:
                    # Mostra a tela de game over
                    self.game.draw()
                    self.game.game_over()
               
        if self.facing == "right":
            current_time = pygame.time.get_ticks()
            if current_time - self.death_time > 100:  # Troca de frame a cada 100ms
                self.death_time = current_time
                self.death_index = (self.death_index + 1)
                if self.death_index < len(self.death_right_animations):
                    self.image = self.death_right_animations[self.death_index]
                else:
                    # Mostra a tela de game over
                    self.game.draw()
                    self.game.game_over()
                
        if self.facing == "left":
            current_time = pygame.time.get_ticks()
            if current_time - self.death_time > 100:  # Troca de frame a cada 100ms
                self.death_time = current_time
                self.death_index = (self.death_index + 1)
                if self.death_index < len(self.death_left_animations):
                    self.image = self.death_left_animations[self.death_index]
                else:
                    # Mostra a tela de game over
                    self.game.draw()
                    self.game.game_over()
                    
    def atacar(self, game, x, y, item, position, level=1):
        """
        Executa um ataque do jogador.
        
        Args:
            game (object): Referência à instância do jogo que gerencia o estado do jogo e os elementos do mundo.
            x (int): Coordenada x da posição de ataque.
            y (int): Coordenada y da posição de ataque.
            item (object): O item ou alvo que o jogador está atacando.
            position (str): A posição ou direção do ataque, como "frente", "trás", "esquerda", "direita".
            level (int, opcional): O nível do ataque, com um valor padrão de 1.
        """
        # Invoca o ataque do jogador, considerando os buffs e delay
        if not self.attacking:
            self.attacking = True
            Attack(game, x, y, item, position, level)
            self.attack_time = pygame.time.get_ticks()
        else:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time > config.itens_delay[item] * (1 - self.game.buffs["firing_speed"]):
                self.attacking = False

        #Davi
        """
        if pygame.joystick.get_count()>0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()

            # Botão de ataque (por exemplo, o botão 0 que é geralmente o "A" no controle)
            attack_button = joystick.get_button(0)

            if attack_button and not self.attacking:
                self.attacking = True
                # Chama a função de ataque
                self.atacar(self.game, self.rect.centerx, self.rect.centery, "sword", self.facing)
                self.attack_time = pygame.time.get_ticks()
            """

    def check_xp_level(self):
        """Verifica e atualiza o nível do jogador com base na experiência acumulada."""
        # Verifica se o personagem subiu de nível
        if self.xp >= self.levels(self.level):
            self.xp = self.xp - self.levels(self.level)
            self.level += 1
            self.game.level_up = True
            
    def levels(self, level):
        """Define a experiência necessária para subir de nível.
        
        Args:
            level (int): O nível desejado para o jogador.

        Returns:
            int: Quantidade de xp para o level.
        """

        xp_level_1 = 200
        
        return int(xp_level_1*math.log(level + 1, 2))
        
    def check_low_life(self):
        """Verifica se a vida do jogador está abaixo de um determinado nível e realiza ações específicas."""
        # Verifica se a vida do jogador está baixa
        if (self.health / self.max_health) <= 0.2:
            self.low_life = True
        else:
            self.low_life = False
            
        # Se estiver toca o som de coracao batendo
        if not self.heart_beating and self.low_life:
            self.game.sounds.all_sounds["low_life"].play(loops=-1)
            self.heart_beating = True
            
        if self.heart_beating and not self.low_life:
            self.game.sounds.all_sounds["low_life"].stop()
            self.heart_beating = False
            
        
                
class Attack(pygame.sprite.Sprite):
    """Representa um ataque no jogo, que pode ser disparado pelo jogador."""

    def __init__(self, game, x, y, item, position, level):
        """
        Inicializa uma nova instância da classe `Attack`.

        Args:
            game (object): Referência à instância do jogo que contém informações sobre o estado do jogo e gerencia os elementos do mundo.
            x (int): Coordenada x da posição inicial do ataque.
            y (int): Coordenada y da posição inicial do ataque.
            item (str): Tipo de item que está sendo usado para o ataque (por exemplo, 'demon_sword', 'energy_ball').
            position (str): Direção em que o ataque é disparado, seguindo a direção do mouse.
            level (int): Nível do ataque, que pode determinar sua força ou características adicionais.
        """
        
        # Define propriedades do ataque
        self.game = game
        self._layer = config.layers["player_layer"]
        self.groups = self.game.all_sprites, self.game.attacks
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.item = item
        self.level = level
        self.animation_speed = config.item_animation_speed[self.item]
        self.count_enemies = 0
        self.attack_sound = True
        
        # Define a imagem inicial do ataque
        keys_animations = list(self.game.sprites.attack_animations[self.item].keys())
        self.image = self.game.sprites.attack_animations[self.item][keys_animations[0]][0]
        
        # Calcula velocidade e direção do ataque usando vetores
        self.speed = config.itens_speed[self.item]
        direction = pygame.math.Vector2(position[0] - x, position[1] - y)
        self.velocity = direction.normalize() * self.speed
        
        # Define a posição de ataque fora do jogador
        x_attack = x + direction.normalize()[0] * self.game.player.rect.width
        y_attack = y + direction.normalize()[1] * self.game.player.rect.height
        
        # Define tamanho e posicao do ataque
        self.x = x_attack
        self.y = y_attack
        self.width = config.tilesize
        self.height = config.tilesize
        self.x_change = 0
        self.y_change = 0
        
        self.animation_loop = 0
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x - self.rect.width/2
        self.rect.y = self.y - self.rect.height/2
        
        
    def update(self):
        """
        Atualiza o estado do ataque a cada quadro.
        """
        # Atualiza o movimento do ataque
        self.movement()
        # Atualiza a animação do ataque
        self.animate()
        # Verifica se o ataque acertou algum inimigo
        self.collide_enemy()
        # Atualiza a posição e verifica a colisão do ataque
        self.rect.x += self.x_change
        self.rect.y += self.y_change
        self.collide_blocks()
        #DAVI
        #self.attack_with_joystick()

        self.x_change = 0
        self.y_change = 0
        
    def movement(self):
        """Atualiza a posição do ataque com base na direção e velocidade definidas."""
        # Calcula o descolamento nos eixos do ataque
        self.x_change = self.velocity[0]
        self.y_change = self.velocity[1]
        
    def animate(self):
        """Atualiza a animação do ataque."""        
        [self.attack_animations] = self.game.sprites.attack_animations[self.item].values()
        # Aplica o som do ataque
        self.game.play_sound(self.item, self.attack_sound)
        self.attack_sound = False
        
        # Cria o loop de animacao
        self.image = self.attack_animations[math.floor(self.animation_loop)]
        angle = self.velocity.angle_to(pygame.math.Vector2(0, -1))  # Alinha com o eixo Y (apontando para cima)
        self.image = pygame.transform.rotate(self.image, angle).convert_alpha()  # Rotaciona o sprite
        # self.rect = self.image.get_rect(center=self.rect.center)  # Atualiza o retângulo
        # Ajusta a velocidade com que o loop ocorre nessa direcao
        self.animation_loop += self.animation_speed
        if self.animation_loop >= (len(self.attack_animations)- 1):
            self.kill()
            
    def collide_enemy(self):
        """
        Verifica a colisão do ataque com inimigos.
        
        Este método percorre todos os inimigos presentes no jogo e verifica se o ataque colidiu com algum deles. Se uma colisão for detectada, ele aplica o dano apropriado ao inimigo e, se necessário, trata outras consequências, como a remoção do ataque.
        """

        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        # Verifica se o ataque acertou algum inimigo
        if hits:
            for sprite in hits:
                # Se o inimigo tiver sido atingido e tiver dentro do limite de inimigos do ataque, ativa o dano do inimigo
                if not sprite.damage and self.count_enemies <= config.enemies_attack_limit:
                    sprite.damage = True
                    sprite.damage_index = 0
                    sprite.damage_reason = self
                    sprite.damage_time = pygame.time.get_ticks()
                    self.count_enemies += 1
                
    def collide_blocks(self):
        """Verifica a colisão do ataque com blocos do cenário."""
        # Verifica se o ataque colidiu com o cenário, se colidir, destroi o ataque
        hits = pygame.sprite.spritecollide(self, self.game.collidable_sprites, False)
        if hits:
            self.kill()
            
