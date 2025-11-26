import pandas as pd
import pytest
from sklearn.linear_model import LinearRegression


@pytest.fixture
def datos_prueba():
    df = pd.DataFrame({
        "X1": [1, 2, 3, 4, 5],
        "X2": [5, 4, 3, 2, 1],
        "Y": [2, 3, 2.5, 4, 5]
    })
    train_df = df.iloc[:4]
    test_df = df.iloc[4:]
    return train_df, test_df


def test_creacion_modelo_visual(datos_prueba):
    train_df, test_df = datos_prueba

    model = LinearRegression()
    model.fit(train_df[["X1", "X2"]], train_df["Y"])

    y_pred_train = model.predict(train_df[["X1", "X2"]])
    y_pred_test = model.predict(test_df[["X1", "X2"]])

    print("\n--- Test visual ---")
    print("Predicciones train:", y_pred_train)
    print("Predicciones test:", y_pred_test)

    assert len(y_pred_train) == len(train_df)
    assert len(y_pred_test) == len(test_df)


def test_prediccion_visual(datos_prueba):
    train_df, test_df = datos_prueba

    model = LinearRegression()
    model.fit(train_df[["X1", "X2"]], train_df["Y"])

    pred = model.predict([[3, 2]])[0]
    print("Predicción:", pred)

    assert isinstance(pred, float)
