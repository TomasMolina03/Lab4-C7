import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# ATENCION: Debe colocar la direccion en la que ha sido publicada la aplicacion en la siguiente linea\
# link del deploy de el Trabajo Practico Numero 8: 
# URL = 'https://ejeciciolabgonzalomanzano.streamlit.app/'

# Función para mostrar la información del alumno
def mostrar_informacion_alumno():
    with st.container():
        st.markdown('**Legajo:** 58.702')
        st.markdown('**Nombre:** Gonzalo Manzano')
        st.markdown('**Comisión:** C7')

# Función para cargar y mostrar el archivo CSV
def cargar_archivo():
    archivo = st.sidebar.file_uploader("Subir archivo CSV", type="csv")
    if archivo:
        datos = pd.read_csv(archivo)
        return datos
    return None

# Función para calcular métricas y gráficos
def mostrar_informacion(datos, sucursal):
    if sucursal != "Todas":
        datos = datos[datos["Sucursal"] == sucursal]

    productos = datos["Producto"].unique()
    for producto in productos:
        datos_producto = datos[datos["Producto"] == producto]
        
        # Validaciones de datos
        if datos_producto["Ingreso_total"].isnull().any():
            st.error(f"El producto '{producto}' tiene valores nulos en la columna 'Ingreso_total'.")
            continue
        if datos_producto["Unidades_vendidas"].isnull().any():
            st.error(f"El producto '{producto}' tiene valores nulos en la columna 'Unidades_vendidas'.")
            continue
        if (datos_producto["Ingreso_total"] < 0).any():
            st.error(f"El producto '{producto}' tiene valores negativos en 'Ingreso_total'.")
            continue
        if (datos_producto["Unidades_vendidas"] <= 0).any():
            st.error(f"El producto '{producto}' tiene valores no positivos en 'Unidades_vendidas'.")
            continue
        
        # Cálculo de métricas
        unidades_vendidas = datos_producto["Unidades_vendidas"].sum()
        ingreso_total = datos_producto["Ingreso_total"].sum()
        costo_total = datos_producto["Costo_total"].sum()
        
        precio_promedio = ingreso_total / unidades_vendidas
        margen_promedio = (ingreso_total - costo_total) / ingreso_total * 100
        
        # Cálculo de delta para Precio Promedio (comparado con el promedio global)
        precio_promedio_global = datos["Ingreso_total"].sum() / datos["Unidades_vendidas"].sum()
        delta_precio = precio_promedio - precio_promedio_global
        precio_promedio_2024 = datos_producto[datos_producto["Año"] == 2024]["Ingreso_total"].sum() / datos_producto[datos_producto["Año"] == 2024]["Unidades_vendidas"].sum()
        precio_promedio_2023 = datos_producto[datos_producto["Año"] == 2023]["Ingreso_total"].sum() / datos_producto[datos_producto["Año"] == 2023]["Unidades_vendidas"].sum()
        margen_promedio_2024 = ((datos_producto[datos_producto["Año"] == 2024]["Ingreso_total"].sum() - datos_producto[datos_producto["Año"] == 2024]["Costo_total"].sum()) / datos_producto[datos_producto["Año"] == 2024]["Ingreso_total"].sum()) * 100
        margen_promedio_2023 = ((datos_producto[datos_producto["Año"] == 2023]["Ingreso_total"].sum() - datos_producto[datos_producto["Año"] == 2023]["Costo_total"].sum()) / datos_producto[datos_producto["Año"] == 2023]["Ingreso_total"].sum()) * 100
        unidades_2024 = datos_producto[datos_producto["Año"] == 2024]["Unidades_vendidas"].sum()
        unidades_2023 = datos_producto[datos_producto["Año"] == 2023]["Unidades_vendidas"].sum()

        # Mostrar métricas
        st.header(producto)
        st.metric("Precio Promedio", f"${precio_promedio:,.2f}", delta=f"{((precio_promedio_2024 / precio_promedio_2023) - 1) * 100:.2f}%")
        st.metric("Margen Promedio", f"{margen_promedio:.2f}%", delta=f"{((margen_promedio_2024 / margen_promedio_2023) - 1) * 100:.2f}%")
        st.metric("Unidades Vendidas", f"{unidades_vendidas:,}", delta=f"{((unidades_2024 / unidades_2023) - 1) * 100:.2f}%")


        # Preparar datos para la columna Fecha
        datos_producto['Año'] = datos_producto['Año'].astype(int)
        datos_producto['Mes'] = datos_producto['Mes'].astype(int)
        datos_producto['Fecha'] = pd.to_datetime(
            datos_producto['Año'].astype(str) + '-' + datos_producto['Mes'].astype(str) + '-01'
        )
        
        # Ordenar por Fecha
        datos_producto.sort_values('Fecha', inplace=True)

        # Gráfico de evolución de ventas
        fig, ax = plt.subplots()
        ax.plot(datos_producto["Fecha"], datos_producto["Unidades_vendidas"], label=producto)
        
        # Agregar línea de tendencia
        x = np.arange(len(datos_producto))
        y = datos_producto["Unidades_vendidas"].values
        slope, intercept, _, _, _ = stats.linregress(x, y)
        tendencia = slope * x + intercept
        ax.plot(datos_producto["Fecha"], tendencia, label="Tendencia", color="red")
        
        ax.set_title("Evolución de Ventas Mensual")
        ax.set_xlabel("Año-Mes")
        ax.set_ylabel("Unidades vendidas")
        ax.legend()
        st.pyplot(fig)

# Interfaz principal de la aplicación
def main():
    st.sidebar.title("Cargar archivo de datos")
    mostrar_informacion_alumno()

    datos = cargar_archivo()
    if datos is not None:
        sucursales = ["Todas"] + datos["Sucursal"].unique().tolist()
        sucursal_seleccionada = st.sidebar.selectbox("Seleccionar Sucursal", sucursales)
        
        st.header(f"Datos de {'Todas las Sucursales' if sucursal_seleccionada == 'Todas' else sucursal_seleccionada}")
        mostrar_informacion(datos, sucursal_seleccionada)
    else:
        st.write("Por favor, sube un archivo CSV desde la barra lateral.")

if __name__ == "__main__":
    main()
