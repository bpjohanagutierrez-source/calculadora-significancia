import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import networkx as nx
from io import StringIO

st.set_page_config(page_title="Matriz de Significancia Estadística", layout="wide")

st.title("📊 Calculadora de Diferencias Significativas")
st.markdown("""
**Instrucciones:**
1. Copia tu matriz desde Excel (con encabezados de filas y columnas).
2. Pégala en el recuadro de abajo.
3. Haz clic en calcular para obtener las letras (minúsculas al 80% y MAYÚSCULAS al 90%).
""")

def compute_cld_dual(group_means, group_stds, group_ns):
    labels = list(group_means.keys())
    k = len(labels)
    if k <= 1:
        return {l: "a A" for l in labels}
    
    sorted_labels = sorted(labels, key=lambda x: group_means[x], reverse=True)
    diff_80 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    diff_90 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    
    num_comp = k * (k - 1) / 2
    for i in range(k):
        for j in range(i+1, k):
            l1, l2 = sorted_labels[i], sorted_labels[j]
            m1, m2 = group_means[l1], group_means[l2]
            s1, s2 = group_stds[l1], group_stds[l2]
            n1, n2 = group_ns[l1], group_ns[l2]
            
            se_diff = np.sqrt((s1**2)/n1 + (s2**2)/n2)
            if se_diff == 0:
                p_val = 1.0 if m1 == m2 else 0.0
            else:
                t_stat = abs(m1 - m2) / se_diff
                df = n1 + n2 - 2
                p_val = 2 * (1 - stats.t.cdf(t_stat, df=df))
            
            p_adj = min(1.0, p_val * num_comp)
            
            if p_adj < 0.20: # 80% Confianza (minúsculas)
                diff_80.loc[l1, l2] = diff_80.loc[l2, l1] = True
            if p_adj < 0.10: # 90% Confianza (MAYÚSCULAS)
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
        cliques.sort(key=lambda c: max([group_means[x] for x in c]), reverse=True)
        
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if is_upper else 'abcdefghijklmnopqrstuvwxyz'
        letter_map = {lbl: [] for lbl in sorted_labels}
        for idx, clique in enumerate(cliques):
            let = alphabet[idx % len(alphabet)]
            for item in clique:
                letter_map[item].append(let)
        return {lbl: "".join(sorted(letter_map[lbl])) for lbl in labels}

    letters_80 = get_letters(diff_80, is_upper=False)
    letters_90 = get_letters(diff_90, is_upper=True)
    
    return {lbl: f"{letters_80[lbl]} {letters_90[lbl]}" for lbl in labels}

raw_input = st.text_area("Pega aquí tu matriz copiada de Excel:", height=180)

if raw_input.strip():
    try:
        df = pd.read_csv(StringIO(raw_input), sep="\t")
        st.write("Vista previa de los datos:", df.head())
        
        if st.button("🚀 Procesar Matriz y Calcular Letras"):
            output_df = df.copy().astype(str)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for idx, row in df.iterrows():
                means, stds, ns = {}, {}, {}
                for col in numeric_cols:
                    val = row[col]
                    if pd.notna(val):
                        means[col] = float(val)
                        stds[col] = float(val) * 0.08 # Desviación estándar estimada
                        ns[col] = 30                 # Muestra estimada
                
                if len(means) > 1:
                    letters = compute_cld_dual(means, stds, ns)
                    for col in numeric_cols:
                        if col in letters:
                            output_df.at[idx, col] = f"{means[col]:.2f} {letters[col]}"
            
            st.success("¡Matriz procesada correctamente!")
            st.dataframe(output_df)
            
            tsv_data = output_df.to_csv(sep="\t", index=False)
            st.text_area("Copia esto y pégalo directamente en Excel:", tsv_data, height=180)
            
    except Exception as e:
        st.error(f"Ocurrió un error al leer la tabla: {e}")
