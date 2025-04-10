import pygame
import pymunk
import pymunk.pygame_util
import sys
import random
import math
from pygame.constants import KMOD_SHIFT
from pygame.locals import *


class LevelSystem:
    def __init__(self):
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = 100
        self.tasks = []
        self.completed_tasks = []
        self.task_pool = [
            {"name": "Create objects", "target": 5, "reward": 50},
            {"name": "Reach speed 100", "target": 5, "reward": 100}
        ]
        self.generate_tasks()
        self.level_up_animation = 0  # Для анимации повышения уровня

    def generate_tasks(self):
        """Генерирует новые задания из пула"""
        self.tasks = random.sample(self.task_pool, 2)
        for task in self.tasks:
            task['current'] = 0

    def add_xp(self, amount):
        """Добавляет опыт и проверяет повышение уровня."""
        self.current_xp += amount
        while self.current_xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        """Повышает уровень и увеличивает требования для следующего уровня."""
        self.level += 1
        self.current_xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)  # Увеличение сложности
        self.generate_tasks()  # Генерация новых заданий
        self.level_up_animation = 255  # Запуск анимации
        print(f"Level up! You are now level {self.level}")

    def update_task(self, task_name, progress=1, extra_data=None):
        """Обновляет прогресс задания."""
        # Убедимся, что extra_data всегда является словарем
        extra_data = extra_data or {}

        for task in self.tasks:
            if task["name"] == task_name:
                if task_name == "Use all shapes":
                    used_shapes = getattr(self, '_used_shapes', set())
                    shape_type = extra_data.get('type')  # Безопасный доступ
                    if shape_type and shape_type not in used_shapes:
                        used_shapes.add(shape_type)
                        task["current"] += 1
                    setattr(self, '_used_shapes', used_shapes)
                else:
                    task["current"] += progress

                if task["current"] >= task["target"]:
                    self.complete_task(task)
                break

    def complete_task(self, task):
        """Завершает задание и выдает награду."""
        self.add_xp(task["reward"])
        self.completed_tasks.append(task)
        self.tasks.remove(task)
        print(f"Task completed: {task['name']}")
        if not self.tasks:  # Если все задания выполнены
            self.generate_tasks()

    def draw_progress(self, screen, font, is_day):
        """Отображает прогресс уровня и заданий по центру экрана."""
        center_x = screen.get_width() // 2
        y_offset = screen.get_height() // 2 - 100

        # Выбор цвета текста в зависимости от времени суток
        text_color = (0, 0, 0) if is_day else (255, 255, 255)

        # Анимация повышения уровня
        if self.level_up_animation > 0:
            level_text = font.render(f"LEVEL UP!", True, (255, 255, 0))
            level_rect = level_text.get_rect(center=(center_x, y_offset))
            alpha_surf = pygame.Surface(level_rect.size, pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, self.level_up_animation))
            level_text.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(level_text, level_rect)
            self.level_up_animation -= 5
            y_offset += 50

        # Отображение текущего уровня
        level_text = font.render(f"Level: {self.level}", True, text_color)
        xp_text = font.render(f"XP: {self.current_xp}/{self.xp_to_next_level}", True, text_color)
        level_rect = level_text.get_rect(center=(center_x, y_offset))
        screen.blit(level_text, level_rect)
        y_offset += 30
        xp_rect = xp_text.get_rect(center=(center_x, y_offset))
        screen.blit(xp_text, xp_rect)
        y_offset += 50

        # Отображение заданий
        for task in self.tasks:
            progress = min(task['current'], task['target'])
            task_text = font.render(
                f"{task['name']}: {progress}/{task['target']}",
                True, text_color
            )
            task_rect = task_text.get_rect(center=(center_x, y_offset))
            screen.blit(task_text, task_rect)
            y_offset += 30

