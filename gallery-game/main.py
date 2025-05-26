import pygame
import random
import math
from shapely.geometry import Polygon, Point, LineString
import numpy as np

WIDTH, HEIGHT = 800, 800
CELL_SIZE = 60
ROWS, COLS = 10, 10
FORGIVENESS_MARGIN = 1.0

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Art Gallery Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

def loading_screen():
    selecting = True
    selected_blocks = 12
    while selecting:
        screen.fill(BLACK)
        title = font.render("Art Gallery Game", True, WHITE)
        instruction = font.render("Choose number of rooms (5-30):", True, GREEN)
        sides_text = font.render(f"Current: {selected_blocks}", True, YELLOW)
        explain1 = font.render("Place guards to cover the gallery walls.", True, WHITE)
        explain2 = font.render("Click inside the shape to place and move guards.", True, WHITE)
        explain3 = font.render("100% coverage required to win.", True, WHITE)
        start_text = font.render("Press ENTER to begin", True, BLUE)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 150))
        screen.blit(sides_text, (WIDTH // 2 - sides_text.get_width() // 2, 200))
        screen.blit(explain1, (WIDTH // 2 - explain1.get_width() // 2, 300))
        screen.blit(explain2, (WIDTH // 2 - explain2.get_width() // 2, 340))
        screen.blit(explain3, (WIDTH // 2 - explain3.get_width() // 2, 380))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 450))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return selected_blocks
                elif event.key == pygame.K_UP and selected_blocks < 30:
                    selected_blocks += 1
                elif event.key == pygame.K_DOWN and selected_blocks > 5:
                    selected_blocks -= 1

def generate_blocky_shape(n_blocks):
    grid = set()
    x, y = COLS // 2, ROWS // 2
    grid.add((x, y))
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    while len(grid) < n_blocks:
        dx, dy = random.choice(directions)
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            grid.add((nx, ny))
            x, y = nx, ny
    blocks = []
    for gx, gy in grid:
        cx, cy = gx * CELL_SIZE + WIDTH // 2 - COLS * CELL_SIZE // 2, gy * CELL_SIZE + HEIGHT // 2 - ROWS * CELL_SIZE // 2
        blocks.append(pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE))
    return blocks

def extract_outer_edges(blocks):
    edge_map = {}
    for rect in blocks:
        corners = [(rect.left, rect.top), (rect.right, rect.top), (rect.right, rect.bottom), (rect.left, rect.bottom)]
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            edge = (a, b) if a < b else (b, a)
            if edge in edge_map:
                edge_map[edge] += 1
            else:
                edge_map[edge] = 1
    boundary_edges = [e for e, count in edge_map.items() if count == 1]
    return boundary_edges

def order_edges(edges):
    edge_dict = {}
    for a, b in edges:
        edge_dict.setdefault(a, []).append(b)
        edge_dict.setdefault(b, []).append(a)
    ordered = [edges[0][0]]
    current = edges[0][1]
    while len(ordered) < len(edges):
        ordered.append(current)
        neighbors = edge_dict[current]
        next_point = neighbors[0] if neighbors[0] != ordered[-2] else neighbors[1]
        current = next_point
    return ordered

N_BLOCKS = loading_screen()
block_rects = generate_blocky_shape(N_BLOCKS)
boundary = order_edges(extract_outer_edges(block_rects))
polygon = Polygon(boundary)
polygon_points = list(polygon.exterior.coords)
MAX_GUARDS = len(polygon_points) // 3
guards = []
dragging_guard = None

def draw_polygon(points):
    pygame.draw.polygon(screen, WHITE, points, 2)

def draw_guards():
    for g in guards:
        pygame.draw.circle(screen, RED, g, 8)
        pygame.draw.circle(screen, BLACK, g, 8, 2)

def visible_points_from_guards():
    visible_points = set()
    rays_to_draw = []
    perimeter = LineString(polygon_points)
    perimeter_length = perimeter.length
    step_size = 1.5
    steps = int(perimeter_length / step_size)
    all_points = []
    for i in range(steps):
        point_on_perimeter = perimeter.interpolate(i * step_size, normalized=False)
        pt = (point_on_perimeter.x, point_on_perimeter.y)
        pt_shapely = Point(pt)
        all_points.append(pt)
        for guard in guards:
            ray = LineString([guard, pt])
            if not polygon.contains(ray) and not polygon.boundary.contains(ray):
                continue
            blocked = False
            for j in range(len(polygon_points)):
                v1, v2 = polygon_points[j], polygon_points[(j + 1) % len(polygon_points)]
                edge = LineString([v1, v2])
                if edge.distance(pt_shapely) < 1e-6:
                    continue
                if ray.crosses(edge) or ray.intersects(edge):
                    blocked = True
                    break
            if not blocked:
                visible_points.add(i)
                rays_to_draw.append((guard, pt))
                break
    softened_visible = set(visible_points)
    for i in range(3, steps - 3):
        if i not in visible_points:
            neighbors = sum((i + o in visible_points) for o in [-3, -2, -1, 1, 2, 3])
            if neighbors >= 5:
                softened_visible.add(i)
    return [all_points[i] for i in softened_visible], rays_to_draw

def draw_coverage():
    visible_pts, rays = visible_points_from_guards()
    for pt in visible_pts:
        pygame.draw.circle(screen, YELLOW, (int(pt[0]), int(pt[1])), 2)
    for ray in rays:
        pygame.draw.line(screen, GRAY, ray[0], ray[1], 1)
    return len(visible_pts)

running = True
while running:
    screen.fill(BLACK)
    draw_polygon(polygon_points)
    visible_count = draw_coverage()
    draw_guards()
    total_points = int(LineString(polygon_points).length / 1.5)
    coverage = visible_count / total_points
    text = font.render(f"Coverage: {int(coverage * 100)}%", True, GREEN)
    screen.blit(text, (20, 20))
    if coverage >= FORGIVENESS_MARGIN:
        win_text = font.render("Success! Full coverage achieved!", True, BLUE)
        screen.blit(win_text, (20, 60))
    elif len(guards) >= MAX_GUARDS:
        text2 = font.render("Max guards placed", True, RED)
        screen.blit(text2, (20, 60))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if event.button == 1:
                for i, g in enumerate(guards):
                    if math.hypot(g[0] - x, g[1] - y) < 10:
                        dragging_guard = i
                        break
                else:
                    if len(guards) < MAX_GUARDS and polygon.contains(Point(x, y)):
                        guards.append((x, y))
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_guard = None
        elif event.type == pygame.MOUSEMOTION and dragging_guard is not None:
            x, y = pygame.mouse.get_pos()
            if polygon.contains(Point(x, y)):
                guards[dragging_guard] = (x, y)
    pygame.display.flip()
    clock.tick(30)
pygame.quit()
