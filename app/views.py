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
import json

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import Client
from .forms import ClientForm
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

def select_client(request):
    clients = Client.objects.all()
    return render(request, 'agents/select_client.html', {'clients':clients})

# Vista para crear cliente
def formCreateClient(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            
            # Verificar si el número de teléfono ya está registrado
            if Client.objects.filter(phone_number=phone_number).exists():
                return render(request, 'forms/formCreateClient.html', {'error_message': 'Este numero de telefono ya esta registrado'})
            
            # Guardar el cliente
            client = form.save(commit=False)
            client.agent = request.user
            client.save()
            
            # Responder con éxito y la URL de redirección
            return redirect('formCreatePlan', client.id)
        else:
            return render(request, 'forms/formCreateClient.html', {'error_message': form.errors})
    else:
        return render(request, 'forms/formCreateClient.html')

# Nueva vista para verificar si el número de teléfono ya existe (usada en AJAX)
def check_phone_number(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        exists = Client.objects.filter(phone_number=phone_number).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})

def formCreatePlan(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    type_sale = request.GET.get('type_sale')
    aca_plan = ObamaCare.objects.filter(client=client).first()
    supplementary_plan = Supp.objects.filter(client=client)
    dependents = Dependent.objects.filter(client=client)

    return render(request, 'forms/formCreatePlan.html', {
        'client': client,
        'aca_plan_data': aca_plan,
        'supplementary_plan_data': supplementary_plan,
        'dependents': dependents,
        'type_sale':type_sale
    })

def fetchAca(request, client_id):
    client = Client.objects.get(id=client_id)
    aca_plan_id = request.POST.get('acaPlanId')

    if aca_plan_id:
        # Si el ID existe, actualiza el registro
        ObamaCare.objects.filter(id=aca_plan_id).update(
            client=client,
            profiling_agent=request.user,
            taxes=request.POST.get('taxes'),
            plan_name=request.POST.get('planName'),
            work=request.POST.get('work'),
            subsidy=request.POST.get('subsidy'),
            carrier=request.POST.get('carrierObama'),
            apply=request.POST.get('applyObama'),
            observation=request.POST.get('observationObama')
        )
        aca_plan = ObamaCare.objects.get(id=aca_plan_id)
        created = False
    else:
        # Si no hay ID, crea un nuevo registro
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
    return JsonResponse({'success': True, 'aca_plan_id': aca_plan.id})

def fetchSupp(request, client_id):
    client = Client.objects.get(id=client_id)
    supp_data = {}
    updated_supp_ids = []  # Lista para almacenar los IDs de los registros suplementarios

    # Filtrar solo los datos que corresponden a suplementario y organizarlos por índices
    for key, value in request.POST.items():
        if key.startswith('supplementary_plan_data'): #pregunta como inicia el string
            # Obtener índice y nombre del campo
            try:
                index = key.split('[')[1].split(']')[0]  # Extrae el índice del suplementario
                field_name = key.split('[')[2].split(']')[0]  # Extrae el nombre del campo
            except IndexError:
                continue  # Ignora las llaves que no tengan el formato esperado
            
            # Inicializar un diccionario para el suplementario si no existe
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
                updated_supp_ids.append(supp_id)  # Agregar el ID actualizado a la lista
            else:  # Si no hay id, crear un nuevo registro
                new_supp = Supp.objects.create(
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
                updated_supp_ids.append(new_supp.id)  # Agregar el ID creado a la lista
    return JsonResponse({'success': True,  'supp_ids': updated_supp_ids})
        
def fetchDependent(request, client_id):
    client = Client.objects.get(id=client_id)
    dependents_data = {}
    updated_dependents_ids = []  # Lista para almacenar los IDs de los registros suplementarios

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

    # Guardar cada dependiente en la base de datos
    for dep_data in dependents_data.values():
        if 'nameDependent' in dep_data:  # Verificar que al menos el nombre esté presente
            dependent_id = dep_data.get('id')  # Obtener el id si está presente

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
                updated_dependents_ids.append(dependent_id)  # Agregar el ID actualizado a la lista
            else:  # Si no hay id, crear un nuevo registro
                new_dependent = Dependent.objects.create(
                    client=client,
                    name=dep_data.get('nameDependent'),
                    apply=dep_data.get('applyDependent'),
                    date_birth=dep_data.get('dateBirthDependent'),
                    migration_status=dep_data.get('migrationStatusDependent'),
                    sex=dep_data.get('sexDependent'),
                    kinship=dep_data.get('kinship'),
                    type_police=dep_data.get('typePolice')
                )
                updated_dependents_ids.append(new_dependent.id)  # Agregar el ID creado a la lista

    return JsonResponse({'success': True,'dependents_ids': updated_dependents_ids}) #Y aki retornes la lista/array.

def clientObamacare(request):
    obamaCare = ObamaCare.objects.select_related('profiling_agent','client').filter(
        profiling_agent_id = request.user.id, is_active = True ) #El error es porque no estas logueado HUevon!
    return render(request, 'table/clientObamacare.html', {'obamaCare':obamaCare})

def clientSupp(request):
    supp = Supp.objects.select_related('profiling_agent','client').filter(
        profiling_agent_id = request.user.id)
    return render(request, 'table/clientSupp.html', {'supps':supp})

def client(request):
    client = Client.objects.select_related('agent').filter(
        agent = request.user.id)
    return render(request, 'table/client.html', {'clients':client})

def toggleObamaStatus(request, obamacare_id):
    # Obtener el cliente por su ID
    obama = get_object_or_404(ObamaCare, id=obamacare_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    obama.is_active = not obama.is_active
    obama.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('clientObamacare')

def toggleSuppStatus(request, supp_id):
    # Obtener el cliente por su ID
    supp = get_object_or_404(Supp, id=supp_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    supp.is_active = not supp.is_active
    supp.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('clientSupp')

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

def clean_field_to_null(value):
    """
    Limpia el valor de un campo. Si el valor está vacío (cadena vacía, None o solo espacios),
    devuelve `None` para que se guarde como NULL en la base de datos.
    """
    if value == '' or value is None or value.strip() == '':
        return None
    return value

def clean_fields_to_null(request, field_names):
    """
    Limpia un conjunto de campos obtenidos desde `request.POST`, 
    convirtiendo los valores vacíos en `None` (NULL en la base de datos).
    Devuelve un diccionario con los campos limpiados.
    """
    cleaned_data = {}
    for field in field_names:
        value = request.POST.get(field)
        cleaned_data[field] = clean_field_to_null(value)
    return cleaned_data

def editClientObama(request, obamacare_id):
    obamacare = ObamaCare.objects.select_related('profiling_agent', 'client').filter(id=obamacare_id).first()

    obsObama = ObservationAgent.objects.filter(id_obamaCare=obamacare_id)

    if obamacare and obamacare.client: 
        dependents = Dependent.objects.filter(client=obamacare.client)

    user = User.objects.filter(role='C')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_obamacare':
            
            # Campos de ObamaCare
            obamacare_fields = [
                'taxes', 'planName', 'carrierObama', 'profiling', 'subsidy', 'ffm', 'required_bearing',
                'date_bearing', 'doc_icon', 'doc_migration', 'statusObama', 'work', 'npm', 
                'date_effective_coverage', 'date_effective_coverage_end', 'apply', 'observationObama'
            ]
            
            # Limpiar los campos de ObamaCare convirtiendo los vacíos en None
            cleaned_obamacare_data = clean_fields_to_null(request, obamacare_fields)
            print("Datos a guardar en ObamaCare:", cleaned_obamacare_data)

            # Actualizar ObamaCare
            ObamaCare.objects.filter(id=obamacare_id).update(
                taxes=cleaned_obamacare_data['taxes'],
                plan_name=cleaned_obamacare_data['planName'],
                carrier=cleaned_obamacare_data['carrierObama'],
                profiling=cleaned_obamacare_data['profiling'],
                subsidy=cleaned_obamacare_data['subsidy'],
                ffm=int(cleaned_obamacare_data['ffm']) if cleaned_obamacare_data['ffm'] else None,
                required_bearing=cleaned_obamacare_data['required_bearing'],
                date_bearing=cleaned_obamacare_data['date_bearing'],
                doc_icon=cleaned_obamacare_data['doc_icon'],
                doc_migration=cleaned_obamacare_data['doc_migration'],
                status=cleaned_obamacare_data['statusObama'],
                work=cleaned_obamacare_data['work'],
                npm=cleaned_obamacare_data['npm'],
                date_effective_coverage=cleaned_obamacare_data['date_effective_coverage'],
                date_effective_coverage_end=cleaned_obamacare_data['date_effective_coverage_end'],
                apply=cleaned_obamacare_data['apply'],
                observation=cleaned_obamacare_data['observationObama']
            )

            return redirect('clientObamacare')

        elif action == 'save_observation_agent':
            
            obs = request.POST.get('obs_agent')

            if obs:
                id_client = request.POST.get('id_client')
                print(request.POST['id_client'])
                client = Client.objects.get(id=id_client)
                id_obama = ObamaCare.objects.get(id=obamacare_id)
                id_user = request.user

                # Crear y guardar la observación
                ObservationAgent.objects.create(
                    id_client=client,
                    id_obamaCare=id_obama,
                    id_user=id_user,
                    content=obs
                )
            
            return redirect('clientObamacare')

    context = {
        'obamacare': obamacare,
        'dependents': dependents,
        'users': user,
        'obsObamaText': '\n'.join([obs.content for obs in obsObama])
    }

    return render(request, 'edit/editClientObama.html', context)

def editClientSupp(request,supp_id):

    supp = Supp.objects.select_related('client','profiling_agent').filter(id=supp_id).first()
    obsSupp = ObservationAgent.objects.filter(id_supp=supp_id)

    if supp and supp.client: 
        dependents = Dependent.objects.filter(client=supp.client)

    action = request.POST.get('action')

    if request.method == 'POST':

        if action == 'save_supp':
                
            # Campos de Supp
            supp_fields = [
                'effectiveDateSupp', 'carrierSuple', 'premiumSupp', 'preventiveSupp', 'policyTypeSupp', 'coverageSupp', 'deducibleSupp',
                'statusSupp', 'typePaymeSupp', 'date_effective_coverage', 'date_effective_coverage_end', 'observationSuple'
            ]
            
            # Limpiar los campos de ObamaCare convirtiendo los vacíos en None
            cleaned_supp_data = clean_fields_to_null(request, supp_fields)
            print("Datos a guardar en Supp:", cleaned_supp_data)

            # Actualizar ObamaCare
            Supp.objects.filter(id=supp_id).update(
                effective_date=cleaned_supp_data['effectiveDateSupp'],
                company=cleaned_supp_data['carrierSuple'],
                policy_type=cleaned_supp_data['policyTypeSupp'],
                premium=cleaned_supp_data['premiumSupp'],
                preventive=cleaned_supp_data['preventiveSupp'],
                coverage=cleaned_supp_data['coverageSupp'],
                deducible=cleaned_supp_data['deducibleSupp'],
                status=cleaned_supp_data['statusSupp'],
                date_effective_coverage=cleaned_supp_data['date_effective_coverage'],
                date_effective_coverage_end=cleaned_supp_data['date_effective_coverage_end'],
                payment_type=cleaned_supp_data['typePaymeSupp'],
                observation=cleaned_supp_data['observationSuple']
            )

            return redirect('clientSupp')  
              
        elif action == 'save_supp_agent':

            obs = request.POST.get('obs_agent')

            if obs:
                id_client = request.POST.get('id_client')
                client = Client.objects.get(id=id_client)
                id_supp = Supp.objects.get(id=supp_id)
                id_user = request.user

                # Crear y guardar la observación
                ObservationAgent.objects.create(
                    id_client=client,
                    id_supp=id_supp,
                    id_user=id_user,
                    content=obs
                )
            
                return redirect('clientSupp')

    context = {
        'supps': supp,
        'dependents': dependents,
        'obsSuppText': '\n'.join([obs.content for obs in obsSupp])
    }
    
    return render(request, 'edit/editClientSupp.html', context)

def formCreateAlert(request):

    if request.method == 'POST':
        formClient = ClientAlertForm(request.POST)
        if formClient.is_valid():
            alert = formClient.save(commit=False)
            alert.agent = request.user
            alert.save()
            return redirect('formCreateAlert')  # Cambia a tu página de éxito

    return render(request, 'forms/formCreateAlert.html')
    
def tableAlert(request):
    
    alert = ClientAlert.objects.select_related('agent').filter(
        agent = request.user.id, 
        is_active = True)
    return render(request, 'table/alert.html', {'alertC':alert})

def toggleAlert(request, alertClient_id):
    # Obtener el cliente por su ID
    alert = get_object_or_404(ClientAlert, id=alertClient_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    alert.is_active = not alert.is_active
    alert.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('alert')

def editAlert(request, alertClient_id):

    alert = ClientAlert.objects.select_related('agent').filter(id=alertClient_id).first()

    if request.method == 'POST':

        alert_fields = ['name_client', 'phone_number', 'datetime', 'content' ]

        # Limpiar los campos 
        cleaned_alert_data = clean_fields_to_null(request, alert_fields)

        ClientAlert.objects.filter(id=alertClient_id).update(
                name_client=cleaned_alert_data['name_client'],
                phone_number=cleaned_alert_data['phone_number'],
                datetime=cleaned_alert_data['datetime'],
                content=cleaned_alert_data['content']
            )
        return redirect('alert')

    return render(request, 'edit/editAlert.html', {'editAlert':alert} )

