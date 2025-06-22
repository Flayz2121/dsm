from django.db import models

class Edge(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    weight = models.IntegerField()

    def __str__(self):
        return f"{self.source} - {self.destination} ({self.weight})"