from django.shortcuts import render
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from collections import defaultdict

def danzig_algorithm(request):
    if request.method == 'POST':
        # Получение входных данных
        nodes = request.POST.get('nodes', '').strip().split()
        matrix_data = {i: {} for i in nodes}
        edges_list = []

        # Сборка матрицы смежности
        for i in nodes:
            for j in nodes:
                value = request.POST.get(f'matrix_{i}_{j}', '0').strip()
                matrix_data[i][j] = value
                if value != '0' and i != j:
                    try:
                        weight = float(value)
                        edges_list.append({
                            'source': i,
                            'destination': j,
                            'weight': weight
                        })
                    except ValueError:
                        pass  # Пропускаем некорректные значения

        # Реализация алгоритма Данцига
        dist = defaultdict(lambda: defaultdict(lambda: float('inf')))
        pred = defaultdict(lambda: defaultdict(lambda: None))
        intermediate_matrices = []

        # Инициализация (только диагональ = 0)
        for u in nodes:
            dist[u][u] = 0
            pred[u][u] = None

        # Сборка начальной матрицы только с прямыми ребрами
        nodes_sorted = sorted(nodes)
        for u in nodes:
            for v in nodes:
                if matrix_data[u][v] != '0' and u != v:
                    try:
                        weight = float(matrix_data[u][v])
                        dist[u][v] = weight
                        pred[u][v] = u
                    except ValueError:
                        dist[u][v] = float('inf')
                        pred[u][v] = None

        # Сохранение начальной матрицы
        matrix_rows = []
        for u in nodes_sorted:
            row = {'node': u, 'distances': []}
            for v in nodes_sorted:
                row['distances'].append({
                    'value': dist[u][v],
                    'display': '∞' if dist[u][v] == float('inf') else str(round(dist[u][v], 2))
                })
            matrix_rows.append(row)
        intermediate_matrices.append({
            'step_node': 'Начальная',
            'rows': matrix_rows
        })

        # Основной алгоритм Данцига (инкрементальное добавление вершин)
        for k in nodes:
            # Обновление расстояний через новую вершину k
            for i in nodes:
                for j in nodes:
                    if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                        if dist[i][j] > dist[i][k] + dist[k][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]
                            pred[i][j] = pred[k][j]

            # Сохранение промежуточной матрицы
            matrix_rows = []
            for u in nodes_sorted:
                row = {'node': u, 'distances': []}
                for v in nodes_sorted:
                    row['distances'].append({
                        'value': dist[u][v],
                        'display': '∞' if dist[u][v] == float('inf') else str(round(dist[u][v], 2))
                    })
                matrix_rows.append(row)
            intermediate_matrices.append({
                'step_node': k,
                'rows': matrix_rows
            })

        # Проверка на отрицательные циклы
        has_negative_cycle = any(dist[u][u] < 0 for u in nodes)

        # Подготовка финальных матриц
        distance_matrix = []
        predecessor_matrix = []
        for u in nodes_sorted:
            distance_row = {'node': u, 'distances': []}
            predecessor_row = {'node': u, 'predecessors': []}
            for v in nodes_sorted:
                distance_row['distances'].append({
                    'value': dist[u][v],
                    'display': '∞' if dist[u][v] == float('inf') else str(round(dist[u][v], 2))
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
        nx.draw_networkx_edges(G, pos, edge_color='#cccccc', width=1, arrowstyle='->', arrowsize=20)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return render(request, 'danzig/result.html', {
            'distance_matrix': distance_matrix,
            'predecessor_matrix': predecessor_matrix,
            'intermediate_matrices': intermediate_matrices,
            'nodes': nodes_sorted,
            'graphic': graphic,
            'edges': edges_list,
            'input_nodes': nodes,
            'matrix_data': matrix_data,
            'has_negative_cycle': has_negative_cycle
        })

    # GET-запрос — форма с тестовыми данными
    nodes = ['A', 'B', 'C', 'D', 'E']
    matrix_data = {
        'A': {'A': '0', 'B': '1', 'C': '2', 'D': '9', 'E': '20'},
        'B': {'A': '10', 'B': '0', 'C': '5', 'D': '1', 'E': '30'},
        'C': {'A': '20', 'B': '2', 'C': '0', 'D': '4', 'E': '60'},
        'D': {'A': '30', 'B': '3', 'C': '6', 'D': '0', 'E': '1'},
        'E': {'A': '40', 'B': '4', 'C': '8', 'D': '10', 'E': '0'}
    }
    return render(request, 'danzig/input.html', {
        'input_nodes': nodes,
        'matrix_data': matrix_data
    })