import tkinter as tk
from tkinter import ttk, messagebox
from sklearn.model_selection import train_test_split
import random

# Variables globales
train_df = None
test_df = None


def iniciar_separacion(df_procesado, frame_pasos_container, func_mostrar_tabla, callback=None, df_original=None):
    """Separa los datos en conjuntos de entrenamiento y prueba según el porcentaje y semilla proporcionados"""
    global train_df, test_df
    
    frame_inputs = ttk.Frame(frame_pasos_container)
    frame_inputs.pack(pady=5, padx=10)

    train_pct_var = tk.StringVar(value="")

    def actualizar_test_pct(*args):
        """Actualiza la etiqueta del porcentaje de test según el porcentaje de entrenamiento ingresado"""
        try:
            val = train_pct_var.get()
            if val:
                train_pct = float(val)
                if 0 < train_pct < 100:
                    test_pct = 100 - train_pct
                    label_test_pct.config(text=f"Porcentaxe de Test: {test_pct:.1f}%")
                else:
                    label_test_pct.config(text="Porcentaxe de Test: --")
            else:
                label_test_pct.config(text="Porcentaxe de Test: --")
        except ValueError:
            label_test_pct.config(text="Porcentaxe de Test: --")

    train_pct_var.trace_add("write", actualizar_test_pct)

    # Campos de entrada
    ttk.Label(frame_inputs, text="Porcentaxe de Entrenamento:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_train_pct = ttk.Entry(frame_inputs, textvariable=train_pct_var, width=10)
    entry_train_pct.grid(row=0, column=1, padx=5, pady=5)

    label_test_pct = ttk.Label(frame_inputs, text="Porcentaxe de Test:")
    label_test_pct.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

    ttk.Label(frame_inputs, text="Semente (para a separación aleatoria):").grid(row=2, column=0, padx=5, pady=5,
                                                                                 sticky="w")
    entry_seed = ttk.Entry(frame_inputs, width=10)

    # Semilla aleatoria por defecto
    semilla_random = random.randint(1, 100)
    entry_seed.insert(0, str(semilla_random))

    entry_seed.grid(row=2, column=1, padx=5, pady=5)

    # Frame para botones de vista
    frame_vista = ttk.Frame(frame_pasos_container)
    btn_train = None
    btn_test = None
    # Si no se proporciona df_original, usar df_procesado
    df_original_completo = df_original if df_original is not None else df_procesado

    def ver_conjunto(df):
        """Muestra el conjunto de datos seleccionado"""
        if func_mostrar_tabla:
            func_mostrar_tabla(df)

    def ver_todos_datos():
        """Muestra todos los datos originales con todas las columnas"""
        if func_mostrar_tabla:
            func_mostrar_tabla(df_original_completo)

    def separar_datos():
        """Separa los datos según el porcentaje y semilla proporcionados."""
        global train_df, test_df, btn_train, btn_test
        try:
            train_pct_str = entry_train_pct.get()
            seed_str = entry_seed.get()

            if not train_pct_str:
                messagebox.showerror("Erro", "Debes encher polo menos o campo do porcentaxe.")
                return

            train_pct = float(train_pct_str)
            if not (0 < train_pct < 100):
                raise ValueError("O porcentaxe debe estar entre 0 e 100.")

            test_pct = 100 - train_pct
            seed = None
            msg_info = "Datos separados aleatoriamente."

            if seed_str.strip():
                try:
                    seed = int(seed_str)
                    msg_info = "Datos separados con semente fixa."
                except ValueError:
                    messagebox.showerror("Erro", "A semente aleatoria debe ser un número enteiro.")
                    return

            if len(df_procesado) < 5:
                messagebox.showerror("Erro", "Non hai suficientes datos para realizar a separación (mínimo 5 filas).")
                return

            train_df, test_df = train_test_split(df_procesado, test_size=test_pct / 100, random_state=seed)

            messagebox.showinfo("Separación Completada",
                                f"{msg_info}\n\n"
                                f"Conxunto de Entrenamento: {len(train_df)} filas\n"
                                f"Conxunto de Test: {len(test_df)} filas")

            # Ocultar widgets de input
            frame_inputs.pack_forget()
            btn_separar.pack_forget()

            # Crear y mostrar botones de visualización
            for widget in frame_vista.winfo_children():
                widget.destroy()

            btn_train = ttk.Button(frame_vista, text="Ver Conxunto de Entrenamento")
            btn_test = ttk.Button(frame_vista, text="Ver Conxunto de Test")
            btn_todos = ttk.Button(frame_vista, text="Ver Todos os Datos")

            btn_train.config(command=lambda: ver_conjunto(train_df))
            btn_test.config(command=lambda: ver_conjunto(test_df))
            btn_todos.config(command=ver_todos_datos)

            btn_todos.pack(side=tk.LEFT, padx=5)
            btn_train.pack(side=tk.LEFT, padx=5)
            btn_test.pack(side=tk.LEFT, padx=5)
            frame_vista.pack(pady=10)

            # Callback al siguiente paso (Creación del modelo)
            if callback:
                callback(train_df, test_df)

        except ValueError as e:
            messagebox.showerror("Erro", f"Entrada inválida: {e}")

    # Botón para separar
    btn_separar = ttk.Button(frame_pasos_container, text="Separar Datos", command=separar_datos)
    btn_separar.pack(pady=10)