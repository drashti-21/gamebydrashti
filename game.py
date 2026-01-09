import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

# =============================
# CONFIG
# =============================
WIDTH, HEIGHT = 100, 100

PLAYER_START_RADIUS = 1.5
PLAYER_MAX_RADIUS = 6.0
GROWTH_RATE = 0.12

FOOD_SIZE = (0.8, 3.0)
BIG_ENEMY_SIZE = (2.5, 6.0)
FOOD_CHANCE = 0.15

ENEMY_SPEED = (0.25, 0.6)
SPAWN_INTERVAL = 15  # frames between new enemy spawn
MAX_ENEMIES = 12

COLLISION_EPSILON = 0.1  # Prevent tunneling

PASTEL_COLORS = [
    "#FFB3BA", "#FFDFBA", "#FFFFBA",
    "#BAFFC9", "#BAE1FF", "#E6BAFF"
]

WAITING, PLAYING, GAME_OVER = 0, 1, 2

# =============================
# STATE
# =============================
game_state = WAITING
player_x, player_y = WIDTH / 2, HEIGHT / 2
player_radius = PLAYER_START_RADIUS
score = 0

enemies = []
frame_count = 0

# =============================
# HELPERS
# =============================
def draw_size(r):
    return (r * 14) ** 2

def spawn_enemy():
    side = random.choice(["left", "right", "top", "bottom"])

    if random.random() < FOOD_CHANCE:
        r = random.uniform(*FOOD_SIZE)
    else:
        r = random.uniform(*BIG_ENEMY_SIZE)

    speed = random.uniform(*ENEMY_SPEED)
    drift = random.uniform(-0.4, 0.4)

    if side == "left":
        x, y, dx, dy = 0, random.uniform(0, HEIGHT), speed, drift
    elif side == "right":
        x, y, dx, dy = WIDTH, random.uniform(0, HEIGHT), -speed, drift
    elif side == "top":
        x, y, dx, dy = random.uniform(0, WIDTH), HEIGHT, drift, -speed
    else:  # bottom
        x, y, dx, dy = random.uniform(0, WIDTH), 0, drift, speed

    return {
        "x": x,
        "y": y,
        "dx": dx,
        "dy": dy,
        "r": r,
        "color": random.choice(PASTEL_COLORS)
    }

def reset_game():
    global enemies, player_radius, game_state, frame_count, score
    enemies = [spawn_enemy() for _ in range(MAX_ENEMIES // 2)]
    player_radius = PLAYER_START_RADIUS
    score = 0
    frame_count = 0
    game_state = WAITING
    status_text.set_text("CLICK TO START")
    status_text.set_color("white")

# =============================
# FIGURE
# =============================
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, WIDTH)
ax.set_ylim(0, HEIGHT)
ax.set_facecolor("#111111")
ax.set_xticks([])
ax.set_yticks([])

status_text = ax.text(
    WIDTH / 2, HEIGHT / 2,
    "CLICK TO START",
    color="white",
    fontsize=24,
    ha="center",
    va="center"
)

score_text = ax.text(
    2, HEIGHT - 3,
    "Score: 0",
    color="white",
    fontsize=12,
    ha="left",
    va="top"
)

enemy_scatter = ax.scatter([], [], s=[], c=[])
player_scatter = ax.scatter([], [], c="white", edgecolors="black")

reset_game()

# =============================
# INPUT
# =============================
def on_click(event):
    global game_state
    if game_state == WAITING:
        game_state = PLAYING
        status_text.set_text("")
    elif game_state == GAME_OVER:
        reset_game()

def on_mouse(event):
    global player_x, player_y
    if event.xdata is not None and event.ydata is not None:
        player_x = min(max(event.xdata, 0), WIDTH)
        player_y = min(max(event.ydata, 0), HEIGHT)

fig.canvas.mpl_connect("button_press_event", on_click)
fig.canvas.mpl_connect("motion_notify_event", on_mouse)

# =============================
# GAME LOOP
# =============================
def update(frame):
    global enemies, player_radius, game_state, frame_count, score
    frame_count += 1

    if game_state != PLAYING:
        return

    # Spawn new enemies randomly
    if frame_count % SPAWN_INTERVAL == 0 and len(enemies) < MAX_ENEMIES:
        enemies.append(spawn_enemy())

    alive = []

    for e in enemies:
        e["x"] += e["dx"]
        e["y"] += e["dy"]

        dist = np.hypot(player_x - e["x"], player_y - e["y"])

        # Collision detection
        if dist <= player_radius + e["r"] + COLLISION_EPSILON:
            if player_radius > e["r"]:
                player_radius = min(player_radius + e["r"] * GROWTH_RATE, PLAYER_MAX_RADIUS)
                score += 1
            else:
                game_state = GAME_OVER
                status_text.set_text("GAME OVER\nCLICK TO RESTART")
                status_text.set_color("red")
                return
        else:
            # Only keep enemies that are visible on screen
            if -6 < e["x"] < WIDTH + 6 and -6 < e["y"] < HEIGHT + 6:
                alive.append(e)

    enemies = alive

    # Update drawing
    if enemies:
        enemy_scatter.set_offsets([[e["x"], e["y"]] for e in enemies])
        enemy_scatter.set_sizes([draw_size(e["r"]) for e in enemies])
        enemy_scatter.set_facecolor([e["color"] for e in enemies])  # full color
        enemy_scatter.set_edgecolors([e["color"] for e in enemies])
    else:
        enemy_scatter.set_offsets(np.empty((0, 2)))

    player_scatter.set_offsets([[player_x, player_y]])
    player_scatter.set_sizes([draw_size(player_radius)])

    score_text.set_text(f"Score: {score}")

# =============================
# RUN
# =============================
ani = FuncAnimation(fig, update, interval=30, cache_frame_data=False)
plt.show()
