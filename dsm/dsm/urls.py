from django.urls import path
from django.views.generic import TemplateView
from kruskal.views import kruskal_algorithm
from ford_fulkerson.views import ford_fulkerson
from dijkstra.views import dijkstra_algorithm
from danzig.views import danzig_algorithm
from floyd_warshall.views import floyd_warshall_algorithm

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('kruskal/', kruskal_algorithm, name='kruskal_algorithm'),
    path('ford-fulkerson/', ford_fulkerson, name='ford_fulkerson'),
    path('dijkstra/', dijkstra_algorithm, name='dijkstra_algorithm'),
    path('danzig/', danzig_algorithm, name='danzig_algorithm'),
    path('floyd-warshall/', floyd_warshall_algorithm, name='floyd_warshall_algorithm'),
]