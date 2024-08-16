from django.shortcuts import get_object_or_404, redirect, render,HttpResponse
from .models import *
from datetime import datetime
import pytz
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum,F,DecimalField
from django.db.models.functions import Coalesce
from collections import defaultdict
from django.urls import reverse
from django.utils.dateparse import parse_date


def home(request):
    return render(request,"home.html")

def payment_summary_view(request):
    payment_summary = Fisherman.get_payment_summary()
    return render(request, 'payment_summary.html', {'payment_summary': payment_summary})

def unpaid_catches_view(request, fisherman_id):
    fisherman = get_object_or_404(Fisherman, id=fisherman_id)
    
    # Calculate unpaid catches
    unpaid_catches = fisherman.get_unpaid_catches()
    total_unpaid_salary = fisherman.calculate_total_due()
    
    # Calculate the price of each unpaid catch
    for catch in unpaid_catches:
        catch.price = catch.weight * catch.fish.price

    # Get available advance
    advance = Advance.objects.filter(fisherman=fisherman)
    total_adv = sum(x.amount for x in advance)  # Sum up the advance amounts

    if request.method == 'POST':
        payment_amount = float(request.POST.get('payment_amount', 0))
        
        if payment_amount <= 0:
            return HttpResponse("Invalid payment amount.", status=400)
        
        min_pay = total_unpaid_salary - total_adv
        # Ensure payment amount does not exceed the total unpaid salary
        if payment_amount < min_pay:
            return HttpResponse("Cannot pay less than total salary - ", status=400)
        
        # Create payment record
        Payment.objects.create(
            fisherman=fisherman,
            payment_date=timezone.now().date(),
            amount=payment_amount,
            payment_type='Catch'
        )
        
        # Mark catches as paid
        for catch in unpaid_catches:
            catch.is_paid = True
            catch.save()
        deduct = float(total_unpaid_salary) - payment_amount
        print(f"remaining -> {deduct}")
        Advance.objects.create(
            fisherman=fisherman,
            amount=-deduct,
            reason="Deduction",
            date_requested=timezone.now().date()
        )
        
        return redirect('unpaid_catches', fisherman_id=fisherman_id)
    
    context = {
        'fisherman': fisherman,
        'unpaid_catches': unpaid_catches,
        'total_unpaid_salary': total_unpaid_salary,
        'advance': advance,
        'total_advance': total_adv,  # Add this line to include total advance
        'min_payment': total_unpaid_salary - total_adv
    }
    return render(request, 'unpaid_catches.html', context)

def log_catch(request):
    if request.method == 'POST':
        fisherman_id = request.POST.get('fisherman')
        fisherman = Fisherman.objects.get(id=fisherman_id)
        fish_ids = [fish.id for fish in Fish.objects.all()]
    
        for fish_id in fish_ids:
            weight = request.POST.get(f'weight_{fish_id}')
            if weight and float(weight) > 0:
                fish = Fish.objects.get(id=fish_id)
                Catch.objects.create(
                    fisherman=fisherman,
                    fish=fish,
                    catch_date=timezone.now().date(),  # Assuming the catch date is today
                    weight=weight,
                    is_paid=False
                )

        return redirect("log_catch")  # Redirect to a success page or another view

    else:
        fishermen = Fisherman.objects.all()
        fish_list = Fish.objects.all()
        return render(request, 'catchByFisherman.html', {'fishermen': fishermen, 'fish_list': fish_list})

