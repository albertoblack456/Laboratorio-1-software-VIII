"""Pruebas del sintetizador de audio.  # LABORATORIO"""
import io
import unittest
import wave

import config
from alertas import sintetizador
from eventos.manejadores import MANEJADORES


class PruebasSintetizador(unittest.TestCase):

    def _abrir(self, patron):
        return wave.open(io.BytesIO(sintetizador.generar_wav(patron)), "rb")

    def test_el_wav_es_valido_y_respeta_la_configuracion(self):
        with self._abrir(config.PATRONES["cpu_alta"]) as w:
            self.assertEqual(w.getnchannels(), config.SONIDO_CANALES)
            self.assertEqual(w.getsampwidth(), config.SONIDO_BYTES_POR_MUESTRA)
            self.assertEqual(w.getframerate(), config.SONIDO_TASA_MUESTREO)

    def test_la_duracion_coincide_con_el_patron(self):
        patron = config.PATRONES["red_desconectada"]
        esperado = sum(int(config.SONIDO_TASA_MUESTREO * ms / config.MS_POR_SEGUNDO)
                       for _, ms in patron)
        with self._abrir(patron) as w:
            self.assertEqual(w.getnframes(), esperado)

    def test_una_nota_produce_sonido(self):
        with self._abrir(((440, 100),)) as w:
            datos = w.readframes(w.getnframes())
        self.assertTrue(any(datos), "una nota de 440 Hz no puede ser silencio")

    def test_la_frecuencia_cero_es_silencio(self):
        with self._abrir(((0, 100),)) as w:
            datos = w.readframes(w.getnframes())
        self.assertFalse(any(datos), "frecuencia 0 debe generar solo ceros")

    def test_duracion_ms_suma_las_notas(self):
        self.assertEqual(sintetizador.duracion_ms(((440, 100), (0, 50))), 150)


class PruebasTablaDeAlertas(unittest.TestCase):
    """La tabla de config.py debe ser coherente."""

    def test_cada_evento_apunta_a_un_patron_existente(self):
        for evento, patron in config.ALERTAS_POR_EVENTO.items():
            self.assertIn(patron, config.PATRONES, evento)

    def test_cada_evento_sonoro_tiene_manejador(self):
        for evento in config.ALERTAS_POR_EVENTO:
            self.assertIn(evento, MANEJADORES, evento)

    def test_todos_los_patrones_son_distintos(self):
        patrones = [tuple(p) for p in config.PATRONES.values()]
        self.assertEqual(len(patrones), len(set(patrones)),
                         "dos problemas distintos no pueden sonar igual")

    def test_los_eventos_pedidos_por_el_enunciado_suenan(self):
        for evento in ("cpu_alta", "ram_alta", "red_pico", "red_desconectada",
                       "red_conectada", "red_sigue_desconectada"):
            self.assertIn(evento, config.ALERTAS_POR_EVENTO)


if __name__ == "__main__":
    unittest.main()
