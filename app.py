import cv2
import mediapipe as mp
import numpy as np

numCirculos = 0
circle_positions = []
circle_positions_history = []

umbral_de_distancia = 45


def distancia_puntos(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)



def detectar_circulos(imagen):
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

    flute_hue = 32  # Tonos amarillos y dorados
    hue_tolerance = 18  # Permitir cierta variación en el tono
    min_saturation = 50  # Saturación mínima
    max_saturation = 255  # Saturación máxima
    min_value = 50  # Valor mínimo (brillo)
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

    param1 = 150
    param2 = 13
    minRadius = 1
    maxRadius = 10

    # Dibujar los círculos detectados en la imagen de salida
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, min(widthScreen, heightScreen) / 16, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        # Almacenar las posiciones de los círculos detectados dentro del rectángulo
        for (cx, cy, _) in circles:
            if x <= cx <= x + w and y <= cy <= y + h:  # Verificar si el círculo está dentro del rectángulo
                circle_positions.append((cx, cy))
                cv2.circle(output, (cx, cy), 5, (0, 255, 0), 2)  # Dibujar el círculo en la imagen de salida

        print("circle pos")
        print(circle_positions)
        print("-------------------")
        print("circle history")
        print(circle_positions_history)
        print("-------------------")
        
    
        # Mantén el historial de longitud history_length
        
        circle_positions_history.append(circle_positions)

        history_length = 60
        if len(circle_positions_history) > history_length:
            circle_positions_history.pop(0)
    # Combinar la imagen de la flauta con los círculos únicos detectados dentro del rectángulo
    resultado = cv2.bitwise_or(flute_only, output)

    return resultado


def main():

    mp_manos = mp.solutions.hands
    manos = mp_manos.Hands()

    cap = cv2.VideoCapture(0)

    width = 640  
    height = 480  

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break
    
        frame = cv2.resize(frame, (width, height))

        frame_deteccion_manos = frame
        frame_deteccion_circulos = frame

        frame_rgb = cv2.cvtColor(frame_deteccion_manos, cv2.COLOR_BGR2RGB)

        results = manos.process(frame_rgb)

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                for landmark in hand_landmarks.landmark:

                    for idx, landmark in enumerate(hand_landmarks.landmark):

                        x = int(landmark.x * frame.shape[1])
                        y = int(landmark.y * frame.shape[0])

                        if idx == 8 or idx == 12 or idx == 16 or idx == 20 :  # Índice, corazón, anular, meñique

                            cv2.circle(frame_deteccion_manos, (x, y), 5, (255, 0, 0), -1)
                        
                        for circle_pos_list in circle_positions_history:
                            for circle_pos in circle_pos_list:
                                distancia = distancia_puntos((x, y), circle_pos)
                                if distancia < umbral_de_distancia:
                                    print("Agujero tapado por landmark")
        
        frame_con_circulos = detectar_circulos(frame_deteccion_circulos)

        frame_combinado = cv2.addWeighted(frame_deteccion_manos, 0.5, frame_con_circulos, 0.5, 0)

        cv2.imshow('MediaFlute', frame_combinado)

        if cv2.waitKey(10) & 0xFF == ord('q'):

            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()





'''
def detectar_circulos(imagen):

    heightScreen, widthScreen = imagen.shape[:2]

    rect_width = 100
    rect_height = 400
    rect_x = int((widthScreen / 2) - (rect_width / 2)) 
    rect_y = 100

    centro = int(rect_x + (rect_width / 2.0))

    # Dibujar el rectángulo en la imagen
    cv2.rectangle(imagen, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (255, 0, 255), 3)

    # Obtener la región de interés (ROI) dentro del rectángulo
    roi = imagen[rect_y:rect_y+rect_height, rect_x:rect_x+rect_width]

    # Convertir la ROI a escala de grises
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Aplica un desenfoque gaussiano para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    param1 = 100
    param2 = 14
    minRadius = 1
    maxRadius = 10


    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, gray.shape[0] / 16, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    # Si se detectan círculos, dibújalos
    if circles is not None:

        circles = np.round(circles[0, :]).astype("int")

        circles_filtrados = []

        for (cx, cy, cr) in circles:

           if cx <= centro + 15 and cx >= centro - 15 and cy > rect_y and cy < rect_y + rect_height:
                circles_filtrados.append((cx, cy, cr))

        #for (cx, cy, cr) in circles_filtrados:
            #cv2.circle(imagen, (cx, cy), cr, (0, 255, 0), 2)

        for(cx, cy, cr) in circles:
            cv2.circle(imagen, (rect_x + cx, rect_y + cy), cr, (0, 255, 0), 2)

    return imagen

'''

'''def detectar_circulos(imagen):
    heightScreen, widthScreen = imagen.shape[:2]

    # Convertir la imagen de BGR a HSV
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    flute_hue = 32  # Tonos amarillos y dorados
    hue_tolerance = 16  # Permitir cierta variación en el tono
    min_saturation = 50  # Saturación mínima
    max_saturation = 255  # Saturación máxima
    min_value = 50  # Valor mínimo (brillo)
    max_value = 255  # Valor máximo (brillo)

    # Calcular los límites inferiores y superiores del rango de color en HSV
    lower_color = np.array([flute_hue - hue_tolerance, min_saturation, min_value])
    upper_color = np.array([flute_hue + hue_tolerance, max_saturation, max_value])

    # Crear una máscara que identifique los píxeles dentro del rango de color
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Aplicar la máscara para aislar la flauta en la imagen original
    flute_only = cv2.bitwise_and(imagen, imagen, mask=mask)

    # Crear una lista para almacenar las posiciones de los círculos detectados
    circle_positions = []

    param1 = 150
    param2 = 13
    minRadius = 1
    maxRadius = 10
    output = np.zeros_like(imagen)

    # Dibujar los círculos detectados en la imagen de salida
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, min(widthScreen, heightScreen) / 16, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        # Almacenar las posiciones de los círculos detectados
        for (cx, cy, _) in circles:
            circle_positions.append((cx, cy))

        # Filtrar los círculos duplicados
        unique_circle_positions = []
        for pos in circle_positions:
            # Comprobar si la posición actual está lo suficientemente lejos de las posiciones únicas ya detectadas
            is_unique = True
            for unique_pos in unique_circle_positions:
                if np.linalg.norm(np.array(pos) - np.array(unique_pos)) < 10:  # Definir una distancia de tolerancia
                    is_unique = False
                    break
            if is_unique:
                unique_circle_positions.append(pos)

        # Dibujar solo los círculos únicos en la imagen de salida
        output = np.zeros_like(imagen)
        for (cx, cy) in unique_circle_positions:
            cv2.circle(output, (cx, cy), 5, (0, 255, 0), 2)

    # Combinar la imagen de la flauta con los círculos únicos detectados
    resultado = cv2.bitwise_or(flute_only, output)

    return resultado'''