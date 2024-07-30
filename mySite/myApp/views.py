from django.shortcuts import render,HttpResponse
from .models import *



from datetime import datetime
import pytz
# Create your views here.


def home(request):
    return HttpResponse("Hello World")


def catches(request):

    if request.method=='POST':

        fisherman = request.POST.get('fishermen')
        fish = request.POST.get('fish')
        qty = request.POST.get('quantity')


        catchTemp = Catch()
        catchTemp.date = datetime.now(pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d")
        catchTemp.catcher = FisherMan.objects.get(id=fisherman)
        catchTemp.fish = Fish.objects.get(id=fish)
        catchTemp.qty = qty

        catchTemp.save()

        fishTemp = Fish.objects.get(id=fish)
        fishTemp.stock += int(qty)
        fishTemp.save()

        fishermanTemp = FisherMan.objects.get(id=fisherman)
        fishermanTemp.income += fishTemp.price * float(qty)
        fishermanTemp.save()

        return HttpResponse("<h1> Form posted </h1>")

    else:
        fishes = Fish.objects.all()
        fisherman = FisherMan.objects.all()

        context = {
            "fishes":fishes,
            "fisherman":fisherman
        }

        return render(request,"form1.html",context)
    


def fisherMan(request,id):

    if request.method=='POST':
        advance = request.POST.get('advance')
        income = request.POST.get('income')
        fisherManTemp = FisherMan.objects.get(id=id)
        fisherManTemp.advance= advance
        fisherManTemp.income= income
        
        print(advance)
        
        fisherManTemp.save()

        return HttpResponse("<h1>Changes Done</h1>")

    fisherManTemp = FisherMan.objects.get(id=id)
    print(fisherManTemp.advance)
    context={
        "fisherman":fisherManTemp
    }

    return render(request,"detailPage.html",context)

def allFisherman(request):

    fishermans = FisherMan.objects.all()

    return render(request,"FishermenIncomeDetail.html",{"fishermans":fishermans})

