"""
Particle Fireworks Simulation
------------------------------
A physics-based fireworks show: rockets launch, explode into hundreds of
glowing particles with gravity, drag, and trailing light. Great full-screen
demo for a crowd.

Requirements:
    pip install pygame

Run:
    python fireworks.py

Controls:
    Click anywhere to launch a firework at that spot.
    SPACE for a random auto-launch.
    ESC or close window to quit.
"""

import pygame
import random
import math
import sys

WIDTH, HEIGHT = 1000, 700
FPS = 60
GRAVITY = 0.05
DRAG = 0.985

COLORS = [
    (255, 80, 80), (255, 180, 60), (255, 240, 100),
    (120, 255, 120), (100, 220, 255), (150, 120, 255),
    (255, 100, 220), (255, 255, 255),
]


class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=2.5, gravity=GRAVITY):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity

    def update(self):
        self.vx *= DRAG
        self.vy *= DRAG
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def draw(self, surf):
        t = max(self.life / self.max_life, 0)
        r, g, b = self.color
        alpha_color = (int(r * t), int(g * t), int(b * t))
        radius = max(1, int(self.size * t))
        pygame.draw.circle(surf, alpha_color, (int(self.x), int(self.y)), radius)


class Rocket:
    """Climbs upward, then explodes into a burst of particles."""
    def __init__(self, x, target_y):
        self.x = x
        self.y = HEIGHT
        self.target_y = target_y
        self.vy = -random.uniform(9, 12)
        self.color = random.choice(COLORS)
        self.trail = []
        self.exploded = False

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.vy += GRAVITY * 0.6
        self.y += self.vy
        if self.vy >= 0 or self.y <= self.target_y:
            self.exploded = True
        return self.exploded

    def draw(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            fade = i / max(len(self.trail), 1)
            c = tuple(int(ch * fade) for ch in self.color)
            pygame.draw.circle(surf, c, (int(tx), int(ty)), 2)
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), 3)

    def explode(self):
        particles = []
        burst_type = random.choice(["sphere", "ring", "double"])
        n = random.randint(80, 140)

        if burst_type == "sphere":
            for _ in range(n):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 6)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                particles.append(Particle(self.x, self.y, vx, vy, self.color,
                                           life=random.randint(50, 90)))
        elif burst_type == "ring":
            speed = random.uniform(4, 6)
            for i in range(n):
                angle = (i / n) * 2 * math.pi
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                particles.append(Particle(self.x, self.y, vx, vy, self.color,
                                           life=random.randint(60, 90)))
        else:  # double ring, two colors
            c2 = random.choice(COLORS)
            for i in range(n):
                angle = (i / n) * 2 * math.pi
                for speed, color in [(3.5, self.color), (6.5, c2)]:
                    vx = math.cos(angle) * speed
                    vy = math.sin(angle) * speed
                    particles.append(Particle(self.x, self.y, vx, vy, color,
                                               life=random.randint(50, 80)))
        return particles


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fireworks — click to launch, SPACE for random, ESC to quit")
    clock = pygame.time.Clock()

    rockets = []
    particles = []
    auto_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    x = random.randint(100, WIDTH - 100)
                    target_y = random.randint(100, 300)
                    rockets.append(Rocket(x, target_y))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                rockets.append(Rocket(mx, my))

        auto_timer += 1
        if auto_timer > 70 and random.random() < 0.05:
            x = random.randint(100, WIDTH - 100)
            target_y = random.randint(100, 300)
            rockets.append(Rocket(x, target_y))
            auto_timer = 0

        # fade background for trailing-light effect
        fade_surf = pygame.Surface((WIDTH, HEIGHT))
        fade_surf.set_alpha(60)
        fade_surf.fill((0, 0, 0))
        screen.blit(fade_surf, (0, 0))

        for rocket in rockets[:]:
            exploded = rocket.update()
            rocket.draw(screen)
            if exploded:
                particles.extend(rocket.explode())
                rockets.remove(rocket)

        for p in particles[:]:
            alive = p.update()
            if alive:
                p.draw(screen)
            else:
                particles.remove(p)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
