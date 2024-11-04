from django.shortcuts import render
from app.models import *
import random
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password

from app.models import *

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
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print('Esta vaina logueo marico')
            return redirect('index')
        else:
            msg = 'Datos incorrectos, intente de nuevo'
            return render(request, 'auth/login.html', {'msg':msg})
    else:
        return render(request, 'auth/login.html')
