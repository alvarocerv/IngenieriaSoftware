import pytest
import pandas as pd
from sklearn.linear_model import LinearRegression
from src.model_logic import guardar_modelo_joblib, cargar_modelo_joblib

@pytest.fixture
def datos_prueba():
    df = pd.DataFrame({
        "X1": [1,2,3,4,5],
        "X2": [5,4,3,2,1],
        "Y":  [2,3,2.5,4,5]
    })
    train_df = df.iloc[:4]
    test_df = df.iloc[4:]
    return train_df, test_df

def test_guardar_y_cargar_modelo(datos_prueba, tmp_path):
    train_df, test_df = datos_prueba

    model = LinearRegression()
    model.fit(train_df[["X1","X2"]], train_df["Y"])

    archivo = tmp_path / "modelo.pkl"

    metricas = {
        "r2_train": model.score(train_df[["X1","X2"]], train_df["Y"]),
        "r2_test": model.score(test_df[["X1","X2"]], test_df["Y"]),
    }

    # ✔ Orden correcto
    guardar_modelo_joblib(archivo, model, ["X1", "X2"], "Y", metricas)

    # Asegurar que existe
    assert archivo.exists()

    # Cargar modelo
    model_cargado, input_cols, output_col, meta = cargar_modelo_joblib(archivo)

    assert input_cols == ["X1", "X2"]
    assert output_col == "Y"
    assert "r2_train" in meta
    assert hasattr(model_cargado, "predict")
