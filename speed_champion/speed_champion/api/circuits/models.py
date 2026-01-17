from django.db import models

class Circuit(models.Model):

    TYPE_CHOICES = [
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ]

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES
    )

    def __str__(self):
        return self.name
