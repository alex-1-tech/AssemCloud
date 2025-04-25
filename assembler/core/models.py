from django.db import models

class Assembly(models.Model):
    name = models.CharField(max_length=100)
    machine = models.ForeignKey('Machine', models.DO_NOTHING)
    parent_assembly = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'assembly'

    def __str__(self):
        return self.name

class Machine(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['-name']
        managed = False
        db_table = 'machine'

    def __str__(self):
        return self.name

class Part(models.Model):
    name = models.CharField(max_length=100)
    assembly = models.ForeignKey(Assembly, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'part'

    def __str__(self):
        return self.name
