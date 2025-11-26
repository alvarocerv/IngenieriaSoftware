import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import sqlite3
import threading

def cargar_dataset(file_path):
    """Carga un dataset desde un archivo CSV, Excel o SQLite y lo devuelve como un DataFrame de pandas"""
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        elif file_path.endswith((".sqlite", ".db")):
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                raise ValueError("No se encontraron tablas en la base de datos SQLite.")
            table_name = tables[0][0]
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            conn.close()
        else:
            raise ValueError("Formato de archivo no válido.")
        return df

    except FileNotFoundError:
        messagebox.showerror("Error", "Archivo no encontrado.")
    except pd.errors.EmptyDataError:
        messagebox.showerror("Error", "El archivo está vacío.")
    except sqlite3.OperationalError:
        messagebox.showerror("Error", "No se pudo leer la base de datos SQLite.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error inesperado", f"Ocurrió un problema:\n{e}")
    return None


def abrir_archivo(entrada_texto, start_progress, stop_progress, mostrar_tabla, iniciar_flujo_paso_1, ventana, set_dataframes):
    """Abre un cuadro de diálogo para seleccionar un archivo de datos, lo carga y actualiza la interfaz"""
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo de datos", 
        filetypes=[("Archivos soportados", "*.csv *.xls *.xlsx *.sqlite *.db"), ("Todos los archivos", "*.*")]
    )
    if not ruta:
        messagebox.showinfo("Carga cancelada", "La carga de archivo fue cancelada.")
        return
    
    entrada_texto.config(state="normal")
    entrada_texto.delete(0, tk.END)
    entrada_texto.insert(0, ruta)
    entrada_texto.config(state="readonly", disabledforeground="black")
    start_progress()
    
    def hilo_carga():
        """Hilo para cargar el dataset y actualizar la interfaz"""
        df = cargar_dataset(ruta)
        def fin():
            """Finaliza la carga del dataset y actualiza la interfaz"""
            stop_progress()
            if df is not None:
                df_original = df.copy()
                df_original_sin_filtrar = df.copy()
                # Actualizar las variables globales en interface.py
                set_dataframes(df_original, df_original_sin_filtrar)
                mostrar_tabla(df_original)
                messagebox.showinfo("Datos cargados", "Archivo cargado exitosamente. Iniciando flujo de preprocesamiento.")
                iniciar_flujo_paso_1(df_original)
            else:
                messagebox.showerror("Error en carga", "No se pudo cargar el archivo.")
        ventana.after(0, fin)
    
    threading.Thread(target=hilo_carga, daemon=True).start()
