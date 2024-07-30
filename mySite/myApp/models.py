import datetime
from django.db import models

# Create your models here.


class FisherMan(models.Model):
    def __str__(self):
        return self.fName+self.lName
    fName = models.CharField(max_length=15)
    lName = models.CharField(max_length=15)
     
    phoneNo = models.CharField(max_length=15,blank=True)

    #money
    advance = models.IntegerField()
    income = models.IntegerField()

class Fish(models.Model):

    def __str__(self):
        return self.name
    
    name = models.CharField(max_length=10)
    price = models.IntegerField()

    stock = models.IntegerField()


class Catch(models.Model):

    date = models.DateField()
    catcher = models.ForeignKey(FisherMan,on_delete=models.CASCADE)
    fish = models.ForeignKey(Fish,on_delete=models.DO_NOTHING)
    qty = models.IntegerField()
    price = models.IntegerField()

    paid = models.BooleanField()



class PaidByManager(models.Model):

    date = models.DateField()

    fisherMan = models.ForeignKey(FisherMan, on_delete=models.DO_NOTHING)

    catchesPaid = models.ManyToManyField(Catch)