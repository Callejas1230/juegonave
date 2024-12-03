import pygame
import sys
import random
import unittest
import json  # Para la persistencia

pygame.init()
pygame.display.set_caption("Sidescrolling Shooter by @Callejas Torrico Cristopher")
clock = pygame.time.Clock()

WIDTH = 800
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Herencia simple
class GameObject():
    def __init__(self, x, y, surface):
        self.x = x
        self.y = y
        self.surface = pygame.image.load(surface).convert()

    def distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def render(self):
        screen.blit(self.surface, (int(self.x), int(self.y)))


# Composición
class HealthBar():
    def __init__(self, max_health):
        self.max_health = max_health
        self.health = max_health

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def render(self, x, y):
        pygame.draw.line(screen, GREEN, (int(x), int(y)), (int(x + (40 * (self.health/self.max_health))), int(y)), 2)


class Player(GameObject):
    def __init__(self):
        super().__init__(0, 0, 'player.png')
        self.dy = 0
        self.dx = 0
        self.score = 0
        self.kills = 0
        self.health_bar = HealthBar(20)

    def up(self):
        self.dy = -6

    def down(self):
        self.dy = 6

    def left(self):
        self.dx = -6

    def right(self):
        self.dx = 6

    def move(self):
        self.y = self.y + self.dy
        self.x = self.x + self.dx
        if self.y < 0:
            self.y = 0
            self.dy = 0
        elif self.y > 550:
            self.y = 550
            self.dy = 0
        if self.x < 0:
            self.x = 0
            self.dx = 0
        elif self.x > 200:
            self.x = 200
            self.dx = 0

    def render(self):
        super().render()
        self.health_bar.render(self.x, self.y)


class Missile(GameObject):
    def __init__(self):
        super().__init__(0, 1000, 'missile.png')
        self.dx = 0
        self.state = "ready"

    def fire(self):
        self.state = "firing"
        self.x = player.x + 25
        self.y = player.y + 16
        self.dx = 10

    def move(self):
        if self.state == "firing":
            self.x = self.x + self.dx
        if self.x > 800:
            self.state = "ready"
            self.y = 1000


class Enemy(GameObject):
    def __init__(self):
        super().__init__(800, random.randint(0, 550), 'enemy.png')
        self.dx = random.randint(10, 50) / -10
        self.dy = 0
        self.health_bar = HealthBar(random.randint(5, 15))
        self.type = "enemy"

    def move(self):
        self.x = self.x + self.dx
        self.y = self.y + self.dy
        if self.x < -30:
            self.x = random.randint(800, 900)
            self.y = random.randint(0, 550)
        if self.y < 0:
            self.y = 0
            self.dy *= -1
        elif self.y > 550:
            self.y = 550
            self.dy *= -1

    def render(self):
        super().render()
        self.health_bar.render(self.x, self.y)


class Star(GameObject):
    def __init__(self):
        super().__init__(random.randint(0, 1000), random.randint(0, 550),
                         random.choice(["yellow_star.png", "red_star.png", "white_star.png"]))
        self.dx = random.randint(10, 50) / -30

    def move(self):
        self.x = self.x + self.dx
        if self.x < 0:
            self.x = random.randint(800, 900)
            self.y = random.randint(0, 550)


# Sonidos
missile_sound = pygame.mixer.Sound("missile.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")
font = pygame.font.SysFont("comicsansms", 24)

player = Player()
missiles = [Missile(), Missile(), Missile()]
enemies = [Enemy() for _ in range(5)]
stars = [Star() for _ in range(30)]


def fire_missile():
    for missile in missiles:
        if missile.state == "ready":
            missile.fire()
            missile_sound.play()
            break


def save_game():
    # Guardamos la información del jugador en un archivo JSON
    game_data = {
        'score': player.score,
        'kills': player.kills,
    }
    with open('save_game.json', 'w') as file:
        json.dump(game_data, file)
    print("Juego guardado exitosamente!")


def load_game():
    try:
        with open('save_game.json', 'r') as file:
            game_data = json.load(file)
            player.score = game_data.get('score', 0)
            player.kills = game_data.get('kills', 0)
            print("Juego cargado exitosamente!")
    except FileNotFoundError:
        print("No se encontró un juego guardado. Comenzando juego nuevo.")
        player.score = 0  # Aseguramos que el score inicie en 0
        player.kills = 0  # Aseguramos que las kills inicien en 0
        player.health_bar.health = player.health_bar.max_health  # La vida del jugador empieza al máximo


def game_loop():
    load_game()  # Cargar el juego al inicio
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()  # Guardar progreso cuando el jugador cierre el juego
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player.up()
                elif event.key == pygame.K_s:
                    player.down()
                elif event.key == pygame.K_a:
                    player.left()
                elif event.key == pygame.K_d:
                    player.right()
                elif event.key == pygame.K_SPACE:
                    fire_missile()
        player.move()
        for missile in missiles:
            missile.move()
        for star in stars:
            star.move()
        for enemy in enemies:
            enemy.move()
            for missile in missiles:
                if enemy.distance(missile) < 20:
                    explosion_sound.play()
                    enemy.health_bar.take_damage(4)
                    if enemy.health_bar.health <= 0:
                        enemy.x = random.randint(800, 900)
                        enemy.y = random.randint(0, 550)
                        player.kills += 1
                        if player.kills % 10 == 0:
                            enemy.surface = pygame.image.load('boss.png').convert()
                            enemy.health_bar = HealthBar(50)
                            enemy.dy = random.randint(-5, 5)
                            enemy.type = "boss"
                        else:
                            enemy.type = "enemy"
                            enemy.dy = 0
                            enemy.surface = pygame.image.load('enemy.png').convert()
                            enemy.health_bar = HealthBar(random.randint(5, 15))
                    else:
                        enemy.x += 20
                    missile.dx = 0
                    missile.x = 0
                    missile.y = 1000
                    missile.state = "ready"
                    player.score += 10
            if enemy.distance(player) < 20:
                explosion_sound.play()
                player.health_bar.take_damage(random.randint(5, 10))
                enemy.health_bar.take_damage(random.randint(5, 10))
                enemy.x = random.randint(800, 900)
                enemy.y = random.randint(0, 550)
                if player.health_bar.health <= 0:
                    print("¡Game Over!")
                    save_game()  # Guardar antes de salir
                    pygame.quit()
                    exit()
        screen.fill(BLACK)
        for star in stars:
            star.render()
        player.render()
        for missile in missiles:
            missile.render()
        for enemy in enemies:
            enemy.render()

        score_surface = font.render(f"Score: {player.score} Kills: {player.kills}", True, WHITE)
        screen.blit(score_surface, (380, 20))
        pygame.display.flip()
        clock.tick(30)


# Pruebas unitarias
class TestCollisions(unittest.TestCase):

    def test_collision(self):
        player = Player()
        enemy = Enemy()
        missile = Missile()

        # Colocar el jugador, enemigo y misil juntos para simular una colisión
        player.x, player.y = 100, 100
        enemy.x, enemy.y = 100, 100
        missile.x, missile.y = 100, 100
        
        # Verificar colisión entre jugador y enemigo
        self.assertTrue(player.distance(enemy) < 20, "Player should collide with enemy")
        # Verificar colisión entre misil y enemigo
        self.assertTrue(missile.distance(enemy) < 20, "Missile should collide with enemy")

        # Mover enemigo lejos del jugador para verificar que no haya colisión
        enemy.x, enemy.y = 300, 300
        self.assertFalse(player.distance(enemy) < 20, "Player should not collide with enemy")


if __name__ == "__main__":
    unittest.main(exit=False)
    game_loop()
