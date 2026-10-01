"""
config.py
Parametros de configuracion del nodo de telemetria.
Todo lo que puede cambiar entre una instalacion y otra vive aqui.
Ningun otro archivo del proyecto debe contener un numero literal.
Unidad 2 - Programacion en Python para sistemas IoT
Facultad de Ingenieria de Sistemas Computacionales - UTP
"""
import os

# --------------------------------------------------------------------------
# Identificacion del nodo
# --------------------------------------------------------------------------
NODO = "laptop-alberto"  # LABORATORIO
UBICACION = "Laboratorio 3 - FISC"
ESTUDIANTE = "Alberto | Grupo IGS132/134"  # LABORATORIO

# --------------------------------------------------------------------------
# Periodos de muestreo, en segundos.
# Cada metrica tiene el suyo: leer los procesos es caro, leer la CPU no.
# --------------------------------------------------------------------------
PERIODO_RAPIDO = 1.0     # cpu, memoria, red, conexion
PERIODO_LENTO = 5.0      # disco, procesos, bateria
PERIODO_REPORTE = 30.0   # resumen periodico hacia la bitacora
REFRESCO_MS = 200        # cada cuanto refresca el dashboard (milisegundos)

# --------------------------------------------------------------------------
# Umbrales. Dos valores por metrica: uno para entrar en alarma y otro,
# mas bajo, para salir de ella. Esa diferencia es la HISTERESIS y evita
# que una lectura oscilando en el limite genere decenas de eventos falsos.
# --------------------------------------------------------------------------
CPU_ALTO = 70.0
CPU_BAJO = 50.0
CPU_NUCLEO_SATURADO = 90.0   # un nucleo individual por encima de esto
RAM_ALTA = 85.0
RAM_BAJA = 75.0
DISCO_LLENO = 90.0           # porcentaje de ocupacion
DISCO_ALIVIADO = 85.0
RED_PICO_KBS = 500.0         # kilobytes por segundo
RED_CALMA_KBS = 200.0
BATERIA_BAJA = 20.0
BATERIA_RECUPERADA = 30.0
PROCESO_PESADO = 50.0        # % de CPU de un solo proceso

# Variacion brusca entre dos muestras consecutivas: evento de anomalia.
SALTO_ANOMALO = 40.0

# --------------------------------------------------------------------------
# Ventana movil y almacenamiento
# --------------------------------------------------------------------------
VENTANA = 10             # muestras que se promedian para evaluar el umbral
MAX_EVENTOS_LOG = 200    # eventos que se conservan en pantalla
ARCHIVO_BITACORA = "bitacora.json"

# --------------------------------------------------------------------------
# Unidad de disco a vigilar. Se detecta sola segun el sistema operativo.
# --------------------------------------------------------------------------
UNIDAD_DISCO = "C:\\" if os.name == "nt" else "/"

# Cantidad de procesos que se muestran en el ranking.
TOP_PROCESOS = 8

# Procesos del sistema que no vale la pena reportar: en Linux los
# 'kworker' y 'kthread' aparecen y desaparecen constantemente y llenarian
# la bitacora de ruido.
PROCESOS_IGNORADOS = ("kworker", "kthread", "ksoftirqd", "migration",
                      "rcu_", "irq/", "svchost")

# ==========================================================================
# LABORATORIO N.1 - Alertas sonoras y conexion de red
# Todo lo nuevo (sonidos, tiempos, umbrales) vive en esta seccion.
# ==========================================================================

# --- Conexion de red (nuevo sensor "conexion") ---------------------------  # LABORATORIO
# Interfaces que NO cuentan como "estar conectado": bucle local y
# adaptadores virtuales. Se compara por prefijo, en minusculas.
INTERFACES_IGNORADAS = ("lo", "loopback", "vethernet", "docker", "veth",
                        "br-", "virbr", "vmnet", "vboxnet", "bluetooth")  # LABORATORIO
RED_RECORDATORIO_S = 10.0    # cada cuantos segundos se recuerda la caida  # LABORATORIO
PORCENTAJE_MAX = 100.0       # LABORATORIO
COLUMNAS_TARJETAS = 4        # tarjetas por fila en el dashboard  # LABORATORIO

# --- Reproductor de alertas ----------------------------------------------  # LABORATORIO
MODO_SILENCIOSO = False      # True: no suena nada, solo se simula (salon de clases)  # LABORATORIO
ALERTAS_COLA_MAX = 6         # tamano maximo de la cola (deque con maxlen)  # LABORATORIO
ALERTAS_ENFRIAMIENTO_S = 8.0 # minimo entre dos sonidos del mismo patron  # LABORATORIO
ALERTAS_CADUCIDAD_S = 20.0   # una alerta que espera mas que esto ya no sirve  # LABORATORIO
ALERTAS_PAUSA_MS = 300       # silencio entre dos alertas consecutivas  # LABORATORIO
MS_POR_SEGUNDO = 1000.0      # LABORATORIO

# --- Sintesis de audio (ondas senoidales, solo biblioteca estandar) -------  # LABORATORIO
SONIDO_TASA_MUESTREO = 22050     # muestras por segundo  # LABORATORIO
SONIDO_AMPLITUD = 12000          # volumen (maximo 32767 en 16 bits)  # LABORATORIO
SONIDO_CANALES = 1               # mono  # LABORATORIO
SONIDO_BYTES_POR_MUESTRA = 2     # 16 bits  # LABORATORIO
SONIDO_RAMPA_MS = 5              # entrada/salida suave: evita el "clic"  # LABORATORIO
SONIDO_PREFIJO_ARCHIVO = "telemetria_"  # LABORATORIO

# Cada patron es una secuencia de notas (frecuencia_hz, duracion_ms).
# Frecuencia 0 = silencio.  # LABORATORIO
PATRONES = {
    # CPU: sirena rapida alternando dos tonos agudos (urgencia)
    "cpu_alta": ((880, 120), (1320, 120), (880, 120), (1320, 120)),
    "cpu_normal": ((660, 150), (440, 250)),                 # bajada suave
    # Memoria: tres pulsos graves (pesadez)
    "ram_alta": ((220, 300), (0, 100), (220, 300), (0, 100), (220, 300)),
    "ram_normal": ((330, 200), (262, 300)),
    # Trafico de red: chirridos muy agudos y cortos (rafaga de datos)
    "red_pico": ((1500, 50), (0, 50), (1500, 50), (0, 50), (1500, 50)),
    # Conexion: bajada larga al caer, subida alegre al recuperarse
    "red_desconectada": ((660, 250), (494, 250), (370, 500)),
    "red_conectada": ((523, 120), (659, 120), (784, 250)),
    "red_recordatorio": ((1000, 80), (0, 120), (1000, 80)),  # doble bip
    # Extras
    "disco_lleno": ((300, 150), (600, 150), (300, 150)),
    "bateria_baja": ((440, 400), (0, 100), (440, 400)),
}  # LABORATORIO

# Que patron suena para cada evento. Un evento que no este aqui no suena.  # LABORATORIO
ALERTAS_POR_EVENTO = {
    "cpu_alta": "cpu_alta",
    "cpu_normal": "cpu_normal",
    "ram_alta": "ram_alta",
    "ram_normal": "ram_normal",
    "red_pico": "red_pico",
    "red_desconectada": "red_desconectada",
    "red_conectada": "red_conectada",
    "red_sigue_desconectada": "red_recordatorio",
    "disco_lleno": "disco_lleno",
    "bateria_baja": "bateria_baja",
}  # LABORATORIO
