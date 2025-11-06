# prueba_joblib.py
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
import joblib

# 1. Crear datos y entrenar modelo
X, y = make_regression(n_samples=100, n_features=1, noise=10, random_state=42)
modelo = LinearRegression()
modelo.fit(X, y)

# 2. Guardar modelo con joblib
joblib.dump(modelo, "modelo_joblib.joblib")
print("✅ Modelo guardado con joblib en 'modelo_joblib.joblib'")

# 3. Cargar modelo desde archivo
modelo_cargado = joblib.load("modelo_joblib.joblib")

# 4. Verificar funcionamiento
pred_original = modelo.predict(X[:5])
pred_cargado = modelo_cargado.predict(X[:5])

print("🔹 Predicciones originales:", pred_original)
print("🔹 Predicciones cargadas:  ", pred_cargado)
print("✅ Verificación:", (pred_original == pred_cargado).all())
