import pygame
import sys
import os
import json
import itertools
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cookie Stop")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BROWN = (210, 105, 30)
COLOR_CYCLE = itertools.cycle([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)])

# Fonts
font = pygame.font.Font(None, 36)

# Game variables
cookies = 0
cookies_per_click = 1
cookies_per_second = 0
fullscreen = False
milestones = {100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000, 5000000}
confetti_particles = []

# Save file paths
save_files = [
    "cookie_clicker_save1.json",
    "cookie_clicker_save2.json",
    "cookie_clicker_save3.json",
]

# Load images
cookie_image_path = os.path.join(os.path.dirname(__file__), "cookie.png")
cookie_image = pygame.image.load(cookie_image_path)
cookie_image = pygame.transform.scale(cookie_image, (150, 150))

# Smaller cookie for confetti
confetti_image = pygame.transform.scale(cookie_image, (20, 20))

start_image_path = os.path.join(os.path.dirname(__file__), "start_image.png")
start_image = pygame.image.load(start_image_path)
start_image = pygame.transform.scale(start_image, (WIDTH, HEIGHT))

# Rotating cookie variables
cookie_angle = 0
cookie_center = (WIDTH // 4, HEIGHT // 2)
cookie_rect = cookie_image.get_rect(center=cookie_center)

# Cycle through colors
current_color = next(COLOR_CYCLE)
color_change_event = pygame.USEREVENT + 2
pygame.time.set_timer(color_change_event, 500)  # Change color every 500ms

# Upgrades
upgrades = [
    {"name": "Better Mixer", "cost": 10, "boost": 1, "type": "click"},
    {"name": "Faster Oven", "cost": 50, "boost": 5, "type": "click"},
    {"name": "Cookie Factory", "cost": 200, "boost": 20, "type": "click"},
    {"name": "Small Auto Clicker", "cost": 100, "boost": 5, "type": "auto"},
    {"name": "Big Auto Clicker", "cost": 500, "boost": 20, "type": "auto"},
]

# Confetti animation
def spawn_confetti():
    for _ in range(50):  # Create 50 particles
        x = random.randint(0, WIDTH)
        y = random.randint(-100, HEIGHT // 2)  # Start above the screen
        speed = random.uniform(1, 3)
        confetti_particles.append({"x": x, "y": y, "speed": speed})

def update_confetti():
    for particle in confetti_particles:
        particle["y"] += particle["speed"]
    confetti_particles[:] = [p for p in confetti_particles if p["y"] < HEIGHT]

def draw_confetti():
    for particle in confetti_particles:
        screen.blit(confetti_image, (particle["x"], particle["y"]))


# Save progress to a specific slot
def save_progress(slot):
    data = {
        "cookies": cookies,
        "cookies_per_click": cookies_per_click,
        "cookies_per_second": cookies_per_second,
        "upgrades": upgrades,
    }
    with open(save_files[slot], "w") as f:
        json.dump(data, f)

# Load progress from a specific slot
def load_progress(slot):
    global cookies, cookies_per_click, cookies_per_second, upgrades
    if os.path.exists(save_files[slot]):
        with open(save_files[slot], "r") as f:
            data = json.load(f)
            cookies = data.get("cookies", 0)
            cookies_per_click = data.get("cookies_per_click", 1)
            cookies_per_second = data.get("cookies_per_second", 0)
            saved_upgrades = data.get("upgrades", [])
            for i in range(len(upgrades)):
                if i < len(saved_upgrades):
                    upgrades[i] = saved_upgrades[i]
        return True
    return False

# Draw text with optional color cycling for specific parts
def draw_text(surface, text, x, y, color=BLACK, highlight_text=None, highlight_color=None):
    if highlight_text is None or highlight_color is None:
        rendered_text = font.render(text, True, color)
        surface.blit(rendered_text, (x, y))
    else:
        # Split the text into static and dynamic parts
        static_text, dynamic_text = text.split(highlight_text)
        static_rendered = font.render(static_text, True, color)
        dynamic_rendered = font.render(highlight_text, True, highlight_color)

        # Render static text
        surface.blit(static_rendered, (x, y))
        static_width = static_rendered.get_width()

        # Render highlighted dynamic text
        surface.blit(dynamic_rendered, (x + static_width, y))

# Start screen
def start_screen():
    global fullscreen

    running = True
    while running:
        screen.blit(start_image, (0, 0))

        # Draw buttons
        start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 250, 200, 50)
        save_menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 180, 200, 50)
        options_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 110, 200, 50)
        pygame.draw.rect(screen, BROWN, start_button)
        pygame.draw.rect(screen, BROWN, save_menu_button)
        pygame.draw.rect(screen, BROWN, options_button)

        draw_text(screen, "Start Game", start_button.x + 30, start_button.y + 10)
        draw_text(screen, "Save Menu", save_menu_button.x + 30, save_menu_button.y + 10)
        draw_text(screen, "Options", options_button.x + 50, options_button.y + 10)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    running = False
                elif save_menu_button.collidepoint(event.pos):
                    save_menu()
                elif options_button.collidepoint(event.pos):
                    options_menu()

