from PIL import Image

def remove_white_background(img):
    # Пример: изменение цвета фона на прозрачный (для PNG изображений)
    img = img.convert("RGBA")
    data = img.getdata()

    new_data = []
    for item in data:
        # Если цвет пикселя близок к белому, делаем его прозрачным
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img = img.convert("RGB")

    # Возвращаем обработанное изображение
    return img
