"""
main.py
Punto de entrada del nodo de telemetria.

Fijese en lo que NO hay en este archivo: ni un umbral, ni un periodo,
ni una llamada a psutil, ni un if encadenado decidiendo que hacer con
cada evento. Todo eso vive en su modulo. main.py solo elige la
presentacion y arranca.

Uso:
    python main.py                    dashboard grafico (tkinter)
    python main.py --consola          dashboard de texto
    python main.py --revisar          comprueba el entorno y sale
    python main.py --silencio         arranca en modo silencioso      (LABORATORIO)
    python main.py --probar-sonidos   reproduce cada alerta una vez   (LABORATORIO)

Las opciones se pueden combinar: python main.py --consola --silencio
"""
import sys


def revisar_entorno():
    """Comprueba que todo lo necesario este instalado."""
    print("Revision del entorno")
    print("-" * 40)
    try:
        import psutil
        print(f"  psutil   OK (version {psutil.__version__})")
    except ImportError:
        print("  psutil   FALTA -> pip install psutil")
        return False
    try:
        import tkinter
        print(f"  tkinter  OK (Tk {tkinter.TkVersion})")
    except ImportError:
        print("  tkinter  FALTA -> use: python main.py --consola")
    import sensores
    activos = sensores.disponibles()
    print("-" * 40)
    for clave, modulo in sensores.LECTORES.items():
        estado = "disponible" if clave in activos else "NO disponible"
        print(f"  {modulo.ETIQUETA:<16} {estado}")
    print("-" * 40)
    print("La bateria aparece como NO disponible en computadoras de")
    print("escritorio. No es un error: es un sensor ausente y el")
    print("programa lo maneja como tal.")
    return True


def probar_sonidos():  # LABORATORIO
    """Reproduce cada alerta una vez, usando el MISMO reproductor no
    bloqueante del nodo: se encola un sonido, se espera con marcas de
    tiempo y se pasa al siguiente."""
    import time
    import alertas
    import config
    alertas.preparar()
    pendientes = list(config.ALERTAS_POR_EVENTO)
    print("Prueba de alertas sonoras")
    print("-" * 40)
    while (pendientes or alertas.estado()["en_cola"]
           or alertas.estado()["sonando"]):
        if pendientes and not alertas.estado()["en_cola"]:
            alertas.encolar(pendientes.pop(0))
        iniciada = alertas.actualizar()
        if iniciada:
            print(f"  {iniciada['evento']:<24} -> {iniciada['patron']}")
        time.sleep(config.REFRESCO_MS / config.MS_POR_SEGUNDO)
    print("-" * 40)
    print("Fin de la prueba.")


def main():
    if "--revisar" in sys.argv:
        revisar_entorno()
        return
    import alertas  # LABORATORIO
    if "--silencio" in sys.argv:  # LABORATORIO
        alertas.silenciar(True)
    if "--probar-sonidos" in sys.argv:  # LABORATORIO
        probar_sonidos()
        return
    if "--consola" in sys.argv:
        from dashboard import consola
        consola.iniciar()
        return
    try:
        from dashboard import ventana
    except ImportError:
        print("tkinter no esta disponible en este equipo.")
        print("Se inicia el dashboard de consola.")
        from dashboard import consola
        consola.iniciar()
        return
    ventana.iniciar()


if __name__ == "__main__":
    main()
