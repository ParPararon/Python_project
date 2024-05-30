import pygame
import sys
import time
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 128, 0)
BUTTON_HOVER_COLOR = (0, 255, 0)
TEXT_COLOR = (255, 255, 255)
PRODUCT_WIDTH, PRODUCT_HEIGHT = 150, 150

# Настройки экрана
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pablo's Parodia")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont(None, 55)
button_font = pygame.font.SysFont(None, 45)
order_font = pygame.font.SysFont(None, 35)

# Тексты
title_text = font.render("Pablo's Parodia", True, BLACK)
start_text = button_font.render("Начать игру", True, TEXT_COLOR)
delete_burger_text = button_font.render("Очистить", True, TEXT_COLOR)
to_kitchen_text = button_font.render("Кухня", True, TEXT_COLOR)
to_hall_text = button_font.render("Гостевой зал", True, TEXT_COLOR)

# Прямоугольники для текста и кнопок
title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
button_to_kitchen_rect = pygame.Rect(25, HEIGHT - 75, 100, 50)
button_to_hall_rect = pygame.Rect(WIDTH - 225, HEIGHT - 75, 200, 50)
start_text_rect = start_text.get_rect(center=button_rect.center)
delete_burger_rect = pygame.Rect(WIDTH - 760, HEIGHT - 150, 150, 50)

# Фоны
colors = {
    "gray": (70, 70, 70),
    "LightBlue": (173, 216, 230),
    "Sienna": (160, 82, 45),
}
rectangles = [
    (0, 0, WIDTH, HEIGHT, "gray"),
    (0, 0, WIDTH, HEIGHT - 80, "Sienna"),
    (0, 0, WIDTH, HEIGHT - 300, "LightBlue"),
]

# Зоны
bun_top_zone = pygame.Rect(50, 50, 100, 100)
bun_bottom_zone = pygame.Rect(200, 50, 100, 100)
lettuce_zone = pygame.Rect(350, 50, 100, 100)
cheese_zone = pygame.Rect(500, 50, 100, 100)
meat_zone = pygame.Rect(650, 50, 100, 100)
burger_zone = pygame.Rect(200, 300, 400, 200)

# Загрузка изображений с заданным размером
def load_image(name, width, height):
    try:
        image = pygame.image.load(name).convert_alpha()
        return pygame.transform.scale(image, (width, height))
    except pygame.error as e:
        print(f"Не удалось загрузить изображение {name}: {e}")
        return None

cooked_meat_image = load_image('cooked_meat.png', 100, 100)
bun_bottom_image = load_image('bun_bottom.png', 100, 100)
bun_top_image = load_image('bun_top.png', 100, 100)
cheese_image = load_image('cheese.png', 100, 100)
lettuce_image = load_image('lettuce.png', 100, 100)
customer_happy_image = load_image('customer_happy.png', 500, 600)
customer_neutral_image = load_image('customer_neutral.png', 500, 600)
customer_sad_image = load_image('customer_sad.png', 500, 600)

# Кнопка сдачи заказа
submit_order_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 75, 200, 50)
submit_order_text = button_font.render("Сдать заказ", True, TEXT_COLOR)
show_percentage = False
match_percentage = 0
percentage_timer = 0

# Переменные экрана
HALL_SCREEN = 0
KITCHEN_SCREEN = 1

current_screen = HALL_SCREEN

all_products = pygame.sprite.Group()

