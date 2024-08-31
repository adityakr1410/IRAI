from datetime import timezone
from django.db import models, transaction
from django.forms import ValidationError
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone as tz

# Owner Model
class Owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

# Manager Model
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.user.username

    def has_perm(self, perm, obj=None):
        return False

    def has_module_perms(self, app_label):
        return False

# Owner to Manager Transaction Model
class OwnerToManagerTransaction(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.owner} gave {self.amount} to {self.manager} on {self.transaction_date}"

    def save(self, *args, **kwargs):
        # Add balance to the manager
        self.manager.balance += Decimal(self.amount)
        self.manager.save()
        super().save(*args, **kwargs)

# Fish Model
class Fish(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    royalty_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

# Fisherman Model
class Fisherman(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    # Calculate the total due for all unpaid catches
    def calculate_total_due(self):
        return sum(catch.weight * catch.fish.price for catch in self.catch_set.filter(is_paid=False))

    # Get all unpaid catches
    def get_unpaid_catches(self):
        return self.catch_set.filter(is_paid=False)

    # Get all catches for the fisherman
    def get_all_catches(self):
        return self.catch_set.all()

    # Process payment for the fisherman
    def pay_fisherman(self):
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
            Payment.objects.create(
                fisherman=self,
                payment_date=timezone.now().date(),
                amount=total_due,
                payment_type='Catch'
            )

    # Static method to get a payment summary of all fishermen
    @staticmethod
    def get_payment_summary():
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

        # Sort by unpaid amounts first
        payment_summary.sort(key=lambda x: x['is_paid'])

        return payment_summary

# Catch Model
class Catch(models.Model):
    fisherman = models.ForeignKey(Fisherman, on_delete=models.CASCADE)
    fish = models.ForeignKey(Fish, on_delete=models.CASCADE)
    catch_date = models.DateField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.fish.name} caught by {self.fisherman.name} on {self.catch_date}'

# Advance Model
class Advance(models.Model):
    fisherman = models.ForeignKey(Fisherman, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    date_requested = models.DateField()
    manager = models.ForeignKey(Manager, null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'Advance of {self.amount} for {self.fisherman.name}'

# Payment Model
class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('Catch', 'Catch'),
        ('Advance', 'Advance'),
    ]

    fisherman = models.ForeignKey(Fisherman, on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    manager = models.ForeignKey(Manager, null=True, blank=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'Payment of {self.amount} to {self.fisherman.name} for {self.get_payment_type_display()}'

# Royalty Fisherman Model
class RoyaltyFisherman(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

# Catch Royalty Model
class CatchRoyalty(models.Model):
    fisherman = models.ForeignKey(RoyaltyFisherman, on_delete=models.CASCADE)
    fish = models.ForeignKey(Fish, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    catch_date = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the parent class's save method

        # Calculate royalty amount
        royalty_amount = self.weight * float(self.fish.royalty_amount)

        # Create PaymentRoyalty record
        PaymentRoyalty.objects.create(
            fisherman=self.fisherman,
            amount=royalty_amount,
            catch=self,
            payment_date=self.catch_date
        )

    def __str__(self):
        return f"{self.fish.name} - {self.weight} kg"

# Payment Royalty Model
class PaymentRoyalty(models.Model):
    fisherman = models.ForeignKey(RoyaltyFisherman, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    catch = models.ForeignKey(CatchRoyalty, on_delete=models.CASCADE, default=1)
    payment_date = models.DateField()

    def __str__(self):
        return f"{self.fisherman.name} - {self.amount} on {self.payment_date}"

# Payment Royalty Received Model
class PaymentRoyaltyReceived(models.Model):
    fisherman = models.ForeignKey(RoyaltyFisherman, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    manager = models.ForeignKey(Manager, null=True, blank=True, on_delete=models.DO_NOTHING)

class MiscellaneousExpense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount of the expense
    spender = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the User who made the expense
    spent_on = models.CharField(max_length=255)  # Short description of what the expense was for
    context = models.TextField(blank=True, null=True)  # Optional detailed context
    date_spent = models.DateField(default=tz.now)  # Date of the expense, defaults to current date

    def __str__(self):
        return f"{self.spender.username} spent {self.amount} on {self.spent_on} on {self.date_spent}"

