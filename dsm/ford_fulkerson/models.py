from django.db import models

class FlowEdge(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    capacity = models.IntegerField()
    flow = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.flow}/{self.capacity})"