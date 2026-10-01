"""Pruebas del sensor y del detector de conexion de red.  # LABORATORIO"""
import unittest
from types import SimpleNamespace
from unittest import mock

import config
from eventos import detectores
from sensores import conexion


def lectura(conectado):
    return {"valor": int(conectado), "unidad": "if", "porcentaje": 0.0,
            "detalle": "", "extra": {"conectado": conectado, "interfaces": []}}


class PruebasDetectorConexion(unittest.TestCase):

    def setUp(self):
        detectores._estado["conexion"] = None
        detectores._estado["red_desde"] = 0.0
        detectores._estado["red_aviso"] = 0.0
        detectores._estado["alarma"].clear()
        parche = mock.patch("eventos.detectores.time")
        self.tiempo = parche.start().time
        self.addCleanup(parche.stop)
        self.tiempo.return_value = 1000.0

    def _detectar(self, conectado, en=None):
        if en is not None:
            self.tiempo.return_value = en
        return detectores.detectar("conexion", lectura(conectado))

    def nombres(self, eventos):
        return [nombre for nombre, _ in eventos]

    def test_la_primera_lectura_no_genera_evento(self):
        self.assertEqual(self._detectar(True), [])

    def test_estable_y_conectado_no_genera_eventos(self):
        self._detectar(True)
        self.assertEqual(self._detectar(True, en=1050.0), [])

    def test_al_caer_la_red_hay_un_evento_de_flanco(self):
        self._detectar(True)
        self.assertEqual(self.nombres(self._detectar(False, en=1010.0)),
                         ["red_desconectada"])

    def test_la_caida_no_se_repite_en_la_vuelta_siguiente(self):
        self._detectar(True)
        self._detectar(False, en=1010.0)
        self.assertEqual(self._detectar(False, en=1011.0), [])

    def test_recordatorio_solo_despues_del_periodo(self):
        self._detectar(True)
        self._detectar(False, en=1010.0)
        antes = 1010.0 + config.RED_RECORDATORIO_S - 1
        self.assertEqual(self._detectar(False, en=antes), [])
        despues = 1010.0 + config.RED_RECORDATORIO_S
        eventos = self._detectar(False, en=despues)
        self.assertEqual(self.nombres(eventos), ["red_sigue_desconectada"])

    def test_el_recordatorio_se_repite_cada_periodo(self):
        self._detectar(True)
        self._detectar(False, en=1010.0)
        t = 1010.0 + config.RED_RECORDATORIO_S
        self.assertEqual(len(self._detectar(False, en=t)), 1)
        self.assertEqual(self._detectar(False, en=t + 1), [])
        t += config.RED_RECORDATORIO_S
        self.assertEqual(len(self._detectar(False, en=t)), 1)

    def test_al_volver_la_red_hay_un_evento_y_el_dato_trae_la_duracion(self):
        self._detectar(True)
        self._detectar(False, en=1010.0)
        eventos = self._detectar(True, en=1040.0)
        self.assertEqual(self.nombres(eventos), ["red_conectada"])
        self.assertEqual(eventos[0][1]["segundos"], 30)

    def test_despues_de_recuperarse_ya_no_hay_recordatorios(self):
        self._detectar(True)
        self._detectar(False, en=1010.0)
        self._detectar(True, en=1020.0)
        self.assertEqual(self._detectar(True, en=2000.0), [])

    def test_si_el_sensor_no_responde_es_sensor_ausente(self):
        eventos = detectores.detectar("conexion", None)
        self.assertEqual(self.nombres(eventos), ["sensor_ausente"])


class PruebasSensorConexion(unittest.TestCase):

    def _interfaces(self, **estados):
        return {n: SimpleNamespace(isup=v) for n, v in estados.items()}

    def test_con_una_interfaz_real_activa_hay_conexion(self):
        falsas = self._interfaces(**{"Wi-Fi": True, "Ethernet": False})
        with mock.patch("psutil.net_if_stats", return_value=falsas):
            datos = conexion.leer()
        self.assertTrue(datos["extra"]["conectado"])
        self.assertEqual(datos["extra"]["interfaces"], ["Wi-Fi"])

    def test_el_bucle_local_y_los_adaptadores_virtuales_no_cuentan(self):
        falsas = self._interfaces(**{"lo": True,
                                     "Loopback Pseudo-Interface 1": True,
                                     "vEthernet (WSL)": True,
                                     "Wi-Fi": False})
        with mock.patch("psutil.net_if_stats", return_value=falsas):
            datos = conexion.leer()
        self.assertFalse(datos["extra"]["conectado"])
        self.assertEqual(datos["valor"], 0)

    def test_si_psutil_falla_el_sensor_devuelve_none(self):
        with mock.patch("psutil.net_if_stats", side_effect=OSError):
            self.assertIsNone(conexion.leer())

    def test_la_lectura_tiene_las_claves_estandar(self):
        falsas = self._interfaces(**{"Wi-Fi": True})
        with mock.patch("psutil.net_if_stats", return_value=falsas):
            datos = conexion.leer()
        for clave in ("valor", "unidad", "porcentaje", "detalle", "extra"):
            self.assertIn(clave, datos)


if __name__ == "__main__":
    unittest.main()
