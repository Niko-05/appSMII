import cv2
import mediapipe as mp
import numpy as np
import time


ref = False

param1 = 90
param2 = 13
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





def tapados(landmarks):
    global flautaReferencia
    tapados = set()

    margen = 15
    for (cx, cy, cr) in flautaReferencia:
        for (x, y) in landmarks:
            if(cx - margen <= x <= cx + margen and cy - margen <= y <= cy + margen):
                tapados.add((cx, cy, cr))

    return tapados


def circlesSinTapar(tapados):
    global flautaReferencia
    sinTapar = set()

    sinTapar = set(flautaReferencia) - tapados
    return sinTapar

def tocarNota(tapados):
    global instanteFinal, instanteInicial, elapsedTime, flautaReferencia, notas 
    if(ref):

        nota = -1
        instanteFinal = time.monotonic()
        elapsedTime = instanteFinal - instanteInicial

        sinTapar = circlesSinTapar(tapados)

        if(elapsedTime >= 1):

            if(len(flautaReferencia) == len(tapados)):
                nota = notas["1"]
                print("La nota tocada es: " + nota)
            

            elif(len(tapados) == 6 and tapados.issubset(flautaReferencia)):

                if(set(flautaReferencia[3]) in sinTapar):
                    nota = notas["5"]
                    print("La nota tocada es: " + nota)

                elif(set(flautaReferencia[0]) in sinTapar):
                    nota = notas["2"]
                    print("La nota tocada es: " + nota)        


            elif(len(tapados) == 5 and tapados.issubset(flautaReferencia)):

                nota = notas["3"]
                print("La nota tocada es: " + nota) 


            elif(len(tapados) == 4 and tapados.issubset(flautaReferencia)):

                if(set(flautaReferencia[0:1]) in sinTapar and  set(flautaReferencia[4]) in sinTapar):
                    nota = notas["7"]
                    print("La nota tocada es: " + nota)


                elif(set(flautaReferencia[0:2]) in sinTapar):

                    nota = notas["4"]
                    print("La nota tocada es: " + nota)


            elif(len(tapados) == 3 and tapados.issubset(flautaReferencia)):

                nota = notas["6"]
                print("La nota tocada es: " + nota)


            elif(len(tapados) == 2 and tapados.issubset(flautaReferencia)):

                if(set(flautaReferencia[0:4]) in sinTapar):
                    nota = notas["8"]
                    print("La nota tocada es: " + nota)

                elif(set(flautaReferencia[0:2]) in sinTapar and set(flautaReferencia[3]) in sinTapar and set(flautaReferencia[5]) in sinTapar):
                    nota = notas["9"]
                    print("La nota tocada es: " + nota)
            

            elif(len(tapados) == 1 and tapados.issubset(flautaReferencia)):

                if(set(flautaReferencia[0:5]) in sinTapar):
                    nota = notas["10"]
                    print("La nota tocada es: " + nota)

                elif(set(flautaReferencia[0:4]) in sinTapar and set(flautaReferencia[6]) in sinTapar):
                    nota = notas["11"]
                    print("La nota tocada es: " + nota)

            instanteInicial = time.monotonic()





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
                if x <= center + 15 and x >= center - 15 and y > rect_y - 30 and y < rect_y + 250:
                    circlesBuenos.append((x, y, r))
                    cv2.circle(frame, (rect_x + x, rect_y + y), r, (0, 255, 0), 2)

        circlesBuenos.sort(key = lambda x: x[1], reverse = True)
        #print(str(circlesBuenos))

        if(len(circlesBuenos) == 7 and not ref):
            print("Detectada nueva referencia")
            ref = True
            nuevaReferencia(circlesBuenos)
            instanteInicial = time.monotonic()

        '''if(numCirculos == len(circlesBuenos)):
            nuevaReferencia(circlesBuenos)'''


        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #_deteccion_manos

        results = manos.process(frame_rgb)

        landmarks = set()

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                for landmark in hand_landmarks.landmark:

                    for idx, landmark in enumerate(hand_landmarks.landmark):

                        x = int(landmark.x * frame.shape[1])
                        y = int(landmark.y * frame.shape[0])

                        if idx == 8 :#or idx == 12 or idx == 16 or idx == 20 :  # Índice, corazón, anular, meñique

                            cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)
                            '''print("----------------------")
                            print(str((x - rect_x, 480 - y)))
                            print("----------------------") '''     
                            landmarks.add((x - rect_x, 480 - y))
        
        

        tocarNota(tapados(landmarks))
        
        

        cv2.imshow("MediaFlute", frame)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
        
        if cv2.waitKey(5) & 0xFF == ord('r'):
            print(str(flautaReferencia))
            break

        if cv2.waitKey(5) & 0xFF == ord(' '):
            print("Obteniendo nueva referencia")
            if len(circlesBuenos) == 7:
                nuevaReferencia(circlesBuenos)
                instanteInicial = time.monotonic()
                ref = True
                print("Nueva referencia encontrada")

            else:
                print("No se corresponde con los agujeros de una flauta")
            
            


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()