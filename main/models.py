from django.db import models


class Record(models.Model):
    category = models.CharField(max_length=100, null=True, blank=True)
    nutrient = models.CharField(max_length=50)
    age_months_start = models.IntegerField()
    age_months_end = models.IntegerField()
    gender = models.CharField(max_length=50, choices=(('M', 'Male'), ('F', 'Female'), ('L', 'Lactating'), ('P', 'Pregnant')))
    amount = models.CharField(max_length=50)
    unit = models.CharField(max_length=50)
    source_type = models.CharField(max_length=500)
    source_name = models.CharField(max_length=500)
    source_url = models.CharField(max_length=500)
    nutrient_notes = models.CharField(max_length=500)

    class Meta:
        unique_together = ("nutrient", "gender", "age_months_start", "age_months_end")