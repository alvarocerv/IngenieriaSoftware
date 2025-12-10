import pandas as pd
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestColumnValidation:
    """Tests para validar que las columnas seleccionadas sean numéricas"""

    def test_columnas_numericas_validas(self):
        """Test con columnas completamente numéricas - debería pasar"""
        df = pd.DataFrame(
            {
                "edad": [25, 30, 35, 40],
                "salario": [30000, 45000, 50000, 60000],
                "años_experiencia": [2, 5, 8, 12],
            }
        )

        # Todas las columnas son numéricas
        for col in df.columns:
            valores = df[col].dropna()
            try:
                pd.to_numeric(valores, errors="raise")
                es_numerica = True
            except (ValueError, TypeError):
                es_numerica = False

            assert es_numerica, f"La columna {col} debería ser numérica"

    def test_columnas_con_nulos_validas(self):
        """Test con columnas numéricas que tienen valores nulos - debería pasar"""
        df = pd.DataFrame(
            {
                "edad": [25, None, 35, 40],
                "salario": [30000, 45000, None, 60000],
                "años_experiencia": [2, 5, 8, None],
            }
        )

        # Todas las columnas son numéricas (ignorando nulos)
        for col in df.columns:
            valores = df[col].dropna()
            try:
                pd.to_numeric(valores, errors="raise")
                es_numerica = True
            except (ValueError, TypeError):
                es_numerica = False

            assert (
                es_numerica
            ), f"La columna {col} debería ser numérica (ignorando nulos)"

    def test_columnas_con_texto_invalidas(self):
        """Test con columnas que contienen texto - deberían fallar"""
        df = pd.DataFrame(
            {
                "nombre": ["Juan", "María", "Pedro", "Ana"],
                "edad": [25, 30, 35, 40],
                "ciudad": ["Madrid", "Barcelona", "Valencia", "Sevilla"],
            }
        )

        columnas_no_numericas = []

        for col in df.columns:
            valores = df[col].dropna()
            try:
                pd.to_numeric(valores, errors="raise")
            except (ValueError, TypeError):
                columnas_no_numericas.append(col)

        assert (
            "nombre" in columnas_no_numericas
        ), "La columna 'nombre' debería ser no numérica"
        assert (
            "ciudad" in columnas_no_numericas
        ), "La columna 'ciudad' debería ser no numérica"
        assert (
            "edad" not in columnas_no_numericas
        ), "La columna 'edad' debería ser numérica"

    def test_columnas_mixtas_invalidas(self):
        """Test con columnas que mezclan números y texto - deberían fallar"""
        df = pd.DataFrame(
            {
                "datos_mixtos": [25, "treinta", 35, "cuarenta"],
                "numeros": [1, 2, 3, 4],
            }
        )

        columnas_no_numericas = []

        for col in df.columns:
            valores = df[col].dropna()
            try:
                pd.to_numeric(valores, errors="raise")
            except (ValueError, TypeError):
                columnas_no_numericas.append(col)

        assert (
            "datos_mixtos" in columnas_no_numericas
        ), "La columna 'datos_mixtos' debería ser no numérica"
        assert (
            "numeros" not in columnas_no_numericas
        ), "La columna 'numeros' debería ser numérica"

    def test_columnas_float_validas(self):
        """Test con columnas de tipo float - debería pasar"""
        df = pd.DataFrame(
            {
                "temperatura": [36.5, 37.2, 36.8, 38.1],
                "presion": [120.5, 130.2, 125.8, 128.3],
            }
        )

        # Todas las columnas son numéricas
        for col in df.columns:
            valores = df[col].dropna()
            try:
                pd.to_numeric(valores, errors="raise")
                es_numerica = True
            except (ValueError, TypeError):
                es_numerica = False

            assert es_numerica, f"La columna {col} debería ser numérica"

    def test_columnas_string_numericos_validas(self):
        """Test con strings que representan números - debería pasar"""
        df = pd.DataFrame(
            {
                "edad_str": ["25", "30", "35", "40"],
                "salario_str": ["30000", "45000", "50000", "60000"],
            }
        )

        # Los strings numéricos deberían convertirse correctamente
        for col in df.columns:
            valores = df[col].dropna()
            try:
                pd.to_numeric(valores, errors="raise")
                es_numerica = True
            except (ValueError, TypeError):
                es_numerica = False

            assert (
                es_numerica
            ), f"La columna {col} con strings numéricos debería ser convertible"
