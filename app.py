import cv2
import mediapipe as mp
import numpy as np
import time
import threading


ref = False

param1 = 100
param2 = 11

notas = {
    "1"  : "Do",
    "2"  : "Re",
    "3"  : "Mi",
    "4"  : "Fa",
    "5"  : "Fa #",
    "6"  : "Sol",
    "7"  : "Sol #",
    "8"  : "La",
    "9"  : "La #",
    "10" : "Si",
    "11" : "Do Agudo"}



instanteInicial = instanteFinal = elapsedTime = None

def compararListas(tuplaCircles, tuplaTapados):
    posiciones_faltantes = []
    for i, tupla in enumerate(tuplaCircles):
        if tupla not in tuplaTapados:
            posiciones_faltantes.append(i)
    return posiciones_faltantes

def tapados(x, y, circles, margen):
    global circlesTapados  # Conjunto para almacenar los círculos tapados por los landmarks
    xNorm = x - 270
    for circle in circles:
        # Comprobar si el landmark está dentro del círculo (con un margen)
        if (xNorm >= circle[0] - margen and xNorm <= circle[0] + circle[2] + margen and
            y >= circle[1] - margen and y <= circle[1] + circle[2] + margen):

            circlesTapados.add(circle)  # Agregar el círculo tapado al conjunto
            
            

def tocarNota():
    global circlesTapados, circlesBuenos, instanteFinal, instanteInicial, elapsedTime, notas 
    if(ref):
        nota = -1
        instanteFinal = time.monotonic()
        sinTapar = compararListas(circlesBuenos, circlesTapados)
        elapsedTime = instanteFinal - instanteInicial
        if(elapsedTime >= 1):
            print(" ")
            print("Circles tapados: " + str(circlesTapados))
            print("--------------------------------------")
            print("Circles buenos: " + str(circlesBuenos))
            print(" ")
            print("--------------------------------------")
            print("Comparacion: " + str(sinTapar))
            print(" ")
            print("--------------------------------------")
            print("--------------------------------------")
            if(len(circlesTapados) == len(circlesBuenos)):
                nota = notas["1"]
                print("La nota tocada es: " + nota)
            
            elif(len(circlesTapados) == 6):
                if(3 in sinTapar):
                    nota = notas["5"]
                    print("La nota tocada es: " + nota)

                elif(0 in sinTapar):
                    nota = notas["2"]
                    print("La nota tocada es: " + nota)        

            elif(len(circlesTapados) == 5 and [0, 1] in sinTapar):
                nota = notas["3"]
                print("La nota tocada es: " + nota) 

            elif(len(circlesTapados) == 4):
                if([0, 1, 4] in sinTapar):
                    nota = notas["7"]
                    print("La nota tocada es: " + nota)
                elif([0, 1, 2] in sinTapar):
                    nota = notas["4"]
                    print("La nota tocada es: " + nota)

            elif(len(circlesTapados) == 3 and [0, 1, 2, 3]):
                nota = notas["6"]
                print("La nota tocada es: " + nota)

            elif(len(circlesTapados) == 2):
                if([0, 1, 2, 3, 4] in sinTapar):
                    nota = notas["8"]
                    print("La nota tocada es: " + nota)

                elif([0, 1, 2, 3, 5] in sinTapar):
                    nota = notas["9"]
                    print("La nota tocada es: " + nota)
            
            elif(len(circlesTapados) == 1):
                if([0, 1, 2, 3, 4, 5] in sinTapar):
                    nota = notas["10"]
                    print("La nota tocada es: " + nota)

                elif([0, 1, 2, 3, 4, 6] in sinTapar):
                    nota = notas["11"]
                    print("La nota tocada es: " + nota)
            
            else:
                print("Nota no detectada. Por favor pon tus manos correctamente")

            instanteInicial = time.monotonic()
            circlesTapados = set()

def detectar_circulos(imagen):

    heightScreen, widthScreen = imagen.shape[:2]
    rect_width = 100
    rect_height = 400
    rect_x = int((widthScreen / 2) - (rect_width / 2)) 
    rect_y = 100
    center = int(rect_width / 2)

    global ref, circlesBuenos, instanteInicial 


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
            if cx <= center + 10 and cx >= center - 10:
                circles_filtrados.add((cx, cy, cr))
                cv2.circle(imagen, (rect_x + cx, rect_y + cy), cr, (0, 255, 0), 2)
                if len(circles_filtrados) == 7 and ref == False:
                    circles 
                    circlesBuenos = sorted(list(circles_filtrados), key=lambda x: x[1])
                    ref = True
                    print(circlesBuenos)
                    instanteInicial = time.monotonic()
            
    return imagen


def actualizar_valor1(valor):
    global param1
    param1 = valor

def actualizar_valor2(valor):
    global param2
    param2 = valor


def main():

    mp_manos = mp.solutions.hands
    manos = mp_manos.Hands()

    global ref, instanteInicial, circlesTapados, param1, param2

    cap = cv2.VideoCapture(0)

    width = 640  
    height = 480

    numCirculos = 7

    rect_width = 100
    rect_height = 400
    rect_x = int((width / 2) - (rect_width / 2)) 
    rect_y = 100
    center = int(rect_width / 2)

    
    minRadius = 1
    maxRadius = 10

    # Crear una ventana de OpenCV con sliders
    cv2.namedWindow('Config')
    cv2.createTrackbar('Param1', 'Config', param1, 500, actualizar_valor1)
    cv2.createTrackbar('Param2', 'Config', param2, 50, actualizar_valor2)

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        # Dibujar el rectángulo en el frame
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_width, rect_y + rect_height), (255, 0, 255), 3)

        # Obtener la región de interés (ROI) dentro del rectángulo
        roi = frame[rect_y:rect_y+rect_height, rect_x:rect_x+rect_width]

        # Convertir la ROI a escala de grises
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Aplica un desenfoque gaussiano para reducir el ruido
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, gray.shape[0] / 16, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)


        circlesBuenos = []
        if circles is not None:
            circle = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circle:
                if x <= center + 15 and x >= center - 15:# and y > rect_y and y < rect_y + rect_height:
                    circlesBuenos.append((x, y, r))
                    cv2.circle(frame, (rect_x + x, rect_y + y), r, (0, 255, 0), 2)

        circlesBuenos.sort()

        if(numCirculos != len(circlesBuenos)):
            instanteInicial = time.monotonic()
            numCirculos = len(circlesBuenos)


        '''param1 = cv2.getTrackbarPos('Param1', 'MediaFlute')
        param2 = cv2.getTrackbarPos('Param2', 'MediaFlute')'''

        #frame_con_circulos = detectar_circulos(frame_deteccion_circulos)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #_deteccion_manos

        results = manos.process(frame_rgb)

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                for landmark in hand_landmarks.landmark:

                    for idx, landmark in enumerate(hand_landmarks.landmark):

                        x = int(landmark.x * frame.shape[1])
                        y = int(landmark.y * frame.shape[0])

                        if idx == 8 or idx == 12 or idx == 16 or idx == 20 :  # Índice, corazón, anular, meñique

                            cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)      
                        
        #tocarNota()
        
        
        
        #frame_combinado = cv2.addWeighted(frame_deteccion_manos, 0.5, frame_con_circulos, 0.5, 0)
        #frame = cv2.resize(frame, (width, height))

        cv2.imshow("MediaFlute", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
        
        if cv2.waitKey(5) & 0xFF == ord(' '):
            print("Reset de referencias")
            ref = False
            


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()