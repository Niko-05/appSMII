def detectar_circulos(imagen):

    global circle_positions_history

    heightScreen, widthScreen = imagen.shape[:2]

    rect_width = 100
    rect_height = 400
    rect_x = int((widthScreen / 2) - (rect_width / 2)) 
    rect_y = 100

    centro = int(rect_x + (rect_width / 2.0))
    x, y, w, h = rect_x, rect_y, rect_width, rect_height

    # Dibujar el rectángulo en la imagen
    cv2.rectangle(imagen, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (255, 0, 255), 3)

    # Convertir la imagen de BGR a HSV
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    flute_hue = 30  # Tonos amarillos y dorados
    hue_tolerance = 26  # Permitir cierta variación en el tono
    min_saturation = 0  # Saturación mínima
    max_saturation = 255  # Saturación máxima
    min_value = 0  # Valor mínimo (brillo)
    max_value = 255  # Valor máximo (brillo)

    # Calcular los límites inferiores y superiores del rango de color en HSV
    lower_color = np.array([flute_hue - hue_tolerance, min_saturation, min_value])
    upper_color = np.array([flute_hue + hue_tolerance, max_saturation, max_value])

    # Crear una máscara que identifique los píxeles dentro del rango de color
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Aplicar la máscara para aislar la flauta en la imagen original
    flute_only = cv2.bitwise_and(imagen, imagen, mask=mask)

    # Dibujar el rectángulo en la imagen de salida
    output = np.zeros_like(imagen)

    # Crear una lista para almacenar las posiciones de los círculos detectados dentro del rectángulo
    circle_positions = []

    param1 = 50
    param2 = 9
    minRadius = 1
    maxRadius = 14

    # Dibujar los círculos detectados en la imagen de salida
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, min(widthScreen, heightScreen) / 16, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        # Almacenar las posiciones de los círculos detectados dentro del rectángulo
        for (cx, cy, _) in circles:
            if x <= cx <= x + w and y <= cy <= y + h:  # Verificar si el círculo está dentro del rectángulo
                if cx <= centro + 15 and cy >= centro - 15 and cy > rect_y and cy < rect_y + rect_height:
                    circle_positions.append((cx, cy))
                    cv2.circle(output, (cx, cy), 5, (0, 255, 0), 2)  # Dibujar el círculo en la imagen de salida

    
        # Mantén el historial de longitud history_length
        if circle_positions:
            circle_positions_history.append(circle_positions)

        history_length = 20
        if len(circle_positions_history) > history_length:
            circle_positions_history.pop(0)

    # Combinar la imagen de la flauta con los círculos únicos detectados dentro del rectángulo
    resultado = cv2.bitwise_or(flute_only, output)

    return resultado

