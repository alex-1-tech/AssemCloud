from django.db import models


class Assembly(models.Model):
    name = models.CharField(max_length=100)
    machine = models.ForeignKey("Machine", models.CASCADE)
    parent_assembly = models.ForeignKey(
        "self", models.DO_NOTHING, blank=True, null=True, related_name="sub_assemblies"
    )

    class Meta:
        managed = True
        db_table = "assembly"

    def __str__(self):
        return self.name


class Machine(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["-name"]
        managed = True
        db_table = "machine"

    def get_root_assemblies(self):
        return Assembly.objects.filter(machine=self, parent_assembly__isnull=True)

    def __str__(self):
        return self.name


class Part(models.Model):
    name = models.CharField(max_length=100)
    assembly = models.ForeignKey(Assembly, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = "part"

    def __str__(self):
        return self.name
