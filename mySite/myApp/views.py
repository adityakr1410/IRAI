from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from .models import *
from datetime import datetime
import pytz
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from collections import defaultdict
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.contrib.auth.decorators import login_required
from datetime import timedelta


def home(request):
    return render(request, "home.html")

def payment_summary_view(request):
    payment_summary = Fisherman.get_payment_summary()
    return render(request, 'payment_summary.html', {'payment_summary': payment_summary})

def unpaid_catches_view(request, fisherman_id):
    fisherman = get_object_or_404(Fisherman, id=fisherman_id)
    unpaid_catches = fisherman.get_unpaid_catches()
    total_unpaid_salary = fisherman.calculate_total_due()

    for catch in unpaid_catches:
        catch.price = catch.weight * catch.fish.price

    advance = Advance.objects.filter(fisherman=fisherman)
    total_adv = sum(x.amount for x in advance)

    managers = Manager.objects.all()

    if request.method == 'POST':
        payment_amount = float(request.POST.get('payment_amount', 0))
        payy = payment_amount
        manager_id = request.POST.get('manager')
        manager = get_object_or_404(Manager, id=manager_id)

        if payment_amount <= 0:
            messages.error(request, "Invalid payment amount. Please enter a positive value.")
            return redirect('unpaid_catches', fisherman_id=fisherman_id)

        adv_amt = 0  # Initialize advance amount variable
        if total_unpaid_salary < payment_amount:
            adv_amt = payment_amount - float(total_unpaid_salary)
            Advance.objects.create(fisherman=fisherman, amount=adv_amt, reason="Given during salary payment", date_requested=timezone.now().date(), manager=manager)

        payment_amount = payment_amount - adv_amt if adv_amt > 0 else payment_amount
        if payment_amount == 0:
            messages.success(request, "Advance successfully recorded.")
            
            print(manager)
            manager.balance = (float(manager.balance) )-  float(payy)
            manager.save()
            return redirect('unpaid_catches', fisherman_id=fisherman_id)
        
        min_pay = total_unpaid_salary - total_adv
        if payment_amount < min_pay:
            messages.error(request, "Cannot pay less than the total salary minus the advance.")
            return redirect('unpaid_catches', fisherman_id=fisherman_id)

        # Create payment and associate it with the manager
        Payment.objects.create(
            fisherman=fisherman,
            payment_date=timezone.now().date(),
            amount=payment_amount,
            payment_type='Catch',
            manager=manager
        )

        for catch in unpaid_catches:
            catch.is_paid = True
            catch.save()

        deduct = float(total_unpaid_salary) - payment_amount
        if deduct > 0:
            Advance.objects.create(
                fisherman=fisherman,
                amount=-deduct,
                reason="Deduction",
                date_requested=timezone.now().date(),
                manager=manager
            )
        print("Hello world "*5)
        # Update manager balance
        manager.balance = float(manager.balance) -  float(payy)
        manager.save()

        messages.success(request, "Payment successfully recorded and catches marked as paid.")
        return redirect('unpaid_catches', fisherman_id=fisherman_id)

    context = {
        'fisherman': fisherman,
        'unpaid_catches': unpaid_catches,
        'total_unpaid_salary': total_unpaid_salary,
        'advance': advance,
        'total_advance': total_adv,
        'min_payment': total_unpaid_salary - total_adv,
        'managers': managers,
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
                    catch_date=timezone.now().date(),
                    weight=weight,
                    is_paid=False
                )

        messages.success(request, "Catch successfully logged.")
        return redirect("log_catch")

    else:
        fishermen = Fisherman.objects.all()
        fish_list = Fish.objects.all()
        return render(request, 'catchByFisherman.html', {'fishermen': fishermen, 'fish_list': fish_list})

def advance_giver(fisherman,amount,reason,date_requested,manager):
    try:
        amount = float(amount)
        Advance.objects.create(
            fisherman=fisherman,
            amount=amount,
            reason=reason,
            date_requested=date_requested,
            manager=manager
        )
        Payment.objects.create(
            fisherman=fisherman,
            payment_date=timezone.now().date(),
            amount=amount,
            payment_type='Advance',
            manager=manager
        )
        manager.balance = float(manager.balance) - float(amount)
        manager.save()
        return True
    except ValueError:
        return False

