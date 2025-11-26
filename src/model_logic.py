# src/model_logic.py
from sklearn.linear_model import LinearRegression
import joblib
import numpy as np

def crear_modelo(train_df):
    """
    Entrena un LinearRegression usando la última columna como target.
    Retorna (model, input_cols, output_col).
    """
    output_col = train_df.columns[-1]
    input_cols = list(train_df.columns[:-1])

    model = LinearRegression()
    X = train_df[input_cols].values
    y = train_df[output_col].values
    model.fit(X, y)
    return model, input_cols, output_col

def predecir(model, input_cols, valores):
    """
    Recibe el modelo, lista de columnas de entrada y una lista de valores
    y devuelve la predicción (float). Lanza ValueError si las longitudes no coinciden.
    """
    if len(valores) != len(input_cols):
        raise ValueError("Cantidad de valores no coincide con columnas de entrada")
    arr = np.array([valores], dtype=float)
    return float(model.predict(arr)[0])

def guardar_modelo_joblib(path, model, input_cols, output_col, meta=None):
    """
    Guarda en disco usando joblib (incluye el modelo y metadatos).
    """
    data = {
        "model": model,
        "input_cols": input_cols,
        "output_col": output_col,
        "meta": meta or {}
    }
    joblib.dump(data, path)

def cargar_modelo_joblib(path):
    """
    Carga y retorna (model, input_cols, output_col, meta)
    """
    data = joblib.load(path)
    return data["model"], data["input_cols"], data["output_col"], data.get("meta", {})
