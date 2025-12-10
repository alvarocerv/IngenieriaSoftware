import pytest
import numpy as np
import json
import tempfile
import os
import sys
from sklearn.linear_model import LinearRegression
import joblib
import pickle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestGuardadoRecuperacionModelo:
    """Pruebas para guardar y recuperar modelos en diferentes formatos"""

    @pytest.fixture
    def modelo_entrenado(self):
        """Crea y entrena un modelo de prueba"""
        X = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]])
        y = np.array([5, 8, 11, 14, 17])

        modelo = LinearRegression()
        modelo.fit(X, y)

        return {
            "modelo": modelo,
            "columnas_entrada": ["feature1", "feature2"],
            "columna_salida": "target",
            "descripcion": "Modelo de prueba automática",
            "metricas": {
                "r2_train": 0.99,
                "r2_test": 0.98,
                "ecm_train": 0.1,
                "ecm_test": 0.2,
            },
        }

    @pytest.fixture
    def directorio_temporal(self):
        """Crea un directorio temporal"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_guardar_modelo_json(self, modelo_entrenado, directorio_temporal):
        """Prueba guardar modelo en formato JSON"""
        modelo = modelo_entrenado["modelo"]
        ruta = os.path.join(directorio_temporal, "modelo.json")

        formula = (
            f"{modelo_entrenado['columna_salida']} = "
            + " + ".join(
                [
                    f"({coef:.6f}*{col})"
                    for coef, col in zip(
                        modelo.coef_, modelo_entrenado["columnas_entrada"]
                    )
                ]
            )
            + f" + ({modelo.intercept_:.6f})"
        )

        info_modelo = {
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": formula,
            "coeficientes": [float(c) for c in modelo.coef_],
            "intercepto": float(modelo.intercept_),
            "metricas": modelo_entrenado["metricas"],
        }

        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(info_modelo, f, indent=4)

        assert os.path.exists(ruta)
        assert os.path.getsize(ruta) > 0

    def test_cargar_modelo_json(self, modelo_entrenado, directorio_temporal):
        """Prueba cargar modelo desde JSON"""
        modelo = modelo_entrenado["modelo"]
        ruta = os.path.join(directorio_temporal, "modelo.json")

        formula = (
            f"{modelo_entrenado['columna_salida']} = "
            + " + ".join(
                [
                    f"({coef:.6f}*{col})"
                    for coef, col in zip(
                        modelo.coef_, modelo_entrenado["columnas_entrada"]
                    )
                ]
            )
            + f" + ({modelo.intercept_:.6f})"
        )

        info_modelo = {
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": formula,
            "coeficientes": [float(c) for c in modelo.coef_],
            "intercepto": float(modelo.intercept_),
            "metricas": modelo_entrenado["metricas"],
        }

        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(info_modelo, f, indent=4)

        # Cargar
        with open(ruta, "r", encoding="utf-8") as f:
            modelo_cargado = json.load(f)

        assert modelo_cargado["descripcion"] == modelo_entrenado["descripcion"]
        assert (
            modelo_cargado["entradas"] == modelo_entrenado["columnas_entrada"]
        )
        np.testing.assert_array_almost_equal(
            modelo_cargado["coeficientes"], modelo.coef_
        )

    def test_guardar_modelo_joblib(
        self, modelo_entrenado, directorio_temporal
    ):
        """Prueba guardar modelo en formato joblib"""
        ruta = os.path.join(directorio_temporal, "modelo.joblib")

        info_completa = {
            "modelo": modelo_entrenado["modelo"],
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": "formula_placeholder",
            "coeficientes": modelo_entrenado["modelo"].coef_.tolist(),
            "intercepto": float(modelo_entrenado["modelo"].intercept_),
            "metricas": modelo_entrenado["metricas"],
        }

        joblib.dump(info_completa, ruta)

        assert os.path.exists(ruta)
        assert os.path.getsize(ruta) > 0

    def test_cargar_modelo_joblib(self, modelo_entrenado, directorio_temporal):
        """Prueba cargar modelo desde joblib"""
        ruta = os.path.join(directorio_temporal, "modelo.joblib")

        info_completa = {
            "modelo": modelo_entrenado["modelo"],
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": "formula_placeholder",
            "coeficientes": modelo_entrenado["modelo"].coef_.tolist(),
            "intercepto": float(modelo_entrenado["modelo"].intercept_),
            "metricas": modelo_entrenado["metricas"],
        }

        joblib.dump(info_completa, ruta)

        # Cargar
        modelo_cargado = joblib.load(ruta)

        assert modelo_cargado["descripcion"] == modelo_entrenado["descripcion"]
        assert isinstance(modelo_cargado["modelo"], LinearRegression)

    def test_guardar_modelo_pickle(
        self, modelo_entrenado, directorio_temporal
    ):
        """Prueba guardar modelo en formato pickle"""
        ruta = os.path.join(directorio_temporal, "modelo.pkl")

        info_completa = {
            "modelo": modelo_entrenado["modelo"],
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": "formula_placeholder",
            "coeficientes": modelo_entrenado["modelo"].coef_.tolist(),
            "intercepto": float(modelo_entrenado["modelo"].intercept_),
            "metricas": modelo_entrenado["metricas"],
        }

        with open(ruta, "wb") as f:
            pickle.dump(info_completa, f)

        assert os.path.exists(ruta)
        assert os.path.getsize(ruta) > 0

    def test_cargar_modelo_pickle(self, modelo_entrenado, directorio_temporal):
        """Prueba cargar modelo desde pickle"""
        ruta = os.path.join(directorio_temporal, "modelo.pkl")

        info_completa = {
            "modelo": modelo_entrenado["modelo"],
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": "formula_placeholder",
            "coeficientes": modelo_entrenado["modelo"].coef_.tolist(),
            "intercepto": float(modelo_entrenado["modelo"].intercept_),
            "metricas": modelo_entrenado["metricas"],
        }

        with open(ruta, "wb") as f:
            pickle.dump(info_completa, f)

        # Cargar
        with open(ruta, "rb") as f:
            modelo_cargado = pickle.load(f)

        assert modelo_cargado["descripcion"] == modelo_entrenado["descripcion"]
        assert isinstance(modelo_cargado["modelo"], LinearRegression)

    def test_prediccion_modelo_recuperado(
        self, modelo_entrenado, directorio_temporal
    ):
        """Prueba que un modelo recuperado puede hacer predicciones"""
        modelo_original = modelo_entrenado["modelo"]
        ruta = os.path.join(directorio_temporal, "modelo.json")

        # Guardar
        info_modelo = {
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": "formula",
            "coeficientes": [float(c) for c in modelo_original.coef_],
            "intercepto": float(modelo_original.intercept_),
            "metricas": modelo_entrenado["metricas"],
        }

        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(info_modelo, f)

        # Cargar y reconstruir modelo
        with open(ruta, "r", encoding="utf-8") as f:
            info_cargada = json.load(f)

        modelo_reconstruido = LinearRegression()
        modelo_reconstruido.coef_ = np.array(info_cargada["coeficientes"])
        modelo_reconstruido.intercept_ = info_cargada["intercepto"]

        # Predecir
        X_prueba = np.array([[1, 2]])
        pred_original = modelo_original.predict(X_prueba)
        pred_reconstruida = modelo_reconstruido.predict(X_prueba)

        np.testing.assert_array_almost_equal(pred_original, pred_reconstruida)

    def test_validar_campos_requeridos(
        self, modelo_entrenado, directorio_temporal
    ):
        """Prueba validación de campos requeridos en modelo guardado"""
        ruta = os.path.join(directorio_temporal, "modelo.json")

        info_modelo = {
            "descripcion": modelo_entrenado["descripcion"],
            "entradas": modelo_entrenado["columnas_entrada"],
            "salida": modelo_entrenado["columna_salida"],
            "formula": "formula",
            "coeficientes": [1.0, 2.0],
            "intercepto": 5.0,
            "metricas": modelo_entrenado["metricas"],
        }

        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(info_modelo, f)

        with open(ruta, "r", encoding="utf-8") as f:
            modelo_cargado = json.load(f)

        campos_requeridos = [
            "descripcion",
            "entradas",
            "salida",
            "formula",
            "coeficientes",
            "intercepto",
            "metricas",
        ]

        for campo in campos_requeridos:
            assert campo in modelo_cargado


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