def give_advance_view(request, fisherman_id):
    fisherman = Fisherman.objects.get(pk=fisherman_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        reason = request.POST.get('reason')
        date_requested = request.POST.get('date_requested')
        
        if not amount or not reason or not date_requested:
            messages.error(request, 'All fields are required.')
        else:
            try:
                amount = float(amount)
                # Create and save the advance
                Advance.objects.create(
                    fisherman=fisherman,
                    amount=amount,
                    reason=reason,
                    date_requested=date_requested
                )
                Payment.objects.create(
                    fisherman = fisherman,
                    payment_date = timezone.now().date(),
                    amount = amount,
                    payment_type = 'Advance'
                )
                messages.success(request, f'Advance of ₹{amount} given to {fisherman.name}.')
                return redirect('payment_summary')
            except ValueError:
                messages.error(request, 'Invalid amount entered.')
    return render(request, 'give_advance.html', {
        'fisherman': fisherman
    })

def log_catch_royalty(request):
    if request.method == 'POST':
        fisherman_id = request.POST.get('fisherman')
        catch_date = request.POST.get('catch_date')
        fisherman = get_object_or_404(RoyaltyFisherman, id=fisherman_id)
        fish_ids = [fish.id for fish in Fish.objects.all()]

        total_amount_due = 0

        for fish_id in fish_ids:
            weight = request.POST.get(f'weight_{fish_id}')
            if weight:
                try:
                    weight = float(weight)
                except ValueError:
                    weight = 0  # Handle invalid weights gracefully

                if weight > 0:
                    fish = get_object_or_404(Fish, id=fish_id)
                    catch = CatchRoyalty.objects.create(
                        fisherman=fisherman,
                        fish=fish,
                        weight=weight,
                        catch_date=catch_date
                    )
                    
                    amount_due = weight * float(fish.royalty_amount)
                    total_amount_due += amount_due
                    
        return redirect('/')  # Redirect to a success page or another view

    else:
        fishermen = RoyaltyFisherman.objects.all()
        fish_list = Fish.objects.all()
        return render(request, 'catchByFishermanRoyalty.html', {'fishermen': fishermen, 'fish_list': fish_list})
    
def fishermanRoyalty_summary(request):
    # Get total amount remaining to be paid by each fishermanRoyalty
    fishermanRoyalties = RoyaltyFisherman.objects.all()

    fManR = []
    for r in fishermanRoyalties:
        total_due = PaymentRoyalty.objects.filter(fisherman=r).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']
        total_received = PaymentRoyaltyRecived.objects.filter(fisherman=r).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']
        fManR.append(
            {
                "pk":r.id,
                "name":r.name,
                "total_due":total_due,
                "total_received":total_received,
                "total_remaining":total_due - total_received
            }
        )
    fManR = sorted(fManR,key=lambda x:x['total_remaining'],reverse=True)
    context = {
        'fishermanRoyalties': fManR,
    }
    return render(request, 'fishermanRoyalty_summary.html', context)

"""
def fishermanRoyalty_summary(request):
    # Get total amount remaining to be paid by each fishermanRoyalty
    fishermanRoyalties = RoyaltyFisherman.objects.annotate(
        total_due=Sum('paymentroyalty__amount'),
        total_received=Sum('paymentroyaltyrecived__amount')
    ).annotate(
        total_remaining=F('total_received') - F('total_due')
    ).order_by('-total_remaining')

    context = {
        'fishermanRoyalties': fishermanRoyalties,
    }
    return render(request, 'fishermanRoyalty_summary.html', context)
"""

def fishermanRoyalty_detail(request, pk):
    fishermanRoyalty = get_object_or_404(RoyaltyFisherman, pk=pk)

    # Get all payments due and received
    payments_due = PaymentRoyalty.objects.filter(fisherman=fishermanRoyalty).order_by('-payment_date')
    payments_received = PaymentRoyaltyRecived.objects.filter(fisherman=fishermanRoyalty).order_by('-payment_date')

    # Aggregate payments due by date with catch details
    payments_due_grouped = defaultdict(lambda: {'total': 0, 'details': []})
    for payment in payments_due:
        payments_due_grouped[payment.payment_date]['total'] += payment.amount
        payments_due_grouped[payment.payment_date]['details'].append({
            'catch': payment.catch,
            'amount': payment.amount,
            'payment_date': payment.payment_date
        })

    # Calculate totals
    total_due = payments_due.aggregate(Sum('amount'))['amount__sum'] or 0
    total_received = payments_received.aggregate(Sum('amount'))['amount__sum'] or 0
    total_to_be_received = total_due - total_received

    # Handle new payment submission
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')

        # Perform validation
        if not amount or not payment_date:
            return redirect(reverse('fishermanRoyalty_detail', args=[pk]))

        amount = Decimal(amount)
        payment_date = parse_date(payment_date)

        with transaction.atomic():
            PaymentRoyaltyRecived.objects.create(
                fisherman=fishermanRoyalty,
                amount=amount,
                payment_date=payment_date
            )
        
        return redirect(reverse('fishermanRoyalty_detail', args=[pk]))

    context = {
        'fishermanRoyalty': fishermanRoyalty,
        'payments_due_grouped': dict(payments_due_grouped),  # Convert defaultdict to dict
        'payments_received': payments_received,
        'total_due': total_due,
        'total_received': total_received,
        'total_to_be_received': total_to_be_received,
    }
    
    return render(request, 'fishermanRoyalty_detail.html', context)
