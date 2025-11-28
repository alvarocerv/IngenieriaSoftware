# Pruebas Automáticas - Aplicación de Regresión Lineal

Este directorio contiene las pruebas unitarias automáticas para todas las funcionalidades de la aplicación.

## Resumen

- **Total de tests**: 46 tests
- **Estado**: Todos los tests pasan sin warnings
- **Framework**: pytest
- **Características**: Sin ventanas de interfaz gráfica durante tests

## Estructura de Pruebas

- **conftest.py**: Configuración global (mocks de Tkinter)
- **test_dataset_loading.py**: Pruebas de carga de datos (8 tests)
- **test_nonexistent_data.py**: Pruebas de preprocesado y manejo de datos faltantes (9 tests)
- **test_column_separation.py**: Pruebas de selección de columnas y separación de datos (12 tests)
- **test_linear_regression.py**: Pruebas del modelo de regresión lineal y métricas (9 tests)
- **test_model_manager.py**: Pruebas de guardado y recuperación de modelos (8 tests)

## Ejecutar las Pruebas

### Ejecutar todas las pruebas
```bash
pytest tests/ -v
```

### Ejecutar un archivo específico
```bash
pytest tests/test_dataset_loading.py -v
```

### Ejecutar pruebas específicas por nombre
```bash
pytest tests/ -k "test_cargar_csv" -v
```

## Configuración

### pytest.ini
Configuración en la raíz del proyecto:
- Supresión automática de warnings de deprecación
- Opciones por defecto (verbose, traceback corto)
- Marcadores personalizados

### conftest.py
Mock automático de Tkinter:
- **No se abrirán ventanas** durante la ejecución de tests
- Mock de messagebox (showerror, showinfo, showwarning)
- Mock de filedialog (asksaveasfilename, askopenfilename)
- Backend matplotlib sin interfaz (Agg)

## Cobertura de Pruebas

Las pruebas cubren las siguientes funcionalidades:

### 1. Carga de Datos
- Carga de archivos CSV
- Carga de archivos Excel (.xlsx, .xls)
- Carga de bases de datos SQLite
- Manejo de archivos inexistentes
- Manejo de formatos no soportados
- Manejo de valores faltantes en carga

### 2. Preprocesado de Datos
- Eliminación de filas con valores faltantes
- Relleno con media
- Relleno con mediana
- Relleno con constante
- Preservación de columnas sin NaN
- Manejo de columnas completamente nulas

### 3. Selección y Separación
- Selección de columnas de entrada y salida
- Separación train/test (diferentes proporciones)
- Verificación de no solapamiento
- Preservación de columnas
- Manejo de datos pequeños

### 4. Modelo de Regresión Lineal
- Creación y entrenamiento del modelo
- Cálculo de predicciones
- Métricas R² (entrenamiento y prueba)
- Métricas ECM (entrenamiento y prueba)
- Verificación de coeficientes
- Generación de fórmula del modelo
- Modelos con una o múltiples variables

### 5. Guardado y Recuperación
- Guardado en formato JSON
- Guardado en formato Joblib
- Guardado en formato Pickle
- Carga desde JSON
- Carga desde Joblib
- Carga desde Pickle
- Validación de campos requeridos
- Preservación de capacidad de predicción

## Requisitos

```bash
pip install pytest pytest-cov pandas numpy scikit-learn openpyxl joblib
```

## Interpretación de Resultados

- **PASSED**: La prueba se ejecutó correctamente
- **FAILED**: La prueba falló, revisa el mensaje de error
- **ERROR**: Hubo un error al ejecutar la prueba
- **SKIPPED**: La prueba fue omitida

## Añadir Nuevas Pruebas

Para añadir nuevas pruebas:

1. Crea un nuevo archivo `test_*.py` en este directorio
2. Usa el decorador `@pytest.fixture` para datos de prueba
3. Nombra las funciones de prueba con el prefijo `test_`
4. Usa assertions (`assert`) para verificar resultados

## CI/CD

Estas pruebas están diseñadas para ejecutarse automáticamente en un pipeline de CI/CD.
