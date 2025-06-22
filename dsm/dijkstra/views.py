from django.shortcuts import render
import networkx as nx
import matplotlib

matplotlib.use('Agg')  # Set non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64


def dijkstra_algorithm(request):
    if request.method == 'POST':
        # Получаем вершины и параметры
        nodes = request.POST.get('nodes', '').strip().split()
        start = request.POST.get('start', '').strip()
        end = request.POST.get('end', '').strip()

        # Собираем матрицу смежности
        edges_list = []
        matrix_data = {i: {} for i in nodes}
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

        # Реализация алгоритма Дейкстры с отслеживанием предшественников
        distances = {node: float('inf') for node in nodes}
        predecessors = {node: None for node in nodes}
        distances[start] = 0

        # Используем множество необработанных вершин
        unvisited = set(nodes)
        while unvisited:
            # Находим вершину с минимальным расстоянием
            current = min(unvisited, key=lambda node: distances[node])
            if distances[current] == float('inf'):
                break  # Все оставшиеся вершины недостижимы
            unvisited.remove(current)

            # Обновляем расстояния до соседей
            for edge in [e for e in edges_list if e['source'] == current]:
                neighbor = edge['destination']
                weight = edge['weight']
                if distances[current] + weight < distances[neighbor]:
                    distances[neighbor] = distances[current] + weight
                    predecessors[neighbor] = current

        # Проверка на отрицательные циклы
        has_negative_cycle = False
        for edge in edges_list:
            if distances[edge['source']] + edge['weight'] < distances[edge['destination']]:
                has_negative_cycle = True
                break

        # Построение пути от start до end
        path = []
        path_length = distances[end] if end in distances else float('inf')
        if path_length != float('inf'):
            current = end
            while current is not None:
                path.append(current)
                current = predecessors[current]
            path.reverse()
            if path[0] != start:
                path = []  # Путь не существует
                path_length = float('inf')

        # Визуализация
        G = nx.DiGraph()  # Используем направленный граф
        for edge in edges_list:
            G.add_edge(edge['source'], edge['destination'], weight=edge['weight'])

        pos = nx.spring_layout(G, seed=42)
        plt.figure(figsize=(10, 6))

        node_colors = []
        for node in G.nodes():
            if node == start:
                node_colors.append('#4CAF50')
            elif node == end:
                node_colors.append('#FF5722')  # Красный для конечной вершины
            elif distances[node] != float('inf'):
                node_colors.append('#2196F3')
            else:
                node_colors.append('#cccccc')

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700)
        labels = {node: f"{node}\n({distances[node] if distances[node] != float('inf') else '∞'})" for node in
                  G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_color='white')

        # Отрисовка рёбер с подсветкой пути
        edge_colors = []
        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        for u, v in G.edges():
            if (u, v) in path_edges:
                edge_colors.append('#FF5722')  # Красный для рёбер пути
            else:
                edge_colors.append('#cccccc')

        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=1)
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return render(request, 'dijkstra/result.html', {
            'distances': distances,
            'has_negative_cycle': has_negative_cycle,
            'start': start,
            'end': end,
            'graphic': graphic,
            'nodes': nodes,
            'edges': edges_list,
            'input_nodes': nodes,
            'matrix_data': matrix_data,
            'input_start': start,
            'input_end': end,
            'path': path,
            'path_length': path_length
        })

    return render(request, 'dijkstra/input.html', {
        'input_nodes': ['A', 'B', 'C', 'D', 'E', 'F'],
        'matrix_data': {}
    })