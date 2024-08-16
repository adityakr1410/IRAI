from datetime import timezone
from django.db import models,transaction
from django.forms import ValidationError
from decimal import Decimal

class Fish(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    royalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.name

class Fisherman(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    
    def calculate_total_due(self):
        """
        Calculate the total amount due for all unpaid catches for this fisherman.
        """
        return sum(catch.weight * catch.fish.price for catch in self.catch_set.filter(is_paid=False))

    def get_unpaid_catches(self):
        """
        Get all unpaid catches for this fisherman.
        """
        return self.catch_set.filter(is_paid=False)

    def get_all_catches(self):
        """
        Get all catches for this fisherman.
        """
        return self.catch_set.all()

    def pay_fisherman(self):
        """
        Process payment for the fisherman by paying the total amount due for all unpaid catches.
        """
        total_due = self.calculate_total_due()
        if total_due <= 0:
            raise ValidationError("No outstanding amount due for this fisherman.")

        with transaction.atomic():
            # Mark all unpaid catches as paid
            unpaid_catches = self.get_unpaid_catches()
            for catch in unpaid_catches:
                catch.is_paid = True
                catch.save()

            # Create a payment record
            payment = Payment.objects.create(
                fisherman=self,
                payment_date=timezone.now().date(),
                amount=total_due,
                payment_type='Catch'
            )

    @staticmethod
    def get_payment_summary():
        """
        Get a summary of total amounts due for all fishermen, sorted by unpaid amounts first.
        """
        fishermen = Fisherman.objects.all()
        payment_summary = []

        for fisherman in fishermen:
            total_due = fisherman.calculate_total_due()
            payment_summary.append({
                'fisherman_id': fisherman.id,
                'name': fisherman.name,
                'total_due': total_due,
                'is_paid': total_due == 0
            })

        # Sort by `is_paid`, putting unpaid amounts at the top
        payment_summary.sort(key=lambda x: x['is_paid'])

        return payment_summary

class Catch(models.Model):
    fisherman = models.ForeignKey(Fisherman, on_delete=models.CASCADE)
    fish = models.ForeignKey(Fish, on_delete=models.CASCADE)
    catch_date = models.DateField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.fish.name} caught by {self.fisherman.name} on {self.catch_date}'

class Advance(models.Model):
    fisherman = models.ForeignKey(Fisherman, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    date_requested = models.DateField()
    
    def __str__(self):
        return f'Advance of {self.amount} for {self.fisherman.name}'

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('Catch', 'Catch'),
        ('Advance', 'Advance'),
    ]
    
    fisherman = models.ForeignKey(Fisherman, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    
    def __str__(self):
        return f'Payment of {self.amount} to {self.fisherman.name} for {self.get_payment_type_display()}'

class RoyaltyFisherman(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name
    
class CatchRoyalty(models.Model):
    fisherman = models.ForeignKey(RoyaltyFisherman, on_delete=models.CASCADE)
    fish = models.ForeignKey(Fish, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    catch_date = models.DateField()

    def save(self, *args, **kwargs):
        # Call the parent class's save method
        super().save(*args, **kwargs)
        
        # Calculate royalty amount
        royalty_amount = self.weight * float(self.fish.royalty_amount)
        
        # Create PaymentRoyalty record
        PaymentRoyalty.objects.create(
            fisherman=self.fisherman,
            amount=royalty_amount,
            catch = self,
            payment_date=self.catch_date
        )

    def __str__(self):
        return f"{self.fish.name} - {self.weight} kg"

class PaymentRoyalty(models.Model):
    fisherman = models.ForeignKey(RoyaltyFisherman, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    catch = models.ForeignKey(CatchRoyalty, on_delete=models.CASCADE,default=1)
    payment_date = models.DateField()

    def __str__(self):
        return f"{self.fisherman.name} - {self.amount} on {self.payment_date}"
    
class PaymentRoyaltyRecived(models.Model):
    fisherman = models.ForeignKey(RoyaltyFisherman, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
