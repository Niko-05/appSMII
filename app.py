import cv2
import mediapipe as mp
import numpy as np


ref = False
circlesBuenos = []

def tapados(x, y, circles, margen):
    tapados = set()  # Conjunto para almacenar los círculos tapados por los landmarks
    xNorm = x - 270
    for circle in circles:
        # Comprobar si el landmark está dentro del círculo (con un margen)
        if (xNorm >= circle[0] - margen and xNorm <= circle[0] + circle[2] + margen and
            y >= circle[1] - margen and y <= circle[1] + circle[2] + margen):

            tapados.add(circle)  # Agregar el círculo tapado al conjunto
            print("Landmark tapando círculo:", circle)
    return tapados

def detectar_circulos(imagen):

    heightScreen, widthScreen = imagen.shape[:2]
    rect_width = 100
    rect_height = 400
    rect_x = int((widthScreen / 2) - (rect_width / 2)) 
    rect_y = 100
    center = int(rect_width / 2)

    global ref
    global circlesBuenos


    # Dibujar el rectángulo en la imagen
    cv2.rectangle(imagen, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (255, 0, 255), 3)


    # Obtener la región de interés (ROI) dentro del rectángulo
    roi = imagen[rect_y:rect_y+rect_height, rect_x:rect_x+rect_width]


    # Convertir la ROI a escala de grises
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)


    # Aplica un desenfoque gaussiano para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)


    param1 = 90
    param2 = 13
    minRadius = 1
    maxRadius = 10
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, gray.shape[0] / 16, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)


    # Si se detectan círculos, dibújalos
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circles_filtrados = set()
        for (cx, cy, cr) in circles:
            if cx <= center + 25 and cx >= center - 25:
                circles_filtrados.add((cx, cy, cr))
                cv2.circle(imagen, (rect_x + cx, rect_y + cy), cr, (0, 255, 0), 2)
                if len(circles_filtrados) == 7 and ref == False:
                    circlesBuenos = sorted(list(circles_filtrados), key=lambda x: x[1])
                    ref = True
                    print(circlesBuenos)
            
    return imagen


def main():

    mp_manos = mp.solutions.hands
    manos = mp_manos.Hands()

    global ref

    cap = cv2.VideoCapture(0)

    width = 640  
    height = 480  

    param1_inicial, param2_inicial = 90, 13

    # Crear una ventana de OpenCV con sliders
    '''cv2.namedWindow('MediaFlute')
    cv2.createTrackbar('Param1', 'MediaFlute', param1_inicial, 500, actualizar_parametros)
    cv2.createTrackbar('Param2', 'MediaFlute', param2_inicial, 50, actualizar_parametros)'''


    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break
    
        frame = cv2.resize(frame, (width, height))

        frame_deteccion_manos = frame
        frame_deteccion_circulos = frame

        '''param1 = cv2.getTrackbarPos('Param1', 'MediaFlute')
        param2 = cv2.getTrackbarPos('Param2', 'MediaFlute')'''

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
                            tapados(x, y, circlesBuenos, 8)
                        
                        
        
        

        frame_combinado = cv2.addWeighted(frame_deteccion_manos, 0.5, frame_con_circulos, 0.5, 0)

        cv2.imshow('MediaFlute', frame_combinado)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
        
        if cv2.waitKey(5) & 0xFF == ord(' '):
            print("Reset de referencias")
            ref = False
            


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()