import networkx as nx
import plotly.graph_objects as go
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

# Чтение данных из CSV файлов
edges_df = pd.read_csv('edges.csv')  # Файл с рёбрами
nodes_df = pd.read_csv('nodes.csv')  # Файл с узлами

# Создание графа на основе данных рёбер
G = nx.from_pandas_edgelist(edges_df, 'Source', 'Target', ['Weight'])

# Добавление узлов с атрибутами
for _, row in nodes_df.iterrows():
    G.add_node(row['Node'], **row.to_dict())

# Находим компоненты связности
components = list(nx.connected_components(G))
component_map = {}
for i, comp in enumerate(components):
    for node in comp:
        component_map[node] = i

# Генерация уникальных цветов для каждого компонента
unique_components = len(components)
colors = list(mcolors.TABLEAU_COLORS.values())
if unique_components > len(colors):
    cmap = plt.get_cmap('tab20')
    colors = [mcolors.to_hex(cmap(i / unique_components)) for i in range(unique_components)]
component_colors = {i: colors[i % len(colors)] for i in range(unique_components)}

# Отладка: Вывод цветов для проверки
print("Component colors mapping:")
for i, color in component_colors.items():
    print(f"Component {i}: {color}")

# Получите координаты узлов для визуализации
pos = nx.spring_layout(G, dim=3, seed=42)

# Генерация 3D графика
edge_x = []
edge_y = []
edge_z = []
for e in edges_df.itertuples():
    x0, y0, z0 = pos[e.Source]
    x1, y1, z1 = pos[e.Target]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    edge_z.extend([z0, z1, None])

node_x = []
node_y = []
node_z = []
node_text = []
node_color = []
for node in G.nodes():
    x, y, z = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_z.append(z)
    node_text.append(node)
    node_color.append(component_colors[component_map[node]])

fig_3d = go.Figure()

# Добавляем рёбра в 3D график
fig_3d.add_trace(go.Scatter3d(
    x=edge_x,
    y=edge_y,
    z=edge_z,
    mode='lines',
    line=dict(width=1, color='#888'),
    opacity=0.7
))

# Добавляем узлы в 3D график
fig_3d.add_trace(go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode='markers+text',
    marker=dict(size=5, color=node_color),
    text=node_text,
    textposition='bottom center',
    opacity=0.9
))

fig_3d.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
    ),
    margin=dict(r=10, l=10, b=10, t=10),
    autosize=True
)

# Сохранение графика в HTML
fig_3d.write_html('3d_graph_plotly_clustering_interactive.html', include_plotlyjs='cdn', post_script='')

# Генерация 2D графика
fig_2d = go.Figure()

# Добавляем рёбра в 2D график
fig_2d.add_trace(go.Scatter(
    x=[pos[e.Source][0] for e in edges_df.itertuples()] + [None],
    y=[pos[e.Source][1] for e in edges_df.itertuples()] + [None],
    mode='lines',
    line=dict(width=1, color='#888'),
    opacity=0.5
))

# Добавляем узлы в 2D график
fig_2d.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    marker=dict(size=5, color=node_color),
    text=node_text,
    textposition='bottom center',
    opacity=0.7
))

fig_2d.update_layout(
    xaxis_title='X',
    yaxis_title='Y',
    margin=dict(r=10, l=10, b=10, t=10),
    autosize=True
)

# Сохранение графика в HTML
fig_2d.write_html('2d_graph_plotly_clustering.html')