def give_advance_view(request, fisherman_id):
    fisherman = get_object_or_404(Fisherman, pk=fisherman_id)
    managers = Manager.objects.all()
    if request.method == 'POST':
        amount = request.POST.get('amount')
        reason = request.POST.get('reason')
        date_requested = request.POST.get('date_requested')
        manager_id = request.POST.get('manager')
        manager = get_object_or_404(Manager, id=manager_id)
        if not amount or not reason or not date_requested:
            messages.error(request, 'All fields are required.')
        else:
            check = advance_giver(fisherman=fisherman,amount=amount,reason=reason,date_requested=date_requested,manager=manager)
            if check:
                messages.success(request, f'Advance of ₹{amount} successfully given to {fisherman.name}.')
                redirect('payment_summary')
            else:
                messages.error(request, 'Invalid amount entered.')
            
    return render(request, 'give_advance.html', {'fisherman': fisherman,"managers":managers})

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
                    weight = 0

                if weight > 0:
                    fish = get_object_or_404(Fish, id=fish_id)
                    CatchRoyalty.objects.create(
                        fisherman=fisherman,
                        fish=fish,
                        weight=weight,
                        catch_date=catch_date
                    )

                    amount_due = weight * float(fish.royalty_amount)
                    total_amount_due += amount_due

        messages.success(request, "Catch for royalty successfully logged.")
        return redirect('/')

    else:
        fishermen = RoyaltyFisherman.objects.all()
        fish_list = Fish.objects.all()
        return render(request, 'catchByFishermanRoyalty.html', {'fishermen': fishermen, 'fish_list': fish_list})

def fishermanRoyalty_summary(request):
    fishermanRoyalties = RoyaltyFisherman.objects.all()

    fManR = []
    for r in fishermanRoyalties:
        total_due = PaymentRoyalty.objects.filter(fisherman=r).aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total']
        total_received = PaymentRoyaltyReceived.objects.filter(fisherman=r).aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total']
        fManR.append(
            {
                "pk": r.id,
                "name": r.name,
                "total_due": total_due,
                "total_received": total_received,
                "total_remaining": total_due - total_received
            }
        )
    fManR = sorted(fManR, key=lambda x: x['total_remaining'], reverse=True)
    context = {
        'fishermanRoyalties': fManR,
    }
    return render(request, 'fishermanRoyalty_summary.html', context)

def fishermanRoyalty_detail(request, pk):
    managers = Manager.objects.all()
    fishermanRoyalty = get_object_or_404(RoyaltyFisherman, pk=pk)

    payments_due = PaymentRoyalty.objects.filter(fisherman=fishermanRoyalty).order_by('-payment_date')
    payments_received = PaymentRoyaltyReceived.objects.filter(fisherman=fishermanRoyalty).order_by('-payment_date')

    payments_due_grouped = defaultdict(lambda: {'total': 0, 'details': []})
    for payment in payments_due:
        payments_due_grouped[payment.payment_date]['total'] += payment.amount
        payments_due_grouped[payment.payment_date]['details'].append({
            'catch': payment.catch,
            'amount': payment.amount,
            'payment_date': payment.payment_date
        })

    total_due = payments_due.aggregate(Sum('amount'))['amount__sum'] or 0
    total_received = payments_received.aggregate(Sum('amount'))['amount__sum'] or 0
    total_to_be_received = total_due - total_received

    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        manager_id = request.POST.get('manager')
        manager = get_object_or_404(Manager, id=manager_id)


        if not amount or not payment_date:
            messages.error(request, "Amount and payment date are required.")
            return redirect(reverse('fishermanRoyalty_detail', args=[pk]))

        try:
            amount = float(amount)
        except ValueError:
            messages.error(request, "Invalid amount entered.")
            return redirect(reverse('fishermanRoyalty_detail', args=[pk]))

        payment_date = parse_date(payment_date)

        PaymentRoyaltyReceived.objects.create(
            fisherman=fishermanRoyalty,
            amount=amount,
            payment_date=payment_date,
            manager=manager
        )

        manager.balance = float(manager.balance) + float(amount)
        manager.save()

        messages.success(request, "Payment successfully recorded.")
        return redirect(reverse('fishermanRoyalty_detail', args=[pk]))

    context = {
        'fishermanRoyalty': fishermanRoyalty,
        'payments_due_grouped': dict(payments_due_grouped),
        'payments_received': payments_received,
        'total_due': total_due,
        'total_received': total_received,
        'total_to_be_received': total_to_be_received,
        'managers':managers
    }

    return render(request, 'fishermanRoyalty_detail.html', context)

