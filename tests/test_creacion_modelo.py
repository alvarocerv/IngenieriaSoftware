import pandas as pd
from src.model_logic import crear_modelo

def test_creacion_modelo():
    df = pd.DataFrame({
        "x": [1, 2, 3, 4],
        "y": [2, 4, 6, 8]
    })

    model, input_cols, output_col = crear_modelo(df)

    # Validaciones básicas
    assert input_cols == ["x"]
    assert output_col == "y"
    assert hasattr(model, "predict")

    # Probamos una predicción simple
    pred = model.predict([[10]])[0]
    assert isinstance(pred, float)
