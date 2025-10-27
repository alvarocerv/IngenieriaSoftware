# FLUJO DE TRABAJO

1. **Fetch y Pull**
Antes de empezar a trabajar hacer **fetch** y **pull** para traer a mi dispositivo las nuevas ramas creadas por mis compañeros.

2. **Crear nueva rama**
Para trabajar en una nueva funcionalidad o modificar algo ya existente crear una nueva rama **a partir de `main`**.
- `feature/nueva-funcionalidad`
- `fix/error-en-login`
- `docs/actualizar-readme`
Si la rama es de interés para mis compañeros, hacer **publish branch**, así todo lo modificado en esa rama podra ser visto por los demás.

3. **Crear o Modificar archivos**
Asegurarse de estar en la **rama correcta**, para hacer todos los cambios correspodientes.
Modificar, crear, borrar archivos...
**Stage** de todos los cambios que quiera guardar en el siguiente commit, deben estar relacionados.
**Commit** de todos los cambios que tengan que ver:
  - **tipo** indica la naturaleza del cambio.
  - **scope** (opcional) indica el área o módulo afectado.
  - **descripción** resume brevemente la modificación, escrita en **imperativo** (por ejemplo, “añadir validación”, no “añadido” ni “añadiendo”).
  `feat: testing interfaz`
  `docs(readme): actualizar intrucciones de instañación`
  `refactor(archivo.py): mejorar comentarios del código`
* Los commit deben estar en **imperativo** (hacer, probar, cambiar...)
**Push** para que los cambios se suban a remoto y pueda ser vistos por todos.

4. **Pull Request**
Una vez todo el código esté listo en esa rama
**Pull Request** desde GitHub
Algún compañero lo revisará, y hará el **Merge** a la rama main
* Una vez hecho el merge **borrar la rama**

