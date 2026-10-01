"""Pruebas del reproductor: cola, marcas de tiempo y no bloqueo.  # LABORATORIO"""
import time
import unittest

import config
from alertas.reproductor import Reproductor


class RelojFalso:
    """Reloj que solo avanza cuando la prueba lo manda."""

    def __init__(self):
        self.ahora = 1000.0

    def __call__(self):
        return self.ahora

    def avanzar(self, segundos):
        self.ahora += segundos


class PruebasReproductor(unittest.TestCase):

    def setUp(self):
        self.reloj = RelojFalso()
        self.emitidos = []
        self.r = Reproductor(reloj=self.reloj, salida=self.emitidos.append,
                             silencioso=False)

    def _duracion_s(self, patron):
        ms = sum(d for _, d in config.PATRONES[patron])
        return (ms + config.ALERTAS_PAUSA_MS) / config.MS_POR_SEGUNDO

    # ---- cola ----------------------------------------------------------
    def test_un_evento_desconocido_no_se_encola(self):
        self.assertFalse(self.r.encolar("evento_que_no_existe"))
        self.assertEqual(self.r.estado()["en_cola"], 0)

    def test_un_evento_con_sonido_se_encola(self):
        self.assertTrue(self.r.encolar("cpu_alta"))
        self.assertEqual(self.r.estado()["en_cola"], 1)

    def test_encolar_no_suena_ni_espera(self):
        self.r.encolar("cpu_alta")
        self.assertEqual(self.emitidos, [])

    def test_no_se_duplica_un_patron_que_ya_espera(self):
        self.r.encolar("cpu_alta")
        self.assertFalse(self.r.encolar("cpu_alta"))
        self.assertEqual(self.r.estado()["en_cola"], 1)

    def test_la_cola_respeta_su_tamano_maximo(self):
        for evento in config.ALERTAS_POR_EVENTO:
            self.r.encolar(evento)
        self.assertEqual(self.r.estado()["en_cola"], config.ALERTAS_COLA_MAX)

    # ---- marcas de tiempo ------------------------------------------------
    def test_enfriamiento_bloquea_y_luego_libera(self):
        self.r.encolar("ram_alta")
        self.r.actualizar()                      # empieza a sonar
        self.reloj.avanzar(self._duracion_s("ram_alta") + 0.1)
        self.r.actualizar()                      # termina
        self.assertFalse(self.r.encolar("ram_alta"),
                         "dentro del enfriamiento no debe volver a entrar")
        self.reloj.avanzar(config.ALERTAS_ENFRIAMIENTO_S)
        self.assertTrue(self.r.encolar("ram_alta"))

    def test_un_solo_sonido_a_la_vez_y_en_orden(self):
        self.r.encolar("cpu_alta")
        self.r.encolar("ram_alta")
        self.r.actualizar()
        self.assertEqual(self.emitidos, ["cpu_alta"])
        self.reloj.avanzar(0.1)                  # todavia suena el primero
        self.r.actualizar()
        self.assertEqual(self.emitidos, ["cpu_alta"])
        self.reloj.avanzar(self._duracion_s("cpu_alta"))
        self.r.actualizar()                      # ya termino: sigue el segundo
        self.assertEqual(self.emitidos, ["cpu_alta", "ram_alta"])

    def test_una_alerta_vieja_se_descarta(self):
        self.r.encolar("cpu_alta")
        self.reloj.avanzar(config.ALERTAS_CADUCIDAD_S + 1)
        self.assertIsNone(self.r.actualizar())
        self.assertEqual(self.emitidos, [])
        self.assertEqual(self.r.estado()["descartadas"], 1)

    # ---- modo silencioso ---------------------------------------------------
    def test_en_modo_silencioso_no_se_emite_pero_la_logica_corre(self):
        self.r.silenciar(True)
        self.r.encolar("red_desconectada")
        iniciada = self.r.actualizar()
        self.assertEqual(self.emitidos, [])
        self.assertEqual(iniciada["patron"], "red_desconectada")
        self.assertEqual(self.r.estado()["sonando"], "red_desconectada")

    def test_alternar_silencio_cambia_el_modo(self):
        antes = self.r.estado()["silencioso"]
        self.assertNotEqual(self.r.alternar_silencio(), antes)

    def test_un_fallo_de_la_salida_no_tumba_el_ciclo(self):
        def salida_rota(_):
            raise OSError("sin tarjeta de sonido")
        r = Reproductor(reloj=self.reloj, salida=salida_rota, silencioso=False)
        r.encolar("cpu_alta")
        self.assertIsNotNone(r.actualizar())     # no lanza excepcion

    # ---- la condicion principal del enunciado ---------------------------------
    def test_actualizar_no_bloquea_mientras_suena_la_alerta(self):
        """Con el reloj REAL: una alerta dura ~0.6 s, pero actualizar()
        debe volver casi al instante."""
        r = Reproductor(silencioso=True)         # reloj real, sin parlantes
        r.encolar("red_desconectada")            # dura 1 segundo
        duracion = self._duracion_s("red_desconectada")
        inicio = time.perf_counter()
        r.actualizar()
        for _ in range(1000):                    # mil vueltas del ciclo
            r.actualizar()
        transcurrido = time.perf_counter() - inicio
        self.assertLess(transcurrido, duracion / 10)


if __name__ == "__main__":
    unittest.main()
