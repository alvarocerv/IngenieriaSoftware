import pytest
import os
import warnings

# Configurar el entorno antes de cualquier import de Tkinter
os.environ["MPLBACKEND"] = "Agg"  # Backend sin interfaz para matplotlib

# Suprimir warnings de deprecation de openpyxl
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, module="openpyxl"
)


# Mock de Tkinter para evitar que se abran ventanas
@pytest.fixture(scope="session", autouse=True)
def mock_tkinter():
    """Mock global de Tkinter para evitar ventanas durante tests"""
    import tkinter
    import tkinter.messagebox
    import tkinter.filedialog

    # Guardar funciones originales
    original_showerror = tkinter.messagebox.showerror
    original_showinfo = tkinter.messagebox.showinfo
    original_showwarning = tkinter.messagebox.showwarning
    original_asksaveasfilename = tkinter.filedialog.asksaveasfilename
    original_askopenfilename = tkinter.filedialog.askopenfilename

    # Reemplazar con funciones que no hacen nada
    tkinter.messagebox.showerror = lambda *args, **kwargs: None
    tkinter.messagebox.showinfo = lambda *args, **kwargs: None
    tkinter.messagebox.showwarning = lambda *args, **kwargs: None
    tkinter.filedialog.asksaveasfilename = lambda *args, **kwargs: ""
    tkinter.filedialog.askopenfilename = lambda *args, **kwargs: ""

    yield

    # Restaurar funciones originales después de los tests
    tkinter.messagebox.showerror = original_showerror
    tkinter.messagebox.showinfo = original_showinfo
    tkinter.messagebox.showwarning = original_showwarning
    tkinter.filedialog.asksaveasfilename = original_asksaveasfilename
    tkinter.filedialog.askopenfilename = original_askopenfilename
