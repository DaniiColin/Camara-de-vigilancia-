import cv2
import utiles
import serial
import time
# import simplejson
from flask import Flask, render_template, Response, jsonify

ser= serial.Serial('/dev/ttyACM0',9600)
temp = []
hum = []
time.sleep(2)

app = Flask(__name__)

camara = cv2.VideoCapture(-1, cv2.CAP_V4L) #,cv2.CAP_V4L2,cv2.CAP_GSTREAMER 
print(camara.isOpened()) 


"""
    Configuraciones de vídeo
"""
FRAMES_VIDEO = 20.0
RESOLUCION_VIDEO = (1280, 720)

UBICACION_LETRA = (0, 15)
FUENTE_LETRA = cv2.FONT_HERSHEY_PLAIN
TAMAÑO_LETRA= 1
COLOR_LETRA = (0, 0, 0)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA
fourcc = cv2.VideoWriter_fourcc(*'XVID')
archivo_video = None
grabando = False



def agregar_fecha_hora_frame(frame):
    cv2.putText(frame, utiles.fecha_y_hora(), UBICACION_LETRA, FUENTE_LETRA,
                TAMAÑO_LETRA, COLOR_LETRA, GROSOR_TEXTO, TIPO_LINEA_TEXTO)

def generador_frames():
    while True:
        ok, imagen = obtener_frame_camara()
        if not ok:
            break
        else:
            # Regresar la imagen en modo de respuesta HTTP
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + imagen + b"\r\n"


def obtener_frame_camara():
    ok, frame = camara.read()
    if not ok:
        return False, None
    agregar_fecha_hora_frame(frame)
    # Escribir en el vídeo en caso de que se esté grabando
    if grabando and archivo_video is not None:
        archivo_video.write(frame)
    # Codificar la imagen como JPG
    _, bufer = cv2.imencode(".jpg", frame)
    imagen = bufer.tobytes()

    return True, imagen


# Cuando visiten la ruta
@app.route("/streaming_camara")
def streaming_camara():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Cuando toman la foto
@app.route("/tomar_foto_descargar")
def descargar_foto():
    ok, frame = obtener_frame_camara()
    if not ok:
        abort(500)
        return
    respuesta = Response(frame)
    respuesta.headers["Content-Type"] = "image/jpeg"
    respuesta.headers["Content-Transfer-Encoding"] = "Binary"
    respuesta.headers["Content-Disposition"] = "attachment; filename=\"foto.jpg\""
    return respuesta


@app.route("/tomar_foto_guardar")
def guardar_foto():
    nombre_foto = utiles.obtener_uuid() + ".jpg"
    ok, frame = camara.read()
    if ok:
        agregar_fecha_hora_frame(frame)
        cv2.imwrite(nombre_foto, frame)
    return jsonify({
        "ok": ok,
        "nombre_foto": nombre_foto,
    })


# Cuando visiten /, servimos el index.html
@app.route('/')
def index():
    return render_template("index.html")


@app.route("/comenzar_grabacion")
def comenzar_grabacion():
    global grabando
    global archivo_video
    if grabando and archivo_video:
        return jsonify(False)
    nombre = utiles.fecha_y_hora_para_nombre_archivo() + ".avi"
    archivo_video = cv2.VideoWriter(
        nombre, fourcc, FRAMES_VIDEO, RESOLUCION_VIDEO)
    grabando = True
    return jsonify(True)


@app.route("/detener_grabacion")
def detener_grabacion():
    global grabando
    global archivo_video
    if not grabando or not archivo_video:
        return jsonify(False)
    grabando = False
    archivo_video.release()
    archivo_video = None
    return jsonify(True)


@app.route("/estado_grabacion")
def estado_grabacion():
    return jsonify(grabando)

@app.route("/mostrarhum_temp") 
def Mostrartemp():
    while True:
        sArduino = ser.readline()
        s = sArduino.decode('UTF-8')
        s=s.rstrip()
        val=s.split('@')
        print(val)
        return jsonify(val)
        
if __name__ == "__main__":
    app.run(host='RAS49', port=5000, threaded=True) #debug=True, host="RAS49"
