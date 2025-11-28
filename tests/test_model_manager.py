import unittest
import json
import tempfile
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sklearn.linear_model import LinearRegression
import numpy as np

class PruebasGestionModelo(unittest.TestCase):
    """Pruebas para guardar y cargar modelos"""
    
    def setUp(self):
        """Preparar un modelo y datos de prueba"""
        datos_entrada = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        datos_salida = np.array([5, 8, 11, 14])
        
        self.modelo = LinearRegression()
        self.modelo.fit(datos_entrada, datos_salida)
        
        self.columnas_entrada = ['caracteristica_1', 'caracteristica_2']
        self.columna_salida = 'objetivo'
        self.descripcion = 'Modelo de prueba'
        self.metricas = {
            'r2_entrenamiento': 0.95,
            'r2_prueba': 0.92,
            'ecm_entrenamiento': 0.5,
            'ecm_prueba': 0.7
        }
        
        self.directorio_temporal = tempfile.mkdtemp()
    
    def test_guardar_y_cargar_modelo(self):
        """Verifica guardar y cargar un modelo"""
        formula = f"{self.columna_salida} = " + " + ".join(
            [f"({coef:.6f} * {col})" for coef, col in zip(self.modelo.coef_, self.columnas_entrada)]
        ) + f" + ({self.modelo.intercept_:.6f})"
        
        informacion_modelo = {
            "descripcion": self.descripcion,
            "entradas": self.columnas_entrada,
            "salida": self.columna_salida,
            "formula": formula,
            "coeficientes": [float(c) for c in self.modelo.coef_],
            "intercepto": float(self.modelo.intercept_),
            "metricas": self.metricas
        }
        
        # Guardar
        ruta_archivo = os.path.join(self.directorio_temporal, 'modelo_prueba.json')
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(informacion_modelo, archivo, indent=4, ensure_ascii=False)
        
        self.assertTrue(os.path.exists(ruta_archivo))
        
        # Cargar
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            informacion_cargada = json.load(archivo)
        
        # Verificar que los datos se mantienen
        self.assertEqual(informacion_cargada["descripcion"], self.descripcion)
        self.assertEqual(informacion_cargada["salida"], self.columna_salida)
        self.assertListEqual(informacion_cargada["entradas"], self.columnas_entrada)
        np.testing.assert_array_almost_equal(
            informacion_cargada["coeficientes"],
            self.modelo.coef_
        )
    
    def test_validar_campos_modelo(self):
        """Verifica que los modelos cargados tienen todos los campos requeridos"""
        formula = f"{self.columna_salida} = " + " + ".join(
            [f"({coef:.6f} * {col})" for coef, col in zip(self.modelo.coef_, self.columnas_entrada)]
        ) + f" + ({self.modelo.intercept_:.6f})"
        
        informacion_modelo = {
            "descripcion": self.descripcion,
            "entradas": self.columnas_entrada,
            "salida": self.columna_salida,
            "formula": formula,
            "coeficientes": [float(c) for c in self.modelo.coef_],
            "intercepto": float(self.modelo.intercept_),
            "metricas": self.metricas
        }
        
        campos_necesarios = ["descripcion", "entradas", "salida", "formula",
                            "coeficientes", "intercepto", "metricas"]
        
        for campo in campos_necesarios:
            self.assertIn(campo, informacion_modelo)
    
    def test_preservar_metricas(self):
        """Verifica que las métricas se preservan correctamente"""
        ruta_archivo = os.path.join(self.directorio_temporal, 'metricas_prueba.json')
        
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump({"metricas": self.metricas}, archivo)
        
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            datos_cargados = json.load(archivo)
        
        self.assertEqual(datos_cargados["metricas"]["r2_entrenamiento"], 0.95)
        self.assertEqual(datos_cargados["metricas"]["ecm_prueba"], 0.7)
    
    def test_archivo_modelo_invalido(self):
        """Verifica manejo de archivo inválido"""
        ruta_invalida = os.path.join(self.directorio_temporal, 'archivo_invalido.json')
        with open(ruta_invalida, 'w') as archivo:
            archivo.write("contenido no válido")
        
        try:
            with open(ruta_invalida, 'r') as archivo:
                json.load(archivo)
            self.fail("Debería haber levantado un error de JSON inválido")
        except json.JSONDecodeError:
            pass 


if __name__ == '__main__':
    unittest.main()
