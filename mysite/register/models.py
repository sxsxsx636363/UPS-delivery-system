from django.db import models

from django.contrib.auth.models import User

class World(models.Model):
    world_id = models.IntegerField(default=0)
    class Meta:
        managed = True

class Warehouse(models.Model):
    warehouse_id = models.IntegerField(primary_key=True)
    x = models.IntegerField(max_length=20)
    y = models.IntegerField(max_length=20)


class Truck(models.Model):
    truck_id = models.IntegerField(primary_key=True)
    x = models.IntegerField(max_length=20)
    y = models.IntegerField(max_length=20)
    status_options = (
        ('idle', 'IDLE'),
        ('traveling', 'TRAVELING'),
        ('arrive', 'ARRIVE'),
        ('loading', 'LOADING'),
        ('delivering', 'DELIVERING')
    )
    package_number = models.IntegerField(default=0)
    status = models.CharField(max_length=32, choices=status_options, default="idle")
    class Meta:
        managed = True

class Package(models.Model):
    tracking_id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(max_length=32,default=-1)
    # owner_id = models.ForeignKey(User, null = True, on_delete=models.CASCADE)
    status_options = (
        ('unready','UNREADY'),
        ('wait_pick','WAIT_PICK'),
        ('delivering','DELIVERING'),
        ('delivered','DELIVERED'),
    )
    status = models.CharField(max_length=32, choices=status_options, default="unready")
    truck_id = models.IntegerField(max_length=50, null=True)
    
    deliver_x = models.IntegerField(max_length=20)
    deliver_y = models.IntegerField(max_length=20)
    # warehouse address
    warehouse_id = models.IntegerField(blank=True, null=True)
    # product info
    description = models.CharField(max_length=100, null=True)
    count = models.IntegerField(max_length=50, null=True)
# Create your models here.
    class Meta:
        managed = True


class WareBindTruck(models.Model):
    unique_id = models.AutoField(primary_key=True)
    warehouse_id = models.IntegerField(blank=False, null=False)
    truck_id = models.IntegerField(blank=False, null=False)
    class Meta:
        managed = True
    def __str__(self):
        return "warehouse_id = " + str(self.warehouse_id) + " truck_id = " + str(self.truck_id)

class Seqnum(models.Model):
    seqnum = models.IntegerField(blank=False, null=False, default=0)
    massege_type_options = (
        ('ugopickup','UGOPICKUP'),
        ('ugodeliver','UGODELIVER'),
        ('uquery','UQUERY'),
        ('upsamazoninitship','UPSAMAZONINITSHIP'),
        ('upsamazonstartship','UPSAMAZONSTARTSHIP'),
        ('upsamazonfinishship','UPSAMAZONFINISHSHIP'),
    )
    massege_type = models.CharField(choices=massege_type_options,  max_length=254)
    truck_id = models.IntegerField(default = -1)
    package_id = models.IntegerField(default = -1)
    class Meta:
        managed = True

class Issue(models.Model):
    unique_id = models.AutoField(primary_key=True)
    tracking_id = models.IntegerField(max_length=32)
    email = models.EmailField(blank=True, null=True, max_length=254)
    content = models.CharField(null=True, max_length=254)