class MainMenu:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font("minecraft_font.ttf", 48)  # Пиксельный шрифт
        self.font_items = pygame.font.Font("minecraft_font.ttf", 36)
        self.menu_items = ["NEW GAME", "EXIT"]  # Измененные названия пунктов меню
        self.selected_item = 0
        self.background_blocks = []  # Список для блоков фона
        self.generate_background()
        self.fade_alpha = 0  # Для анимации появления

    def generate_background(self):
        """Генерирует случайные блоки для фона."""
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color = random.choice([(139, 69, 19), (160, 82, 45), (210, 105, 30)])
            size = random.randint(20, 50)
            self.background_blocks.append((x, y, size, color))

    def draw_background(self):
        """Рисует движущийся фон из блоков."""
        for i, (x, y, size, color) in enumerate(self.background_blocks):
            pygame.draw.rect(self.screen, color, (x, y, size, size))
            self.background_blocks[i] = ((x - 1) % self.width, y, size, color)

    def draw(self):
        """Отрисовывает главное меню."""
        self.screen.fill((92, 148, 252))  # Небесно-голубой фон
        self.draw_background()

        # Анимация появления
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(self.fade_alpha)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        if self.fade_alpha > 0:
            self.fade_alpha -= 5

        # Заголовок
        title = self.font_title.render("PHYSICAL SANDBOX", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 4))
        self.screen.blit(title, title_rect)

        # Пункты меню
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            text = self.font_items.render(item, True, color)
            rect = text.get_rect(center=(self.width // 2, self.height // 2 + i * 50))
            self.screen.blit(text, rect)

    def handle_events(self, events):
        """Обрабатывает события в главном меню."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_item = max(0, self.selected_item - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = min(len(self.menu_items) - 1, self.selected_item + 1)
                elif event.key == pygame.K_RETURN:
                    return self.menu_items[self.selected_item]
        return None


class PhysicsSandbox:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Физическая песочница")
        # Добавляем флаг для отображения меню
        self.show_menu = True
        self.main_menu = MainMenu(self.screen, self.width, self.height)
        # Физическое пространство
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)
        # Настройки отрисовки
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.font = pygame.font.SysFont("Arial", 14)
        self.large_font = pygame.font.SysFont("Arial", 24, bold=True)
        # Цикл день/ночь
        self.day_time = 0  # 0-2400, где 600 - восход, 1800 - закат
        self.is_day = True
        self.sky_color = (135, 206, 250)  # Начальный цвет неба
        self.stars = []
        self.create_stars()
        # Создание статического пола и стен
        self.create_boundaries()
        # Список цветов для объектов
        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 0, 0), (0, 128, 0), (0, 0, 128)
        ]
        self.body_colors = {}  # {body: color}
        # Перетаскивание объектов
        self.dragging_body = None
        self.drag_joint = None
        # Глобальные силы
        self.wind_strength = 0
        self.attraction_strength = 0
        self.global_forces_enabled = True
        # Настройки объектов
        self.object_types = ["ball", "box", "polygon", "triangle"]
        self.current_object_type = 0  # Индекс в object_types
        self.object_size = 30
        self.object_mass = 45
        self.object_elasticity = 0.5
        self.object_friction = 0.5
        # Выбранный объект для редактирования
        self.selected_body = None
        self.edit_mode = False
        # Панель инструментов
        self.toolbar_rect = pygame.Rect(self.width - 210, 10, 200, 350)
        self.button_rects = []
        self.create_ui()
        # Система уровней
        self.level_system = LevelSystem()  # Tasks are generated automatically

    def create_stars(self):
        """Создает звезды для ночного неба"""
        self.stars = []
        for _ in range(200):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height // 2)
            self.stars.append((x, y))

    def update_day_night_cycle(self):
        """Обновляет цикл день/ночь"""
        self.day_time += 1
        if self.day_time > 2400:
            self.day_time = 0

        if 600 <= self.day_time < 1800:
            # День
            if not self.is_day:
                self.is_day = True
            # Плавное изменение цвета неба от светло-голубого до темно-синего
            t = (self.day_time - 600) / 1200
            r = max(0, min(255, int(135 + (25 - 135) * t)))
            g = max(0, min(255, int(206 + (102 - 206) * t)))
            b = max(0, min(255, int(250 + (50 - 250) * t)))
            self.sky_color = (r, g, b)
        else:
            # Ночь
            if self.is_day:
                self.is_day = False
            # Плавное изменение цвета неба от темно-синего до черного
            t = (self.day_time - 1800) / 600 if self.day_time >= 1800 else (self.day_time + 600) / 600
            r = max(0, min(255, int(25 + (0 - 25) * t)))
            g = max(0, min(255, int(102 + (0 - 102) * t)))
            b = max(0, min(255, int(50 + (0 - 50) * t)))
            self.sky_color = (r, g, b)

    def draw_background(self):
        """Рисует фон с циклом день/ночь"""
        # Заливка неба
        self.screen.fill(self.sky_color)

        # Рисуем солнце или луну
        sun_moon_x = self.width * (self.day_time % 2400) / 2400
        sun_moon_y = self.height // 3 - abs(self.day_time % 1200 - 600) / 600 * (self.height // 4)
        if 600 <= self.day_time < 1800:
            pygame.draw.circle(self.screen, (255, 255, 0), (int(sun_moon_x), int(sun_moon_y)), 50)
        else:
            pygame.draw.circle(self.screen, (200, 200, 200), (int(sun_moon_x), int(sun_moon_y)), 50)

        # Рисуем звезды ночью
        if not self.is_day:
            for x, y in self.stars:
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 1)

    def draw_next_object_info(self):
        """Отображает характеристики следующего объекта"""
        x_offset = self.width - 200
        y_offset = self.height - 150
        info = [
            f"Следующий объект: {self.object_types[self.current_object_type]}",
            f"Размер: {self.object_size}",
            f"Масса: {self.object_mass}",
            f"Упругость: {self.object_elasticity:.1f}",
            f"Трение: {self.object_friction:.1f}"
        ]
        for line in info:
            text = self.font.render(line, True, (0, 0, 0))
            self.screen.blit(text, (x_offset, y_offset))
            y_offset += 20

    def create_boundaries(self):
        """Создает границы (пол и стены)"""
        thickness = 20
        # Пол
        floor = pymunk.Segment(
            self.space.static_body,
            (0, self.height - thickness),
            (self.width, self.height - thickness),
            thickness
        )
        # Левая стена
        left_wall = pymunk.Segment(
            self.space.static_body,
            (0, 0),
            (0, self.height),
            thickness
        )
        # Правая стена
        right_wall = pymunk.Segment(
            self.space.static_body,
            (self.width, 0),
            (self.width, self.height),
            thickness
        )
        for wall in [floor, left_wall, right_wall]:
            wall.elasticity = 0.8
            wall.friction = 1.0
            self.space.add(wall)

    def create_ui(self):
        """Создает элементы интерфейса"""
        button_height = 30
        button_width = 180
        # Кнопки для выбора типа объекта
        types = ["Шар (1)", "Куб (2)", "Полигон (3)", "Треугольник (4)"]
        for i, text in enumerate(types):
            rect = pygame.Rect(
                self.width - button_width - 20,
                50 + i * (button_height + 10),
                button_width,
                button_height
            )
            self.button_rects.append(("type", i, rect, text))
        # Кнопки для параметров
        params = [
            ("Размер (+/-)", "size"),
            ("Масса (Q/E)", "mass"),
            ("Упругость (R/F)", "elasticity"),
            ("Трение (T/Y)", "friction")
        ]
        for i, (text, param) in enumerate(params):
            rect = pygame.Rect(
                self.width - button_width - 20,
                200 + i * (button_height + 10),
                button_width,
                button_height
            )
            self.button_rects.append((param, None, rect, text))

    def add_ball(self, pos, radius=None, mass=None, elasticity=None, friction=None):
        """Добавляет круглый объект"""
        radius = radius or self.object_size
        mass = mass or self.object_mass
        elasticity = elasticity or self.object_elasticity
        friction = friction or self.object_friction
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = pos
        shape = pymunk.Circle(body, radius)
        shape.elasticity = elasticity
        shape.friction = friction
        self.space.add(body, shape)
        color = random.choice(self.colors)
        self.body_colors[body] = color
        # Обновляем задание по созданию объектов
        self.level_system.update_task("Create objects")
        return body

    def add_box(self, pos, size=None, mass=None, elasticity=None, friction=None):
        """Добавляет квадратный объект"""
        size = size or self.object_size
        mass = mass or self.object_mass
        elasticity = elasticity or self.object_elasticity
        friction = friction or self.object_friction
        moment = pymunk.moment_for_box(mass, (size, size))
        body = pymunk.Body(mass, moment)
        body.position = pos
        shape = pymunk.Poly.create_box(body, (size, size))
        shape.elasticity = elasticity
        shape.friction = friction
        self.space.add(body, shape)
        color = random.choice(self.colors)
        self.body_colors[body] = color
        # Обновляем задание по созданию объектов
        self.level_system.update_task("Create objects")
        return body

    def add_polygon(self, pos, vertices=None, mass=None, elasticity=None, friction=None):
        """Добавляет полигональный объект"""
        mass = mass or self.object_mass
        elasticity = elasticity or self.object_elasticity
        friction = friction or self.object_friction
        if vertices is None:
            vertices = []
            for _ in range(5):
                angle = random.uniform(0, 6.28)
                radius = random.uniform(self.object_size * 0.5, self.object_size)
                vertices.append((radius * math.cos(angle), radius * math.sin(angle)))
        moment = pymunk.moment_for_poly(mass, vertices)
        body = pymunk.Body(mass, moment)
        body.position = pos
        shape = pymunk.Poly(body, vertices)
        shape.elasticity = elasticity
        shape.friction = friction
        self.space.add(body, shape)
        color = random.choice(self.colors)
        self.body_colors[body] = color
        # Обновляем задание по созданию объектов
        self.level_system.update_task("Create objects")
        return body

    def add_triangle(self, pos, size=None, mass=None, elasticity=None, friction=None):
        """Добавляет треугольный объект"""
        size = size or self.object_size
        mass = mass or self.object_mass
        elasticity = elasticity or self.object_elasticity
        friction = friction or self.object_friction
        vertices = [(0, -size), (size, size), (-size, size)]
        moment = pymunk.moment_for_poly(mass, vertices)
        body = pymunk.Body(mass, moment)
        body.position = pos
        shape = pymunk.Poly(body, vertices)
        shape.elasticity = elasticity
        shape.friction = friction
        self.space.add(body, shape)
        color = random.choice(self.colors)
        self.body_colors[body] = color
        # Обновляем задание по созданию объектов
        self.level_system.update_task("Create objects")
        return body

    def apply_global_forces(self):
        """Применяет ветер и притяжение ко всем объектам"""
        if not self.global_forces_enabled:
            return
        for body in self.space.bodies:
            if body.body_type == pymunk.Body.DYNAMIC:
                body.apply_force_at_local_point((self.wind_strength * 100, 0), (0, 0))
                body.apply_force_at_local_point((0, self.attraction_strength * 100), (0, 0))

    def handle_dragging(self):
        """Обрабатывает перетаскивание объектов мышью"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pymunk = pymunk.pygame_util.get_mouse_pos(mouse_pos)
        if pygame.mouse.get_pressed()[0]:  # ЛКМ зажата
            if not self.dragging_body:
                # Находим тело под курсором
                query = self.space.point_query_nearest(
                    mouse_pymunk, 0, pymunk.ShapeFilter()
                )
                if query and query.shape.body.body_type == pymunk.Body.DYNAMIC:
                    self.dragging_body = query.shape.body
                    self.drag_joint = pymunk.PivotJoint(
                        self.space.static_body,
                        self.dragging_body,
                        (0, 0),
                        self.dragging_body.world_to_local(mouse_pymunk)
                    )
                    self.drag_joint.max_force = 50000
                    self.space.add(self.drag_joint)
        else:
            if self.dragging_body:
                self.space.remove(self.drag_joint)
                self.drag_joint = None
                self.dragging_body = None
        if self.drag_joint:
            self.drag_joint.anchor_b = self.dragging_body.world_to_local(mouse_pymunk)

    def draw_physics_info(self):
        """Отображает физические параметры объектов в левом углу"""
        # Информация о выбранном объекте
        if self.selected_body:
            body = self.selected_body
            velocity = body.velocity
            shape = next(iter(body.shapes)) if body.shapes else None
            info = [
                f"Тип: {self.get_shape_type(body)}",
                f"Масса: {body.mass:.1f}",
                f"Скорость: ({velocity.x:.1f}, {velocity.y:.1f})",
                f"Позиция: ({body.position.x:.1f}, {body.position.y:.1f})",
            ]
            if shape:
                info.extend([
                    f"Упругость: {shape.elasticity:.1f}",
                    f"Трение: {shape.friction:.1f}"
                ])
            y_offset = 10
            for line in info:
                text = self.font.render(line, True, (0, 0, 0))
                self.screen.blit(text, (10, y_offset))
                y_offset += 20

    def get_shape_type(self, body):
        """Возвращает тип формы тела"""
        if not body.shapes:
            return "Unknown"
        shape = next(iter(body.shapes))  # Получаем первую форму из множества
        if isinstance(shape, pymunk.Circle):
            return "Ball"
        elif isinstance(shape, pymunk.Poly):
            if len(shape.get_vertices()) == 3:
                return "Triangle"
            elif len(shape.get_vertices()) == 4:
                return "Box"
            else:
                return "Polygon"
        return "Unknown"

    def draw_ui(self):
        """Отрисовывает элементы интерфейса"""
        # Панель инструментов
        pygame.draw.rect(self.screen, (200, 200, 200), self.toolbar_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.toolbar_rect, 2)
        # Заголовок
        title = self.large_font.render("Инструменты", True, (0, 0, 0))
        self.screen.blit(title, (self.toolbar_rect.x + 10, self.toolbar_rect.y + 10))
        # Кнопки
        for btn_type, btn_id, rect, text in self.button_rects:
            color = (150, 150, 255) if (btn_type == "type" and btn_id == self.current_object_type) else (200, 200, 200)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (100, 100, 100), rect, 2)
            text_surf = self.font.render(text, True, (0, 0, 0))
            self.screen.blit(text_surf, (rect.x + 10, rect.y + 8))

    def handle_ui_click(self, pos):
        """Обрабатывает клики по интерфейсу"""
        for btn_type, btn_id, rect, text in self.button_rects:
            if rect.collidepoint(pos):
                if btn_type == "type":
                    self.current_object_type = btn_id
                elif btn_type == "size":
                    self.object_size = max(10, min(100, self.object_size + (
                        10 if pygame.key.get_mods() & KMOD_SHIFT else 5)))
                elif btn_type == "mass":
                    self.object_mass = max(1, min(100,
                                                  self.object_mass + (5 if pygame.key.get_mods() & KMOD_SHIFT else 1)))
                elif btn_type == "elasticity":
                    self.object_elasticity = max(0, min(1, self.object_elasticity + (
                        0.2 if pygame.key.get_mods() & KMOD_SHIFT else 0.1)))
                elif btn_type == "friction":
                    self.object_friction = max(0, min(2, self.object_friction + (
                        0.2 if pygame.key.get_mods() & KMOD_SHIFT else 0.1)))

    def clear_all_objects(self):
        """Полностью удаляет все физические объекты"""
        # Удаляем все динамические тела
        for body in list(self.space.bodies):
            if body.body_type == pymunk.Body.DYNAMIC:  # Используем body_type вместо is_static
                self.space.remove(body)
        # Удаляем все динамические формы (на всякий случай)
        for shape in list(self.space.shapes):
            if shape.body and shape.body.body_type != pymunk.Body.STATIC:
                self.space.remove(shape)
        self.body_colors.clear()
        self.selected_body = None
        self.dragging_body = None
        if self.drag_joint:
            self.space.remove(self.drag_joint)
            self.drag_joint = None


    def run(self):
        """Основной цикл приложения"""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            if self.show_menu:
                # Обработка событий главного меню
                action = self.main_menu.handle_events(events)
                if action == "NEW GAME":
                    self.show_menu = False
                elif action == "EXIT":
                    self.running = False
                # Отрисовка главного меню
                self.main_menu.draw()
            else:
                # Основной игровой цикл
                for event in events:
                    # Добавление объектов по клику мыши
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if event.button == 1:  # ЛКМ
                            if self.toolbar_rect.collidepoint(mouse_pos):
                                self.handle_ui_click(mouse_pos)
                            else:
                                # Создание объекта
                                obj_type = self.object_types[self.current_object_type]
                                if obj_type == "ball":
                                    self.add_ball(mouse_pos)
                                elif obj_type == "box":
                                    self.add_box(mouse_pos)
                                elif obj_type == "polygon":
                                    self.add_polygon(mouse_pos)
                                elif obj_type == "triangle":
                                    self.add_triangle(mouse_pos)
                        elif event.button == 3:  # ПКМ
                            # Выбор объекта для просмотра параметров
                            mouse_pymunk = pymunk.pygame_util.get_mouse_pos(mouse_pos)
                            query = self.space.point_query_nearest(
                                mouse_pymunk, 0, pymunk.ShapeFilter()
                            )
                            if query and query.shape.body.body_type == pymunk.Body.DYNAMIC:
                                self.selected_body = query.shape.body
                    # Обработка клавиш
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.clear_all_objects()
                            self.show_menu = True
                        elif event.key == pygame.K_SPACE:
                            # Полное удаление всех объектов
                            self.clear_all_objects()
                        elif event.key == pygame.K_g:
                            self.global_forces_enabled = not self.global_forces_enabled
                        elif event.key == pygame.K_1:
                            self.current_object_type = 0  # Шар
                        elif event.key == pygame.K_2:
                            self.current_object_type = 1  # Куб
                        elif event.key == pygame.K_3:
                            self.current_object_type = 2  # Полигон
                        elif event.key == pygame.K_4:
                            self.current_object_type = 3  # Треугольник
                        elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                            self.object_size = min(100, self.object_size + 5)
                        elif event.key == pygame.K_MINUS:
                            self.object_size = max(10, self.object_size - 5)
                        elif event.key == pygame.K_q:
                            self.object_mass = min(100, self.object_mass + 1)
                        elif event.key == pygame.K_e:
                            self.object_mass = max(1, self.object_mass - 1)
                        elif event.key == pygame.K_r:
                            self.object_elasticity = min(1.0, self.object_elasticity + 0.1)
                        elif event.key == pygame.K_f:
                            self.object_elasticity = max(0, self.object_elasticity - 0.1)
                        elif event.key == pygame.K_t:
                            self.object_friction = min(2.0, self.object_friction + 0.1)
                        elif event.key == pygame.K_y:
                            self.object_friction = max(0, self.object_friction - 0.1)
                # Управление ветром и притяжением
                keys = pygame.key.get_pressed()
                if keys[pygame.K_w]:
                    self.wind_strength += 0.1
                if keys[pygame.K_s]:
                    self.wind_strength -= 0.1
                if keys[pygame.K_a]:
                    self.attraction_strength -= 0.1
                if keys[pygame.K_d]:
                    self.attraction_strength += 0.1
                # Обновление цикла день/ночь
                self.update_day_night_cycle()
                # Отрисовка фона
                self.draw_background()
                # Отрисовка объектов
                for body, color in self.body_colors.items():
                    border_color = (255, 255, 0) if body == self.selected_body else (0, 0, 0)
                    for shape in body.shapes:
                        if isinstance(shape, pymunk.Circle):
                            pygame.draw.circle(
                                self.screen, color,
                                (int(body.position.x), int(body.position.y)),
                                int(shape.radius), 0
                            )
                            pygame.draw.circle(
                                self.screen, border_color,
                                (int(body.position.x), int(body.position.y)),
                                int(shape.radius), 2
                            )
                        elif isinstance(shape, pymunk.Poly):
                            vertices = [v.rotated(body.angle) + body.position for v in shape.get_vertices()]
                            pygame.draw.polygon(self.screen, color, vertices)
                            pygame.draw.polygon(self.screen, border_color, vertices, 2)
                # Отрисовка статических объектов (границ)
                for shape in self.space.static_body.shapes:
                    if isinstance(shape, pymunk.Segment):
                        pygame.draw.line(
                            self.screen, (0, 0, 0),
                            shape.a, shape.b,
                            3
                        )
                # Применение глобальных сил
                self.apply_global_forces()
                # Перетаскивание объектов
                self.handle_dragging()
                # Отображение информации и интерфейса
                self.draw_physics_info()
                self.draw_next_object_info()
                self.draw_ui()
                # Проверка скорости для задания
                for body in self.space.bodies:
                    if body.body_type == pymunk.Body.DYNAMIC:
                        velocity = math.hypot(body.velocity.x, body.velocity.y)
                        if velocity > 100:
                            self.level_system.update_task("Reach speed 100")
                        # Проверка использования разных форм
                        shape_type = self.get_shape_type(body)
                        self.level_system.update_task("Use all shapes", {"type": shape_type})
                # Отображение прогресса уровня и заданий по центру
                self.level_system.draw_progress(self.screen, self.large_font, self.is_day)
                # Обновление физики
                dt = 1.0 / self.fps
                self.space.step(dt)
            # Обновление экрана
            pygame.display.flip()
            self.clock.tick(self.fps)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    sandbox = PhysicsSandbox()
    sandbox.run()