import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time
import pandas as pd

st.set_page_config(page_title="Routing Simulator", layout="wide")

# 🎨 UI Header
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>📡 Routing Algorithm Simulator</h1>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar Controls
st.sidebar.header("⚙️ Controls")

algorithm = st.sidebar.selectbox("Select Algorithm", ["Dijkstra", "Bellman-Ford"])
source = st.sidebar.text_input("Source Node", "A")
destination = st.sidebar.text_input("Destination Node", "F")

delay = st.sidebar.slider("⏱ Animation Speed (seconds)", 0.1, 2.0, 1.0)

st.sidebar.markdown("### 🌐 Custom Network Input")
edge_input = st.sidebar.text_area(
    "Enter edges (format: A-B-1, B-C-2)",
    "A-B-1, B-C-2, A-D-4, B-E-3, C-F-5, D-E-1, E-F-2"
)

# 🔧 Build Graph from User Input
G = nx.Graph()

try:
    edges = edge_input.split(",")
    for edge in edges:
        u, v, w = edge.strip().split("-")
        G.add_edge(u, v, weight=float(w))
except:
    st.error("❌ Invalid edge format")

pos = nx.spring_layout(G)

# 📊 Graph Drawing Function
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
        # Algorithm execution
        if algorithm == "Dijkstra":
            path = nx.dijkstra_path(G, source, destination)
            cost = nx.dijkstra_path_length(G, source, destination)
        else:
            path = nx.bellman_ford_path(G, source, destination)
            cost = nx.bellman_ford_path_length(G, source, destination)

        hops = len(path) - 1

        # Output
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

        # 📊 Comparison Chart
        st.subheader("📊 Algorithm Comparison")

        d_path = nx.dijkstra_path(G, source, destination)
        d_cost = nx.dijkstra_path_length(G, source, destination)

        b_path = nx.bellman_ford_path(G, source, destination)
        b_cost = nx.bellman_ford_path_length(G, source, destination)

        data = pd.DataFrame({
            "Algorithm": ["Dijkstra", "Bellman-Ford"],
            "Cost": [d_cost, b_cost],
            "Hops": [len(d_path)-1, len(b_path)-1]
        })

        st.table(data)
        st.bar_chart(data.set_index("Algorithm"))

    except:
        st.error("❌ Error: Check nodes or graph connectivity")