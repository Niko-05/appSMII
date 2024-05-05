import cv2
import mediapipe as mp
import numpy as np
import time


ref = False
showRectangulo = True
showCirculos = True
showLandmarks = True
opts = False

posNotaActual = 0
notaTocada = -1

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
    "5"  : "Fa#",
    "6"  : "Sol",
    "7"  : "Sol#",
    "8"  : "La",
    "9"  : "La#",
    "10" : "Si",
    "11" : "Do Agudo"}


def drawPentagram(frame):
    cv2.line(frame, (0, 20), (640, 20), (0, 0, 0), 1, cv2.LINE_AA)
    cv2.line(frame, (0, 40), (640, 40), (0, 0, 0), 1, cv2.LINE_AA)
    cv2.line(frame, (0, 60), (640, 60), (0, 0, 0), 1, cv2.LINE_AA)
    cv2.line(frame, (0, 80), (640, 80), (0, 0, 0), 1, cv2.LINE_AA)
    cv2.line(frame, (0, 100), (640, 100), (0, 0, 0), 1, cv2.LINE_AA)

def drawNota(frame, y, x, color):
    cv2.circle(frame, (x, y), 10, color, -1, cv2.LINE_AA)

def drawMarcaSost(frame, y, x, color):
    cv2.line(frame, (x - 32, y + 10), (x - 12, y + 8), color, 2, cv2.LINE_AA)
    cv2.line(frame, (x - 32, y - 8), (x - 12, y - 10), color, 2, cv2.LINE_AA)
    cv2.line(frame, (x - 30, y + 12), (x - 30, y - 12), color, 2, cv2.LINE_AA)
    cv2.line(frame, (x - 14, y + 12), (x - 14, y - 12), color, 2, cv2.LINE_AA)

def drawNotaDo(frame, x, color):
    drawNota(frame, 120, x, color)

def drawNotaRe(frame, x, color):
    drawNota(frame, 110, x, color)

def drawNotaMi(frame, x, color):
    drawNota(frame, 100, x, color)

def drawNotaFa(frame, x, color):
    drawNota(frame, 90, x, color)

def drawNotaFaSost(frame, x, color):
    drawMarcaSost(frame, 90, x, color)
    drawNota(frame, 90, x, color)

def drawNotaSol(frame, x, color):
    drawNota(frame, 80, x, color)

def drawNotaSolSost(frame, x, color):
    drawMarcaSost(frame, 80, x, color)
    drawNota(frame, 80, x, color)

def drawNotaLa(frame, x, color):
    drawNota(frame, 70, x, color)

def drawNotaLaSost(frame, x, color):
    drawMarcaSost(frame, 70, x, color)
    drawNota(frame, 70, x, color)

def drawNotaSi(frame, x, color):
    drawNota(frame, 60, x, color)

def drawNotaDoAgudo(frame, x, color):
    drawNota(frame, 50, x, color)

def drawPartitura(frame, partitura):
    global posNotaActual, notas
    espacio = 50
    colorNotaTocada = (0, 255, 0)
    colorNotaSinTocar = (0, 0, 0)

    for i in range(len(partitura)):
        color = colorNotaTocada
        if(i >= posNotaActual):
            color = colorNotaSinTocar
        nota = partitura[i]

        if(nota == notas["1"]):
            drawNotaDo(frame, espacio, color)

        elif(nota == notas["2"]):
            drawNotaRe(frame, espacio, color)

        elif(nota == notas["3"]):
            drawNotaMi(frame, espacio, color)

        elif(nota == notas["4"]):
            drawNotaFa(frame, espacio, color)

        elif(nota == notas["5"]):
            drawNotaFaSost(frame, espacio, color)

        elif(nota == notas["6"]):
            drawNotaSol(frame, espacio, color)

        elif(nota == notas["7"]):
            drawNotaSolSost(frame, espacio, color)

        elif(nota == notas["8"]):
            drawNotaLa(frame, espacio, color)

        elif(nota == notas["9"]):
            drawNotaLaSost(frame, espacio, color)

        elif(nota == notas["10"]):
            drawNotaSi(frame, espacio, color)

        elif(nota == notas["11"]):
            drawNotaDoAgudo(frame, espacio, color)

        else:
            print("Fallo al imprimir la partitura")
        
        espacio = espacio + 50


