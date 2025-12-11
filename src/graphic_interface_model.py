import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import pandas as pd
import numpy as np

_mousebind_installed = (
    False  # ya no se usará para binding global, mantenido por compatibilidad
)


def dibujar_ui_model_creation(
    tab_modelo,
    notebook_visor,
    train_df,
    test_df,
    guardar_callback=None,
    start_progress=None,
    stop_progress=None,
    tab_predicciones=None,
):
    """Crea la interfaz de creación de modelo dentro del Frame de la pestaña provisto"""

    # Scrollable frame dentro de la pestaña recibida
    canvas = tk.Canvas(tab_modelo)
    scrollbar_v = ttk.Scrollbar(
        tab_modelo, orient="vertical", command=canvas.yview
    )
    scrollbar_h = ttk.Scrollbar(
        tab_modelo, orient="horizontal", command=canvas.xview
    )
    canvas.configure(
        yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set
    )
    scrollbar_v.pack(side="right", fill="y")
    scrollbar_h.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    frame_content = ttk.Frame(canvas)
    frame_id = canvas.create_window((0, 0), window=frame_content, anchor="nw")
    frame_content.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
    )
    canvas.bind(
        "<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width)
    )

    # Scroll con rueda del mouse (binding por entrada/salida para no interferir con otras pestañas)
    def _on_mousewheel(event):
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_wheel(_):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_wheel(_):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _bind_wheel)
    canvas.bind("<Leave>", _unbind_wheel)

    # La descripción se ubicará debajo de métricas y gráfico
    txt_descripcion = None

    prediction_frame_ref = [None]

    def crear_modelo_thread():
        """Crea el modelo en un hilo separado para no bloquear la interfaz"""
        if start_progress:
            start_progress()
        try:
            output_col = train_df.columns[-1]
            input_cols = list(train_df.columns[:-1])

            X_train = train_df[input_cols]
            y_train = train_df[output_col]
            X_test = test_df[input_cols]
            y_test = test_df[output_col]

            # Validar que no haya NaN en los datos
            if X_train.isnull().any().any() or y_train.isnull().any():
                nan_cols = X_train.columns[X_train.isnull().any()].tolist()
                if y_train.isnull().any():
                    nan_cols.append(output_col)
                raise ValueError(
                    f"Los datos contienen valores faltantes en las columnas: {', '.join(nan_cols)}. "
                    "Por favor, revisa el paso de preprocesado de datos."
                )

            # Simulación proceso pesado
            time.sleep(0.5)
            model = LinearRegression()
            model.fit(X_train, y_train)

            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)

            r2_train = r2_score(y_train, y_pred_train)
            ecm_train = mean_squared_error(y_train, y_pred_train)
            r2_test = r2_score(y_test, y_pred_test)
            ecm_test = mean_squared_error(y_test, y_pred_test)

            def _render():
                mostrar_resultados(
                    frame_content,
                    model,
                    input_cols,
                    output_col,
                    y_pred_train,
                    y_pred_test,
                    r2_train,
                    ecm_train,
                    r2_test,
                    ecm_test,
                    prediction_frame_ref,
                    train_df,
                    test_df,
                    txt_descripcion,
                    guardar_callback
                )

            frame_content.after(0, _render)
        except Exception as e:
            frame_content.after(
                0,
                lambda: messagebox.showerror(
                    "Error en Modelo", f"Ocurrió un error: {str(e)}"
                ),
            )
        finally:
            if stop_progress:
                stop_progress()

    threading.Thread(target=crear_modelo_thread, daemon=True).start()


