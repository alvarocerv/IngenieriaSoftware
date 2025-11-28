import pytest
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestCreacionModelo:
    """Pruebas para la creación y entrenamiento del modelo de regresión lineal"""
    
    @pytest.fixture
    def datos_entrenamiento(self):
        """Crea datos de entrenamiento sintéticos"""
        np.random.seed(42)
        X = np.random.rand(100, 2) * 10
        y = 3 * X[:, 0] + 2 * X[:, 1] + 5 + np.random.randn(100) * 0.5
        
        df_train = pd.DataFrame(X, columns=['feature1', 'feature2'])
        df_train['target'] = y
        
        return df_train
    
    @pytest.fixture
    def datos_prueba(self):
        """Crea datos de prueba sintéticos"""
        np.random.seed(123)
        X = np.random.rand(30, 2) * 10
        y = 3 * X[:, 0] + 2 * X[:, 1] + 5 + np.random.randn(30) * 0.5
        
        df_test = pd.DataFrame(X, columns=['feature1', 'feature2'])
        df_test['target'] = y
        
        return df_test
    
    def test_crear_modelo_regresion(self, datos_entrenamiento):
        """Prueba la creación de un modelo de regresión lineal"""
        X_train = datos_entrenamiento[['feature1', 'feature2']]
        y_train = datos_entrenamiento['target']
        
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        assert modelo is not None
        assert hasattr(modelo, 'coef_')
        assert hasattr(modelo, 'intercept_')
        assert len(modelo.coef_) == 2
    
    def test_predicciones_modelo(self, datos_entrenamiento, datos_prueba):
        """Prueba que el modelo realiza predicciones correctamente"""
        X_train = datos_entrenamiento[['feature1', 'feature2']]
        y_train = datos_entrenamiento['target']
        X_test = datos_prueba[['feature1', 'feature2']]
        
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        predicciones = modelo.predict(X_test)
        
        assert predicciones is not None
        assert len(predicciones) == len(X_test)
        assert isinstance(predicciones, np.ndarray)
    
    def test_metricas_r2(self, datos_entrenamiento, datos_prueba):
        """Prueba el cálculo de R²"""
        X_train = datos_entrenamiento[['feature1', 'feature2']]
        y_train = datos_entrenamiento['target']
        X_test = datos_prueba[['feature1', 'feature2']]
        y_test = datos_prueba['target']
        
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        y_pred_train = modelo.predict(X_train)
        y_pred_test = modelo.predict(X_test)
        
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        
        assert 0 <= r2_train <= 1
        assert r2_test >= 0.9  # Debería ser alto para datos sintéticos
    
    def test_metricas_ecm(self, datos_entrenamiento, datos_prueba):
        """Prueba el cálculo del Error Cuadrático Medio"""
        X_train = datos_entrenamiento[['feature1', 'feature2']]
        y_train = datos_entrenamiento['target']
        X_test = datos_prueba[['feature1', 'feature2']]
        y_test = datos_prueba['target']
        
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        y_pred_train = modelo.predict(X_train)
        y_pred_test = modelo.predict(X_test)
        
        ecm_train = mean_squared_error(y_train, y_pred_train)
        ecm_test = mean_squared_error(y_test, y_pred_test)
        
        assert ecm_train >= 0
        assert ecm_test >= 0
        assert ecm_test < 1.0  # Debe ser bajo para datos sintéticos
    
    def test_coeficientes_modelo(self, datos_entrenamiento):
        """Prueba que los coeficientes están cerca de los valores esperados"""
        X_train = datos_entrenamiento[['feature1', 'feature2']]
        y_train = datos_entrenamiento['target']
        
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        # Los coeficientes deberían estar cerca de [3, 2]
        assert modelo.coef_[0] == pytest.approx(3.0, abs=0.5)
        assert modelo.coef_[1] == pytest.approx(2.0, abs=0.5)
        assert modelo.intercept_ == pytest.approx(5.0, abs=1.0)
    
    def test_formula_modelo(self, datos_entrenamiento):
        """Prueba la generación de la fórmula del modelo"""
        X_train = datos_entrenamiento[['feature1', 'feature2']]
        y_train = datos_entrenamiento['target']
        
        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        
        columnas = ['feature1', 'feature2']
        columna_salida = 'target'
        
        formula = f"{columna_salida} = " + " + ".join(
            [f"({modelo.coef_[i]:.4f}*{col})" for i, col in enumerate(columnas)]
        ) + f" + ({modelo.intercept_:.4f})"
        
        assert 'target' in formula
        assert 'feature1' in formula
        assert 'feature2' in formula
        assert '+' in formula
    
    def test_modelo_una_variable(self):
        """Prueba modelo con una sola variable de entrada"""
        X = np.array([[1], [2], [3], [4], [5]])
        y = np.array([2, 4, 6, 8, 10])
        
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        assert len(modelo.coef_) == 1
        assert modelo.coef_[0] == pytest.approx(2.0, abs=0.01)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