def printNota(partitura, frame):
    if(posNotaActual > 0):
        global notas
        nota = partitura[posNotaActual - 1]

        if(nota == notas["1"]):
            cv2.putText(frame, "Do", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["2"]):
            cv2.putText(frame, "Re", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["3"]):
            cv2.putText(frame, "Mi", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["4"]):
            cv2.putText(frame, "Fa", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["5"]):
            cv2.putText(frame, "Fa#", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["6"]):
            cv2.putText(frame, "Sol", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["7"]):
            cv2.putText(frame, "Sol#", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["8"]):
            cv2.putText(frame, "La", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["9"]):
            cv2.putText(frame, "La#", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["10"]):
            cv2.putText(frame, "Si", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

        elif(nota == notas["11"]):
            cv2.putText(frame, "Do'", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA, False)

def printNotaTocada(nota, frame):
    global notas
    mensaje = ""

    if(nota == notas["1"]):
        mensaje = mensaje + "Do"

    elif(nota == notas["2"]):
        mensaje = mensaje + "Re"

    elif(nota == notas["3"]):
        mensaje = mensaje + "Mi"

    elif(nota == notas["4"]):
        mensaje = mensaje + "Fa"

    elif(nota == notas["5"]):
        mensaje = mensaje + "Fa#"

    elif(nota == notas["6"]):
        mensaje = mensaje + "Sol"

    elif(nota == notas["7"]):
        mensaje = mensaje + "Sol#"

    elif(nota == notas["8"]):
        mensaje = mensaje + "La"

    elif(nota == notas["9"]):
        mensaje = mensaje + "La#"

    elif(nota == notas["10"]):
        mensaje = mensaje + "Si"

    elif(nota == notas["11"]):
        mensaje = mensaje + "Do'"

    else:
        mensaje = mensaje + "Desconocida"
    
    cv2.putText(frame, mensaje, (400,300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2, cv2.LINE_AA, False)


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
    

def tocarNota(tapados, partitura):
    global instanteFinal, instanteInicial, elapsedTime, flautaReferencia, notas, notaTocada, posNotaActual
    if(ref):

        nota = -1
        instanteFinal = time.monotonic()
        elapsedTime = instanteFinal - instanteInicial
        sinTapar = circlesSinTapar(tapados)
        index = -1
        

        if(elapsedTime >= 2):

            if(len(flautaReferencia) == len(tapados)):
                nota = notas["1"]
                print("La nota tocada es: " + nota)
            

            elif(len(tapados) == 6 and tapados.issubset(flautaReferencia)):
                hueco4 = {flautaReferencia[3]}
                hueco1 = {flautaReferencia[0]}

                if(hueco4 == sinTapar):
                    nota = notas["5"]
                    print("La nota tocada es: " + nota)

                elif(hueco1 == sinTapar):
                    nota = notas["2"]
                    print("La nota tocada es: " + nota)       


            elif(len(tapados) == 5 and tapados.issubset(flautaReferencia)):

                nota = notas["3"]
                print("La nota tocada es: " + nota) 


            elif(len(tapados) == 4 and tapados.issubset(flautaReferencia)):
                hueco5 = {flautaReferencia[4]}

                if(set(flautaReferencia[0:2]).issubset(sinTapar) and  hueco5.issubset(sinTapar)):
                    nota = notas["7"]
                    print("La nota tocada es: " + nota)


                elif(set(flautaReferencia[0:3]) == sinTapar):

                    nota = notas["4"]
                    print("La nota tocada es: " + nota)


            elif(len(tapados) == 3 and tapados.issubset(flautaReferencia)):

                nota = notas["6"]
                print("La nota tocada es: " + nota)


            elif(len(tapados) == 2 and tapados.issubset(flautaReferencia)):
                hueco6 = {flautaReferencia[5]}

                if(set(flautaReferencia[0:5]).issubset(sinTapar)):
                    nota = notas["8"]
                    print("La nota tocada es: " + nota)

                elif(set(flautaReferencia[0:4]).issubset(sinTapar) and hueco6.issubset(sinTapar)):
                    nota = notas["9"]
                    print("La nota tocada es: " + nota)


            elif(len(tapados) == 1 and tapados.issubset(flautaReferencia)):
                hueco7 = {flautaReferencia[6]}

                if(set(flautaReferencia[0:6]).issubset(sinTapar)):
                    nota = notas["10"]
                    print("La nota tocada es: " + nota)

                elif(set(flautaReferencia[0:5]).issubset(sinTapar) and hueco7.issubset(sinTapar)):
                    nota = notas["11"]
                    print("La nota tocada es: " + nota)

            if(posNotaActual < len(partitura) - 1 and partitura[posNotaActual] == nota):
                posNotaActual = posNotaActual + 1
            
            notaTocada = nota
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

    global ref, instanteInicial, param1, param2, minRadius, maxRadius, showRectangulo, showCirculos, showLandmarks, opts, posNotaActual

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

    posNotaActual = 0
    partitura = ["Re", "Re", "La", "La", "Si", "Si", "La#"]
    

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break
        
        drawPentagram(frame)
        drawPartitura(frame, partitura)
        printNota(partitura, frame)

        # Dibujar el rectángulo en el frame
        if(showRectangulo):
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
                    if(showCirculos):
                        cv2.circle(frame, (rect_x + x, rect_y + y), r, (0, 255, 0), 2)

        circlesBuenos.sort(key = lambda x: x[1])

        if(len(circlesBuenos) == 7 and not ref):
            print("Detectada nueva referencia")
            ref = True
            nuevaReferencia(circlesBuenos)
            instanteInicial = time.monotonic()


        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #_deteccion_manos

        results = manos.process(frame_rgb)

        landmarks = set()

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                for landmark in hand_landmarks.landmark:

                    for idx, landmark in enumerate(hand_landmarks.landmark):

                        x = int(landmark.x * frame.shape[1])
                        y = int(landmark.y * frame.shape[0])

                        if idx == 8 or idx == 12 or idx == 16 or idx == 20 :  # Índice, corazón, anular, meñique
                            if(showLandmarks):
                                cv2.circle(frame, (x, y), 5, (255, 0, 0), -1) 

                            landmarks.add((x - rect_x, 480 - y))
        
        

        tocarNota(tapados(landmarks), partitura)
        printNotaTocada(notaTocada, frame)
        

        cv2.imshow("MediaFlute", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if cv2.waitKey(1) & 0xFF == ord(' '):
            print("Obteniendo nueva referencia")
            ref = False
        
        if cv2.waitKey(1) & 0xFF == ord('c'):

            if(showCirculos):
                showCirculos = False

            else:
                showCirculos = True
        
        if cv2.waitKey(1) & 0xFF == ord('l'):

            if(showLandmarks):
                showLandmarks = False
            
            else:
                showLandmarks = True

        if cv2.waitKey(1) & 0xFF == ord('r'):

            if(showRectangulo):
                showRectangulo = False
            
            else:
                showRectangulo = True           

        if cv2.waitKey(1) & 0xFF == ord('o'):
            if(not opts):
                cv2.namedWindow('Config')
                cv2.createTrackbar('Param1', 'Config', param1, 500, actualizar_valor1)
                cv2.createTrackbar('Param2', 'Config', param2, 50, actualizar_valor2)
                cv2.createTrackbar('Mín Radio', 'Config', minRadius, 50, actualizar_valor3)
                cv2.createTrackbar('Máx Radio', 'Config', maxRadius, 50, actualizar_valor4)
                opts = True
            


    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()