def manager_list_view(request):
    """
    View to display a list of all managers and their current balance.
    """
    managers = Manager.objects.all()
    return render(request, 'manager_list.html', {'managers': managers})

def manager_detail_view(request, manager_id):
    """
    View to display all payments sent and received by a specific manager.
    """
    manager = get_object_or_404(Manager, id=manager_id)
    payments_sent = Payment.objects.filter(manager=manager)
    payments_received = PaymentRoyaltyReceived.objects.filter(manager=manager)

    context = {
        'manager': manager,
        'payments_sent': payments_sent,
        'payments_received': payments_received,
    }
    return render(request, 'manager_detail.html', context)




@login_required
def give_money_to_manager_view(request):
    owner = get_object_or_404(Owner, user=request.user)  # Ensure the logged-in user is an owner

    if request.method == "POST":
        manager_id = request.POST.get('manager')
        amount = request.POST.get('amount')
        note = request.POST.get('note')

        # Validation
        if not manager_id or not amount:
            messages.error(request, "Manager and amount are required fields.")
            return redirect('give_money_to_manager')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Amount must be greater than zero.")
                return redirect('give_money_to_manager')
        except ValueError:
            messages.error(request, "Invalid amount.")
            return redirect('give_money_to_manager')

        manager = get_object_or_404(Manager, id=manager_id)

        # Create the transaction
        transaction = OwnerToManagerTransaction.objects.create(
            owner=owner,
            manager=manager,
            amount=amount,
            note=note
        )

        messages.success(request, f"Successfully transferred {transaction.amount} to {transaction.manager}.")
        return redirect('home')

    managers = Manager.objects.all()  # Fetch all managers to populate the dropdown
    context = {
        'managers': managers
    }
    return render(request, 'give_money_to_manager.html', context)

def add_money_to_manager(request):
    if request.method == 'POST':
        owner_id = request.POST.get('owner')
        manager_id = request.POST.get('manager')
        amount = request.POST.get('amount')
        note = request.POST.get('note', '')

        try:
            owner = Owner.objects.get(id=owner_id)
            manager = Manager.objects.get(id=manager_id)
            amount = Decimal(amount)

            # Create the transaction
            transaction = OwnerToManagerTransaction(
                owner=owner,
                manager=manager,
                amount=amount,
                note=note
            )
            transaction.save()

            messages.success(request, f'{amount} was successfully added to {manager.user.username} by {owner.user.username}.')
            return redirect('add_money')  # Redirect back to the form page
        except (Owner.DoesNotExist, Manager.DoesNotExist):
            messages.error(request, 'Owner or Manager not found.')
        except ValueError:
            messages.error(request, 'Invalid amount. Please enter a valid number.')

    owners = Owner.objects.all()
    managers = Manager.objects.all()
    return render(request, 'add_money_to_manager.html', {'owners': owners, 'managers': managers})

def add_miscellaneous_expense(request):
    users = User.objects.all()  # Fetch all users for the dropdown

    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        spender_id = request.POST.get('spender')  # Get spender from form data
        spent_on = request.POST.get('spent_on')
        context = request.POST.get('context')
        date_spent = request.POST.get('date_spent', timezone.now().date())  # Defaults to today if not provided

        # Convert date_spent to the correct format
        date_spent = timezone.datetime.strptime(date_spent, '%Y-%m-%d').date() if date_spent else timezone.now().date()

        try:
            spender = User.objects.get(id=spender_id)  # Fetch the selected user as the spender
        except User.DoesNotExist:
            messages.error(request, 'Selected user does not exist.')
            return redirect('add_miscellaneous_expense')

        # Create the MiscellaneousExpense instance
        MiscellaneousExpense.objects.create(
            amount=amount,
            spender=spender,
            spent_on=spent_on,
            context=context,
            date_spent=date_spent
        )

        # Check if the spender is a manager and update their balance if necessary
        try:
            manager = Manager.objects.get(user=spender)
            # Deduct the amount from the manager's balance
            manager.balance = float(manager.balance) -amount
            manager.save()
        except Manager.DoesNotExist:
            # The spender is not a manager, no need to adjust balance
            pass

        messages.success(request, 'Miscellaneous expense added successfully.')
        return redirect('add_miscellaneous_expense')  # Redirect back to the form page

    return render(request, 'add_miscellaneous_expense.html', {'users': users})

    return render(request, 'add_miscellaneous_expense.html', {'users': users})


