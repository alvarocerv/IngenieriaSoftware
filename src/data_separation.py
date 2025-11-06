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

    # Limpiar el contenedor de pasos
    for widget in frame_pasos_container.winfo_children():
        widget.destroy()

    # Etiqueta de paso
    frame_pasos_container.config(text="Paso 3: Separación de Datos")
    # Frame para inputs
    frame_inputs = ttk.Frame(frame_pasos_container)
    frame_inputs.pack(pady=5)

    train_pct_var = tk.StringVar(value="")

    def actualizar_test_pct(*args):
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

    # Porcentaje de entrenamiento
    ttk.Label(frame_inputs, text="Porcentaje de Entrenamiento:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_train_pct = ttk.Entry(frame_inputs, textvariable=train_pct_var, width=10)
    entry_train_pct.insert(0, "")
    entry_train_pct.grid(row=0, column=1, padx=5, pady=5)
    

    # Etiqueta para porcentaje de test 
    label_test_pct = ttk.Label(frame_inputs, text="Porcentaje de Test: %")  
    label_test_pct.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

    #semilla
    ttk.Label(frame_inputs, text="Semilla (para la separación aleatoria):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_seed = ttk.Entry(frame_inputs, width=10)
    entry_seed.insert(0, " ")  
    entry_seed.grid(row=2, column=1, padx=5, pady=5)

    # frame para botones (lo creamos aquí para usarlo luego)
    frame_vista = ttk.Frame(frame_pasos_container)

    def separar_datos():
        global train_df, test_df
        try:
            # --- Validaciones ---
            train_pct_str = entry_train_pct.get()
            seed_str = entry_seed.get()  # <-- Leemos la semilla

            if not train_pct_str:
                messagebox.showerror("Error", "Debes rellenar al menos el campo de porcentaje.")
                return

            train_pct = float(train_pct_str)
            if not (0 < train_pct < 100):
                raise ValueError("El porcentaje debe estar entre 0 y 100.")

            test_pct = 100 - train_pct

            # --- CAMBIO: 'seed' es ahora condicional ---
            seed = None  # Default a None (aleatorio)
            msg_info = "Datos separados aleatoriamente."  # Mensaje por defecto

            if seed_str:  # Si el usuario SÍ escribió algo
                try:
                    seed = int(seed_str)  # Intentamos convertirlo a número
                    msg_info = "Datos separados correctamente."  # Actualizamos mensaje
                except ValueError:
                    messagebox.showerror("Error", "La semilla aleatoria debe ser un número entero.")
                    return

            if len(df_procesado) < 5:
                messagebox.showerror("Error", "No hay suficientes datos para realizar la separación (mínimo 5 filas).")
                return

            # --- Realizar la separación ---
            # 'seed' será un número o None, dependiendo de lo que hizo el usuario
            train_df, test_df = train_test_split(df_procesado, test_size=test_pct / 100, random_state=seed)

            # Mostrar confirmación
            messagebox.showinfo("Separación Completada",
                                f"{msg_info}\n\n"
                                f"Conjunto de Entrenamiento: {len(train_df)} filas\n"
                                f"Conjunto de Test: {len(test_df)} filas")

            # --- Lógica de botones (sin cambios) ---

            # 1. Ocultar widgets del Paso 3 que ya no se usan
            frame_inputs.pack_forget()
            btn_separar.pack_forget()

            # 2. Mostrar botones de visualización ("Ver Conjunto...")
            frame_vista.pack(pady=10)

            # 3. Botón para avanzar al Paso 4
            if callback:
                ttk.Button(
                    frame_pasos_container,
                    text="Avanzar al Paso 4: Crear Modelo",
                    command=lambda: callback(train_df, test_df)  # Llama al Paso 4
                ).pack(pady=20)

        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")


    # Botón para separar (Guardamos la referencia en 'btn_separar')
    btn_separar = ttk.Button(frame_pasos_container, text="Separar Datos", command=separar_datos)
    btn_separar.pack(pady=10)

    # botón para ver los conjuntos (AHORA SE MUESTRAN DESDE 'separar_datos')
    ttk.Button(frame_vista, text="Ver Conjunto de Entrenamiento",
               command=lambda: func_mostrar_tabla(train_df)).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame_vista, text="Ver Conjunto de Test",
               command=lambda: func_mostrar_tabla(test_df)).pack(side=tk.LEFT, padx=5)

    