# Nodo de telemetria - Laboratorio N.1: Alertas sonoras

Desarrollo de Software VIII - UTP / FISC. Base: Actividad en Clase N.3.
Todo lo agregado o modificado para el laboratorio esta marcado con `# LABORATORIO`.

## Instalacion

```
python -m venv entorno
entorno\Scripts\activate          # Windows
source entorno/bin/activate       # Linux y macOS
pip install -r requirements.txt
```

## Ejecucion (siempre desde la carpeta raiz del proyecto)

| Comando | Que hace |
|---|---|
| `python main.py` | Dashboard grafico (tkinter) |
| `python main.py --consola` | Dashboard de texto |
| `python main.py --silencio` | Arranca en modo silencioso (para el salon) |
| `python main.py --probar-sonidos` | Reproduce cada alerta una vez |
| `python main.py --revisar` | Comprueba el entorno |
| `python generador.py` | Genera carga para provocar eventos (2.a ventana) |
| `python -m unittest discover -v` | Pruebas unitarias |

## Estructura nueva

```
alertas/
  __init__.py       interfaz: encolar, actualizar, estado, silenciar
  sintetizador.py   genera el audio (WAV) de cada patron
  reproductor.py    cola (deque) + marcas de tiempo: no bloquea
sensores/conexion.py   nuevo sensor: hay / no hay conexion
tests/                 pruebas unitarias (unittest)
```

Sonidos, tiempos y umbrales: solo en `config.py`.
