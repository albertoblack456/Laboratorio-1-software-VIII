"""
alertas/sintetizador.py  (LABORATORIO: archivo nuevo)

Convierte un patron de notas en un archivo WAV en memoria.

Responsabilidad unica: generar el audio. No reproduce, no decide cuando
suena y no conoce los eventos. Solo usa la biblioteca estandar (math,
wave, struct, io): no hace falta instalar nada mas.

Un patron es una secuencia de notas (frecuencia_hz, duracion_ms); una
frecuencia de 0 es un silencio.
"""
import io
import math
import struct
import wave

import config


def _muestras_de(duracion_ms):  # LABORATORIO
    """Cantidad de muestras que dura una nota."""
    return int(config.SONIDO_TASA_MUESTREO * duracion_ms / config.MS_POR_SEGUNDO)


def _nota(frecuencia, duracion_ms):  # LABORATORIO
    """Lista de muestras enteras de una nota (onda senoidal)."""
    total = _muestras_de(duracion_ms)
    if frecuencia <= 0:
        return [0] * total
    rampa = max(1, _muestras_de(config.SONIDO_RAMPA_MS))
    muestras = []
    for i in range(total):
        # Entrada y salida suaves: sin ellas se oye un "clic" en cada nota.
        envolvente = min(1.0, i / rampa, (total - 1 - i) / rampa)
        onda = math.sin(math.tau * frecuencia * i / config.SONIDO_TASA_MUESTREO)
        muestras.append(int(config.SONIDO_AMPLITUD * envolvente * onda))
    return muestras


def duracion_ms(patron):  # LABORATORIO
    """Duracion total del patron en milisegundos."""
    return sum(duracion for _, duracion in patron)


def generar_wav(patron):  # LABORATORIO
    """Devuelve los bytes de un WAV mono de 16 bits con el patron."""
    muestras = []
    for frecuencia, duracion in patron:
        muestras.extend(_nota(frecuencia, duracion))
    memoria = io.BytesIO()
    with wave.open(memoria, "wb") as archivo:
        archivo.setnchannels(config.SONIDO_CANALES)
        archivo.setsampwidth(config.SONIDO_BYTES_POR_MUESTRA)
        archivo.setframerate(config.SONIDO_TASA_MUESTREO)
        archivo.writeframes(struct.pack(f"<{len(muestras)}h", *muestras))
    return memoria.getvalue()
