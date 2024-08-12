from django.shortcuts import get_object_or_404, redirect, render,HttpResponse
from .models import *


from datetime import datetime
import pytz
# Create your views here.
from django.utils import timezone
from django.contrib import messages


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
    total_adv = 0
    for x in advance:
        total_adv += x.amount

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
        
        Advance.objects.create(
            fisherman = fisherman,
            amount = -deduct,
            reason = "Deduction",
            date_requested = timezone.now().date()
        )
        

        return redirect('unpaid_catches', fisherman_id=fisherman_id)
    
    context = {
        'fisherman': fisherman,
        'unpaid_catches': unpaid_catches,
        'total_unpaid_salary': total_unpaid_salary,
        'advance': advance,
        'min_payment':(total_unpaid_salary - total_adv)
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

