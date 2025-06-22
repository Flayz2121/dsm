from django.shortcuts import render
import networkx as nx
import matplotlib

matplotlib.use('Agg')  # Set non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import defaultdict


def floyd_warshall_algorithm(request):
    if request.method == 'POST':
        # Получаем вершины и матрицу смежности
        nodes = request.POST.get('nodes', '').strip().split()
        matrix_data = {i: {} for i in nodes}
        edges_list = []

        # Собираем матрицу смежности
        for i in nodes:
            for j in nodes:
                value = request.POST.get(f'matrix_{i}_{j}', '0').strip()
                matrix_data[i][j] = value
                if value != '0' and i != j:
                    try:
                        weight = int(value)
                        edges_list.append({
                            'source': i,
                            'destination': j,
                            'weight': weight
                        })
                    except ValueError:
                        pass  # Пропускаем некорректные значения

        # Реализация алгоритма Флойда-Уоршелла
        dist = defaultdict(dict)
        pred = defaultdict(dict)  # Матрица предшественников

        # Инициализация матриц
        for u in nodes:
            for v in nodes:
                if u == v:
                    dist[u][v] = 0
                    pred[u][v] = None
                elif matrix_data[u][v] != '0':
                    try:
                        dist[u][v] = int(matrix_data[u][v])
                        pred[u][v] = u
                    except ValueError:
                        dist[u][v] = float('inf')
                        pred[u][v] = None
                else:
                    dist[u][v] = float('inf')
                    pred[u][v] = None

        # Основной алгоритм
        for k in nodes:
            for i in nodes:
                for j in nodes:
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pred[i][j] = pred[k][j]

        # Проверка на отрицательные циклы
        has_negative_cycle = any(dist[u][u] < 0 for u in nodes)

        # Подготовка данных для таблиц
        nodes_sorted = sorted(nodes)
        distance_matrix = []
        predecessor_matrix = []
        for u in nodes_sorted:
            distance_row = {'node': u, 'distances': []}
            predecessor_row = {'node': u, 'predecessors': []}
            for v in nodes_sorted:
                distance_row['distances'].append({
                    'value': dist[u][v],
                    'display': '∞' if dist[u][v] == float('inf') else str(dist[u][v])
                })
                predecessor_row['predecessors'].append({
                    'value': pred[u][v],
                    'display': '-' if pred[u][v] is None else pred[u][v]
                })
            distance_matrix.append(distance_row)
            predecessor_matrix.append(predecessor_row)

        # Визуализация графа
        G = nx.DiGraph()
        for edge in edges_list:
            G.add_edge(edge['source'], edge['destination'], weight=edge['weight'])

        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(10, 6))

        nx.draw_networkx_nodes(G, pos, node_color='#2196F3', node_size=700)
        nx.draw_networkx_labels(G, pos, font_color='white')
        nx.draw_networkx_edges(G, pos, edge_color='#cccccc', width=1,
                               arrowstyle='->', arrowsize=20)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return render(request, 'floyd_warshall/result.html', {
            'distance_matrix': distance_matrix,
            'predecessor_matrix': predecessor_matrix,
            'nodes': nodes_sorted,
            'graphic': graphic,
            'edges': edges_list,
            'input_nodes': nodes,
            'matrix_data': matrix_data,
            'has_negative_cycle': has_negative_cycle,
            'infinity': float('inf')
        })

    # GET-запрос — форма с тестовыми данными
    nodes = ['A', 'B', 'C', 'D', 'E']
    matrix_data = {
        'A': {'A': '0', 'B': '0', 'C': '0', 'D': '0', 'E': '0'},
        'B': {'A': '0', 'B': '0', 'C': '0', 'D': '0', 'E': '0'},
        'C': {'A': '0', 'B': '0', 'C': '0', 'D': '0', 'E': '0'},
        'D': {'A': '0', 'B': '0', 'C': '0', 'D': '0', 'E': '0'},
        'E': {'A': '0', 'B': '0', 'C': '0', 'D': '0', 'E': '0'}
    }
    return render(request, 'floyd_warshall/input.html', {
        'input_nodes': nodes,
        'matrix_data': matrix_data
    })