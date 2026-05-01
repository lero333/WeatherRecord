import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Файл для хранения данных
        self.data_file = "trainings.json"

        # Список тренировок
        self.trainings = []

        # Создание интерфейса
        self.create_widgets()

        # Загрузка данных
        self.load_data()

        # Обновление таблицы
        self.update_table()

    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление тренировки", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.training_type = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога"],
                                          width=15)
        self.training_type.grid(row=0, column=3, padx=5, pady=5)
        self.training_type.set("Бег")

        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.duration_entry = ttk.Entry(input_frame, width=15)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопка добавления
        add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        add_btn.grid(row=0, column=6, padx=10, pady=5)

        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по типу
        ttk.Label(filter_frame, text="Фильтр по типу:").pack(side="left", padx=5)
        self.type_filter = ttk.Combobox(filter_frame, values=["Все", "Бег", "Плавание", "Велосипед", "Силовая", "Йога"],
                                        width=15)
        self.type_filter.set("Все")
        self.type_filter.pack(side="left", padx=5)
        self.type_filter.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").pack(side="left", padx=5)
        self.date_filter = ttk.Entry(filter_frame, width=15)
        self.date_filter.pack(side="left", padx=5)

        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.update_table)
        filter_btn.pack(side="left", padx=5)

        clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_btn.pack(side="left", padx=5)

        # Таблица для отображения тренировок
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы
        columns = ("id", "date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Настройка заголовков
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")

        # Настройка ширины колонок
        self.tree.column("id", width=50)
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)

        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Кнопка удаления
        delete_btn = ttk.Button(self.root, text="Удалить выбранную тренировку", command=self.delete_training)
        delete_btn.pack(pady=5)

        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готово", relief="sunken")
        self.status_bar.pack(fill="x", padx=10, pady=5)

    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        """Проверка длительности (положительное число)"""
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False

    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.training_type.get()
        duration = self.duration_entry.get().strip()

        # Валидация
        if not date:
            messagebox.showerror("Ошибка", "Введите дату!")
            return

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return

        if not training_type:
            messagebox.showerror("Ошибка", "Выберите тип тренировки!")
            return

        if not duration:
            messagebox.showerror("Ошибка", "Введите длительность!")
            return

        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return

        # Создание новой тренировки
        new_id = len(self.trainings) + 1
        training = {
            "id": new_id,
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }

        self.trainings.append(training)
        self.save_data()
        self.update_table()

        # Очистка полей
        self.duration_entry.delete(0, tk.END)

        self.status_bar.config(text=f"Добавлена тренировка: {training_type} - {duration} мин")

    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления!")
            return

        # Получение ID тренировки
        item = self.tree.item(selected[0])
        training_id = item['values'][0]

        # Удаление из списка
        self.trainings = [t for t in self.trainings if t['id'] != training_id]

        # Перенумерация ID
        for i, training in enumerate(self.trainings, 1):
            training['id'] = i

        self.save_data()
        self.update_table()
        self.status_bar.config(text=f"Тренировка удалена")

    def update_table(self):
        """Обновление таблицы с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Применение фильтров
        filtered_trainings = self.trainings.copy()

        # Фильтр по типу
        type_filter_value = self.type_filter.get()
        if type_filter_value != "Все":
            filtered_trainings = [t for t in filtered_trainings if t['type'] == type_filter_value]

        # Фильтр по дате
        date_filter_value = self.date_filter.get().strip()
        if date_filter_value:
            if self.validate_date(date_filter_value):
                filtered_trainings = [t for t in filtered_trainings if t['date'] == date_filter_value]
            elif date_filter_value:
                messagebox.showwarning("Предупреждение", "Неверный формат даты в фильтре!")

        # Добавление в таблицу
        for training in filtered_trainings:
            self.tree.insert("", "end",
                             values=(training['id'], training['date'], training['type'], training['duration']))

        self.status_bar.config(text=f"Показано: {len(filtered_trainings)} из {len(self.trainings)} тренировок")

    def clear_filter(self):
        """Сброс фильтров"""
        self.type_filter.set("Все")
        self.date_filter.delete(0, tk.END)
        self.update_table()

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
            return False

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
                return True
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
                self.trainings = []
                return False
        return True


def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()


if __name__ == "__main__":
    main()