from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render

def master_transaction_view(request):
    # Fetch all transactions
    payments = Payment.objects.all().order_by('payment_date')
    # advances = Advance.objects.all().order_by('payment_date')
    royalty_payments = PaymentRoyaltyReceived.objects.all().order_by('payment_date')
    miscellaneous_expenses = MiscellaneousExpense.objects.all().order_by('date_spent')

    # Combine and group transactions by date
    transactions = {}
    total_last_7_days_received = 0
    total_last_7_days_spent = 0

    for payment in payments:
        date = payment.payment_date
        if date not in transactions:
            transactions[date] = {
                'fisherman': [],
                'royalty': [],
                'miscellaneous': [],
                'total_amount_spent': 0,
                'total_amount_received': 0
            }
        transactions[date]['fisherman'].append(payment)
        transactions[date]['total_amount_spent'] += payment.amount

    for royalty_payment in royalty_payments:
        date = royalty_payment.payment_date
        if date not in transactions:
            transactions[date] = {
                'fisherman': [],
                'royalty': [],
                'miscellaneous': [],
                'total_amount_spent': 0,
                'total_amount_received': 0
            }
        transactions[date]['royalty'].append(royalty_payment)
        transactions[date]['total_amount_received'] += royalty_payment.amount

    for expense in miscellaneous_expenses:
        date = expense.date_spent
        if date not in transactions:
            transactions[date] = {
                'fisherman': [],
                'royalty': [],
                'miscellaneous': [],
                'total_amount_spent': 0,
                'total_amount_received': 0
            }
        transactions[date]['miscellaneous'].append(expense)
        transactions[date]['total_amount_spent'] += expense.amount

    # Sort transactions by date
    sorted_transactions = dict(sorted(transactions.items(), reverse=True))

    # Calculate total for the last 7 days
    today = timezone.now().date()
    last_week_start = today - timedelta(days=7)
    
    for date, types in sorted_transactions.items():
        if date >= last_week_start:
            total_last_7_days_received += types['total_amount_received']
            total_last_7_days_spent += types['total_amount_spent']

    total_last_7_days = total_last_7_days_received - total_last_7_days_spent

    context = {
        'transactions': sorted_transactions,
        'total_last_7_days': total_last_7_days,
    }
    
    return render(request, 'master_transaction.html', context)



def add_fisherman(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        if name and phone_number:
            Fisherman.objects.create(name=name, phone_number=phone_number)
            messages.success(request, 'Fisherman added successfully.')
            return redirect('add_fisherman')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'add_fisherman.html')

# Add Royalty Fisherman View
def add_royalty_fisherman(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        if name and phone_number:
            RoyaltyFisherman.objects.create(name=name, phone_number=phone_number)
            messages.success(request, 'Royalty fisherman added successfully.')
            return redirect('add_royalty_fisherman')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'add_royalty_fisherman.html')

# Edit Fish Prices View
def edit_fish_prices(request):
    fishes = Fish.objects.all()
    if request.method == 'POST':
        fish_id = request.POST.get('fish_id')
        fish_name = request.POST.get('fish_name')
        price = request.POST.get('price')
        royalty_amount = request.POST.get('royalty_amount')
        
        # Update fish price
        if fish_id:
            fish = get_object_or_404(Fish, id=fish_id)
            fish.price = price
            fish.royalty_amount = royalty_amount
            fish.save()
            messages.success(request, f'{fish_name} updated successfully.')
        
        # Add new fish
        elif fish_name and price:
            Fish.objects.create(name=fish_name, price=price, royalty_amount=royalty_amount or 0)
            messages.success(request, f'New fish {fish_name} added successfully.')
        else:
            messages.error(request, 'Please fill out all required fields.')

        return redirect('edit_fish_prices')

    return render(request, 'edit_fish_prices.html', {'fishes': fishes})

# Delete Fish View
def delete_fish(request, fish_id):
    fish = get_object_or_404(Fish, id=fish_id)
    fish_name = fish.name
    fish.delete()
    messages.success(request, f'{fish_name} deleted successfully.')
    return redirect('edit_fish_prices')

