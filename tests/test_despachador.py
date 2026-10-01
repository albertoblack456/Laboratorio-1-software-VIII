"""Pruebas de los manejadores de red y de la integracion con las alertas.  # LABORATORIO"""
import unittest
from unittest import mock

import almacenamiento as registro
from eventos import despachador
from eventos.manejadores import MANEJADORES

NUEVOS = {
    "red_desconectada": {"interfaces": 0},
    "red_conectada": {"segundos": 12, "interfaces": 1},
    "red_sigue_desconectada": {"segundos": 30},
}


class PruebasManejadoresDeRed(unittest.TestCase):

    def test_los_tres_eventos_nuevos_estan_registrados(self):
        for nombre in NUEVOS:
            self.assertIn(nombre, MANEJADORES)

    def test_cada_manejador_devuelve_nivel_y_mensaje(self):
        for nombre, dato in NUEVOS.items():
            nivel, mensaje = MANEJADORES[nombre](dato)
            self.assertIn(nivel, ("INFO", "AVISO", "ALERTA", "FALLA"))
            self.assertTrue(mensaje)

    def test_la_caida_es_una_alerta(self):
        self.assertEqual(MANEJADORES["red_desconectada"](NUEVOS["red_desconectada"])[0],
                         "ALERTA")


class PruebasIntegracionConAlertas(unittest.TestCase):

    def setUp(self):
        registro.limpiar_eventos()

    def test_atender_registra_el_evento_y_pide_el_sonido(self):
        with mock.patch("eventos.despachador.alertas.encolar") as encolar:
            creado = despachador.atender("red_desconectada",
                                         NUEVOS["red_desconectada"])
        encolar.assert_called_once_with("red_desconectada")
        self.assertEqual(creado["nivel"], "ALERTA")
        self.assertEqual(registro.eventos()[-1]["origen"], "red_desconectada")

    def test_un_evento_sin_manejador_no_pide_sonido(self):
        with mock.patch("eventos.despachador.alertas.encolar") as encolar:
            creado = despachador.atender("evento_inventado", {})
        encolar.assert_not_called()
        self.assertEqual(creado["nivel"], "FALLA")

    def test_un_manejador_defectuoso_no_pide_sonido(self):
        with mock.patch("eventos.despachador.alertas.encolar") as encolar:
            creado = despachador.atender("red_conectada", {})   # faltan claves
        encolar.assert_not_called()
        self.assertEqual(creado["nivel"], "FALLA")


if __name__ == "__main__":
    unittest.main()
