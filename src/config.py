# Variavel que armazena o tamanho de certos objetos
tilesize = 1

# Variavel que define as camadas dos objetos
layers = {"player_layer": 3,
          "enemy_layer": 2,
          "block_layer": 1}

max_health = {"player": 1000,
              "enemies": {
                  "skeleton": 1000
                  }
              }

damage = {
    "enemies": {
        "skeleton": 10
        },
    "itens": {
        "wave": {
            1: 10
            },
        "energy_ball": {
            1: 30,
            2: 50,
            3: 100,
            4: 150,
            5: 200
            }
        }
    }

# Variavel que define a velocidade do jogador
player_speed = 7

itens_speed = {
    "wave": 1,
    "energy_ball": 10
    }

itens_delay = {
    "wave": 550,
    "energy_ball": 550
    }

# Variavel que define a velocidade base dos inimigos
enemy_speed = {
    "skeleton" : 3
}

enemy_xp = {
    "skeleton": 150
    }

# Campo de visão do inimigo
enemy_fov = 800

# Cor vermelha em rgb
red = (255, 0 , 0)

# Largura do personagem principal
width = 77

# Tamanho do personagem principal
char_size = (width, (width*32)/22)

# Tmanho base para os personagens
size = 77

damage_delay = 400

spawn_delay = 400
despawn_delay = 1000