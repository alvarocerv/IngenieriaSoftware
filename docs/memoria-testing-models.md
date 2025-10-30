
# Documentación del Proceso de Investigación y Desarrollo del Modelo  
## Comparación entre *scikit-learn* y *statsmodels* en el análisis del conjunto de datos *housing*

---

### 1. Objetivo del estudio

El objetivo principal de esta investigación fue desarrollar y comparar un modelo de regresión lineal empleando dos bibliotecas de Python ampliamente utilizadas:  
- **scikit-learn**, centrada en el aprendizaje automático y la predicción.  
- **statsmodels**, enfocada en el análisis estadístico y la interpretación detallada de parámetros.

El modelo busca estimar el valor medio de una vivienda (`median_house_value`) en función de variables explicativas como el ingreso medio (`median_income`), la edad media de las viviendas (`housing_median_age`), y otras variables estructurales (número de habitaciones, dormitorios, etc.).

### 2. Preparación de los datos

Durante la limpieza y preparación de los datos se identificaron los siguientes aspectos clave:

- El archivo contenía valores decimales con coma, por lo que fue necesario reemplazarlas por puntos para convertir las columnas a tipo numérico.  
- Se seleccionaron las variables relevantes para el análisis (`median_income` como predictor y `median_house_value` como variable dependiente).  
- En algunos casos se realizó una división del conjunto en entrenamiento y prueba para evaluar la capacidad predictiva del modelo.


### 3. Resultados con *statsmodels*

Los resultados del modelo de regresión lineal ajustado con *statsmodels* mostraron un coeficiente positivo y significativo para la variable `median_income`, lo que indica que a medida que el ingreso medio aumenta, también lo hace el valor medio de la vivienda.  

El coeficiente de determinación **R²** se situó alrededor de 0.68, lo que sugiere que el modelo explica aproximadamente el 68% de la variabilidad del precio medio de las viviendas.  
Además, los valores de *p* indicaron una fuerte significancia estadística en la relación entre las variables.


### 4. Resultados con *scikit-learn*

Los resultados obtenidos mediante *scikit-learn* fueron consistentes con los de *statsmodels*.  
El intercepto y el coeficiente estimados fueron prácticamente idénticos, y el valor de **R²** también rondó el 0.68.  

Esto confirmó que ambos enfoques aplican la misma base matemática (mínimos cuadrados ordinarios), aunque presentan diferencias en la forma de interpretar y reportar los resultados.


### 5. Dificultades encontradas y soluciones

| **Archivo no encontrado** | Python no localizaba `housing.csv`. | Se verificó la ruta con `os.getcwd()` y se movió el archivo al mismo directorio del script. |
| **Separador decimal incorrecto** | Algunas columnas usaban coma (`,`) en lugar de punto (`.`). | Se reemplazaron con operaciones de texto antes de convertir a valores numéricos. |
| **Formato de entrada en scikit-learn** | El modelo requería un arreglo bidimensional. | Se ajustó la estructura de los datos para cumplir el formato. |
| **Falta de intercepto en statsmodels** | Sin añadir la constante, el modelo no incluía término independiente. | Se incorporó la constante de forma manual. |


### 6. Comparación entre *statsmodels* y *scikit-learn*

| Criterio | **statsmodels** | **scikit-learn** |
|-----------|----------------|-----------------|
| **Orientación** | Análisis estadístico e inferencia. | Predicción y Machine Learning. |
| **Salida** | Resumen completo (coeficientes, p-values, IC, R², F-test). | Solo coeficientes e intercepto. |
| **Interpretabilidad** | Muy alta. Ideal para investigación. | Limitada; se centra en rendimiento predictivo. |
| **Uso en pipelines** | No diseñado para producción ML. | Compatible con Pipeline y GridSearchCV. |
| **Diagnóstico de residuos** | Herramientas estadísticas integradas. | Requiere cálculos manuales. |
| **Facilidad de uso** | Más técnico y detallado. | Más simple e intuitivo. |


### 7. Conclusiones

- Ambos enfoques entregan resultados consistentes y válidos.  
- *statsmodels* es ideal para **análisis exploratorio y validación de hipótesis**, gracias a su salida estadística detallada.  
- *scikit-learn* es preferible cuando el objetivo es **implementar el modelo en producción o integrarlo en sistemas predictivos**.  
- En el conjunto *housing*, el **ingreso medio (`median_income`)** se confirmó como una variable fuertemente predictiva del valor medio de las viviendas.


### 8. Recomendaciones

1. Ampliar el modelo incorporando variables adicionales (edad de la vivienda, población, dormitorios).  
2. Normalizar los datos para evitar problemas de escala.  
3. Evaluar modelos no lineales como Random Forest o Gradient Boosting para capturar relaciones más complejas.  
4. Visualizar la relación entre ingreso medio y valor de vivienda mediante gráficos de dispersión para confirmar la linealidad.  
