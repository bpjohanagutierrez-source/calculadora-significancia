Python
import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import networkx as nx
from io import StringIO

st.set_page_config(page_title="Calculadora de Significancia Estadística", layout="wide")

st.title("📊 Calculadora de Diferencias Significativas")
st.markdown("""
Esta herramienta procesa matrices de medias de investigación de mercados fila por fila.
* **Mayúsculas:** Significancia al 90% de confianza ($p < 0.10$).
* **Minúsculas:** Significancia al 80% de confianza ($p < 0.20$).
""")

col1, col2 = st.columns(2)
with col1:
    col_samples_input = st.text_input(
        "Tamaños de muestra (N) por columna:",
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
except ValueError:
    sample_sizes = [590]

def compute_cld_exact(row_means, n_list, cv):
    labels = list(row_means.keys())
    k = len(labels)
    if k <= 1:
        return {l: "A" for l in labels}
    
    sorted_labels = sorted(labels, key=lambda x: row_means[x], reverse=True)
    
    diff_80 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    diff_90 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    
    for i in range(k):
        for j in range(i+1, k):
            l1, l2 = sorted_labels[i], sorted_labels[j]
            idx1, idx2 = labels.index(l1), labels.index(l2)
            
            m1, m2 = row_means[l1], row_means[l2]
            n1 = n_list[idx1] if idx1 < len(n_list) else n_list[-1]
            n2 = n_list[idx2] if idx2 < len(n_list) else n_list[-1]
            
            # Cálculo de la desviación estándar estimada por celda
            s1 = max(0.1, m1 * cv)
            s2 = max(0.1, m2 * cv)
            
            se_diff = np.sqrt((s1**2)/n1 + (s2**2)/n2)
            
            if se_diff == 0:
                p_val = 1.0
            else:
                t_stat = abs(m1 - m2) / se_diff
                df = n1 + n2 - 2
                p_val = 2 * (1 - stats.t.cdf(t_stat, df=df))
            
            # Asignación de diferencias por umbral p
            if p_val < 0.20: # 80% Confianza
                diff_80.loc[l1, l2] = diff_80.loc[l2, l1] = True
            if p_val < 0.10: # 90% Confianza
                diff_90.loc[l1, l2] = diff_90.loc[l2, l1] = True

    def get_letters(diff_matrix, is_upper=False):
        G = nx.Graph()
        G.add_nodes_from(sorted_labels)
        for i in range(k):
            for j in range(i+1, k):
                l1, l2 = sorted_labels[i], sorted_labels[j]
                if not diff_matrix.loc[l1, l2]:
                    G.add_edge(l1, l2)
        cliques = list(nx.find_cliques(G))
        cliques.sort(key=lambda c: max([row_means[x] for x in c]), reverse=True)
        
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if is_upper else 'abcdefghijklmnopqrstuvwxyz'
        letter_map = {lbl: [] for lbl in sorted_labels}
        for idx, clique in enumerate(cliques):
            let = alphabet[idx % len(alphabet)]
            for item in clique:
                letter_map[item].append((let, idx))
        return letter_map

    map_80 = get_letters(diff_80, is_upper=False)
    map_90 = get_letters(diff_90, is_upper=True)
    
    final_res = {}
    for lbl in labels:
        items_90 = map_90[lbl]
        items_80 = map_80[lbl]
        
        indices_90 = {idx for _, idx in items_90}
        upper_str = "".join(sorted([let for let, _ in items_90]))
        
        valid_lowers = [let for let, idx in items_80 if idx not in indices_90]
        lower_str = "".join(sorted(valid_lowers))
        
        res = f"{lower_str}{upper_str}".strip()
        final_res[lbl] = res if res else upper_str
        
    return final_res

raw_input = st.text_area("Pega aquí tu matriz copiada directamente desde Excel:", height=200)

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
                    letters = compute_cld_exact(row_means, sample_sizes, cv_factor)
                    for col in numeric_cols:
                        if col in letters:
                            output_df.at[idx, col] = f"{row_means[col]:.2f}{letters[col]}"
            
            st.success("¡Matriz procesada con éxito fila por fila!")
            st.dataframe(output_df)
            
            tsv_data = output_df.to_csv(sep="\t", index=False)
            st.text_area("Resultado listo para copiar de vuelta a Excel:", tsv_data, height=200)
            
    except Exception as e:
        st.error(f"Error procesando los datos: {e}")