# Классы для продуктов и зон
class Product(pygame.sprite.Sprite):
    def __init__(self, image, x, y, product_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.original_position = self.rect.topleft
        self.is_dragging = False
        self.is_placed = False
        self.product_type = product_type

    def update(self):
        if self.is_dragging:
            self.rect.center = pygame.mouse.get_pos()

    def start_drag(self):
        if not self.is_placed:
            self.is_dragging = True

    def stop_drag(self):
        self.is_dragging = False

bun_bottom = Product(bun_bottom_image, 0, 0, "Нижняя булка")
bun_top = Product(bun_top_image, 0, 0, "Верхняя булка")
cheese = Product(cheese_image, 0, 0, "Сыр")
lettuce = Product(lettuce_image, 0, 0, "Салат")
meat = Product(cooked_meat_image, 0, 0, "Мясцо")

list_products = [bun_bottom, bun_top, cheese, lettuce, meat]
orders = []

# Заказы клиентов
class Customer:
    def __init__(self):
        self.order_time = time.time()
        self.order_interval = 5
        self.orders = []
        self.reaction_start_time = 0
        self.current_reaction_image = customer_neutral_image  # Нейтральная реакция по умолчанию

    def generate_order(self):
        if time.time() - self.order_time >= self.order_interval:
            self.order_time = time.time()
            order = [bun_bottom]
            num_ingredients = random.randint(3, 5)
            for _ in range(num_ingredients):
                order.append(random.choice(list_products[2:]))  # Добавляем случайные продукты
            order.append(bun_top)
            self.orders.append(order)
            print("Новый заказ:", [product.product_type for product in order])

    def get_orders(self):
        return self.orders

    def set_reaction(self, match_percentage):
        if match_percentage > 75:
            self.current_reaction_image = customer_happy_image
        elif match_percentage > 50:
            self.current_reaction_image = customer_neutral_image
        else:
            self.current_reaction_image = customer_sad_image
        self.reaction_start_time = time.time()

    def draw_reaction(self, screen):
        if time.time() - self.reaction_start_time < 2:
            screen.blit(self.current_reaction_image, (WIDTH // 2 - 50, 0))
        else:
            self.current_reaction_image = customer_neutral_image  # Возврат к нейтральной реакции
            screen.blit(self.current_reaction_image, (WIDTH // 2 - 50, 0))

customer = Customer()

def start_screen():
    while True:
        screen.fill(WHITE)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        screen.blit(title_text, title_rect)

        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
            if mouse_click[0]:
                main_game()
        else:
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect)

        screen.blit(start_text, start_text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

def main_game():
    global current_screen, orders, show_percentage, match_percentage, percentage_timer
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    handle_mouse_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    handle_mouse_release(event.pos)

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        screen.fill(WHITE)

        if current_screen == HALL_SCREEN:
            draw_hall_screen(mouse_pos, mouse_click)
        elif current_screen == KITCHEN_SCREEN:
            draw_kitchen_screen(mouse_pos, mouse_click)

        pygame.display.flip()
        clock.tick(FPS)

def handle_mouse_click(pos):
    global current_screen
    if current_screen == KITCHEN_SCREEN:
        if bun_bottom_zone.collidepoint(pos):
            new_product = create_product(bun_bottom_image, pos[0], pos[1], "Нижняя булка")
            all_products.add(new_product)
        elif bun_top_zone.collidepoint(pos):
            new_product = create_product(bun_top_image, pos[0], pos[1], "Верхняя булка")
            all_products.add(new_product)
        elif lettuce_zone.collidepoint(pos):
            new_product = create_product(lettuce_image, pos[0], pos[1], "Салат")
            all_products.add(new_product)
        elif cheese_zone.collidepoint(pos):
            new_product = create_product(cheese_image, pos[0], pos[1], "Сыр")
            all_products.add(new_product)
        elif meat_zone.collidepoint(pos):
            new_product = create_product(cooked_meat_image, pos[0], pos[1], "Мясцо")
            all_products.add(new_product)
        for product in all_products:
            if product.rect.collidepoint(pos):
                product.start_drag()

    if current_screen == HALL_SCREEN:
        if submit_order_rect.collidepoint(pos):
            submit_order()
        
    if button_to_kitchen_rect.collidepoint(pos):
        current_screen = KITCHEN_SCREEN
    elif button_to_hall_rect.collidepoint(pos):
        current_screen = HALL_SCREEN

def handle_mouse_release(pos):
    if current_screen == KITCHEN_SCREEN:
        for product in all_products:
            if product.is_dragging:
                product.stop_drag()
                if product.rect.colliderect(burger_zone):
                    product.is_placed = True
                else:
                    all_products.remove(product)

def draw_hall_screen(mouse_pos, mouse_click):
    global orders, show_percentage, match_percentage, percentage_timer
    screen.fill(WHITE)
    customer.generate_order()
    orders = customer.get_orders()
    
    if orders:
        order = orders[0]
        order_text = order_font.render(f"Заказ:", True, BLACK)
        screen.blit(order_text, (50, 200))
        
        for j, product in enumerate(order):
            ingredient_text = order_font.render(f"  {product.product_type}", True, BLACK)
            screen.blit(ingredient_text, (50, 230 + j * 20))
    
    if show_percentage:
        percentage_text = order_font.render(f"Cходство: {match_percentage:.2f}%", True, BLACK)
        screen.blit(percentage_text, (WIDTH // 2 - 100, 200))
        if time.time() - percentage_timer > 2:
            show_percentage = False

    customer.draw_reaction(screen)
    
    if button_to_kitchen_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_to_kitchen_rect)
        if mouse_click[0]:
            current_screen = KITCHEN_SCREEN
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_to_kitchen_rect)
    screen.blit(to_kitchen_text, button_to_kitchen_rect.topleft)

    pygame.draw.rect(screen, BUTTON_COLOR, submit_order_rect)
    screen.blit(submit_order_text, submit_order_rect.topleft)

def submit_order():
    global orders, show_percentage, match_percentage, percentage_timer
    if not orders:
        return
    # Получение первого заказа
    order = orders[0]
    # Сравнение заказа с продуктами из кухни
    kitchen_products = list(all_products)  # Преобразуем группу в список для упрощения индексации
    match_count = 0
    min_length = min(len(order), len(kitchen_products))  # Находим минимальную длину для безопасного перебора
    
    for i in range(min_length):
        if order[i].product_type == kitchen_products[i].product_type:
            match_count += 1

    # Вычисление процента совпадений
    match_percentage = (match_count / len(order)) * 100 if order else 0

    # Установка реакции клиента
    customer.set_reaction(match_percentage)

    # Удаление первого заказа
    orders.pop(0)
    all_products.empty()

    # Отображение процента совпадений
    show_percentage = True
    percentage_timer = time.time()

def draw_kitchen_screen(mouse_pos, mouse_click):
    screen.fill(WHITE)
    for rect in rectangles:
        pygame.draw.rect(screen, colors[rect[4]], rect[:4])

    screen.blit(bun_top_image, bun_top_zone.topleft)
    screen.blit(bun_bottom_image, bun_bottom_zone.topleft)
    screen.blit(lettuce_image, lettuce_zone.topleft)
    screen.blit(cheese_image, cheese_zone.topleft)
    screen.blit(cooked_meat_image, meat_zone.topleft)
    pygame.draw.rect(screen, (255, 0, 0), burger_zone, 2)

    if button_to_hall_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_to_hall_rect)
        if mouse_click[0]:
            current_screen = HALL_SCREEN
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_to_hall_rect)
    screen.blit(to_hall_text, button_to_hall_rect.topleft)

    if delete_burger_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, delete_burger_rect)
        if mouse_click[0]:
            all_products.empty()
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, delete_burger_rect)
    screen.blit(delete_burger_text, delete_burger_rect.topleft)

    all_products.update()
    all_products.draw(screen)

def create_product(image, x, y, type):
    return Product(image, x, y, type)

start_screen()