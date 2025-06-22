from collections import defaultdict, deque
from django.shortcuts import render
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def ford_fulkerson(request):
    if request.method == 'POST':
        vertices = request.POST.getlist('vertices[]')
        source = request.POST.get('source')
        sink = request.POST.get('sink')

        n = len(vertices)
        capacity = []
        for i in range(n):
            row = []
            for j in range(n):
                val = request.POST.get(f'matrix_{i}_{j}', '0')
                try:
                    val_int = int(val)
                except ValueError:
                    val_int = 0
                row.append(val_int)
            capacity.append(row)

        # Создаём остаточный граф
        graph = defaultdict(dict)
        for i in range(n):
            for j in range(n):
                if capacity[i][j] > 0:
                    graph[vertices[i]][vertices[j]] = capacity[i][j]
                else:
                    graph[vertices[i]][vertices[j]] = 0

        def bfs(residual_graph, s, t, parent):
            visited = set()
            queue = deque([s])
            visited.add(s)
            while queue:
                u = queue.popleft()
                for v in residual_graph[u]:
                    if v not in visited and residual_graph[u][v] > 0:
                        visited.add(v)
                        parent[v] = u
                        if v == t:
                            return True
                        queue.append(v)
            return False

        # Алгоритм Форда-Фалкерсона
        parent = {}
        max_flow = 0
        residual_graph = graph.copy()  # Копия графа для остаточного графа

        while bfs(residual_graph, source, sink, parent):
            path_flow = float('inf')
            s = sink
            while s != source:
                path_flow = min(path_flow, residual_graph[parent[s]][s])
                s = parent[s]

            max_flow += path_flow
            v = sink
            while v != source:
                u = parent[v]
                residual_graph[u][v] -= path_flow
                residual_graph[v][u] = residual_graph[v].get(u, 0) + path_flow
                v = parent[v]

        # Матрица потока
        flow_matrix = [[0] * n for _ in range(n)]
        edges_list = []
        for i in range(n):
            for j in range(n):
                original = capacity[i][j]
                residual = residual_graph[vertices[i]][vertices[j]]
                flow = original - residual
                if original > 0:
                    flow_matrix[i][j] = max(flow, 0)
                    edges_list.append({
                        'source': vertices[i],
                        'destination': vertices[j],
                        'capacity': original,
                        'flow': max(flow, 0)
                    })

        # Нахождение минимального разреза
        min_cut = []
        reachable = set()
        queue = deque([source])
        reachable.add(source)
        while queue:
            u = queue.popleft()
            for v in residual_graph[u]:
                if v not in reachable and residual_graph[u][v] > 0:
                    reachable.add(v)
                    queue.append(v)

        # Рёбра разреза: из достижимых в недостижимые вершины
        for u in reachable:
            for v in vertices:
                if v not in reachable and capacity[vertices.index(u)][vertices.index(v)] > 0:
                    min_cut.append({
                        'source': u,
                        'destination': v,
                        'capacity': capacity[vertices.index(u)][vertices.index(v)]
                    })

        # Визуализация графа
        G = nx.DiGraph()
        G.add_nodes_from(vertices)

        for edge in edges_list:
            G.add_edge(edge['source'], edge['destination'],
                       capacity=edge['capacity'],
                       flow=edge['flow'],
                       label=f"{edge['flow']}/{edge['capacity']}")

        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(10, 6))

        nx.draw_networkx_nodes(G, pos, node_color='#2196F3', node_size=700)
        if source in G.nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=[source], node_color='#4CAF50', node_size=800)
        if sink in G.nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=[sink], node_color='#F44336', node_size=800)

        edge_colors = ['#4CAF50' if edge['flow'] > 0 else '#cccccc' for edge in edges_list]
        edge_widths = [2 if edge['flow'] > 0 else 1 for edge in edges_list]

        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths,
                               arrowstyle='-|>', arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_color='white')
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Подготовка данных для матриц
        capacity_data = [{'row_index': i, 'vertex': vertices[i], 'values': capacity[i]} for i in range(n)]
        flow_matrix_data = [{'row_index': i, 'vertex': vertices[i], 'values': flow_matrix[i]} for i in range(n)]

        return render(request, 'ford_fulkerson/result.html', {
            'vertices': vertices,
            'capacity_data': capacity_data,
            'flow_matrix': flow_matrix_data,
            'edges': edges_list,
            'max_flow': max_flow,
            'graphic': graphic,
            'source': source,
            'sink': sink,
            'input_source': source,
            'input_sink': sink,
            'input_vertices': vertices,
            'min_cut': min_cut
        })

    # GET-запрос — форма с тестовыми данными
    vertices = ['A', 'B', 'C', 'D', 'E']
    n = len(vertices)
    capacity = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0,0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]

    capacity_data = [{'row_index': i, 'vertex': vertices[i], 'values': capacity[i]} for i in range(n)]

    return render(request, 'ford_fulkerson/input.html', {
        'vertices': vertices,
        'capacity_data': capacity_data,
        'source': vertices[0],
        'sink': vertices[-1],
    })