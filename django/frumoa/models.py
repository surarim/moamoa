from django.db import models

class log(models.Model):
  id = models.BigAutoField(primary_key=True)
  date = models.DateField(db_index=True)
  time = models.TimeField(db_index=True)
  ip = models.GenericIPAddressField(db_index=True)
  text = models.CharField(max_length=200, db_index=True)
  class Meta:
    db_table = "log"
