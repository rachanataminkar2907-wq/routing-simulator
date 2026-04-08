import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time
import pandas as pd

st.set_page_config(page_title="Routing Simulator", layout="wide")

# 🎨 Header
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>📡 Routing Algorithm Simulator</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Controls")

algorithm = st.sidebar.selectbox("Select Algorithm", ["Dijkstra", "Bellman-Ford"])
source = st.sidebar.text_input("Source Node", "A")
destination = st.sidebar.text_input("Destination Node", "D")
delay = st.sidebar.slider("⏱ Animation Speed", 0.1, 2.0, 1.0)

st.sidebar.markdown("### 🌐 Custom Network Input")

# ✅ Example with negative edge
edge_input = st.sidebar.text_area(
    "Enter edges (format: A-B-1, B-C-2)",
    "A-B-4, A-C-2, B-C--5, C-D-3"
)

# 🔧 Directed Graph
G = nx.DiGraph()

# 🧠 FIXED Parsing (handles negative values)
try:
    edges = edge_input.split(",")
    for edge in edges:
        parts = edge.strip().split("-", 2)   # 🔥 important fix
        if len(parts) != 3:
            raise ValueError(f"Invalid edge: {edge}")
        u, v, w = parts[0], parts[1], float(parts[2])
        G.add_edge(u, v, weight=w)
except Exception as e:
    st.error(f"❌ Invalid edge format: {e}")

pos = nx.spring_layout(G, seed=42)

# 🎨 Draw Graph
def draw_graph(highlight_edges=None, highlight_node=None):
    plt.clf()
    edge_labels = nx.get_edge_attributes(G, 'weight')

    nx.draw(G, pos, with_labels=True, node_color='#90CAF9', node_size=2000)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if highlight_edges:
        nx.draw_networkx_edges(G, pos, edgelist=highlight_edges, edge_color='red', width=3)

    if highlight_node:
        nx.draw_networkx_nodes(G, pos, nodelist=[highlight_node], node_color='yellow', node_size=2500)

    st.pyplot(plt)

# 🚀 Run Simulation
if st.button("🚀 Run Simulation"):
    try:
        # ⚠️ Dijkstra warning
        if algorithm == "Dijkstra":
            for _, _, w in G.edges(data='weight'):
                if w < 0:
                    st.warning("⚠️ Dijkstra cannot handle negative weights!")

        # 🔍 Run algorithm
        if algorithm == "Dijkstra":
            path = nx.dijkstra_path(G, source, destination)
            cost = nx.dijkstra_path_length(G, source, destination)
        else:
            # 🔥 Negative cycle detection
            if nx.negative_edge_cycle(G):
                st.error("❌ Graph contains a negative cycle!")
                st.stop()

            path = nx.bellman_ford_path(G, source, destination)
            cost = nx.bellman_ford_path_length(G, source, destination)

        hops = len(path) - 1

        # ✅ Output
        st.success("✅ Path Found!")
        col1, col2, col3 = st.columns(3)

        col1.metric("📍 Path", " → ".join(path))
        col2.metric("💰 Cost", cost)
        col3.metric("🔁 Hops", hops)

        # 🎬 Animation
        st.subheader("📦 Packet Traversal Animation")
        placeholder = st.empty()

        edges_in_path = list(zip(path, path[1:]))

        for i in range(len(path)):
            plt.figure()

            current_edges = edges_in_path[:i]

            nx.draw(G, pos, with_labels=True, node_color='#90CAF9', node_size=2000)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))

            if current_edges:
                nx.draw_networkx_edges(G, pos, edgelist=current_edges, edge_color='red', width=3)

            nx.draw_networkx_nodes(G, pos, nodelist=[path[i]], node_color='yellow', node_size=2500)

            placeholder.pyplot(plt)
            time.sleep(delay)

        st.success("🎯 Packet Reached Destination!")

        # 📊 Comparison
        st.subheader("📊 Algorithm Comparison")

        results = []

        # Dijkstra
        try:
            d_path = nx.dijkstra_path(G, source, destination)
            d_cost = nx.dijkstra_path_length(G, source, destination)
            results.append(["Dijkstra", d_cost, len(d_path) - 1])
        except:
            results.append(["Dijkstra", "Error", "Error"])

        # Bellman-Ford
        try:
            if nx.negative_edge_cycle(G):
                results.append(["Bellman-Ford", "Neg Cycle", "Neg Cycle"])
            else:
                b_path = nx.bellman_ford_path(G, source, destination)
                b_cost = nx.bellman_ford_path_length(G, source, destination)
                results.append(["Bellman-Ford", b_cost, len(b_path) - 1])
        except:
            results.append(["Bellman-Ford", "Error", "Error"])

        df = pd.DataFrame(results, columns=["Algorithm", "Cost", "Hops"])

        st.table(df)
        st.bar_chart(df.set_index("Algorithm"))

    except Exception as e:
        st.error(f"❌ Error: {e}")
