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
            return redirect(motivationalPhrase)
        else:
            msg = 'Datos incorrectos, intente de nuevo'
            return render(request, 'auth/login.html', {'msg':msg})
    else:
        return render(request, 'auth/login.html')
    
def logout_(request):
    logout(request)
    return redirect(index)
    
@login_required(login_url='/login')
def motivationalPhrase(request):
    randomInt = random.randint(1,174)
    motivation = Motivation.objects.filter(id=randomInt).first()
    context = {'motivation':motivation}
    return render (request, 'motivationalPhrase.html',context)

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
        return render(request, 'forms/formCreateClient.html')
    
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
            supp_data = {}

            # Filtrar solo los datos que corresponden a dependents y organizarlos por índices
            for key, value in request.POST.items():
                print(value)
                if key.startswith('supplementary_plan_data'): #pregunta como inicia el string
                    # Obtener índice y nombre del campo
                    try:
                        index = key.split('[')[1].split(']')[0]  # Extrae el índice del dependiente
                        field_name = key.split('[')[2].split(']')[0]  # Extrae el nombre del campo
                    except IndexError:
                        continue  # Ignora las llaves que no tengan el formato esperado
                    
                    # Inicializar un diccionario para el dependiente si no existe
                    if index not in supp_data:
                        supp_data[index] = {}

                    # Almacenar el valor del campo en el diccionario correspondiente
                    supp_data[index][field_name] = value

            # Guardar cada dependiente en la base de datos
            for sup_data in supp_data.values():
                if 'carrierSuple' in sup_data:  # Verificar que al menos el nombre esté presente
                    supp_id = sup_data.get('id')  # Obtener el id si está presente

                    if supp_id:  # Si se proporciona un id, actualizar el registro existente
                        Supp.objects.filter(id=supp_id).update(
                            client=client,
                            profiling_agent=request.user,
                            effective_date=sup_data.get('effectiveDateSupp'),
                            company=sup_data.get('carrierSuple'),
                            premium=sup_data.get('premiumSupp'),
                            policy_type=sup_data.get('policyTypeSupp'),
                            preventive=sup_data.get('preventiveSupp'),
                            coverage=sup_data.get('coverageSupp'),
                            deducible=sup_data.get('deducibleSupp'),
                            observation=sup_data.get('observationSuple')
                        )
                    else:  # Si no hay id, crear un nuevo registro
                        Supp.objects.create(
                            client=client,
                            profiling_agent=request.user,
                            effective_date=sup_data.get('effectiveDateSupp'),
                            company=sup_data.get('carrierSuple'),
                            premium=sup_data.get('premiumSupp'),
                            policy_type=sup_data.get('policyTypeSupp'),
                            preventive=sup_data.get('preventiveSupp'),
                            coverage=sup_data.get('coverageSupp'),
                            deducible=sup_data.get('deducibleSupp'),
                            observation=sup_data.get('observationSuple')
                        )

            return JsonResponse({'success': True})
        elif type_sale == 'DEPENDENTS':
            dependents_data = {}

            # Filtrar solo los datos que corresponden a dependents y organizarlos por índices
            for key, value in request.POST.items():
                if key.startswith('dependent'):
                    # Obtener índice y nombre del campo
                    try:
                        index = key.split('[')[1].split(']')[0]  # Extrae el índice del dependiente
                        field_name = key.split('[')[2].split(']')[0]  # Extrae el nombre del campo
                    except IndexError:
                        continue  # Ignora las llaves que no tengan el formato esperado
                    
                    # Inicializar un diccionario para el dependiente si no existe
                    if index not in dependents_data:
                        dependents_data[index] = {}

                    # Almacenar el valor del campo en el diccionario correspondiente
                    dependents_data[index][field_name] = value

                    print('entre')

            # Guardar cada dependiente en la base de datos
            for dep_data in dependents_data.values():
                if 'nameDependent' in dep_data:  # Verificar que al menos el nombre esté presente
                    dependent_id = dep_data.get('id')  # Obtener el id si está presente
                    print(dependent_id)

                    if dependent_id:  # Si se proporciona un id, actualizar el registro existente
                        Dependent.objects.filter(id=dependent_id).update(
                            client=client,
                            name=dep_data.get('nameDependent'),
                            apply=dep_data.get('applyDependent'),
                            date_birth=dep_data.get('dateBirthDependent'),
                            migration_status=dep_data.get('migrationStatusDependent'),
                            sex=dep_data.get('sexDependent'),
                            kinship=dep_data.get('kinship'),
                            type_police=dep_data.get('typePolice')                            
                        )
                        print('hola')
                    else:  # Si no hay id, crear un nuevo registro
                        Dependent.objects.create(
                            client=client,
                            name=dep_data.get('nameDependent'),
                            apply=dep_data.get('applyDependent'),
                            date_birth=dep_data.get('dateBirthDependent'),
                            migration_status=dep_data.get('migrationStatusDependent'),
                            sex=dep_data.get('sexDependent'),
                            kinship=dep_data.get('kinship'),
                            type_police=dep_data.get('typePolice')
                        )
                        print('holass')

            return JsonResponse({'success': True})

    aca_plan = ObamaCare.objects.filter(client=client).first()
    supplementary_plan = Supp.objects.filter(client=client)
    dependents = Dependent.objects.filter(client=client)
    print(dependents)

    return render(request, 'forms/formCreatePlan.html', {
        'client': client,
        'aca_plan_data': aca_plan,
        'supplementary_plan_data': supplementary_plan,
        'dependents': dependents
    })


def delete_dependent(request, dependent_id):
    if request.method == 'POST':
        try:
            # Buscar y eliminar el dependiente por ID
            dependent = Dependent.objects.get(id=dependent_id)
            dependent.delete()
            return JsonResponse({'success': True})
        except Dependent.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dependent not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_supp(request, supp_id):
    if request.method == 'POST':
        try:
            # Buscar y eliminar el dependiente por ID
            supp = Supp.objects.get(id=supp_id)
            supp.delete()
            return JsonResponse({'success': True})
        except Supp.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dependent not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def table(request):
    return render(request, 'table.html')
