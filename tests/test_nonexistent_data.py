import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestPreprocesadoDatosInexistentes:
    """Pruebas para el preprocesado y manejo de datos inexistentes usando pandas directamente"""

    @pytest.fixture
    def datos_con_nan(self):
        """Crea un DataFrame con valores faltantes"""
        return pd.DataFrame(
            {
                "col1": [1.0, 2.0, np.nan, 4.0, 5.0],
                "col2": [10.0, np.nan, 30.0, np.nan, 50.0],
                "col3": [100.0, 200.0, 300.0, 400.0, 500.0],
            }
        )

    def test_eliminar_filas_con_nan(self, datos_con_nan):
        """Prueba eliminación de filas con valores faltantes"""
        resultado = datos_con_nan.copy()
        resultado.dropna(inplace=True)

        assert len(resultado) < len(datos_con_nan)
        assert resultado.isnull().sum().sum() == 0  # No debe haber NaN
        assert len(resultado) == 2  # Solo 2 filas completas

    def test_rellenar_con_media(self, datos_con_nan):
        """Prueba rellenar valores faltantes con la media"""
        resultado = datos_con_nan.copy()
        cols_numericas = resultado.select_dtypes(include=np.number).columns
        resultado[cols_numericas] = resultado[cols_numericas].fillna(
            resultado[cols_numericas].mean()
        )

        assert len(resultado) == len(datos_con_nan)
        assert resultado.isnull().sum().sum() == 0

        # Verificar que la media se aplicó correctamente
        media_col1_original = datos_con_nan["col1"].mean()
        assert resultado.loc[2, "col1"] == pytest.approx(
            media_col1_original, rel=1e-5
        )

    def test_rellenar_con_mediana(self, datos_con_nan):
        """Prueba rellenar valores faltantes con la mediana"""
        resultado = datos_con_nan.copy()
        cols_numericas = resultado.select_dtypes(include=np.number).columns
        resultado[cols_numericas] = resultado[cols_numericas].fillna(
            resultado[cols_numericas].median()
        )

        assert len(resultado) == len(datos_con_nan)
        assert resultado.isnull().sum().sum() == 0

        # Verificar que la mediana se aplicó correctamente
        mediana_col1_original = datos_con_nan["col1"].median()
        assert resultado.loc[2, "col1"] == pytest.approx(
            mediana_col1_original, rel=1e-5
        )

    def test_rellenar_con_constante(self, datos_con_nan):
        """Prueba rellenar valores faltantes con una constante"""
        valor_constante = 999
        resultado = datos_con_nan.copy()
        resultado.fillna(valor_constante, inplace=True)

        assert len(resultado) == len(datos_con_nan)

        # Los valores NaN deben ser reemplazados por la constante
        assert resultado.loc[2, "col1"] == valor_constante

    def test_sin_valores_faltantes(self):
        """Prueba con DataFrame sin valores faltantes"""
        datos_sin_nan = pd.DataFrame(
            {"col1": [1, 2, 3, 4, 5], "col2": [10, 20, 30, 40, 50]}
        )

        resultado = datos_sin_nan.copy()
        cols_numericas = resultado.select_dtypes(include=np.number).columns
        resultado[cols_numericas] = resultado[cols_numericas].fillna(
            resultado[cols_numericas].mean()
        )

        pd.testing.assert_frame_equal(resultado, datos_sin_nan)

    def test_columna_completamente_nula(self):
        """Prueba con una columna completamente nula"""
        datos = pd.DataFrame(
            {
                "col1": [1, 2, 3],
                "col2": [np.nan, np.nan, np.nan],
                "col3": [10, 20, 30],
            }
        )

        resultado = datos.copy()
        cols_numericas = resultado.select_dtypes(include=np.number).columns
        resultado[cols_numericas] = resultado[cols_numericas].fillna(
            resultado[cols_numericas].mean()
        )

        # La columna con todos NaN debe quedar con NaN
        assert resultado["col2"].isnull().all()
        assert not resultado["col1"].isnull().any()
        assert not resultado["col3"].isnull().any()

    def test_deteccion_valores_faltantes(self, datos_con_nan):
        """Prueba la detección de valores faltantes"""
        missing_info = datos_con_nan.isnull().sum()
        missing_cols = missing_info[missing_info > 0]

        assert len(missing_cols) == 2  # col1 y col2 tienen NaN
        assert "col1" in missing_cols.index
        assert "col2" in missing_cols.index
        assert missing_cols["col1"] == 1
        assert missing_cols["col2"] == 2

    def test_preservar_columnas_sin_nan(self, datos_con_nan):
        """Prueba que las columnas sin NaN se preservan correctamente"""
        resultado = datos_con_nan.copy()
        cols_numericas = resultado.select_dtypes(include=np.number).columns
        resultado[cols_numericas] = resultado[cols_numericas].fillna(
            resultado[cols_numericas].mean()
        )

        # col3 no tiene NaN, debe quedar igual
        pd.testing.assert_series_equal(
            resultado["col3"], datos_con_nan["col3"], check_names=False
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
