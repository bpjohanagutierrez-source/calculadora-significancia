import streamlit as st
import numpy as np
import pandas as pd
from scipy.stats import norm

st.set_page_config(page_title="Calculadora de Significancia", layout="wide")

st.title("Calculadora de Significancia Estadística (80% / 90%)")

st.markdown("""
**Instrucciones:**
1. Ingresa los tamaños de muestra ($N$) separados por comas.
2. Pega la matriz de datos/porcentajes (los valores por columna).
3. La aplicación calculará automáticamente las letras de significancia comparando cada columna.
""")

# Entradas del usuario
col1, col2 = st.columns([1, 2])

with col1:
    n_input = st.text_input(
        "Tamaños de muestra (N) por columna:", 
        value="590, 598, 618, 595, 597, 577"
    )

with col2:
    matrix_input = st.text_area(
        "Matriz de datos (copia de Excel o texto):",
        value="""63.10 60.50 63.27 61.01 60.60 57.50
52.00 51.00 52.43 52.27 51.40 47.70
45.60 41.60 41.26 38.99 40.90 38.80
40.30 37.50 37.54 35.97 36.70 33.80""",
        height=150
    )

def calcular_significancia(val1, n1, val2, n2, letra_col2):
    p1 = val1 / 100.0 if val1 > 1 else val1
    p2 = val2 / 100.0 if val2 > 1 else val2
    
    if p1 <= p2:
        return ""
        
    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * ((1 / n1) + (1 / n2)))
    
    if se == 0:
        return ""
        
    z = (p1 - p2) / se
    
    if z >= 1.282: # 90% confianza
        return letra_col2.upper()
    elif z >= 0.842: # 80% confianza
        return letra_col2.lower()
    return ""

if st.button("Calcular Significancias", type="primary"):
    try:
        # Parsear Muestras
        muestras = [float(x.strip()) for x in n_input.replace('\t', ',').split(',') if x.strip()]
        num_cols = len(muestras)
        
        if num_cols < 2:
            st.error("Ingresa al menos 2 tamaños de muestra.")
            st.stop()
            
        # Parsear Matriz
        numeros = []
        for linea in matrix_input.strip().split('\n'):
            elementos = linea.replace('\t', ' ').split(' ')
            for el in elementos:
                if el.strip():
                    try:
                        numeros.append(float(el.strip()))
                    except ValueError:
                        pass

        matriz = []
        for i in range(0, len(numeros), num_cols):
            fila = numeros[i:i + numcols] if 'numcols' in locals() else numeros[i:i + num_cols]
            if len(fila) == num_cols:
                matriz.append(fila)

        if not matriz:
            st.error(f"No se pudieron organizar los datos en {num_cols} columnas. Revisa los valores ingresados.")
            st.stop()

        # Generar Encabezados (A, B, C...)
        letras_cols = [chr(65 + i) for i in range(num_cols)]
        headers = [f"{letras_cols[i]} (n={int(muestras[i])})" for i in range(num_cols)]

        # Procesar Calculo
        filas_resultado = []
        for fila in matriz:
            fila_res = []
            for col1_idx, val1 in enumerate(fila):
                n1 = muestras[col1_idx]
                letras_sig = ""
                for col2_idx, val2 in enumerate(fila):
                    if col1_idx != col2_idx:
                        n2 = muestras[col2_idx]
                        letra = letras_cols[col2_idx]
                        letras_sig += calcular_significancia(val1, n1, val2, n2, letra)
                
                # Texto celda
                texto = f"{val1:.2f} {letras_sig}".strip()
                fila_res.append(texto)
            filas_resultado.append(fila_res)

        # Crear DataFrame para Streamlit
        df_res = pd.DataFrame(filas_resultado, columns=headers)
        
        st.subheader("Resultado")
        st.dataframe(df_res, use_container_width=True)

        # Crear versión en texto plano tabulado para copiar directo a Excel/Sheets
        tsv_text = "\t".join(headers) + "\n"
        for fila in filas_resultado:
            tsv_text += "\t".join(fila) + "\n"

        st.text_area("Formato listo para copiar a Excel / Google Sheets (Ctrl + A -> Ctrl + C):", value=tsv_text, height=200)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los datos: {e}")
