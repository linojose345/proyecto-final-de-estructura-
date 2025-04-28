import heapq
import tkinter as tk
from tkinter import ttk, messagebox

class NodoTarea:
    def _init_(self, nombre, prioridad, fecha_limite):
        self.nombre = nombre
        self.prioridad = prioridad
        self.fecha_limite = fecha_limite
        self.siguiente = None

class ListaEnlazadaTareas:
    def _init_(self):
        self.cabeza = None

    def agregar_tarea(self, nombre, prioridad, fecha_limite):
        nuevo_nodo = NodoTarea(nombre, prioridad, fecha_limite)
        if not self.cabeza:
            self.cabeza = nuevo_nodo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo_nodo

    def eliminar_tarea(self, nombre):
        actual = self.cabeza
        previo = None
        while actual:
            if actual.nombre == nombre:
                if previo:
                    previo.siguiente = actual.siguiente
                else:
                    self.cabeza = actual.siguiente
                return True
            previo = actual
            actual = actual.siguiente
        return False

    def actualizar_tarea(self, nombre, nueva_prioridad, nueva_fecha):
        actual = self.cabeza
        while actual:
            if actual.nombre == nombre:
                actual.prioridad = nueva_prioridad
                actual.fecha_limite = nueva_fecha
                return True
            actual = actual.siguiente
        return False

    def mostrar_tareas(self):
        tareas = []
        actual = self.cabeza
        while actual:
            tareas.append((actual.nombre, actual.prioridad, actual.fecha_limite))
            actual = actual.siguiente
        return tareas

class ColaPrioridadTareas:
    def _init_(self):
        self.cola = []

    def agregar_tarea(self, nombre, prioridad, fecha_limite):
        heapq.heappush(self.cola, (prioridad, fecha_limite, nombre))

    def obtener_tarea_mas_urgente(self):
        return heapq.heappop(self.cola) if self.cola else None

    def mostrar_tareas(self):
        return sorted(self.cola)  # Ordenadas por prioridad


class InterfazTareas:
    def _init_(self, root):
        self.root = root
        self.root.title("Gestión de Tareas Académicas")
        self.lista_tareas = ListaEnlazadaTareas()
        self.cola_prioridad = ColaPrioridadTareas()

        # Etiquetas y entradas
        tk.Label(root, text="Nombre:").grid(row=0, column=0)
        tk.Label(root, text="Prioridad (1-5):").grid(row=1, column=0)  # Prioridad de 1 a 5
        tk.Label(root, text="Fecha Límite (YYYY-MM-DD):").grid(row=2, column=0)

        self.nombre_var = tk.StringVar()
        self.prioridad_var = tk.IntVar()
        self.fecha_var = tk.StringVar()

        tk.Entry(root, textvariable=self.nombre_var).grid(row=0, column=1)
        tk.Entry(root, textvariable=self.prioridad_var).grid(row=1, column=1)
        tk.Entry(root, textvariable=self.fecha_var).grid(row=2, column=1)

        # Botones
        tk.Button(root, text="Agregar Tarea", command=self.agregar_tarea).grid(row=3, column=0, columnspan=2)
        tk.Button(root, text="Eliminar Tarea", command=self.eliminar_tarea).grid(row=4, column=0, columnspan=2)
        tk.Button(root, text="Actualizar Tarea", command=self.actualizar_tarea).grid(row=5, column=0, columnspan=2)  # Botón de actualizar

        # Tabla de tareas
        self.tabla = ttk.Treeview(root, columns=("Nombre", "Prioridad", "Fecha"), show="headings")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Prioridad", text="Prioridad")
        self.tabla.heading("Fecha", text="Fecha Límite")
        self.tabla.grid(row=6, column=0, columnspan=2)

    def agregar_tarea(self):
        nombre = self.nombre_var.get()
        prioridad = self.prioridad_var.get()
        fecha = self.fecha_var.get()
        if nombre and 1 <= prioridad <= 5 and fecha:  # Prioridad de 1 a 5
            self.lista_tareas.agregar_tarea(nombre, prioridad, fecha)
            self.cola_prioridad.agregar_tarea(nombre, prioridad, fecha)
            messagebox.showinfo("Éxito", "Tarea agregada correctamente")
            self.mostrar_tareas()
        else:
            messagebox.showwarning("Error", "Datos inválidos. Prioridad debe ser entre 1 y 5.")

    def eliminar_tarea(self):
        nombre = self.nombre_var.get()
        if self.lista_tareas.eliminar_tarea(nombre):
            messagebox.showinfo("Éxito", "Tarea eliminada correctamente")
            self.mostrar_tareas()
        else:
            messagebox.showwarning("Error", "Tarea no encontrada")

    def actualizar_tarea(self):
        nombre = self.nombre_var.get()
        nueva_prioridad = self.prioridad_var.get()
        nueva_fecha = self.fecha_var.get()
        if nombre and 1 <= nueva_prioridad <= 5 and nueva_fecha:  # Prioridad de 1 a 5
            if self.lista_tareas.actualizar_tarea(nombre, nueva_prioridad, nueva_fecha):
                messagebox.showinfo("Éxito", "Tarea actualizada correctamente")
                self.mostrar_tareas()
            else:
                messagebox.showwarning("Error", "Tarea no encontrada")
        else:
            messagebox.showwarning("Error", "Datos inválidos. Prioridad debe ser entre 1 y 5.")

    def mostrar_tareas(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        for tarea in self.lista_tareas.mostrar_tareas():
            self.tabla.insert("", "end", values=tarea)

def menu_consola():
    lista_tareas = ListaEnlazadaTareas()
    cola_prioridad = ColaPrioridadTareas()

    while True:
        print("\n📌 Menú de Gestión de Tareas:")
        print("1. Agregar Tarea")
        print("2. Eliminar Tarea")
        print("3. Mostrar Tareas")
        print("4. Obtener Tarea más Urgente")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre de la tarea: ")
            prioridad = int(input("Prioridad (1-5): "))  # Prioridad de 1 a 5
            fecha = input("Fecha Límite (YYYY-MM-DD): ")
            lista_tareas.agregar_tarea(nombre, prioridad, fecha)
            cola_prioridad.agregar_tarea(nombre, prioridad, fecha)
            print("✅ Tarea agregada.")

        elif opcion == "2":
            nombre = input("Nombre de la tarea a eliminar: ")
            if lista_tareas.eliminar_tarea(nombre):
                print("✅ Tarea eliminada.")
            else:
                print("⚠️ Tarea no encontrada.")

        elif opcion == "3":
            tareas = lista_tareas.mostrar_tareas()
            if tareas:
                print("\n📌 Lista de Tareas:")
                for tarea in tareas:
                    print(f"- {tarea[0]} (Prioridad: {tarea[1]}, Fecha: {tarea[2]})")
            else:
                print("⚠️ No hay tareas registradas.")

        elif opcion == "4":
            tarea = cola_prioridad.obtener_tarea_mas_urgente()
            if tarea:
                print(f"🔹 Tarea más urgente: {tarea[2]} (Prioridad: {tarea[0]}, Fecha: {tarea[1]})")
            else:
                print("⚠️ No hay tareas en la cola.")

        elif opcion == "5":
            print("👋 Saliendo del sistema...")
            break
        else:
            print("⚠️ Opción inválida. Intente de nuevo.")


root = tk.Tk()
app = InterfazTareas(root)
root.mainloop()
