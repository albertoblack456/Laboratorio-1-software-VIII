"""
alertas/reproductor.py  (LABORATORIO: archivo nuevo)

Reproductor de alertas sonoras que NO bloquea el ciclo de monitoreo.

Como se evita el bloqueo (las tres piezas trabajan juntas):

  1. Una COLA (deque con maxlen) guarda lo que hay que sonar. encolar()
     solo anota: nunca suena ni espera.
  2. MARCAS DE TIEMPO en lugar de time.sleep(): al iniciar un sonido se
     calcula cuando termina (_fin_actual). actualizar() se llama en cada
     vuelta del ciclo, compara la hora actual con esa marca y, si ya
     termino, saca el siguiente de la cola. Si no, devuelve enseguida.
  3. La emision del sonido es ASINCRONA: en Windows se usa
     winsound.PlaySound con SND_ASYNC, que devuelve de inmediato mientras
     el sistema operativo reproduce el audio por su cuenta.

Proteccion contra saturacion: enfriamiento por patron, sin duplicados en
la cola, cola de tamano maximo y caducidad de alertas viejas.

La hora y la salida de sonido se inyectan en el constructor para poder
probar la clase con un reloj falso y sin parlantes.
"""
import os
import sys
import tempfile
import time
from collections import deque

import config
import almacenamiento as registro
from . import sintetizador

try:  # LABORATORIO
    import winsound   # solo existe en Windows
except ImportError:   # macOS y Linux: se usa la campana del sistema
    winsound = None


def _ruta_wav(clave):  # LABORATORIO
    """Ruta del WAV de un patron dentro de la carpeta temporal."""
    nombre = f"{config.SONIDO_PREFIJO_ARCHIVO}{clave}.wav"
    return os.path.join(tempfile.gettempdir(), nombre)


def _escribir_wav(clave):  # LABORATORIO
    ruta = _ruta_wav(clave)
    with open(ruta, "wb") as archivo:
        archivo.write(sintetizador.generar_wav(config.PATRONES[clave]))
    return ruta


def salida_sistema(clave):  # LABORATORIO
    """Emite el patron sin esperar a que termine.

    winsound no permite SND_MEMORY junto con SND_ASYNC, por eso el audio
    se escribe antes en un archivo temporal (ver Reproductor.preparar).
    """
    if winsound is not None:
        ruta = _ruta_wav(clave)
        if not os.path.exists(ruta):
            ruta = _escribir_wav(clave)
        winsound.PlaySound(ruta, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        sys.stdout.write("\a")   # campana del sistema
        sys.stdout.flush()


class Reproductor:  # LABORATORIO
    """Cola de alertas sonoras con temporizacion por marcas de tiempo."""

    def __init__(self, reloj=time.time, salida=salida_sistema, silencioso=None):
        self._reloj = reloj
        self._salida = salida
        self.silencioso = (config.MODO_SILENCIOSO if silencioso is None
                           else silencioso)
        # Si la cola se llena, deque descarta sola la alerta mas antigua.
        self._cola = deque(maxlen=config.ALERTAS_COLA_MAX)
        self._ultimo_por_patron = {}   # patron -> marca de su ultimo encolado
        self._sonando = None           # patron que suena ahora, o None
        self._fin_actual = 0.0         # marca en que termina el sonido actual
        self.reproducidas = 0
        self.descartadas = 0

    def preparar(self):
        """Genera de antemano los WAV, para no gastar tiempo durante el ciclo.

        Se reescriben siempre: asi un cambio en config.PATRONES se oye.
        """
        if winsound is None:
            return
        for clave in config.PATRONES:
            _escribir_wav(clave)

    def encolar(self, evento):
        """Pide el sonido de un evento. Devuelve True si quedo en la cola."""
        patron = config.ALERTAS_POR_EVENTO.get(evento)
        if patron is None:
            return False                      # este evento no suena
        ahora = self._reloj()
        ultimo = self._ultimo_por_patron.get(patron)
        if ultimo is not None and ahora - ultimo < config.ALERTAS_ENFRIAMIENTO_S:
            return False                      # enfriamiento: sono hace poco
        if any(item["patron"] == patron for item in self._cola):
            return False                      # ya esta esperando su turno
        self._cola.append({"patron": patron, "evento": evento, "marca": ahora})
        self._ultimo_por_patron[patron] = ahora
        return True

    def actualizar(self):
        """Un paso del reproductor. NO bloquea: se llama en cada ciclo.

        Devuelve el elemento que empezo a sonar en esta llamada, o None.
        """
        ahora = self._reloj()
        if self._sonando is not None and ahora >= self._fin_actual:
            self._sonando = None              # el sonido actual ya termino
        if self._sonando is not None:
            return None                       # sigue sonando: no hay nada que hacer
        while self._cola:
            item = self._cola.popleft()
            if ahora - item["marca"] > config.ALERTAS_CADUCIDAD_S:
                self.descartadas += 1         # alerta vieja: ya no sirve
                continue
            return self._iniciar(item, ahora)
        return None

    def _iniciar(self, item, ahora):
        clave = item["patron"]
        if not self.silencioso:
            try:
                self._salida(clave)           # asincrono: devuelve enseguida
            except Exception as error:
                registro.registrar_evento(
                    "FALLA", "alerta", f"No se pudo emitir el sonido: {error}")
        duracion = sintetizador.duracion_ms(config.PATRONES[clave])
        pausa = config.ALERTAS_PAUSA_MS
        self._fin_actual = ahora + (duracion + pausa) / config.MS_POR_SEGUNDO
        self._sonando = clave
        self.reproducidas += 1
        sufijo = " (modo silencioso)" if self.silencioso else ""
        registro.registrar_evento(
            "INFO", "alerta", f"Alerta sonora '{clave}'{sufijo}")
        return item

    def silenciar(self, valor):
        self.silencioso = bool(valor)
        return self.silencioso

    def alternar_silencio(self):
        return self.silenciar(not self.silencioso)

    def estado(self):
        return {
            "sonando": self._sonando,
            "en_cola": len(self._cola),
            "silencioso": self.silencioso,
            "reproducidas": self.reproducidas,
            "descartadas": self.descartadas,
        }
