import pygame
import random
import sys

pygame.init()
pygame.font.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Screen settings
WIDTH = 1200
HEIGHT = 700
MID_W = WIDTH // 2
MID_H = HEIGHT // 2
REL_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Triangular Assault")

# Fonts
hud_font = pygame.font.Font('assets/VCR_OSD_MONO_1.001.ttf', 40)
screen_font = pygame.font.SysFont('Arial', 30)
screen_font_bold = pygame.font.SysFont('Arial Bold', 120)

# Sound effects
bounce_sound_effect = pygame.mixer.Sound('assets/bounce.wav')
scoring_sound_effect = pygame.mixer.Sound('assets/scoring-sound.wav')
death_sound_effect = pygame.mixer.Sound('assets/explode.ogg')

# Player
direction = 0
player_r = (
    (MID_W - REL_SIZE, MID_H - REL_SIZE),
    (MID_W + REL_SIZE // 2, MID_H),
    (MID_W - REL_SIZE, MID_H + REL_SIZE)
)
player_l = (
    (MID_W + REL_SIZE, MID_H + REL_SIZE),
    (MID_W - REL_SIZE // 2, MID_H),
    (MID_W + REL_SIZE, MID_H - REL_SIZE)
)

# Walls
topper = pygame.Rect(0, MID_H - (REL_SIZE * 4), WIDTH, REL_SIZE)
bottom = pygame.Rect(0, MID_H + (REL_SIZE * 3), WIDTH, REL_SIZE)

# Initial HUD stats
score = 0
life = 3
wave = 0
combo = 0

# Variable trigger control
bullets = []
move_left = False
shot_timer = 0
shot_delay = 90  # 1.5 segundos a 60 FPS
last_shot_time = 0


def handle_shooting():
    global bullets, direction, score, life, combo, shot_timer, shot_delay, last_shot_time

    keys = pygame.key.get_pressed()

    if (keys[pygame.K_a] or keys[pygame.K_d]) and shot_timer <= 0:
        current_time = pygame.time.get_ticks()

        # Verifica se o último disparo foi há mais de 1.5 segundos ou se o jogador pressionou rapidamente as teclas
        if current_time - last_shot_time >= shot_delay or shot_timer == 0:
            player_position = player_l[1] if keys[pygame.K_a] else player_r[1]
            direction_of_bullet = -1 if keys[pygame.K_a] else 1
            bullets.append((player_position[0], player_position[1], direction_of_bullet))
            scoring_sound_effect.play()
            shot_timer = 90
            last_shot_time = current_time
    new_bullets = []
    for bullet in bullets:
        bx, by, dir = bullet
        bx += 5 * dir
        by = max(MID_H - (REL_SIZE * 4), min(MID_H + (REL_SIZE * 3), by))

        # Check for collision with the top and bottom dashed lines
        top_line_y = MID_H - (REL_SIZE * 4)
        bottom_line_y = MID_H + (REL_SIZE * 3)
        if top_line_y <= by <= bottom_line_y:
            # Check for collision with the left dashed line
            left_line_x = MID_W // 2
            # Check for collision with the right dashed line
            right_line_x = MID_W + MID_W // 2
            if left_line_x <= bx <= right_line_x:
                new_bullets.append((bx, by, dir))

    # Update the bullet
    bullets = new_bullets
    # Time
    if shot_timer > 0:
        shot_timer -= 1


def draw_game():
    screen.fill(BLACK)
    # Draw hud
    score_text = hud_font.render(f'SCORE: {score}', True, WHITE, BLACK)
    life_text = hud_font.render(f'LIFE: {life}', True, WHITE, BLACK)
    wave_text = hud_font.render(f'WAVE: {wave}', True, WHITE, BLACK)
    combo_text = hud_font.render(f'COMBO: {combo}', True, WHITE, BLACK)
    screen.blit(score_text, (20, 10))
    screen.blit(life_text, (WIDTH - 200, 10))
    screen.blit(combo_text, (20, 50))
    screen.blit(wave_text, (MID_W - 80, 10))

    if game_start:
        # Draw scenario
        pygame.draw.rect(screen, WHITE, topper)
        pygame.draw.rect(screen, WHITE, bottom)

        # Draw dotted lines
        start_y = MID_H - (REL_SIZE * 4)
        end_y = MID_H + (REL_SIZE * 3)
        dot_size = 10
        dot_space = 5
        y = start_y
        while y < end_y:
            pygame.draw.line(screen, WHITE, (MID_W // 2, y), (MID_W // 2, y + dot_size))
            pygame.draw.line(screen, WHITE, (3 * MID_W // 2, y), (3 * MID_W // 2, y + dot_size))
            y += dot_size + dot_space

        # Draw player
        if direction == 0:
            pygame.draw.polygon(screen, WHITE, player_r)
        else:
            pygame.draw.polygon(screen, WHITE, player_l)

        # Draw bullets
        for bullet in bullets:
            pygame.draw.circle(screen, WHITE, (int(bullet[0]), int(bullet[1])), 5)
    else:
        # Title
        title_txt = 'GAME OVER' if life <= 0 else 'TRIANGULAR ASSAULT'
        title = screen_font_bold.render(title_txt, True, WHITE, BLACK)
        title_w = title.get_width()
        title_h = title.get_height()

        # Subtitle
        subtitle_txt = "To play again press 'space'" if life <= 0 else "To play press 'space'"
        subtitle = screen_font.render(subtitle_txt, True, WHITE, BLACK)
        subtitle_w = subtitle.get_width()

        # Draw title and subtitle
        screen.blit(title, (MID_W - title_w // 2, MID_H - title_h // 2))
        screen.blit(subtitle, (MID_W - subtitle_w // 2, MID_H + title_h // 2))


# Game stats
running = True
game_start = False
desired_direction = None

while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif keys[pygame.K_SPACE]:
            if not game_start:
                game_start = True
                score = 0
                combo = 0
                wave = 1
                life = 3

    if desired_direction is not None:
        direction = desired_direction

    if game_start:
        handle_shooting()
        for bullet in bullets:
            pygame.draw.circle(screen, WHITE, (int(bullet[0]), int(bullet[1])), 5)

        # Player movement
        if keys[pygame.K_a]:
            desired_direction = 1
        elif keys[pygame.K_d]:
            desired_direction = 0
        else:
            desired_direction = None

        # Player death
        if life <= 0:
            game_start = False
            death_sound_effect.play()
    # Draw
    draw_game()

    # update screen
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
