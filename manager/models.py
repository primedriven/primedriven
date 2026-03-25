from django.db import models


class ProgressBar(models.Model):
    percent = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.percent}"
