import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestSeparacionDatos:
    """Pruebas para la separación de datos en entrenamiento y prueba"""

    @pytest.fixture
    def datos_completos(self):
        """Crea un DataFrame de prueba"""
        return pd.DataFrame(
            {
                "feature1": range(100),
                "feature2": range(100, 200),
                "target": range(200, 300),
            }
        )

    def test_separacion_80_20(self, datos_completos):
        """Prueba separación 80-20"""
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            datos_completos, test_size=0.2, random_state=42
        )

        assert len(train_df) == 80
        assert len(test_df) == 20
        assert len(train_df) + len(test_df) == len(datos_completos)

    def test_separacion_70_30(self, datos_completos):
        """Prueba separación 70-30"""
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            datos_completos, test_size=0.3, random_state=42
        )

        assert len(train_df) == 70
        assert len(test_df) == 30

    def test_columnas_preservadas(self, datos_completos):
        """Prueba que las columnas se preservan en ambos conjuntos"""
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            datos_completos, test_size=0.2, random_state=42
        )

        assert list(train_df.columns) == list(datos_completos.columns)
        assert list(test_df.columns) == list(datos_completos.columns)

    def test_sin_solapamiento(self, datos_completos):
        """Prueba que no hay solapamiento entre train y test"""
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            datos_completos, test_size=0.2, random_state=42
        )

        # Los índices no deben solaparse
        indices_train = set(train_df.index)
        indices_test = set(test_df.index)

        assert len(indices_train.intersection(indices_test)) == 0

    def test_proporcion_minima(self, datos_completos):
        """Prueba con proporción muy pequeña"""
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            datos_completos, test_size=0.9, random_state=42
        )

        assert len(train_df) == 10
        assert len(test_df) == 90

    def test_proporcion_maxima(self, datos_completos):
        """Prueba con proporción muy grande"""
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            datos_completos, test_size=0.01, random_state=42
        )

        assert len(train_df) == 99
        assert len(test_df) == 1

    def test_datos_pequeños(self):
        """Prueba con conjunto de datos pequeño"""
        from sklearn.model_selection import train_test_split

        datos_pequeños = pd.DataFrame(
            {"col1": [1, 2, 3, 4, 5], "col2": [10, 20, 30, 40, 50]}
        )

        train_df, test_df = train_test_split(
            datos_pequeños, test_size=0.4, random_state=42
        )

        assert len(train_df) == 3
        assert len(test_df) == 2


class TestSeleccionColumnas:
    """Pruebas para la selección de columnas de entrada y salida"""

    @pytest.fixture
    def datos_muestra(self):
        """Crea un DataFrame de muestra"""
        return pd.DataFrame(
            {
                "col_a": [1, 2, 3, 4, 5],
                "col_b": [10, 20, 30, 40, 50],
                "col_c": [100, 200, 300, 400, 500],
                "objetivo": [1000, 2000, 3000, 4000, 5000],
            }
        )

    def test_seleccionar_columnas_entrada(self, datos_muestra):
        """Prueba selección de columnas de entrada"""
        columnas_entrada = ["col_a", "col_b"]
        resultado = datos_muestra[columnas_entrada]

        assert list(resultado.columns) == columnas_entrada
        assert len(resultado.columns) == 2

    def test_seleccionar_columna_salida(self, datos_muestra):
        """Prueba selección de columna de salida"""
        columna_salida = "objetivo"
        resultado = datos_muestra[[columna_salida]]

        assert columna_salida in resultado.columns
        assert len(resultado.columns) == 1

    def test_separar(self, datos_muestra):
        """Prueba separación completa"""
        columnas_entrada = ["col_a", "col_b", "col_c"]
        columna_salida = "objetivo"

        X = datos_muestra[columnas_entrada]
        y = datos_muestra[columna_salida]

        assert len(X.columns) == 3
        assert isinstance(y, pd.Series)
        assert len(X) == len(y)

    def test_verificar_columnas_numericas(self, datos_muestra):
        """Prueba que las columnas seleccionadas son numéricas"""
        for col in datos_muestra.columns:
            assert datos_muestra[col].dtype in ["int64", "float64"]

    def test_columna_no_existe(self, datos_muestra):
        """Prueba manejo de columna que no existe"""
        try:
            datos_muestra[["columna_inexistente"]]
            assert False, "Debería lanzar KeyError"
        except KeyError:
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
