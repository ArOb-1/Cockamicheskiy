import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
num_nodes = 1000

# Создайте уникальные узлы
nodes = [f"Node_{i}" for i in range(num_nodes)]

# Создайте случайные связи
edges = []
np.random.seed(42)  # Для воспроизводимости результатов
for _ in range(num_nodes * 2):  # Установите количество связей
    source = np.random.choice(nodes)
    target = np.random.choice(nodes)
    while source == target:  # Убедитесь, что связь не само-ссылка
        target = np.random.choice(nodes)
    weight = np.random.randint(1, 10)  # Вес ребра от 1 до 10
    edges.append([source, target, weight])

# Создайте DataFrame и сохраните в CSV
df = pd.DataFrame(edges, columns=['Source', 'Target', 'Weight'])
df.to_csv('file.csv', index=False)
# Загрузка данных и создание графа
df = pd.read_csv('file.csv')
G = nx.from_pandas_edgelist(df, 'Source', 'Target', ['Weight'])

# Поиск компонент связности
components = list(nx.connected_components(G))
component_map = {node: i for i, comp in enumerate(components) for node in comp}

# Генерация цветов
unique_components = len(components)
colors = list(mcolors.TABLEAU_COLORS.values())
if unique_components > len(colors):
    cmap = plt.get_cmap('tab20')
    colors = [mcolors.to_hex(cmap(i / unique_components)) for i in range(unique_components)]
component_colors = {i: colors[i % len(colors)] for i in range(unique_components)}

# Координаты узлов
pos = nx.spring_layout(G, dim=3, seed=42)

# 3D график
fig_3d = go.Figure()

# Добавление рёбер
edge_x = []
edge_y = []
edge_z = []
for e in df.itertuples():
    x0, y0, z0 = pos[e.Source]
    x1, y1, z1 = pos[e.Target]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])
    edge_z.extend([z0, z1, None])

fig_3d.add_trace(go.Scatter3d(
    x=edge_x,
    y=edge_y,
    z=edge_z,
    mode='lines',
    line=dict(width=2, color='#888'),
))

# Добавление узлов
node_x, node_y, node_z = zip(*[pos[node] for node in G.nodes()])
node_color = [component_colors[component_map[node]] for node in G.nodes()]

fig_3d.add_trace(go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode='markers+text',
    marker=dict(size=8, color=node_color),
    text=list(G.nodes()),
    textposition='bottom center'
))

fig_3d.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z'
    ),
    margin=dict(r=10, l=10, b=10, t=10),
    autosize=True
)

fig_3d.write_html('3d_graph_plotly_clustering_interactive.html')

# 2D график
fig_2d = go.Figure()

# Добавление рёбер
edge_x_2d = [pos[e.Source][0] for e in df.itertuples()] + [None]
edge_y_2d = [pos[e.Source][1] for e in df.itertuples()] + [None]

fig_2d.add_trace(go.Scatter(
    x=edge_x_2d,
    y=edge_y_2d,
    mode='lines',
    line=dict(width=2, color='#888'),
))

# Добавление узлов
fig_2d.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',
    marker=dict(size=8, color=node_color),
    text=list(G.nodes()),
    textposition='bottom center'
))

fig_2d.update_layout(
    xaxis_title='X',
    yaxis_title='Y',
    margin=dict(r=10, l=10, b=10, t=10),
    autosize=True
)

fig_2d.write_html('2d_graph_plotly_clustering.html')
