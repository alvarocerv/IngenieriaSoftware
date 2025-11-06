# pickle

**Descripción**:
pickle es la biblioteca estándar de Python para serializar y deserializar objetos, convirtiéndolos en una secuencia de bytes que puede almacenarse o transmitirse.

**Uso típico**:
Guardar objetos pequeños o medianos, incluyendo modelos de machine learning entrenados.

**Ventaja**:

Incluida en la biblioteca estándar (no requiere instalación adicional).

Muy sencilla de usar.

Compatible con prácticamente cualquier objeto Python.

**Desventajas**:

Menos eficiente para objetos grandes o con arreglos NumPy extensos.

Archivos resultantes suelen ocupar más espacio que otros métodos.

No es seguro cargar archivos pickle provenientes de fuentes no confiables, ya que puede ejecutarse código malicioso durante la deserialización.

# joblib

**Descripción**:
joblib está optimizada para trabajar con objetos grandes y estructuras basadas en NumPy, como los modelos de machine learning entrenados con scikit-learn.

**Uso típico**:
Guardar modelos de machine learning, conjuntos de datos grandes o resultados de procesamiento numérico intensivo.

**Ventajas**:

Mayor velocidad y eficiencia en comparación con pickle para objetos grandes.

Ofrece opciones de compresión para reducir el tamaño de los archivos.

Especialmente recomendada para modelos de scikit-learn.

**Desventajas**:

Requiere instalación adicional (pip install joblib).

Menos adecuada para objetos Python no numéricos o muy personalizados.