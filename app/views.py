from django.shortcuts import render, HttpResponse
from app.models import *
import random
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from app.forms import *
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required

from app.models import *

# Create your views here.

def login_(request):
    if request.user.is_authenticated:
        return redirect(index)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print('Esta vaina logueo marico')
            return redirect(index)
        else:
            msg = 'Datos incorrectos, intente de nuevo'
            return render(request, 'auth/login.html', {'msg':msg})
    else:
        return render(request, 'auth/login.html')
    
def logout_(request):
    logout(request)
    return redirect(index)
    
def motivation(request):
    randomInt = random.randint(1,174)
    motivation = Motivation.objects.filter(id=randomInt).first()
    context = {'motivation':motivation}
    return render (request, 'motivation.html',context)

def index(request):
    return render(request, 'index.html')


@login_required(login_url='/login')
def formCreateClient(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.agent = request.user
            client.save()
            return redirect(formCreatePlan, client.id)
        else:
            return HttpResponse('Mensaje de error en el formulario (Luego lo hacemos)')
    else:   
        return render(request, 'formCreateClient.html')
    
        # client = Client()
        # client.agent_usa = request.POST['agent_usa']
        # client.first_name = request.POST['fisrtName']
        # client.last_name = request.POST['lastName']
        # client.phone_number = request.POST['phoneNumber']
        # client.email = request.POST['email']
        # client.address = request.POST['address']
        # client.zipcode = request.POST['zipCode']
        # client.city = request.POST['city']
        # client.state = request.POST['state']
        # client.country = request.POST['country']
        # client.sex = request.POST['sex']
        # client.old = request.POST['old']
        # client.migration_status = request.POST['migration_status']
        # client.date_birth = request.POST['dateBirth']
        # client.save()

@login_required(login_url='/login')
def formCreatePlan(request, client_id):
    print(request.POST.get('type_sales'))
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        type_sale = request.POST.get('type_sales')

        if type_sale == 'ACA':
            aca_plan, created = ObamaCare.objects.update_or_create(
                client=client,
                profiling_agent=request.user,
                defaults={
                    'taxes': request.POST.get('taxes'),
                    'plan_name': request.POST.get('planName'),
                    'work': request.POST.get('work'),
                    'subsidy': request.POST.get('subsidy'),
                    'carrier': request.POST.get('carrierObama'),
                    'apply': request.POST.get('applyObama'),
                    'observation': request.POST.get('observationObama')
                }
            )
            print(aca_plan, created)
            return JsonResponse({'success': True})
        elif type_sale == 'SUPLEMENTARIO':
            supplementary_plan, created = Supp.objects.update_or_create(
                client=client,
                defaults={
                    'effective_date': request.POST.get('effectiveDate'),
                    'company': request.POST.get('carrierSuple'),
                    'premium': request.POST.get('premium'),
                    'policy_type': request.POST.get('policyType'),
                    'preventive': request.POST.get('preventive'),
                    'coverage': request.POST.get('coverage'),
                    'deducible': request.POST.get('deducible'),
                    'observation': request.POST.get('observationSuple')
                }
            )
            return JsonResponse({'success': True})
        elif type_sale == 'DEPENDENTS':
            dependents, created = Dependent.objects.update_or_create(
                client=client,
                name=request.POST.get('nameDependent'),
                defaults={
                    'apply': request.POST.get('applyDependent'),
                    'date_of_birth': request.POST.get('dateBirthDependent'),
                    'migration_status': request.POST.get('migrationStatusDependent'),
                    'sex': request.POST.get('sexDependent')
                }
            )
            return JsonResponse({'success': True})

    aca_plan = ObamaCare.objects.filter(client=client).first()
    supplementary_plan = Supp.objects.filter(client=client).first()
    dependents = Dependent.objects.filter(client=client)

    return render(request, 'formCreatePlan.html', {
        'client': client,
        'aca_plan_data': aca_plan,
        'supplementary_plan_data': supplementary_plan,
        'dependents': dependents
    })





