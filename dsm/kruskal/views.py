import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render


def kruskal_algorithm(request):
    vertices = ['A', 'B', 'C', 'D', 'E', 'F']
    if request.method == 'POST':
        # Читаем матрицу смежности из формы
        matrix = []
        size = len(vertices)
        for i in range(size):
            row = []
            for j in range(size):
                key = f"matrix_{i}_{j}"
                val = request.POST.get(key, '0')
                try:
                    w = int(val)
                except ValueError:
                    w = 0
                row.append(w)
            matrix.append(row)

        # Преобразуем матрицу в список рёбер (только i >= j, чтобы не дублировать)
        edges_list = []
        for i in range(size):
            for j in range(i + 1):
                weight = matrix[i][j]
                if weight > 0:
                    edges_list.append({
                        'source': vertices[i],
                        'destination': vertices[j],
                        'weight': weight
                    })

        # Алгоритм Краскала
        edges_sorted = sorted(edges_list, key=lambda x: x['weight'])
        parent = {}

        def find(u):
            while parent.get(u, u) != u:
                u = parent.get(u, u)
            return u

        def union(u, v):
            parent[find(u)] = find(v)

        mst = []
        node_set = set(vertices)

        for edge in edges_sorted:
            u, v = edge['source'], edge['destination']
            if find(u) != find(v):
                mst.append(edge)
                union(u, v)
                if len(mst) == len(node_set) - 1:
                    break

        # Общий вес дерева
        total_weight = sum(edge['weight'] for edge in mst)

        # Визуализация
        G = nx.Graph()
        for edge in edges_list:
            G.add_edge(edge['source'], edge['destination'], weight=edge['weight'])

        pos = nx.spring_layout(G, seed=42)

        plt.figure(figsize=(10, 6))
        nx.draw_networkx_nodes(G, pos, node_color='#2196F3', node_size=700)
        nx.draw_networkx_labels(G, pos, font_color='white')

        # Все рёбра серым
        nx.draw_networkx_edges(G, pos, edge_color='#cccccc', width=1)

        # Рёбра MST красным
        nx.draw_networkx_edges(G, pos, edgelist=[(e['source'], e['destination']) for e in mst],
                               edge_color='#ff5722', width=3)

        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        plt.close()
        graphic = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return render(request, 'kruskal/result.html', {
            'edges': edges_list,
            'mst': mst,
            'graphic': graphic,
            'nodes': vertices,
            'matrix': matrix,
            'total_weight': total_weight
        })

    return render(request, 'kruskal/input.html', {
        'vertices': vertices
    })
