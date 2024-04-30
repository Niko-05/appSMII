import cv2
import mediapipe as mp
import numpy as np
import time
import threading


ref = False

param1 = 100
param2 = 11
minRadius = 1
maxRadius = 10

instanteInicial = instanteFinal = elapsedTime = None

flautaReferencia = []

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





            

'''def tocarNota():
    global instanteFinal, instanteInicial, elapsedTime, notas 
    if(ref):
        nota = -1
        instanteFinal = time.monotonic()
        sinTapar = None
        elapsedTime = instanteFinal - instanteInicial
        if(elapsedTime >= 1):
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
            '''




def actualizar_valor1(valor):
    global param1
    param1 = valor

def actualizar_valor2(valor):
    global param2
    param2 = valor

def actualizar_valor3(valor):
    global minRadius
    minRadius = valor

def actualizar_valor4(valor):
    global maxRadius
    maxRadius = valor

def nuevaReferencia(flautaTiempoReal):
    global flautaReferencia
    flautaReferencia = flautaTiempoReal
    
    for c in flautaReferencia:
        print(str(c))

def main():

    global ref, instanteInicial, param1, param2, minRadius, maxRadius

    mp_manos = mp.solutions.hands
    manos = mp_manos.Hands()

    cap = cv2.VideoCapture(0)

    width = 640  
    height = 480

    numCirculos = 7

    rect_width = 100
    rect_height = 400
    rect_x = int((width / 2) - (rect_width / 2)) 
    rect_y = 100
    center = int(rect_width / 2)

    
   

    # Crear una ventana de OpenCV con sliders
    cv2.namedWindow('Config')
    cv2.createTrackbar('Param1', 'Config', param1, 500, actualizar_valor1)
    cv2.createTrackbar('Param2', 'Config', param2, 50, actualizar_valor2)
    cv2.createTrackbar('minRadius', 'Config', minRadius, 50, actualizar_valor3)
    cv2.createTrackbar('maxRadius', 'Config', maxRadius, 50, actualizar_valor4)

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
                if x <= center + 15 and x >= center - 15 and y > rect_y: #and y < rect_y + rect_height:
                    circlesBuenos.append((x, y, r))
                    cv2.circle(frame, (rect_x + x, rect_y + y), r, (0, 255, 0), 2)

        circlesBuenos.sort()

        if(numCirculos != len(circlesBuenos)):
            instanteInicial = time.monotonic()
            numCirculos = len(circlesBuenos)

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