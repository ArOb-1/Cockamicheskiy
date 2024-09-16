import networkx as nx
import plotly.graph_objects as go
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import pandas as pd

# Чтение данных из CSV файлов, содержащих информацию о рёбрах и узлах графа
edges_df = pd.read_csv('edges.csv')  # Чтение файла с рёбрами (источник, цель и вес ребра)
nodes_df = pd.read_csv('nodes.csv')  # Чтение файла с узлами (идентификатор узла и его атрибуты)

# Создание графа на основе данных рёбер с использованием NetworkX
G = nx.from_pandas_edgelist(edges_df, 'Source', 'Target', ['Weight'])

# Добавление узлов в граф с атрибутами из таблицы узлов
for _, row in nodes_df.iterrows():
    G.add_node(row['Node'], **row.to_dict())

# Находим компоненты связности в графе (группы узлов, между которыми есть путь)
components = list(nx.connected_components(G))
component_map = {}  # Словарь для маппинга узлов к их компонентам
for i, comp in enumerate(components):
    for node in comp:
        component_map[node] = i  # Присваиваем узлам индекс их компонента

# Генерация уникальных цветов для каждой компоненты графа
unique_components = len(components)  # Количество компонент
colors = list(mcolors.TABLEAU_COLORS.values())  # Используем встроенные цвета matplotlib
# Если компонент больше, чем доступных цветов, используем палитру 'tab20'
if unique_components > len(colors):
    cmap = plt.get_cmap('tab20')  # Загружаем палитру с большим количеством цветов
    colors = [mcolors.to_hex(cmap(i / unique_components)) for i in range(unique_components)]
# Создаём маппинг цветов для каждой компоненты
component_colors = {i: colors[i % len(colors)] for i in range(unique_components)}

# Отладочный вывод для проверки назначения цветов компонентам
print("Component colors mapping:")
for i, color in component_colors.items():
    print(f"Component {i}: {color}")

# Получение 3D координат узлов с использованием spring_layout
# Определяем положение узлов в трёхмерном пространстве для визуализации
pos = nx.spring_layout(G, dim=3, seed=42)

# Подготовка данных для рёбер графа (координаты начала и конца каждого ребра)
edge_x = []
edge_y = []
edge_z = []
for e in edges_df.itertuples():
    x0, y0, z0 = pos[e.Source]
    x1, y1, z1 = pos[e.Target]
    edge_x.extend([x0, x1, None])  # Добавляем координаты концов ребра и None для разрыва
    edge_y.extend([y0, y1, None])
    edge_z.extend([z0, z1, None])

# Подготовка данных для узлов графа (координаты и цвет узла)
node_x = []
node_y = []
node_z = []
node_text = []
node_color = []
for node in G.nodes():
    x, y, z = pos[node]
    node_x.append(x)  # Координаты X узла
    node_y.append(y)  # Координаты Y узла
    node_z.append(z)  # Координаты Z узла
    node_text.append(node)  # Текстовое отображение узла
    node_color.append(component_colors[component_map[node]])  # Цвет в зависимости от компоненты

# Создание 3D графика с помощью Plotly
fig_3d = go.Figure()

# Добавление рёбер на 3D график
fig_3d.add_trace(go.Scatter3d(
    x=edge_x,
    y=edge_y,
    z=edge_z,
    mode='lines',
    line=dict(width=1, color='#888'),
    opacity=0.7  # Полупрозрачность рёбер
))

# Добавление узлов на 3D график
fig_3d.add_trace(go.Scatter3d(
    x=node_x,
    y=node_y,
    z=node_z,
    mode='markers+text',  # Узлы с текстовыми подписями
    marker=dict(size=5, color=node_color),  # Цвет узлов в зависимости от компоненты
    text=node_text,  # Подписи узлов
    textposition='bottom center',  # Позиция текста
    opacity=0.9  # Прозрачность узлов
))

# Настройка осей и внешнего вида 3D графика
fig_3d.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
    ),
    margin=dict(r=10, l=10, b=10, t=10),  # Поля графика
    autosize=True
)

# Сохранение 3D графика в HTML файл для интерактивного просмотра
fig_3d.write_html('3d_graph_plotly_clustering_interactive.html', include_plotlyjs='cdn', post_script='')

# Генерация 2D графика для более простой визуализации
fig_2d = go.Figure()

# Добавление рёбер на 2D график (используются только координаты X и Y)
fig_2d.add_trace(go.Scatter(
    x=[pos[e.Source][0] for e in edges_df.itertuples()] + [None],
    y=[pos[e.Source][1] for e in edges_df.itertuples()] + [None],
    mode='lines',
    line=dict(width=1, color='#888'),
    opacity=0.5  # Прозрачность рёбер
))

# Добавление узлов на 2D график (используются только координаты X и Y)
fig_2d.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode='markers+text',  # Узлы с текстовыми подписями
    marker=dict(size=5, color=node_color),  # Цвет узлов
    text=node_text,
    textposition='bottom center',
    opacity=0.7
))

# Настройка осей и внешнего вида 2D графика
fig_2d.update_layout(
    xaxis_title='X',
    yaxis_title='Y',
    margin=dict(r=10, l=10, b=10, t=10),
    autosize=True
)

# Сохранение 2D графика в HTML файл
fig_2d.write_html('2d_graph_plotly_clustering.html')