def mostrar_resultados(
    frame_content,
    model,
    input_cols,
    output_col,
    y_pred_train,
    y_pred_test,
    r2_train,
    ecm_train,
    r2_test,
    ecm_test,
    prediction_frame_ref,
    train_df,
    test_df,
    txt_descripcion,
    guardar_callback
):
    """Muestra los resultados del modelo en la interfaz"""

    # Título y descripción
    ttk.Label(
        frame_content, text="Resultados del Modelo", font=("Arial", 12, "bold")
    ).pack(pady=(10, 5))

    formula_str = (
        f"{output_col} = "
        + " + ".join(
            [
                f"({model.coef_[i]:.4f}*{col})"
                for i, col in enumerate(input_cols)
            ]
        )
        + f" + ({model.intercept_:.4f})"
    )
    ttk.Label(
        frame_content,
        text=f"Fórmula: {formula_str}",
        font=("Courier", 10),
        wraplength=700,
    ).pack(pady=5, padx=10)

    # Métricas
    cols = ("Métrica", "Entrenamiento", "Test")
    tree_metrics = ttk.Treeview(
        frame_content, columns=cols, show="headings", height=2
    )
    for col in cols:
        tree_metrics.heading(col, text=col)
        tree_metrics.column(col, width=200, anchor="center")
    tree_metrics.insert(
        "", "end", values=("R²", f"{r2_train:.4f}", f"{r2_test:.4f}")
    )
    tree_metrics.insert(
        "", "end", values=("ECM", f"{ecm_train:.4f}", f"{ecm_test:.4f}")
    )
    tree_metrics.pack(pady=5, padx=10, fill="x")

    # Gráfico si solo 1 variable: test vs predicción
    # Se dibuja siempre
    def _crear_fig_modelo():
        fig = plt.Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.scatter(
            train_df[input_cols[0]],
            train_df[output_col],
            label="Train",
            alpha=0.7,
        )
        ax.scatter(
            test_df[input_cols[0]],
            test_df[output_col],
            marker="x",
            label="Test",
        )
        ax.plot(
            train_df[input_cols[0]].values,
            y_pred_train,
            linewidth=2,
            label="Ajuste",
        )
        ax.set_xlabel(input_cols[0])
        ax.set_ylabel(output_col)
        ax.legend(loc="best")
        # Rotar etiquetas del eje X para evitar superposición
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        return fig

    def _crear_fig_predicciones(x_vals, y_preds, x_label, y_label):
        fig = plt.Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        # x = valor real de la columna de salida (test), y = predicción según la fórmula
        ax.scatter(
            x_vals, y_preds, color="red", label="Predicción (test)", alpha=0.8
        )
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        # Límites combinados para dibujar líneas de referencia correctamente
        try:
            xmin = float(np.nanmin(x_vals))
            xmax = float(np.nanmax(x_vals))
            ymin = float(np.nanmin(y_preds))
            ymax = float(np.nanmax(y_preds))
            low = min(xmin, ymin)
            high = max(xmax, ymax)
        except Exception:
            low, high = 0.0, 1.0

        # Línea y = x (45°): referencia de predicción perfecta
        x_line = np.linspace(low, high, 100)
        ax.plot(
            x_line,
            x_line,
            color="black",
            linestyle="--",
            label="Referencia (y = x)",
        )

        ax.set_title("Valores Reales Test (X) vs Predicción (Y)")
        ax.set_xlim(low, high)
        ax.set_ylim(low, high)
        ax.grid(True)
        ax.legend(loc="best")
        # Rotar etiquetas del eje X para evitar superposición
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        return fig

    # Frame contenedor para los gráficos
    charts_frame = ttk.Frame(frame_content)
    charts_frame.pack(fill="both", expand=True, padx=10, pady=5)

    if len(input_cols) == 1:
        # Dos columnas con mismo peso
        left_frame = ttk.Frame(charts_frame)
        right_frame = ttk.Frame(charts_frame)
        left_frame.grid(row=0, column=0, sticky="nsew")
        right_frame.grid(row=0, column=1, sticky="nsew")
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)

        # Figura del modelo (izquierda)
        fig_model = _crear_fig_modelo()
        canvas_model = FigureCanvasTkAgg(fig_model, master=left_frame)
        canvas_model.draw()
        canvas_model.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig_model)

        # Figura predicciones (derecha): x = valor real de la columna de salida, y = predicción según la fórmula
        x_real_vals = test_df[output_col].values
        # Obtener predicciones usando todas las columnas de entrada
        X_test_full = test_df[input_cols]
        y_pred_vals = model.predict(X_test_full)
        fig_pred = _crear_fig_predicciones(
            x_real_vals, y_pred_vals, output_col, "predicción " + output_col
        )
        canvas_pred = FigureCanvasTkAgg(fig_pred, master=right_frame)
        canvas_pred.draw()
        canvas_pred.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig_pred)
    else:
        # Solo mostramos el nuevo gráfico. Como no hay una única variable de entrada,
        # como x usaremos el índice de las muestras.
        single_frame = ttk.Frame(charts_frame)
        single_frame.pack(fill="both", expand=True)

        # Usar como eje X los valores reales de la columna de salida
        x_real_vals = test_df[output_col].values
        # Obtener predicciones usando todas las columnas de entrada
        X_test_full = test_df[input_cols]
        y_pred_vals = model.predict(X_test_full)
        fig_pred = _crear_fig_predicciones(
            x_real_vals, y_pred_vals, output_col, "predicción " + output_col
        )
        canvas_pred = FigureCanvasTkAgg(fig_pred, master=single_frame)
        canvas_pred.draw()
        canvas_pred.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig_pred)

    # Descripción debajo de métricas y gráfico
    ttk.Label(
        frame_content,
        text="Descripción del Modelo:",
        font=("Arial", 11, "bold"),
    ).pack(pady=(10, 5))
    txt_descripcion = tk.Text(frame_content, height=4, width=70)
    txt_descripcion.pack(padx=10, pady=5)

    # Botones acciones (Guardar / Predicciones) debajo de la descripción
    botones_frame = ttk.Frame(frame_content)
    botones_frame.pack(pady=10)
    if guardar_callback:
        metricas = {
            "r2_train": r2_train,
            "r2_test": r2_test,
            "ecm_train": ecm_train,
            "ecm_test": ecm_test,
        }
        ttk.Button(
            botones_frame,
            text="Guardar Modelo",
            command=lambda: guardar_callback(
                model,
                input_cols,
                output_col,
                txt_descripcion.get("1.0", tk.END).strip(),
                metricas,
            ),
        ).pack(side="left", padx=5)

    # Predicción interactiva
    if prediction_frame_ref[0] is not None:
        prediction_frame_ref[0].destroy()

    frame_pred = ttk.LabelFrame(
        frame_content, text="Predicción Interactiva", padding=10
    )
    frame_pred.pack(fill="x", expand=True, pady=10, padx=10)
    prediction_frame_ref[0] = frame_pred

    input_entries = {}
    row_frame = ttk.Frame(frame_pred)
    row_frame.pack(fill="x", pady=5)

    # Entradas en línea
    for col in input_cols:
        ttk.Label(row_frame, text=f"{col}:", width=12, anchor="w").pack(
            side="left", padx=(0, 2)
        )
        ent = ttk.Entry(row_frame, width=8)
        ent.pack(side="left", padx=(0, 10))
        input_entries[col] = ent

    # Label de resultado en la misma línea
    ttk.Label(
        row_frame,
        text=f"Resultado ({output_col}):",
        font=("Arial", 11, "bold"),
    ).pack(side="left", padx=(20, 5))
    lbl_resultado_pred = ttk.Label(
        row_frame, text="-", font=("Arial", 11, "bold"), foreground="green"
    )
    lbl_resultado_pred.pack(side="left")

    def ejecutar_prediccion():
        """Ejecuta la predicción usando el modelo con los valores ingresados"""
        try:
            valores = [float(input_entries[col].get()) for col in input_cols]
            # Usar DataFrame para preservar nombres y evitar warnings
            valores_df = pd.DataFrame([valores], columns=input_cols)
            pred = model.predict(valores_df)[0]
            lbl_resultado_pred.config(text=f"{pred:.4f}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al predecir: {e}")

    ttk.Button(
        frame_pred, text="Calcular Predicción", command=ejecutar_prediccion
    ).pack(pady=5, anchor="w")
