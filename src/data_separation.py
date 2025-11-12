import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sklearn.model_selection import train_test_split

# variables globales
train_df = None
test_df = None


def iniciar_separacion(df_procesado, frame_pasos_container, func_mostrar_tabla, callback=None):
    """
    Dibuja la interfaz para separación de datos y realiza la separación
    """
    global train_df, test_df

    # ... (Resto del código de inicialización, sin cambios) ...

    # Frame para inputs
    frame_inputs = ttk.Frame(frame_pasos_container)
    frame_inputs.pack(pady=5, padx=10)

    train_pct_var = tk.StringVar(value="")

    def actualizar_test_pct(*args):
        # ... (Lógica de actualización de porcentaje, sin cambios) ...
        try:
            train_pct = float(train_pct_var.get())
            if 0 < train_pct < 100:
                test_pct = 100 - train_pct
                label_test_pct.config(text=f"Porcentaje de Test: {test_pct:.1f}%")
            else:
                label_test_pct.config(text="Porcentaje de Test: --")
        except ValueError:
            label_test_pct.config(text="Porcentaje de Test: --")

    train_pct_var.trace_add("write", actualizar_test_pct)

    # ... (Entradas de porcentaje y semilla, sin cambios) ...
    ttk.Label(frame_inputs, text="Porcentaje de Entrenamiento:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_train_pct = ttk.Entry(frame_inputs, textvariable=train_pct_var, width=10)
    entry_train_pct.insert(0, "")
    entry_train_pct.grid(row=0, column=1, padx=5, pady=5)

    label_test_pct = ttk.Label(frame_inputs, text="Porcentaje de Test: %")
    label_test_pct.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

    ttk.Label(frame_inputs, text="Semilla (para la separación aleatoria):").grid(row=2, column=0, padx=5, pady=5,
                                                                                 sticky="w")
    entry_seed = ttk.Entry(frame_inputs, width=10)
    entry_seed.insert(0, " ")
    entry_seed.grid(row=2, column=1, padx=5, pady=5)

    # frame para botones de vista
    frame_vista = ttk.Frame(frame_pasos_container)
    btn_train = None
    btn_test = None

    def ver_conjunto(df, boton_actual, boton_opuesto):
        """
        CORRECCIÓN CLAVE: Esta función ahora SOLO cambia el estado de los botones.
        NO llama a func_mostrar_tabla(df) para evitar que la tabla superior se filtre.
        """

        # Mantenemos la funcionalidad de habilitar/deshabilitar
        boton_opuesto.config(state=tk.DISABLED)
        boton_actual.config(state=tk.NORMAL)

        # Opcional: Mostrar un mensaje informativo en lugar de filtrar la tabla.
        # messagebox.showinfo("Conjunto Visualizado",
        #                     f"El conjunto de {len(df)} filas ha sido seleccionado, pero la tabla superior permanece sin filtrar.")

    def separar_datos():
        global train_df, test_df, btn_train, btn_test

        try:
            # --- Validaciones y Separación (sin cambios) ---
            train_pct_str = entry_train_pct.get()
            seed_str = entry_seed.get()

            if not train_pct_str:
                messagebox.showerror("Error", "Debes rellenar al menos el campo de porcentaje.")
                return

            train_pct = float(train_pct_str)
            if not (0 < train_pct < 100):
                raise ValueError("El porcentaje debe estar entre 0 y 100.")

            test_pct = 100 - train_pct
            seed = None
            msg_info = "Datos separados aleatoriamente."

            if seed_str.strip():
                try:
                    seed = int(seed_str)
                    msg_info = "Datos separados correctamente."
                except ValueError:
                    messagebox.showerror("Error", "La semilla aleatoria debe ser un número entero.")
                    return

            if len(df_procesado) < 5:
                messagebox.showerror("Error", "No hay suficientes datos para realizar la separación (mínimo 5 filas).")
                return

            train_df, test_df = train_test_split(df_procesado, test_size=test_pct / 100, random_state=seed)

            messagebox.showinfo("Separación Completada",
                                f"{msg_info}\n\n"
                                f"Conjunto de Entrenamiento: {len(train_df)} filas\n"
                                f"Conjunto de Test: {len(test_df)} filas")

            # 1. Ocultar widgets de input del Paso 3
            frame_inputs.pack_forget()
            btn_separar.pack_forget()

            # 2. Crear y mostrar botones de visualización (Entrenamiento/Test)
            for widget in frame_vista.winfo_children():
                widget.destroy()

            btn_train = ttk.Button(frame_vista, text="Ver Conjunto de Entrenamiento")
            btn_test = ttk.Button(frame_vista, text="Ver Conjunto de Test")

            # Asignamos los comandos que NO llaman a func_mostrar_tabla(df)
            btn_train.config(command=lambda: ver_conjunto(train_df, btn_train, btn_test))
            btn_test.config(command=lambda: ver_conjunto(test_df, btn_test, btn_train))

            btn_train.pack(side=tk.LEFT, padx=5)
            btn_test.pack(side=tk.LEFT, padx=5)
            frame_vista.pack(pady=10)

            # 3. Llama al callback que dibuja el Paso 4
            if callback:
                callback(train_df, test_df)

        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")

    # Botón para separar
    btn_separar = ttk.Button(frame_pasos_container, text="Separar Datos", command=separar_datos)
    btn_separar.pack(pady=10)