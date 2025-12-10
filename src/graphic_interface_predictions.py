import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd


def dibujar_grafico_predicciones(
    tab_grafico, modelo, df_test, nombre_col_entrada, nombre_col_salida
):
    """Dibuja el gráfico de predicciones en una nueva pesñaña"""
    if df_test is None or modelo is None:
        return
    if isinstance(nombre_col_entrada, list) and len(nombre_col_entrada) != 1:
        return
    if isinstance(nombre_col_entrada, list):
        nombre_col_entrada = nombre_col_entrada[0]

    # Extraer datos
    x_test = df_test[nombre_col_entrada].values
    y_test = df_test[nombre_col_salida].values
    # Usar DataFrame para preservar nombre de la feature y evitar warnings
    x_df = pd.DataFrame(x_test, columns=[nombre_col_entrada])
    y_pred = modelo.predict(x_df)

    # Crear figura
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(x_test, y_test, color="blue", label="Test (real)", alpha=0.7)
    ax.scatter(x_test, y_pred, color="red", label="Predicción", alpha=0.7)

    # Línea de ajuste basada en TODOS los puntos de test (reales y predichos)
    # Combinamos ambas series para obtener una recta promedio que represente tendencia global
    x_line = np.linspace(x_test.min(), x_test.max(), 100)
    combined_x = np.concatenate([x_test, x_test])
    combined_y = np.concatenate([y_test, y_pred])
    # Ajuste lineal sobre la combinación (2 * n puntos)
    slope, intercept = np.polyfit(combined_x, combined_y, 1)
    y_line = slope * x_line + intercept
    ax.plot(
        x_line, y_line, color="green", label="Línea de ajuste", linewidth=2
    )

    ax.set_xlabel(nombre_col_entrada)
    ax.set_ylabel(nombre_col_salida)
    ax.set_title("Predicciones vs Test")
    ax.legend()
    ax.grid(True)

    # Integrar en Tkinter dentro del Frame provisto
    canvas = FigureCanvasTkAgg(fig, master=tab_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Evitar fugas de memoria
    plt.close(fig)
