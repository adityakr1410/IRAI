from django.db import models

# Create your models here.


class FisherMan(models):
    def __name__(self):
        return self.name
    
    fName = models.CharField(15)
    lName = models.CharField(15)
     
    phoneNo = models.CharField(15,required=False)