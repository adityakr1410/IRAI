from datetime import timezone
from django.db import models,transaction
from django.forms import ValidationError

class Fish(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
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

            # Create a payment log
            PaymentLog.objects.create(
                payment=payment,
                log_date=timezone.now().date(),
                log_description=f'Payment of {total_due} for all unpaid catches.'
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

class PaymentLog(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    log_date = models.DateField()
    log_description = models.TextField()
    
    def __str__(self):
        return f'Log for payment ID {self.payment.id} on {self.log_date}'
