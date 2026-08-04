import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import networkx as nx
from io import StringIO

st.set_page_config(page_title="Calculadora de Significancia Estadística", layout="wide")

st.title("📊 Calculadora de Diferencias Significativas")
st.markdown("""
**Instrucciones:**
1. Ingresa los tamaños de muestra ($N$) de tus columnas (separados por comas).
2. Pega tu matriz de datos copiada directamente de Excel.
3. Haz clic en **Procesar Matriz** para obtener la nomenclatura exacta (ej. `63.10beF`).
""")

# 1. Entrada de muestras
col_samples_input = st.text_input(
    "Tamaños de muestra (N) por columna separados por comas:",
    value="590, 598, 618, 595, 597, 577"
)

try:
    sample_sizes = [int(n.strip()) for n in col_samples_input.split(",") if n.strip()]
except ValueError:
    sample_sizes = [590]

def compute_row_letters(row_values, n_list, p_alpha_80=0.20, p_alpha_90=0.10):
    labels = list(row_values.keys())
    k = len(labels)
    if k <= 1:
        return {l: "A" for l in labels}
    
    means = np.array([row_values[l] for l in labels])
    ns = np.array([n_list[i] if i < len(n_list) else n_list[-1] for i in range(k)])
    
    # Estimación de la varianza residual a partir de las medias y las muestras (ANOVA de la fila)
    grand_mean = np.average(means, weights=ns)
    ss_between = np.sum(ns * (means - grand_mean)**2)
    df_between = k - 1
    ms_between = ss_between / df_between if df_between > 0 else 1.0
    
    # Estimación del MSE poblacional para la prueba LSD / Tukey
    mse = ms_between / 1.5 
    
    # Ordenar de mayor a menor
    sorted_labels = sorted(labels, key=lambda x: row_values[x], reverse=True)
    
    diff_80 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    diff_90 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    
    for i in range(k):
        for j in range(i+1, k):
            l1, l2 = sorted_labels[i], sorted_labels[j]
            idx1, idx2 = labels.index(l1), labels.index(l2)
            
            m1, m2 = row_values[l1], row_values[l2]
            n1, n2 = ns[idx1], ns[idx2]
            
            se_diff = np.sqrt(mse * (1.0/n1 + 1.0/n2))
            if se_diff == 0:
                p_val = 1.0
            else:
                t_stat = abs(m1 - m2) / se_diff
                df = np.sum(ns) - k
                p_val = 2 * (1 - stats.t.cdf(t_stat, df=df))
            
            if p_val < p_alpha_80: # Significativo al 80% (minúscula)
                diff_80.loc[l1, l2] = diff_80.loc[l2, l1] = True
            if p_val < p_alpha_90: # Significativo al 90% (MAYÚSCULA)
                diff_90.loc[l1, l2] = diff_90.loc[l2, l1] = True

    def build_letters(diff_matrix, is_upper=False):
        G = nx.Graph()
        G.add_nodes_from(sorted_labels)
        for i in range(k):
            for j in range(i+1, k):
                l1, l2 = sorted_labels[i], sorted_labels[j]
                if not diff_matrix.loc[l1, l2]:
                    G.add_edge(l1, l2)
        cliques = list(nx.find_cliques(G))
        cliques.sort(key=lambda c: max([row_values[x] for x in c]), reverse=True)
        
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if is_upper else 'abcdefghijklmnopqrstuvwxyz'
        letter_map = {lbl: [] for lbl in sorted_labels}
        for idx, clique in enumerate(cliques):
            let = alphabet[idx % len(alphabet)]
            for item in clique:
                letter_map[item].append(let)
        return {lbl: "".join(sorted(letter_map[lbl])) for lbl in labels}

    map_80 = build_letters(diff_80, is_upper=False)
    map_90 = build_letters(diff_90, is_upper=True)
    
    final_res = {}
    for lbl in labels:
        l_80 = map_80[lbl]
        l_90 = map_90[lbl]
        
        # Filtra redundancias exactas entre ambos niveles
        clean_80 = "".join([c for c in l_80 if c.upper() not in l_90])
        
        # Combina manteniendo el formato exacto (ej. beF, Ac)
        res = f"{clean_80}{l_90}".strip()
        final_res[lbl] = res if res else l_90
        
    return final_res

# 2. Entrada de matriz
st.subheader("2. Pega tu matriz de Excel")
raw_input = st.text_area("Pega aquí tus datos copiados de Excel:", height=180)

if raw_input.strip():
    try:
        df = pd.read_csv(StringIO(raw_input), sep="\t")
        st.write("Vista previa de la tabla ingresada:", df.head())
        
        if st.button("🚀 Procesar Matriz y Calcular Significancias"):
            output_df = df.copy().astype(str)
            numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
            
            for idx, row in df.iterrows():
                row_vals = {}
                for col in numeric_cols:
                    val = row[col]
                    if pd.notna(val):
                        row_vals[col] = float(val)
                
                if len(row_vals) > 1:
                    letters = compute_row_letters(row_vals, sample_sizes)
                    for col in numeric_cols:
                        if col in letters:
                            output_df.at[idx, col] = f"{row_vals[col]:.2f}{letters[col]}"
            
            st.success("¡Matriz procesada con éxito!")
            st.dataframe(output_df)
            
            tsv_data = output_df.to_csv(sep="\t", index=False)
            st.text_area("Copia esto y pégalo directamente en Excel:", tsv_data, height=200)
            
    except Exception as e:
        st.error(f"Error al procesar la matriz: {e}")
