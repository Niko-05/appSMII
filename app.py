import cv2
import mediapipe as mp
import numpy as np


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
                
        for(cx, cy, cr) in circles:
            cv2.circle(imagen, (rect_x + cx, rect_y + cy), cr, (0, 255, 0), 2)
    return imagen


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

        frame_con_circulos = detectar_circulos(frame_deteccion_circulos)

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
                        
                        
        
        

        frame_combinado = cv2.addWeighted(frame_deteccion_manos, 0.5, frame_con_circulos, 0.5, 0)

        cv2.imshow('MediaFlute', frame_combinado)

        if cv2.waitKey(10) & 0xFF == ord('q'):

            break
    


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()