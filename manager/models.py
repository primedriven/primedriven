from django.db import models


class ProgressBar(models.Model):
    percent = models.DecimalField(max_digits=5, decimal_places=2)
    winning_number = models.CharField(max_length=200, blank=True, null=True)
    draw_date = models.CharField(max_length=200, blank=True, null=True)
    draw_time = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.percent}"
