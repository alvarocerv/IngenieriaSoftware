import pandas as pd
import pytest
from src.model_logic import crear_modelo, predecir


def test_predecir_valores_correctos():
    df = pd.DataFrame({
        "x": [1, 2, 3],
        "y": [3, 5, 7]  # y = 2x + 1
    })

    model, input_cols, output_col = crear_modelo(df)

    pred = predecir(model, input_cols, [10])  # 21
    assert abs(pred - 21) < 1e-6


def test_predecir_num_valores_incorrecto():
    df = pd.DataFrame({
        "a": [1],
        "b": [2],
        "y": [3]
    })
    model, input_cols, output_col = crear_modelo(df)

    with pytest.raises(ValueError):
        predecir(model, input_cols, [1])  # solo 1 valor en vez de 2
