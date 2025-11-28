import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
import sqlite3

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.dataset_loading import cargar_dataset


class TestCargaDatos:
    """Pruebas para la carga de diferentes formatos de datos"""
    
    @pytest.fixture
    def datos_prueba(self):
        """Crea un DataFrame de prueba"""
        return pd.DataFrame({
            'columna1': [1, 2, 3, 4, 5],
            'columna2': [10, 20, 30, 40, 50],
            'salida': [100, 200, 300, 400, 500]
        })
    
    @pytest.fixture
    def directorio_temporal(self):
        """Crea un directorio temporal para archivos de prueba"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Limpiar después de las pruebas
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_cargar_csv(self, datos_prueba, directorio_temporal):
        """Prueba la carga de archivos CSV"""
        ruta_csv = os.path.join(directorio_temporal, 'test.csv')
        datos_prueba.to_csv(ruta_csv, index=False)
        
        df_cargado = cargar_dataset(ruta_csv)
        
        assert df_cargado is not None
        assert len(df_cargado) == 5
        assert list(df_cargado.columns) == ['columna1', 'columna2', 'salida']
        pd.testing.assert_frame_equal(df_cargado, datos_prueba)
    
    def test_cargar_excel(self, datos_prueba, directorio_temporal):
        """Prueba la carga de archivos Excel"""
        ruta_excel = os.path.join(directorio_temporal, 'test.xlsx')
        datos_prueba.to_excel(ruta_excel, index=False)
        
        df_cargado = cargar_dataset(ruta_excel)
        
        assert df_cargado is not None
        assert len(df_cargado) == 5
        assert list(df_cargado.columns) == ['columna1', 'columna2', 'salida']
    
    def test_cargar_sqlite(self, datos_prueba, directorio_temporal):
        """Prueba la carga de bases de datos SQLite"""
        ruta_db = os.path.join(directorio_temporal, 'test.db')
        
        # Crear base de datos SQLite
        conn = sqlite3.connect(ruta_db)
        datos_prueba.to_sql('datos', conn, index=False, if_exists='replace')
        conn.close()
        
        df_cargado = cargar_dataset(ruta_db)
        
        assert df_cargado is not None
        assert len(df_cargado) == 5
        assert 'columna1' in df_cargado.columns
    
    def test_valores_faltantes(self, directorio_temporal):
        """Prueba la carga de CSV con valores faltantes"""
        datos_con_nan = pd.DataFrame({
            'columna1': [1, 2, np.nan, 4, 5],
            'columna2': [10, np.nan, 30, 40, 50],
            'salida': [100, 200, 300, np.nan, 500]
        })
        
        ruta_csv = os.path.join(directorio_temporal, 'test_nan.csv')
        datos_con_nan.to_csv(ruta_csv, index=False)
        
        df_cargado = cargar_dataset(ruta_csv)
        
        assert df_cargado is not None
        assert len(df_cargado) == 5
        assert df_cargado.isnull().sum().sum() == 3  # 3 valores NaN
    
    def test_archivo_inexistente(self):
        """Prueba el manejo de archivos que no existen"""
        df_cargado = cargar_dataset('archivo_que_no_existe.csv')
        assert df_cargado is None
    
    def test_formato_no_soportado(self, directorio_temporal):
        """Prueba el manejo de formatos no soportados"""
        ruta_txt = os.path.join(directorio_temporal, 'test.txt')
        with open(ruta_txt, 'w') as f:
            f.write('contenido de prueba')
        
        df_cargado = cargar_dataset(ruta_txt)
        assert df_cargado is None
    
    def test_archivo_vacio(self, directorio_temporal):
        """Prueba la carga de un CSV vacío"""
        ruta_csv = os.path.join(directorio_temporal, 'vacio.csv')
        pd.DataFrame().to_csv(ruta_csv, index=False)
        
        df_cargado = cargar_dataset(ruta_csv)
        
        # Debe retornar None o un DataFrame vacío
        assert df_cargado is None or len(df_cargado) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
