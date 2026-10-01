"""
Paquete alertas  (LABORATORIO: paquete nuevo)
---------------------------------------------
Reaccion sonora a los eventos del nodo de telemetria.

    sintetizador.py   genera el audio de cada patron (solo biblioteca estandar)
    reproductor.py    cola + marcas de tiempo: suena sin bloquear el ciclo

El resto del programa solo necesita cinco funciones:

    encolar(evento)       pide el sonido de un evento (no suena ni espera)
    actualizar()          un paso del reproductor, se llama en cada ciclo
    estado()              que suena, cuanto hay en cola, modo silencioso
    silenciar(valor)      fija el modo silencioso
    alternar_silencio()   cambia entre sonido y silencio

Los sonidos, los tiempos y los umbrales viven en config.py.
"""
from .reproductor import Reproductor

_instancia = Reproductor()   # LABORATORIO: un unico reproductor para el nodo


def preparar():
    _instancia.preparar()


def encolar(evento):
    return _instancia.encolar(evento)


def actualizar():
    return _instancia.actualizar()


def estado():
    return _instancia.estado()


def silenciar(valor):
    return _instancia.silenciar(valor)


def alternar_silencio():
    return _instancia.alternar_silencio()
