from django.db import models

class Constraint(models.Model):
    coefficients = models.JSONField()  # Коэффициенты при переменных
    constant = models.FloatField()     # Свободный член

    def __str__(self):
        return f"{self.coefficients} ≤ {self.constant}"