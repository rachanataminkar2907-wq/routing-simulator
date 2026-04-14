import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide")
st.title("📡 Routing Algorithm Simulator")

# Sidebar
algorithm = st.sidebar.selectbox("Select Algorithm", ["Dijkstra", "Bellman-Ford"])
mode = st.sidebar.selectbox("Select Mode", ["Theoretical", "Practical"])
speed = st.sidebar.slider("⏱️ Animation Speed", 0.1, 2.0, 1.0)

st.sidebar.markdown("---")
edge_input = st.sidebar.text_area(
    "Add Edges (u v weight)",
    "A B 5\nB C 2\nA C -2\nA D -5\nD C 2"
)

# Build Graph
G = nx.DiGraph()

for line in edge_input.split("\n"):
    try:
        u, v, w = line.split()
        G.add_edge(u, v, weight=float(w))
    except:
        pass

# 🔥 Clean fixed layout (no overlap)
pos = {
    'A': (0, 1),
    'B': (-1, 0),
    'C': (1, 0),
    'D': (0, -1)
}

# Draw function
def draw_graph(path_edges=[], current_node=None):
    plt.figure()

    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2000)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    # Highlight shortest path
    if path_edges:
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color="red", width=3)

    # Moving packet
    if current_node:
        x, y = pos[current_node]
        plt.scatter(x, y, s=600)

    st.pyplot(plt)

# Get all paths (DFS)
def get_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]

    paths = []
    for node in graph.neighbors(start):
        if node not in path:
            new_paths = get_all_paths(graph, node, end, path)
            for p in new_paths:
                paths.append(p)
    return paths

# Source & Destination
nodes = list(G.nodes())
if len(nodes) >= 2:
    source = st.selectbox("Source", nodes)
    target = st.selectbox("Target", nodes)

    if st.button("Run Simulation"):

        # Practical Mode Handling
        if mode == "Practical":
            negative_edges = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] < 0]
            if negative_edges:
                st.warning("Negative edges ignored in practical mode")
                G.remove_edges_from(negative_edges)

        try:
            # Show all paths
            st.subheader("📊 All Possible Paths")
            all_paths = get_all_paths(G, source, target)

            for p in all_paths:
                cost = sum(G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1))
                st.write(f"Path: {' → '.join(p)} | Cost: {cost}")

            # Run Algorithm
            if algorithm == "Dijkstra":
                for u, v, d in G.edges(data=True):
                    if d['weight'] < 0:
                        st.error("Dijkstra cannot handle negative weights")
                        st.stop()

                shortest_path = nx.dijkstra_path(G, source, target)
                shortest_cost = nx.dijkstra_path_length(G, source, target)

            else:
                shortest_path = nx.bellman_ford_path(G, source, target)
                shortest_cost = nx.bellman_ford_path_length(G, source, target)

            st.success(f"✅ Shortest Path: {' → '.join(shortest_path)} | Cost: {shortest_cost}")

            # 🔥 Animation
            st.subheader("📦 Shortest Path Tracking")

            path_edges = list(zip(shortest_path, shortest_path[1:]))
            placeholder = st.empty()

            for i in range(len(shortest_path)):
                plt.figure()

                # Draw all edges in black
                nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=2000)
                labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

                # Highlight only shortest path
                nx.draw_networkx_edges(G, pos, edgelist=path_edges[:i], edge_color="red", width=3)

                # Moving packet
                current_node = shortest_path[i]
                x, y = pos[current_node]
                plt.scatter(x, y, s=600)

                placeholder.pyplot(plt)
                time.sleep(speed)

        except nx.NetworkXUnbounded:
            st.error("Negative cycle detected!")
        except:
            st.error("No valid path found")

else:
    st.info("Add at least 2 nodes")
