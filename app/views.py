from django.shortcuts import render
from app.models import *
import random

# Create your views here.

def login_(request):
    return render(request, 'login.html')
    
def motivation(request):
    randomInt = random.randint(1,174)
    print(randomInt)
    motivation = Motivation.objects.filter(id=randomInt).first()
    context = {'motivation':motivation}
    print(context)
    return render (request, 'motivation.html',context)

def index (request):
    return render(request, 'index.html')
