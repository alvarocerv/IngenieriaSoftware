# Aplicación de Regresión Lineal

Bienvenido al repositorio oficial de la **Aplicación de Regresión Lineal**. Esta herramienta construida en Python permite a los usuarios cargar conjuntos de datos, preprocesarlos y generar modelos de predicción mediante algoritmos de regresión lineal con una interfaz gráfica intuitiva.

## Características Principales

El flujo de trabajo de la aplicación está dividido en pasos lógicos para facilitar el análisis de datos:

- **Carga de Datos Versátil**: Soporte para archivos `.csv`, `.xlsx` (Excel) y `.db` (SQLite).
- **Visualización de Datos**: Tabla interactiva para visualizar los datos crudos y procesados.
- **Pipeline de Preprocesamiento**:
    - **Paso 1 - Selección de Columnas**: Define interactivamente tus variables de entrada (features) y tu variable de salida (target).
    - **Paso 2 - Limpieza de Datos**: Herramientas para manejar valores nulos o inexistentes.
    - **Paso 3 - Separación**: División automática de datos en conjuntos de entrenamiento (Train) y prueba (Test).
- **Modelado**: Creación de modelos de Regresión Lineal utilizando `scikit-learn`.
- **Evaluación y Predicción**:
    - Visualización de métricas de rendimiento ($R^2$ y Error Cuadrático Medio).
    - Gráficos de dispersión y líneas de tendencia.
    - Interfaz para realizar predicciones manuales con nuevos datos.
- **Gestión de Modelos**: Funcionalidad para guardar y cargar modelos entrenados.

## Requisitos Previos

Para ejecutar este proyecto necesitas tener instalado **Python 3.8** o superior.

Las dependencias principales del proyecto son:
- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`
- `openpyxl` (para soporte Excel)

## Instalación

Sigue estos pasos para preparar el entorno de desarrollo:

### 1. Clonar el repositorio
```
    git clone [https://github.com/alvarocerv/ingenieriasoftware.git](https://github.com/alvarocerv/ingenieriasoftware.git)
    cd ingenieriasoftware
```

### Entorno virtual (Opcional)
Recomendamos la creación de un entorno virtual para evitar conflictos entre las versiones de 
las librerías de este trabajo con las de otros proyectos de Python en su ordenador.

### En Windows:
    python -m venv venv
    .\venv\Scripts\activate

### En macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

La aparición de `(venv)` al principio de su línea de comandos indicará que el entorno está activo.

### Instalar dependencias
    pip install -r requirements.txt

## Cómo usar la aplicación
Para iniciar la interfaz gráfica principal, asegúrese de estar en la carpeta raíz del proyecto y ejecute:
    
    python src/main.py

### Flujo de trabajo sugerido:
1. **Cargar:** Haga clic en "Abrir archivo". Puede usar los archivos de ejemplo incluidos en la carpeta src/ (como housing.csv).
2. **Configurar:** Siga los paneles numerados que aparecerán en la parte inferior:
   - Seleccione las columnas que desee analizar.
   - Decida qué hacer con los datos vacíos (si los hay).
   - Confirme la proporción de datos para entrenamiento y pruebe.
3. **Analizar:** Una vez completados los pasos, la aplicación entrenará el modelo.
4. **Resultados:** Se abrirá automáticamente la pestaña Modelo, donde verá la fórmula matemática, la precisión ($R^2$) y podrá 
   realizar predicciones con nuevos datos.

## Pruebas (Testing)
Este proyecto cuenta con una suite completa de pruebas automatizadas para garantizar la calidad del software.
Para ejecutar todas las pruebas:
    
    pytest tests/ -v
Para más detalles, consulte la [Documentación de Pruebas](tests/README_TESTS.md)

## Contribución
Si desea contribuir al proyecto, por favor revise nuestra [Guía de contribución](CONTRIBUTING.md) para conocer las normas de
estilo y el flujo de trabajo.

## Licencia
Este proyecto ha sido desarrollado como parte de la asignatura de Ingeniería de Software.

