class LevelSystem:
    def __init__(self):
        self.level = 1
        self.current_xp = 0
        self.xp_to_next_level = 100
        self.tasks = []
        self.completed_tasks = []

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
        print(f"Level up! You are now level {self.level}")

    def add_task(self, task_name, target_value, reward_xp):
        """Добавляет новое задание."""
        self.tasks.append({
            "name": task_name,
            "target": target_value,
            "current": 0,
            "reward": reward_xp
        })

    def update_task(self, task_name, progress=1):
        """Обновляет прогресс задания."""
        for task in self.tasks:
            if task["name"] == task_name:
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

    def draw_progress(self, screen, font):
        """Отображает прогресс уровня и заданий."""
        y_offset = 10
        level_text = font.render(f"Level: {self.level}", True, (0, 0, 0))
        xp_text = font.render(f"XP: {self.current_xp}/{self.xp_to_next_level}", True, (0, 0, 0))
        screen.blit(level_text, (10, y_offset))
        y_offset += 20
        screen.blit(xp_text, (10, y_offset))
        y_offset += 30
        for task in self.tasks:
            task_text = font.render(
                f"{task['name']}: {task['current']}/{task['target']}",
                True, (0, 0, 0)
            )
            screen.blit(task_text, (10, y_offset))
            y_offset += 20