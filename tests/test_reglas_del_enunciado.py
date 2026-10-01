"""Comprueba por codigo las reglas de la seccion G del enunciado.  # LABORATORIO"""
import ast
import glob
import unittest

# Archivos nuevos del laboratorio: ahi NO puede haber numeros literales.
ARCHIVOS_NUEVOS = glob.glob("alertas/*.py") + ["sensores/conexion.py"]
PERMITIDOS = {0, 1}   # 0 y 1 (incluido -1) son indices y contadores, no parametros


def _arbol(ruta):
    with open(ruta, encoding="utf-8") as f:
        return ast.parse(f.read())


class PruebasReglas(unittest.TestCase):

    def test_ningun_archivo_nuevo_tiene_numeros_literales(self):
        """Regla G.6: todo numero vive en config.py."""
        for ruta in ARCHIVOS_NUEVOS:
            for nodo in ast.walk(_arbol(ruta)):
                if (isinstance(nodo, ast.Constant)
                        and isinstance(nodo.value, (int, float))
                        and not isinstance(nodo.value, bool)
                        and nodo.value not in PERMITIDOS):
                    self.fail(f"{ruta}:{nodo.lineno} tiene el literal {nodo.value}")

    def test_el_paquete_alertas_no_usa_sleep(self):
        """Objetivo 3: el reproductor no puede esperar con time.sleep()."""
        for ruta in glob.glob("alertas/*.py"):
            for nodo in ast.walk(_arbol(ruta)):
                if isinstance(nodo, ast.Attribute) and nodo.attr == "sleep":
                    self.fail(f"{ruta}:{nodo.lineno} usa sleep")

    def test_el_paquete_alertas_tiene_init(self):
        self.assertIn("alertas/__init__.py", glob.glob("alertas/*.py"))


if __name__ == "__main__":
    unittest.main()
