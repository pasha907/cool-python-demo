"""
Mandelbrot Fractal Zoom
------------------------
A real-time animated zoom into the Mandelbrot set, rendered with smooth
coloring. Looks incredible on a projector or shared screen.

Requirements:
    pip install numpy pygame

Run:
    python fractal_zoom.py

Controls:
    Click anywhere to re-center the zoom on that point.
    Press R to reset.
    Press ESC or close window to quit.
"""

import numpy as np
import pygame
import sys

WIDTH, HEIGHT = 900, 700
MAX_ITER = 150
ZOOM_SPEED = 1.035

# Target point to zoom into (a classic beautiful spot in the Mandelbrot set)
TARGET_X, TARGET_Y = -0.743643887037151, 0.13182590420533

def mandelbrot(width, height, center_x, center_y, scale, max_iter):
    x = np.linspace(center_x - scale, center_x + scale, width)
    y = np.linspace(center_y - scale * height / width, center_y + scale * height / width, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    div_time = np.zeros(C.shape, dtype=float)
    mask = np.ones(C.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask] ** 2 + C[mask]
        diverged = np.abs(Z) > 2
        newly_diverged = diverged & mask
        div_time[newly_diverged] = i + 1 - np.log(np.log(np.abs(Z[newly_diverged]) + 1e-10)) / np.log(2)
        mask[diverged] = False
        if not mask.any():
            break

    div_time[mask] = max_iter
    return div_time

def color_map(div_time, max_iter):
    t = div_time / max_iter
    r = (9 * (1 - t) * t ** 3 * 255).astype(np.uint8)
    g = (15 * (1 - t) ** 2 * t ** 2 * 255).astype(np.uint8)
    b = (8.5 * (1 - t) ** 3 * t * 255).astype(np.uint8)
    return np.dstack([r, g, b])

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mandelbrot Zoom — click to re-center, R to reset")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    center_x, center_y = TARGET_X, TARGET_Y
    scale = 2.5

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    center_x, center_y, scale = TARGET_X, TARGET_Y, 2.5
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                nx = center_x + (mx - WIDTH / 2) / WIDTH * 2 * scale
                ny = center_y + (my - HEIGHT / 2) / HEIGHT * 2 * scale * HEIGHT / WIDTH
                center_x, center_y = nx, ny
                scale = 2.5

        div_time = mandelbrot(WIDTH, HEIGHT, center_x, center_y, scale, MAX_ITER)
        rgb = color_map(div_time, MAX_ITER)
        surf = pygame.surfarray.make_surface(np.transpose(rgb, (1, 0, 2)))
        screen.blit(surf, (0, 0))

        info = font.render(f"zoom: {2.5/scale:,.0f}x   (click to recenter, R to reset)", True, (255, 255, 255))
        screen.blit(info, (10, 10))

        pygame.display.flip()
        scale /= ZOOM_SPEED
        if scale < 1e-13:
            scale = 2.5
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
