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
1. Ingresa el tamaño de muestra ($N$) para cada una de tus columnas.
2. Pega tu matriz de datos copiada directamente desde Excel.
3. Haz clic en **Procesar Matriz** para generar la tabla formateada (ej. `63.10beF`).
""")

# Área para definir muestras específicas por columna
st.subheader("1. Configuración del tamaño de muestra (N)")
col_samples_input = st.text_input(
    "Ingresa los valores de N separados por comas (en orden de tus columnas de Excel):",
    value="590, 598, 618, 595, 597, 577"
)

# Procesamiento de la lista de N
try:
    sample_sizes = [int(n.strip()) for n in col_samples_input.split(",") if n.strip()]
except ValueError:
    st.error("Por favor ingresa únicamente números enteros separados por comas para las muestras.")
    sample_sizes = [100]

def compute_cld_exact_custom(group_means, group_stds, n_dict):
    labels = list(group_means.keys())
    k = len(labels)
    if k <= 1:
        return {l: "A" for l in labels}
    
    sorted_labels = sorted(labels, key=lambda x: group_means[x], reverse=True)
    diff_80 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    diff_90 = pd.DataFrame(False, index=sorted_labels, columns=sorted_labels)
    
    num_comp = k * (k - 1) / 2
    for i in range(k):
        for j in range(i+1, k):
            l1, l2 = sorted_labels[i], sorted_labels[j]
            m1, m2 = group_means[l1], group_means[l2]
            s1, s2 = group_stds[l1], group_stds[l2]
            n1, n2 = n_dict[l1], n_dict[l2]
            
            # Error estándar usando la muestra específica de cada columna
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

    def get_cliques_map(diff_matrix, is_upper=False):
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
                letter_map[item].append((let, idx))
        return letter_map

    map_80 = get_cliques_map(diff_80, is_upper=False)
    map_90 = get_cliques_map(diff_90, is_upper=True)
    
    final_letters = {}
    for lbl in labels:
        items_90 = map_90[lbl]
        items_80 = map_80[lbl]
        
        indices_90 = {idx for _, idx in items_90}
        
        upper_str = "".join(sorted([let for let, _ in items_90]))
        
        # Mantiene las minúsculas combinables y filtra las redundantes directas
        valid_lowers = [let for let, idx in items_80 if idx not in indices_90]
        lower_str = "".join(sorted(valid_lowers))
        
        # Formato compacto pegado (minúsculas primero y luego MAYÚSCULAS o viceversa)
        res = f"{lower_str}{upper_str}".strip()
        final_letters[lbl] = res if res else upper_str
            
    return final_letters

st.subheader("2. Pega tu matriz de Excel")
raw_input = st.text_area("Pega aquí los datos copiados directamente de Excel:", height=180)

if raw_input.strip():
    try:
        df = pd.read_csv(StringIO(raw_input), sep="\t")
        st.write("Vista previa de los datos ingresados:", df.head())
        
        if st.button("🚀 Procesar Matriz y Calcular Significancias"):
            output_df = df.copy().astype(str)
            numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
            
            # Asignación de muestras por columna
            n_dict = {}
            for i, col in enumerate(numeric_cols):
                if i < len(sample_sizes):
                    n_dict[col] = sample_sizes[i]
                else:
                    n_dict[col] = sample_sizes[-1] # Usa el último si faltan valores
            
            for idx, row in df.iterrows():
                means, stds = {}, {}
                for col in numeric_cols:
                    val = row[col]
                    if pd.notna(val):
                        means[col] = float(val)
                        stds[col] = float(val) * 0.08 # SD estimada del 8%
                
                if len(means) > 1:
                    letters = compute_cld_exact_custom(means, stds, n_dict)
                    for col in numeric_cols:
                        if col in letters:
                            # Formato compacto directo sin espacios (ej: 63.10beF)
                            output_df.at[idx, col] = f"{means[col]:.2f}{letters[col]}"
            
            st.success("¡Matriz procesada con éxito!")
            st.dataframe(output_df)
            
            tsv_data = output_df.to_csv(sep="\t", index=False)
            st.text_area("Resultado listo para copiar y pegar de vuelta en Excel:", tsv_data, height=200)
            
    except Exception as e:
        st.error(f"Error al procesar la matriz: {e}")
