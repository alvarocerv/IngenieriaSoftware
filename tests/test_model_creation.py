import unittest
import numpy as np
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sklearn.linear_model import LinearRegression

class PruebasCreacionModelo(unittest.TestCase):
    """Pruebas para la creación y predicción de modelos"""
    
    def setUp(self):
        """Preparar datos de prueba"""
        # y = 2x + 1
        np.random.seed(42)
        self.datos_entrada = np.array([[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]])
        self.datos_salida = 2 * self.datos_entrada.ravel() + 1 + np.random.normal(0, 0.1, 10)
        
        self.modelo = LinearRegression()
        self.modelo.fit(self.datos_entrada, self.datos_salida)
    
    def test_entrenar_modelo(self):
        """Verifica que el modelo se entrena correctamente"""
        self.assertIsNotNone(self.modelo)
        self.assertIsNotNone(self.modelo.coef_)
        self.assertIsNotNone(self.modelo.intercept_)
    
    def test_generar_predicciones(self):
        """Verifica que el modelo genera predicciones correctas"""
        predicciones = self.modelo.predict(self.datos_entrada)
        self.assertEqual(len(predicciones), len(self.datos_salida))
        self.assertTrue(np.all(np.isfinite(predicciones)))
    
    def test_prediccion_valor_individual(self):
        """Verifica predicción de un solo valor"""
        datos_prueba = np.array([[5]])
        prediccion = self.modelo.predict(datos_prueba)
        self.assertEqual(len(prediccion), 1)
        self.assertGreater(prediccion[0], 10)


if __name__ == '__main__':
    unittest.main()