# Save menu
def save_menu():
    running = True
    while running:
        screen.fill(GRAY)

        # Draw save/load slots
        save_buttons = [
            pygame.Rect(WIDTH // 2 - 250, 150 + i * 80, 200, 50) for i in range(3)
        ]
        load_buttons = [
            pygame.Rect(WIDTH // 2 + 50, 150 + i * 80, 200, 50) for i in range(3)
        ]
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)

        for i, (save_button, load_button) in enumerate(zip(save_buttons, load_buttons)):
            pygame.draw.rect(screen, BROWN, save_button)
            pygame.draw.rect(screen, BROWN, load_button)
            draw_text(screen, f"Save Slot {i + 1}", save_button.x + 30, save_button.y + 10)
            draw_text(screen, f"Load Slot {i + 1}", load_button.x + 30, load_button.y + 10)

        pygame.draw.rect(screen, BROWN, back_button)
        draw_text(screen, "Back", back_button.x + 70, back_button.y + 10)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, (save_button, load_button) in enumerate(zip(save_buttons, load_buttons)):
                    if save_button.collidepoint(event.pos):
                        save_progress(i)
                        print(f"Saved progress to Slot {i + 1}")
                    elif load_button.collidepoint(event.pos):
                        if load_progress(i):
                            print(f"Loaded progress from Slot {i + 1}")
                        else:
                            print(f"No save found in Slot {i + 1}")
                if back_button.collidepoint(event.pos):
                    return
                


# Main game loop
def main_game():
    global cookies, cookies_per_click, cookies_per_second, cookie_angle, current_color

    clock = pygame.time.Clock()
    running = True
    auto_click_event = pygame.USEREVENT + 1
    pygame.time.set_timer(auto_click_event, 1000)  # Trigger auto-click every second

    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if cookie is clicked
                if cookie_rect.collidepoint(event.pos):
                    cookies += cookies_per_click
                # Check for upgrades
                for i, rect in enumerate(upgrade_button_rects):
                    if rect.collidepoint(event.pos):
                        if cookies >= upgrades[i]["cost"]:
                            cookies -= upgrades[i]["cost"]
                            if upgrades[i]["type"] == "click":
                                cookies_per_click += upgrades[i]["boost"]
                            elif upgrades[i]["type"] == "auto":
                                cookies_per_second += upgrades[i]["boost"]
                            upgrades[i]["cost"] = int(upgrades[i]["cost"] * 1.5)

                # Check milestones
                if cookies in milestones:
                     #milestones.remove(cookies)
                     spawn_confetti()

                # Check for save menu button
                if save_menu_button.collidepoint(event.pos):
                    save_menu()

                # Check for quit button
                if quit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            elif event.type == auto_click_event:
                cookies += cookies_per_second
            elif event.type == color_change_event:
                current_color = next(COLOR_CYCLE)

        # Rotate the cookie image
        cookie_angle = (cookie_angle + 1) % 360
        rotated_cookie = pygame.transform.rotate(cookie_image, cookie_angle)
        cookie_rect = rotated_cookie.get_rect(center=cookie_center)
        screen.blit(rotated_cookie, cookie_rect)

        # Draw upgrades
        for i, rect in enumerate(upgrade_button_rects):
            pygame.draw.rect(screen, BROWN, rect)
            draw_text(screen, f"{upgrades[i]['name']} - Cost: {upgrades[i]['cost']}", rect.x + 10, rect.y + 10)

        # Draw stats with cycling color only on numbers
        draw_text(screen, f"Cookies: {cookies}", 50, 20, BLACK, highlight_text=str(cookies), highlight_color=current_color)
        draw_text(screen, f"Cookies per click: {cookies_per_click}", 50, 50, BLACK, highlight_text=str(cookies_per_click), highlight_color=current_color)
        draw_text(screen, f"Cookies per second: {cookies_per_second}", 50, 80, BLACK, highlight_text=str(cookies_per_second), highlight_color=current_color)

        # Draw save menu button
        save_menu_button = pygame.Rect(WIDTH - 300, HEIGHT - 70, 120, 50)
        pygame.draw.rect(screen, BROWN, save_menu_button)
        draw_text(screen, "Save Menu", save_menu_button.x + 10, save_menu_button.y + 10)

        # Draw quit button
        quit_button = pygame.Rect(WIDTH - 150, HEIGHT - 70, 120, 50)
        pygame.draw.rect(screen, BROWN, quit_button)
        draw_text(screen, "Quit", quit_button.x + 30, quit_button.y + 10)

        # Update and draw confetti
        update_confetti()
        draw_confetti()

        pygame.display.flip()
        clock.tick(60)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Create upgrade button rectangles
    upgrade_button_rects = []
    for i in range(len(upgrades)):
        upgrade_button_rects.append(pygame.Rect(WIDTH // 2 + 50, 100 + i * 80, 300, 50))

    start_screen()
    main_game()
