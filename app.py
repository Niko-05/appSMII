import cv2
import mediapipe as mp
import numpy as np

numCirculos = 0
circle_positions = []
circle_positions_history = []

reference_circles = []

umbral_de_distancia = 10


def distancia_puntos(p1, p2):
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def agrupar_puntos(puntos, radio):
    grupos = []
    puntos_no_asignados = puntos

    while puntos_no_asignados:
        punto_actual = puntos_no_asignados.pop()
        vecinos = [punto_actual]
        for punto in puntos_no_asignados.copy():
            if distancia_puntos(punto, punto_actual) <= radio:
                vecinos.append(punto)
                puntos_no_asignados.remove(punto)
        grupos.append(vecinos)

    return grupos

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
    

        if cv2.waitKey(1) & 0xFF == ord('r'):
           puntos = agrupar_puntos(circle_positions_history, 10)
           print(puntos)


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()