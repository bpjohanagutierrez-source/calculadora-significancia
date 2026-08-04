import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from io import StringIO

st.set_page_config(page_title="Calculadora de Significancia Estadística", layout="wide")

st.title("📊 Calculadora de Diferencias Significativas (Notación por Columna)")
st.markdown("""
Esta herramienta compara cada columna contra las demás ($A, B, C, D, E, F...$) e indica las letras de las columnas sobre las cuales existe una ventaja significativa.
* **Mayúsculas:** Significancia al 90% de confianza ($p < 0.10$).
* **Minúsculas:** Significancia al 80% de confianza ($p < 0.20$).
""")

col1, col2 = st.columns(2)
with col1:
    col_samples_input = st.text_input(
        "Tamaños de muestra (N) por columna (en orden):",
        value="590, 598, 618, 595, 597, 577"
    )
with col2:
    cv_factor = st.number_input(
        "Sensibilidad / CV Estimado (%):", 
        min_value=1.0, 
        max_value=100.0, 
        value=25.0, 
        step=1.0
    ) / 100.0

try:
    sample_sizes = [int(n.strip()) for n in col_samples_input.split(",") if n.strip()]
except Exception:
    sample_sizes = [590]

def compute_column_comparison(row_means, n_list, cv):
    cols = list(row_means.keys())
    k = len(cols)
    if k <= 1:
        return {c: "" for c in cols}
    
    # Asignación de letras de referencia a las columnas (A, B, C, D, E, F...)
    col_letters_upper = [chr(65 + i) for i in range(k)]
    col_letters_lower = [chr(97 + i) for i in range(k)]
    
    final_res = {}
    
    for i in range(k):
        target_col = cols[i]
        m1 = row_means[target_col]
        n1 = n_list[i] if i < len(n_list) else n_list[-1]
        s1 = max(0.1, m1 * cv)
        
        upper_letters = []
        lower_letters = []
        
        for j in range(k):
            if i == j:
                continue # No se compara consigo misma
                
            comp_col = cols[j]
            m2 = row_means[comp_col]
            n2 = n_list[j] if j < len(n_list) else n_list[-1]
            s2 = max(0.1, m2 * cv)
            
            # Prueba t unilateral: revisa si target_col es significativamente mayor que comp_col
            if m1 > m2:
                se_diff = np.sqrt((s1**2)/n1 + (s2**2)/n2)
                if se_diff > 0:
                    t_stat = (m1 - m2) / se_diff
                    df_val = n1 + n2 - 2
                    p_val = 1 - stats.t.cdf(t_stat, df=df_val)
                    
                    if p_val < 0.10: # 90%
                        upper_letters.append(col_letters_upper[j])
                    elif p_val < 0.20: # 80%
                        lower_letters.append(col_letters_lower[j])
                        
        # Formato combinado pegado sin espacios (ej. beF)
        sig_str = "".join(sorted(lower_letters)) + "".join(sorted(upper_letters))
        final_res[target_col] = sig_str
        
    return final_res

raw_input = st.text_area("Pega aquí la tabla de medias desde Excel:", height=200)

if raw_input.strip():
    try:
        df = pd.read_csv(StringIO(raw_input), sep="\t")
        st.write("Vista previa de los datos ingresados:", df.head())
        
        if st.button("🚀 Calcular Significancias Exactas"):
            output_df = df.copy().astype(str)
            numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
            
            for idx, row in df.iterrows():
                row_means = {}
                for col in numeric_cols:
                    val = row[col]
                    if pd.notna(val):
                        row_means[col] = float(val)
                
                if len(row_means) > 1:
                    letters = compute_column_comparison(row_means, sample_sizes, cv_factor)
                    for col in numeric_cols:
                        if col in letters:
                            sig = letters[col]
                            # Formatea concatenando la media y la cadena de significancia
                            output_df.at[idx, col] = f"{row_means[col]:.2f}{sig}"
            
            st.success("¡Matriz procesada con éxito!")
            st.dataframe(output_df)
            
            tsv_data = output_df.to_csv(sep="\t", index=False)
            st.text_area("Resultado listo para copiar de vuelta a Excel:", tsv_data, height=200)
            
    except Exception as e:
        st.error(f"Error procesando los datos: {e}")
