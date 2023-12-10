import tkinter as tk
from tkinter import filedialog, colorchooser, simpledialog
from PIL import Image, ImageTk, ImageDraw

class PhotoEditorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Фоторедактор")
        self.master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth(), master.winfo_screenheight()))

        self.original_image = None
        self.user_drawing = None
        self.action_stack = []

        self.draw_color = "black"
        self.line_width = 5
        self.scale_factor = tk.DoubleVar()
        self.scale_factor.set(1.0)

        self.canvas = tk.Canvas(master, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.draw = None
        self.last_x, self.last_y = 0, 0
        self.current_drawing = []

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        self.canvas.bind("<MouseWheel>", self.zoom_with_wheel)
        self.master.bind("<Control-z>", self.undo)

        self.menu_bar = tk.Menu(master)
        self.master.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.file_menu.add_command(label="Открыть", command=self.open_image)
        self.file_menu.add_command(label="Сохранить как", command=self.save_image_as)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Правка", menu=self.edit_menu)
        self.edit_menu.add_command(label="Изменить размер", command=self.resize_image)
        self.edit_menu.add_command(label="Повернуть", command=self.rotate_image)
        self.edit_menu.add_command(label="Отразить", command=self.flip_image)

        self.draw_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Рисовать", menu=self.draw_menu)
        self.draw_menu.add_command(label="Выбрать цвет", command=self.choose_color)
        self.draw_menu.add_command(label="Выбрать толщину линии", command=self.choose_line_width)

        self.zoom_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Масштаб", menu=self.zoom_menu)
        self.zoom_menu.add_command(label="Приблизить", command=self.zoom_in)
        self.zoom_menu.add_command(label="Отдалить", command=self.zoom_out)

        self.status_label = tk.Label(master, text="Добро пожаловать в Фоторедактор!", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.master.bind("<Configure>", self.on_window_resize)

        icon_size = (24, 24)
        self.icon_resize = tk.PhotoImage(file="icons/resize.png").subsample(3)
        self.icon_rotate = tk.PhotoImage(file="icons/rotate.png").subsample(3)
        self.icon_flip = tk.PhotoImage(file="icons/flip.png").subsample(3)
        self.icon_color = tk.PhotoImage(file="icons/color.png").subsample(3)
        self.icon_zoom_in = tk.PhotoImage(file="icons/zoom_in.png").subsample(3)
        self.icon_zoom_out = tk.PhotoImage(file="icons/zoom_out.png").subsample(3)

        self.button_resize = tk.Button(master, image=self.icon_resize, command=self.resize_image)
        self.button_rotate = tk.Button(master, image=self.icon_rotate, command=self.rotate_image)
        self.button_flip = tk.Button(master, image=self.icon_flip, command=self.flip_image)
        self.button_color = tk.Button(master, image=self.icon_color, command=self.choose_color)
        self.button_zoom_in = tk.Button(master, image=self.icon_zoom_in, command=self.zoom_in)
        self.button_zoom_out = tk.Button(master, image=self.icon_zoom_out, command=self.zoom_out)

        self.button_resize.pack(side=tk.TOP, pady=2)
        self.button_rotate.pack(side=tk.TOP, pady=2)
        self.button_flip.pack(side=tk.TOP, pady=2)
        self.button_color.pack(side=tk.TOP, pady=2)
        self.button_zoom_in.pack(side=tk.TOP, pady=2)
        self.button_zoom_out.pack(side=tk.TOP, pady=2)

        self.zoom_label = tk.Label(master, text="Уровень масштабирования:")
        self.zoom_label.pack(side=tk.TOP, pady=2)

    def on_window_resize(self, event):
        if self.original_image:
            self.resize_image()

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            self.original_image = Image.open(file_path)
            self.user_drawing = self.original_image.copy()
            self.display_image()
            self.status_label.config(text=f"Изображение открыто: {file_path}")

    def save_image_as(self):
        if self.original_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG файлы", "*.png")])
            if file_path:
                self.user_drawing.save(file_path)
                self.status_label.config(text=f"Изображение сохранено как: {file_path}")

    def resize_image(self):
        if self.original_image:
            width, height = self.master.winfo_width(), self.master.winfo_height()
            resized_image = self.user_drawing.resize((width, height), Image.ANTIALIAS)
            self.user_drawing = resized_image.copy()
            self.display_image()

    def rotate_image(self):
        if self.original_image:
            angle = int(tk.simpledialog.askstring("Повернуть", "Введите угол поворота:"))
            rotated_image = self.user_drawing.rotate(angle)
            self.user_drawing = rotated_image.copy()
            self.display_image()

    def flip_image(self):
        if self.original_image:
            flipped_image = self.user_drawing.transpose(Image.FLIP_LEFT_RIGHT)
            self.user_drawing = flipped_image.copy()
            self.display_image()

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.draw_color = color
            # Обновление цвета линии в ImageDraw
            self.draw = ImageDraw.Draw(self.user_drawing)
            self.draw.line([0, 0, 0, 0], fill=self.draw_color, width=self.line_width)
            self.update_canvas()  # Добавляем вызов обновления холста

    def choose_line_width(self):
        width = int(tk.simpledialog.askstring("Выбрать толщину линии", "Введите толщину линии:"))
        if width > 0:
            self.line_width = width
            # Обновление толщины линии в ImageDraw
            self.draw = ImageDraw.Draw(self.user_drawing)
            self.draw.line([0, 0, 0, 0], fill=self.draw_color, width=self.line_width)
            self.update_canvas()  # Добавляем вызов обновления холста

    def paint(self, event):
        if self.draw is None:
            # Инициализация ImageDraw при первом движении мыши
            self.draw = ImageDraw.Draw(self.user_drawing)
            x, y = event.x, event.y
            self.last_x, self.last_y = x, y
        else:
            x, y = (event.x - self.line_width), (event.y - self.line_width)
            x2, y2 = (event.x + self.line_width), (event.y + self.line_width)
            self.canvas.create_oval(x, y, x2, y2, fill=self.draw_color, width=self.line_width, outline="black")
            self.draw.line([self.last_x, self.last_y, x, y], fill=self.draw_color, width=self.line_width)
            self.last_x, self.last_y = x, y
        self.update_canvas()  # Добавляем вызов обновления холста
        self.current_drawing.append(self.user_drawing.copy())  # Добавляем текущий рисунок

    def reset(self, event):
        if self.original_image and self.user_drawing:
            if self.action_stack:
                self.action_stack.pop()
                if self.action_stack:
                    self.user_drawing = self.action_stack[-1].copy()
                else:
                    # Добавьте проверку на None перед вызовом copy()
                    if self.original_image is not None:
                        self.user_drawing = self.original_image.copy()
                    else:
                        # Если оригинальное изображение отсутствует, можете предпринять другие действия, например, не обновлять user_drawing
                        return
                self.display_image()
            else:
                # Если нет действий в стеке, отображаем оригинальное изображение
                if self.original_image is not None:
                    self.user_drawing = self.original_image.copy()
                    self.display_image()
                else:
                    # Если оригинальное изображение отсутствует, можете предпринять другие действия
                    return

    def zoom_with_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        elif event.delta < 0:
            self.zoom_out()

    def zoom_in(self):
        current_value = self.scale_factor.get()
        if current_value < 2.0:
            new_value = round(current_value + 0.1, 1)
            self.scale_factor.set(new_value)
            self.zoom_label.config(text=f"Уровень масштабирования: {new_value:.2f}")
            self.display_image()

    def zoom_out(self):
        current_value = self.scale_factor.get()
        if current_value > 0.1:
            new_value = round(current_value - 0.1, 1)
            self.scale_factor.set(new_value)
            self.zoom_label.config(text=f"Уровень масштабирования: {new_value:.2f}")
            self.display_image()

    def display_image(self):
        scale_factor = self.scale_factor.get()
        resized_image = self.user_drawing.resize(
            (int(self.user_drawing.width * scale_factor), int(self.user_drawing.height * scale_factor)),
            Image.ANTIALIAS
        )
        display_image = ImageTk.PhotoImage(resized_image)
        self.canvas.config(width=resized_image.width, height=resized_image.height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=display_image)
        self.canvas.image = display_image  # Сохраняем ссылку на изображение, чтобы избежать сборки мусора
            
    def undo(self, event):
        if self.action_stack:
            self.action_stack.pop()
            if self.action_stack:
                self.current_drawing = self.action_stack[-1].copy()
                self.user_drawing = self.current_drawing[-1].copy()
                self.display_image()


if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoEditorApp(root)
    root.mainloop()
