from collections import defaultdict
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

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta
import calendar
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.db.models import Count
from datetime import date

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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
            return redirect(motivationalPhrase)
        else:
            msg = 'Datos incorrectos, intente de nuevo'
            return render(request, 'auth/login.html', {'msg':msg})
    else:
        return render(request, 'auth/login.html')
        
def logout_(request):

     # Verifica si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logout(request)
        return JsonResponse({
            'status': 'success', 
            'redirect_url': '/login/'  # URL a la que redirigir después del logout
        })
    else:
        # Cierre de sesión manual tradicional
        logout(request)
        return redirect(index)
    
@login_required(login_url='/login')
def motivationalPhrase(request):
    randomInt = random.randint(1,174)
    motivation = Motivation.objects.filter(id=randomInt).first()
    context = {'motivation':motivation}
    return render (request, 'motivationalPhrase.html',context)

@login_required(login_url='/login') 
def select_client(request):

    # Roles con acceso ampliado
    roleAuditar = ['S', 'Admin']

    if request.user.role in roleAuditar:
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(agent = request.user.id)
    
    return render(request, 'agents/select_client.html', {'clients':clients})

def update_type_sales(request, client_id):
    if request.method == 'POST':
        type_sales = request.POST.get('type_sales')
        if type_sales:
            client = get_object_or_404(Client, id=client_id)
            client.type_sales = type_sales
            client.save()
            # Redirige a la URL previa con el ID del cliente
            return redirect('formCreatePlan', client_id=client_id)

# Vista para crear cliente
@login_required(login_url='/login') 
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
            client.is_active = 1
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

@login_required(login_url='/login') 
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
            agent=request.user,
            status_color = 1,
            profiling = 'NO',
            taxes=request.POST.get('taxes'),
            agent_usa=request.POST.get('agent_usa'),
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
            agent=request.user,
            defaults={
                'taxes': request.POST.get('taxes'),
                'agent_usa': request.POST.get('agent_usa'),
                'plan_name': request.POST.get('planName'),
                'work': request.POST.get('work'),
                'subsidy': request.POST.get('subsidy'),
                'carrier': request.POST.get('carrierObama'),
                'apply': request.POST.get('applyObama'),
                'observation': request.POST.get('observationObama'),
                'status_color': 1,
                'profiling':'NO'
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
                    status='REGISTERED',
                    status_color = 1,
                    agent=request.user,
                    effective_date=sup_data.get('effectiveDateSupp'),
                    agent_usa=sup_data.get('agent_usa'),
                    company=sup_data.get('carrierSuple'),
                    premium=sup_data.get('premiumSupp'),
                    policy_type=sup_data.get('policyTypeSupp'),
                    preventive=sup_data.get('preventiveSupp'),
                    coverage=sup_data.get('coverageSupp'),
                    deducible=sup_data.get('deducibleSupp'),
                    observation=sup_data.get('observationSuple'),
                )
                updated_supp_ids.append(supp_id)  # Agregar el ID actualizado a la lista
            else:  # Si no hay id, crear un nuevo registro
                new_supp = Supp.objects.create(
                    client=client,
                    status='REGISTERED',
                    agent=request.user,
                    effective_date=sup_data.get('effectiveDateSupp'),
                    agent_usa=sup_data.get('agent_usa'),
                    company=sup_data.get('carrierSuple'),
                    premium=sup_data.get('premiumSupp'),
                    policy_type=sup_data.get('policyTypeSupp'),
                    preventive=sup_data.get('preventiveSupp'),
                    coverage=sup_data.get('coverageSupp'),
                    deducible=sup_data.get('deducibleSupp'),
                    observation=sup_data.get('observationSuple'),
                    status_color = 1
                )
                updated_supp_ids.append(new_supp.id)  # Agregar el ID creado a la lista
    return JsonResponse({'success': True,  'supp_ids': updated_supp_ids})
        
def fetchDependent(request, client_id):
    client = Client.objects.get(id=client_id)
    dependents_data = {}
    updated_dependents_ids = []

    # Procesar datos de dependientes como antes
    for key, value in request.POST.items():
        if key.startswith('dependent'):
            try:
                index = key.split('[')[1].split(']')[0]
                field_name = key.split('[')[2].split(']')[0]
            except IndexError:
                continue
            
            if index not in dependents_data:
                dependents_data[index] = {}

            dependents_data[index][field_name] = value

    # Crear lista de dependientes
    dependents_to_add = []
    for dep_data in dependents_data.values():
        if 'nameDependent' in dep_data:
            dependent_id = dep_data.get('id')

            # Procesar múltiples valores de type_police
            type_police_values = dep_data.get('typePoliceDependents', [])
            type_police = ", ".join(type_police_values.split(',') if type_police_values else [])

            # Lógica para asociar ObamaCare
            obamacare = None
            if 'ACA' in type_police:
                # Buscar un plan ObamaCare para el cliente
                obamacare = ObamaCare.objects.filter(client=client).first()

            # Crear o actualizar Dependent
            if dependent_id:
                dependent = Dependent.objects.get(id=dependent_id)
                for attr, value in {
                    'name': dep_data.get('nameDependent'),
                    'apply': dep_data.get('applyDependent'),
                    'date_birth': dep_data.get('dateBirthDependent'),
                    'migration_status': dep_data.get('migrationStatusDependent'),
                    'sex': dep_data.get('sexDependent'),
                    'kinship': dep_data.get('kinship'),
                    'type_police': type_police,
                    'obamacare': obamacare
                }.items():
                    setattr(dependent, attr, value)
                dependent.save()
            else:
                dependent = Dependent.objects.create(
                    client=client,
                    name=dep_data.get('nameDependent'),
                    apply=dep_data.get('applyDependent'),
                    date_birth=dep_data.get('dateBirthDependent'),
                    migration_status=dep_data.get('migrationStatusDependent'),
                    sex=dep_data.get('sexDependent'),
                    kinship=dep_data.get('kinship'),
                    type_police=type_police,
                    obamacare=obamacare
                )

            dependents_to_add.append(dependent)
            updated_dependents_ids.append(dependent.id)

    # Obtener todos los Supp para este cliente
    supps = Supp.objects.filter(client=client)
    
    # Agregar todos los dependientes a cada Supp
    for supp in supps:
        supp.dependents.clear()  # Limpiar relaciones existentes
        supp.dependents.add(*dependents_to_add)

    return JsonResponse({
        'success': True,
        'dependents_ids': updated_dependents_ids
    })

@login_required(login_url='/login')
def clientObamacare(request):
    
    roleAuditar = ['S', 'C',  'AU']
    
    if request.user.role in roleAuditar:
        obamaCare = ObamaCare.objects.select_related('agent','client').filter(is_active = True)
    elif request.user.role == 'Admin':
        obamaCare = ObamaCare.objects.select_related('agent', 'client').filter(is_active=True)

    elif request.user.role == 'A':
        obamaCare = ObamaCare.objects.select_related('agent','client').filter(agent = request.user.id, is_active = True ) 

    
    return render(request, 'table/clientObamacare.html', {'obamaCare':obamaCare})

@login_required(login_url='/login')
def clientSupp(request):

    roleAuditar = ['S', 'C',  'AU']
    
    if request.user.role in roleAuditar:
        supp = Supp.objects.select_related('agent','client').filter(is_active = True )
    elif request.user.role == 'Admin':
        supp = Supp.objects.select_related('agent','client')
    elif request.user.role == 'A':
        supp = Supp.objects.select_related('agent','client').filter(agent = request.user.id, is_active = True)

    return render(request, 'table/clientSupp.html', {'supps':supp})

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

def editClient(request,agent_id):

    # Campos de Client
    client_fields = [
        'agent_usa', 'first_name', 'last_name', 'phone_number', 'email', 'address', 'zipcode',
        'city', 'state', 'county', 'sex', 'old', 'migration_status'
    ]
    
    #formateo de fecha para guardalar como se debe en BD ya que la obtengo USA
    fecha_str = request.POST.get('date_birth')  # Formato MM/DD/YYYY
    dateNew = datetime.strptime(fecha_str, '%m/%d/%Y').date()

    # Limpiar los campos de Client convirtiendo los vacíos en None
    cleaned_client_data = clean_fields_to_null(request, client_fields)

    # Actualizar Client
    client = Client.objects.filter(id=agent_id).update(
        agent_usa=cleaned_client_data['agent_usa'],
        first_name=cleaned_client_data['first_name'],
        last_name=cleaned_client_data['last_name'],
        phone_number=cleaned_client_data['phone_number'],
        email=cleaned_client_data['email'],
        address=cleaned_client_data['address'],
        zipcode=cleaned_client_data['zipcode'],
        city=cleaned_client_data['city'],
        state=cleaned_client_data['state'],
        county=cleaned_client_data['county'],
        sex=cleaned_client_data['sex'],
        old=cleaned_client_data['old'],
        date_birth=dateNew,
        migration_status=cleaned_client_data['migration_status']
    )

    return client

def editClientObama(request, client_id, obamacare_id):
    obamacare = ObamaCare.objects.select_related('agent', 'client').filter(id=obamacare_id).first()
    dependents = Dependent.objects.select_related('obamacare').filter(obamacare=obamacare)

    obsObama = ObservationAgent.objects.filter(id_obamaCare=obamacare_id)
  
    users = User.objects.filter(role='C')
    list_drow = dropDownList.objects.filter(profiling_obama__isnull=False)

    obsCus = ObservationCustomer.objects.select_related('agent').filter(client_id=obamacare.client.id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_obamacare':

            editClient(request, client_id)
            dependents= editDepentsObama(request, obamacare_id)


            # Campos de ObamaCare
            obamacare_fields = [
                'taxes', 'planName', 'carrierObama', 'profiling', 'subsidy', 'ffm', 'required_bearing',
                'doc_income', 'doc_migration', 'statusObama', 'work', 'npm', 'date_effective_coverage',
                'date_effective_coverage_end', 'apply', 'observationObama', 'agent_usa'
            ]
            
            # Limpiar los campos de ObamaCare convirtiendo los vacíos en None
            cleaned_obamacare_data = clean_fields_to_null(request, obamacare_fields)

            #formateo de fecha para guardalar como se debe en BD ya que la obtengo USA
            date_bearing = request.POST.get('date_bearing')  # Formato MM/DD/YYYY
            date_effective_coverage = request.POST.get('date_effective_coverage')  # Formato MM/DD/YYYY
            date_effective_coverage_end = request.POST.get('date_effective_coverage_end')  # Formato MM/DD/YYYY

            # Conversión solo si los valores no son nulos o vacíos
            if date_bearing not in [None, '']:
                date_bearing_new = datetime.strptime(date_bearing, '%m/%d/%Y').date()
            else:
                date_bearing_new = None

            if date_effective_coverage not in [None, '']:
                date_effective_coverage_new = datetime.strptime(date_effective_coverage, '%m/%d/%Y').date()
            else:
                date_effective_coverage_new = None

            if date_effective_coverage_end not in [None, '']:
                date_effective_coverage_end_new = datetime.strptime(date_effective_coverage_end, '%m/%d/%Y').date()
            else:
                date_effective_coverage_end_new = None


            # Recibir el valor seleccionado del formulario
            selected_profiling = request.POST.get('profiling')

            sw = True
            color = obamacare.status_color

            # Recorrer los usuarios
            for user in users:
                # Comparar el valor seleccionado con el username de cada usuario
                if selected_profiling == user.username:
                    color = 3
                    sw = False
                    break  # Si solo te interesa el primer match, puedes salir del bucle
            
            for list_drow in list_drow:
                if selected_profiling == list_drow.profiling_obama:
                    color = 2
                    sw = False
                    break
            
            if selected_profiling == 'VENTA CAIDA' or selected_profiling == 'CLIENTE CANCELO':
                color = 4                    

            if selected_profiling is not None:  # Solo actualizamos profiling_date si profiling no es None - DannyZz
                profiling_date = timezone.now().date()
                profiling = cleaned_obamacare_data['profiling']
            else:
                profiling_date = obamacare.profiling_date  # Mantener el valor anterior si profiling es None - DannyZz
                profiling = obamacare.profiling
                sw = False

            if sw :
                color = 1  


            # Actualizar ObamaCare
            ObamaCare.objects.filter(id=obamacare_id).update(
                taxes=cleaned_obamacare_data['taxes'],
                agent_usa=cleaned_obamacare_data['agent_usa'],
                plan_name=cleaned_obamacare_data['planName'],
                carrier=cleaned_obamacare_data['carrierObama'],
                profiling=profiling,
                profiling_date=profiling_date,  # Se actualiza solo si profiling no es None - DannyZz
                subsidy=cleaned_obamacare_data['subsidy'],
                ffm=int(cleaned_obamacare_data['ffm']) if cleaned_obamacare_data['ffm'] else None,
                required_bearing=cleaned_obamacare_data['required_bearing'],
                date_bearing=date_bearing_new,
                doc_income=cleaned_obamacare_data['doc_income'],
                status_color = color,
                doc_migration=cleaned_obamacare_data['doc_migration'],
                status=cleaned_obamacare_data['statusObama'],
                work=cleaned_obamacare_data['work'],
                npm=cleaned_obamacare_data['npm'],
                date_effective_coverage=date_effective_coverage_new,
                date_effective_coverage_end=date_effective_coverage_end_new,
                apply=cleaned_obamacare_data['apply'],
                observation=cleaned_obamacare_data['observationObama']
            )

            return redirect('clientObamacare')

        elif action == 'save_observation_agent':
            
            obs = request.POST.get('obs_agent')

            if obs:
                id_client = request.POST.get('id_client')
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
        'users': users,
        'obsObamaText': '\n'.join([obs.content for obs in obsObama]),
        'obsCustomer': obsCus,
        'list_drow': list_drow,
        'dependents' : dependents
    }

    return render(request, 'edit/editClientObama.html', context)

def editClientSupp(request, client_id,supp_id):

    supp = Supp.objects.select_related('client','agent').filter(id=supp_id).first()
    obsSupp = ObservationAgent.objects.filter(id_supp=supp_id)
    obsCus = ObservationCustomer.objects.select_related('agent').filter(client_id=supp.client.id)
    list_drow = dropDownList.objects.filter(profiling_supp__isnull=False)

    # Obtener el objeto Supp que tiene el id `supp_id`
    supp_instance = Supp.objects.get(id=supp_id)

    # Obtener todos los dependientes asociados a este Supp
    dependents = supp_instance.dependents.all()


    action = request.POST.get('action')

    if request.method == 'POST':

        if action == 'save_supp':

            editClient(request, client_id)
            dependents= editDepentsSupp(request, supp_id)

            #formateo de fecha para guardalar como se debe en BD ya que la obtengo USA
            date_effective_coverage = request.POST.get('date_effective_coverage')  # Formato MM/DD/YYYY
            date_effective_coverage_end = request.POST.get('date_effective_coverage_end')  # Formato MM/DD/YYYY
            date_effective_coverage_new = datetime.strptime(date_effective_coverage, '%m/%d/%Y').date()
            date_effective_coverage_end_new = datetime.strptime(date_effective_coverage_end, '%m/%d/%Y').date()
                
            # Campos de Supp
            supp_fields = [
                'effectiveDateSupp', 'carrierSuple', 'premiumSupp', 'preventiveSupp', 'coverageSupp', 'deducibleSupp',
                'statusSupp', 'typePaymeSupp', 'observationSuple', 'agent_usa'
            ]
            
            # Limpiar los campos de ObamaCare convirtiendo los vacíos en None
            cleaned_supp_data = clean_fields_to_null(request, supp_fields)

            # Recibir el valor seleccionado del formulario
            selected_status= request.POST.get('statusSupp')

            color = 1         

            for list_drow in list_drow:
                if selected_status == list_drow.profiling_supp:
                    if selected_status != 'ACTIVE':
                        color = 2
                        break         
                    if selected_status == 'ACTIVE':
                        color = 3 
                        break  


            # Actualizar Supp
            Supp.objects.filter(id=supp_id).update(
                effective_date=cleaned_supp_data['effectiveDateSupp'],
                agent_usa=cleaned_supp_data['agent_usa'],
                company=cleaned_supp_data['carrierSuple'],
                premium=cleaned_supp_data['premiumSupp'],
                preventive=cleaned_supp_data['preventiveSupp'],
                coverage=cleaned_supp_data['coverageSupp'],
                deducible=cleaned_supp_data['deducibleSupp'],
                status=cleaned_supp_data['statusSupp'],
                status_color=color,
                date_effective_coverage=date_effective_coverage_new,
                date_effective_coverage_end=date_effective_coverage_end_new,
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
        'obsSuppText': '\n'.join([obs.content for obs in obsSupp]),
        'obsCustomer': obsCus,
        'list_drow': list_drow
    }
    
    return render(request, 'edit/editClientSupp.html', context)

def editDepentsObama(request, obamacare_id):
    # Obtener todos los dependientes asociados al ObamaCare
    dependents = Dependent.objects.filter(obamacare=obamacare_id)    

    if request.method == "POST":
        for dependent in dependents:

            # Resetear la fecha guardarla como se debe porque la traigo en formato USA
            date_birth = request.POST.get(f'dateBirthDependent_{dependent.id}')
            dateNew = datetime.strptime(date_birth, '%m/%d/%Y').date()

            # Obtener los datos enviados por cada dependiente
            dependent_id = request.POST.get(f'dependentId_{dependent.id}')
            name = request.POST.get(f'nameDependent_{dependent.id}')
            apply = request.POST.get(f'applyDependent_{dependent.id}')
            kinship = request.POST.get(f'kinship_{dependent.id}')
            migration_status = request.POST.get(f'migrationStatusDependent_{dependent.id}')
            sex = request.POST.get(f'sexDependent_{dependent.id}')
            
            # Verificar si el ID coincide
            if dependent.id == int(dependent_id):  # Verificamos si el ID coincide
                
                # Verificamos que todos los campos tengan datos
                if name and apply and kinship and date_birth and migration_status and sex:
                    dependent.name = name
                    dependent.apply = apply
                    dependent.kinship = kinship
                    dependent.date_birth = dateNew
                    dependent.migration_status = migration_status
                    dependent.sex = sex

                    dependent.save()

    # Retornar todos los dependientes actualizados (o procesados)
    return dependents

def editDepentsSupp(request, supp_id):
    
    # Obtener el objeto Supp que tiene el id `supp_id`
    supp_instance = Supp.objects.get(id=supp_id)

    # Obtener todos los dependientes asociados a este Supp
    dependents = supp_instance.dependents.all()

    if request.method == "POST":
        for dependent in dependents:

            date_birth = request.POST.get(f'dateBirthDependent_{dependent.id}')
            dateNew = datetime.strptime(date_birth, '%m/%d/%Y').date()

            # Aquí obtenemos los datos enviados a través del formulario para cada dependiente
            dependent_id = request.POST.get(f'dependentId_{dependent.id}')  # Cambiar a 'dependentId_{dependent.id}'
            
            if dependent_id is None:
                continue  # Si no se encuentra el dependentId, continuamos con el siguiente dependiente
            
            # Verificamos si el dependent_id recibido coincide con el ID del dependiente actual
            if dependent.id == int(dependent_id):
                name = request.POST.get(f'nameDependent_{dependent.id}')
                apply = request.POST.get(f'applyDependent_{dependent.id}')
                kinship = request.POST.get(f'kinship_{dependent.id}')
                date_birth = request.POST.get(f'dateBirthDependent_{dependent.id}')
                migration_status = request.POST.get(f'migrationStatusDependent_{dependent.id}')
                sex = request.POST.get(f'sexDependent_{dependent.id}')
                
                
                # Verificamos si los demás campos existen y no son None
                if name and apply and kinship and date_birth and migration_status and sex:
                    # Actualizamos los campos del dependiente
                    dependent.name = name
                    dependent.apply = apply
                    dependent.kinship = kinship
                    dependent.date_birth = dateNew
                    dependent.migration_status = migration_status
                    dependent.sex = sex
                    
                    # Guardamos el objeto dependiente actualizado
                    dependent.save()
    
    # Retornar los dependientes que fueron actualizados o procesados
    return dependents

@login_required(login_url='/login') 
def formCreateAlert(request):

    if request.method == 'POST':
        formClient = ClientAlertForm(request.POST)
        if formClient.is_valid():
            alert = formClient.save(commit=False)
            alert.agent = request.user
            alert.save()
            return redirect('formCreateAlert')  # Cambia a tu página de éxito

    return render(request, 'forms/formCreateAlert.html')

@login_required(login_url='/login')    
def tableAlert(request):

    roleAuditar = ['S', 'C',  'AU']
    
    if request.user.role in roleAuditar:
        alert = ClientAlert.objects.select_related('agent').filter(is_active = True)
    elif request.user.role == 'Admin':
        alert = ClientAlert.objects.select_related('agent')
    elif request.user.role == 'A':
        alert = ClientAlert.objects.select_related('agent').filter(agent = request.user.id, is_active = True)
    
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

@login_required(login_url='/login') 
def formCreateUser(request):

    users = User.objects.all()

    roles = User.ROLES_CHOICES  # Obtén las opciones dinámicamente desde el modelo

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        role = request.POST.get('role')
        
        try:
            # Validar si el username ya existe
            if User.objects.filter(username=username).exists():
                
                return render(request, 'forms/formCreateUser.html', {'msg':f'El nombre de usuario "{username}" ya está en uso.','users':users, 'type':'error'})
            
            # Crear el usuario si no existe el username
            user = User.objects.create(
                username=username,
                password=make_password(password),  # Encriptar la contraseña
                email=email,
                last_name=last_name,
                first_name=first_name,
                role=role
            )

            context = {
                'msg':f'Usuario {user.username} creado con éxito.',
                'users':users,
                'type':'good',
                'roles': roles
            }

            return render(request, 'forms/formCreateUser.html', context)

        except Exception as e:
            return HttpResponse(str(e))
            
    return render(request, 'forms/formCreateUser.html',{'users':users,'roles': roles})

def editUser(request, user_id):
    # Obtener el usuario a editar o devolver un 404 si no existe
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Recuperar los datos del formulario
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)
        username = request.POST.get('username', user.username)
        password = request.POST.get('password', None)
        role = request.POST.get('role', user.role)
        is_active = request.POST.get('is_active', user.is_active)

        # Verificar si el nuevo username ya existe en otro usuario
        if username != user.username and User.objects.filter(username=username).exists():
            return JsonResponse({'error': f'El nombre de usuario "{username}" ya está en uso.'}, status=400)

        # Actualizar los datos del usuario
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        user.role = role
        user.is_active = is_active

        # Actualizar la contraseña si se proporciona una nueva
        if password:
            user.password = make_password(password)

        # Guardar los cambios
        user.save()

        # Redirigir a otra vista o mostrar un mensaje de éxito
        return redirect('formCreateUser')  

    # Renderizar el formulario con los datos actuales del usuario
    context = {'users': user}
    return render(request, 'edit/editUser.html', context)

def toggleUser(request, user_id):
    # Obtener el cliente por su ID
    user = get_object_or_404(User, id=user_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    user.is_active = not user.is_active
    user.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('formCreateUser')

def saveCustomerObservation(request):
    if request.method == "POST":
        content = request.POST.get('textoIngresado')
        plan_id = request.POST.get('plan_id')
        type_plan = request.POST.get('type_plan')
        typeCall = request.POST.get('typeCall')

        # Obtenemos las observaciones seleccionadas
        observations = request.POST.getlist('observaciones[]')  # Lista de valores seleccionados
        
        # Convertir las observaciones a una cadena (por ejemplo, separada por comas o saltos de línea)
        typification_text = ", ".join(observations)  # Puedes usar "\n".join(observations) si prefieres saltos de línea

        if type_plan == 'ACA':
            plan = ObamaCare.objects.get(id=plan_id)
        elif type_plan == 'SUPP':
            plan = Supp.objects.get(id=plan_id) 

        if content.strip():  # Validar que el texto no esté vacío
            ObservationCustomer.objects.create(
                client=plan.client,
                agent=request.user,
                id_plan=plan.id,
                type_police=type_plan,
                typeCall=typeCall,
                typification=typification_text, # Guardamos las observaciones en el campo 'typification'
                content=content
            )
            messages.success(request, "Observación guardada exitosamente.")
        else:
            messages.error(request, "El contenido de la observación no puede estar vacío.")

        if type_plan == 'ACA':
            return redirect('editClientObama', plan.id)
        elif type_plan == 'SUPP':
            return redirect('editClientSupp', plan.id)        
        
    else:
        return HttpResponse("Método no permitido.", status=405)

@login_required(login_url='/login') 
def typification(request):

    # Obtener parámetros de fecha del request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Consulta base
    typification = ObservationCustomer.objects.select_related('agent', 'client').filter(is_active = True)

    # Si no se proporcionan fechas, mostrar registros del mes actual
    if not start_date and not end_date:
        # Obtener el primer día del mes actual con zona horaria
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Obtener el último día del mes actual
        if today.month == 12:
            # Si es diciembre, el último día será el 31
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            # Para otros meses, usar el día anterior al primer día del siguiente mes
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month+1) - timezone.timedelta(seconds=1))
        
        typification = typification.filter(created_at__range=[first_day_of_month, last_day_of_month])
    
    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        # Convertir fechas a objetos datetime con zona horaria
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        
        typification = typification.filter(
            created_at__range=[start_date, end_date]
        )

    # Ordenar por fecha de creación descendente
    typification = typification.order_by('-created_at')

    return render(request, 'table/typification.html', {
        'typification': typification,
        'start_date': start_date,
        'end_date': end_date
    })

def get_observation_detail(request, observation_id):
    try:
        # Obtener el registro específico
        observation = ObservationCustomer.objects.select_related('agent', 'client').get(id=observation_id)
        
        # Preparar los datos para el JSON
        data = {
            'agent_name': f"{observation.agent.first_name} {observation.agent.last_name}",
            'client_name': f"{observation.client.first_name} {observation.client.last_name}",
            'type_police': observation.type_police,
            'type_call': observation.typeCall,
            'created_at': observation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'typification': observation.typification,
            'content': observation.content,
        }
        
        return JsonResponse(data)
    except ObservationCustomer.DoesNotExist:
        return JsonResponse({'error': 'Registro no encontrado'}, status=404)

def toggleTypification(request, typifications_id):
    # Obtener el cliente por su ID
    typi = get_object_or_404(ObservationCustomer, id=typifications_id)
    
    # Cambiar el estado de is_active (True a False o viceversa)
    typi.is_active = not typi.is_active
    typi.save()  # Guardar los cambios en la base de datos
    
    # Redirigir de nuevo a la página actual con un parámetro de éxito
    return redirect('typification')

@login_required(login_url='/login') 
def index(request):
    obama = countSalesObama(request)
    supp = countSalesSupp(request)
    chartOne = chartSaleIndex(request)
    tableStatusAca = tableStatusObama(request)
    tableStatusSup = tableStatusSupp(request)

    # Asegúrate de que chartOne sea un JSON válido
    chartOne_json = json.dumps(chartOne)

    context = {
        'obama':obama,
        'supp':supp,
        'chartOne':chartOne_json,
        'tableStatusObama':tableStatusAca,
        'tableStatusSup':tableStatusSup
    }      

    return render(request, 'dashboard/index.html', context)
 
def countSalesObama(request):

    # Obtener el mes y el año actuales
    now = timezone.now()

    # Calcular el primer día del mes
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calcular el último día del mes
    last_day = calendar.monthrange(now.year, now.month)[1]  # Obtiene el último día del mes
    end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    roleAuditar = ['S', 'C',  'AU', 'Admin']
    
    if request.user.role in roleAuditar:        
        all = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        active = ObamaCare.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        process = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).filter(Q(status_color=2) | Q(status_color=1)).count()
        cancell = ObamaCare.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
    elif request.user.role == 'A':
        all = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        active = ObamaCare.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        process = ObamaCare.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(Q(status_color=2) | Q(status_color=1)).filter(agent = request.user.id, is_active = True ).count()
        cancell = ObamaCare.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
       
   
    dicts = {
        'all': all,
        'active':active,
        'process':process,
        'cancell':cancell
    }
    return dicts

def countSalesSupp(request):

    # Obtener el mes y el año actuales
    now = timezone.now()

    # Calcular el primer día del mes
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Calcular el último día del mes
    last_day = calendar.monthrange(now.year, now.month)[1]  # Obtiene el último día del mes
    end_of_month = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    roleAuditar = ['S', 'C',  'AU', 'Admin']
    
    if request.user.role in roleAuditar:
        all = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        active = Supp.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
        process = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).filter(Q(status_color=2) | Q(status_color=1)).count()
        cancell = Supp.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month,is_active = True).count()
    elif request.user.role == 'A':
        all = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        active = Supp.objects.filter(status_color=3,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()
        process = Supp.objects.filter(created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).filter(Q(status_color=2) | Q(status_color=1)).count()
        cancell = Supp.objects.filter(status_color=4,created_at__gte=start_of_month,created_at__lte=end_of_month).filter(agent = request.user.id, is_active = True ).count()


    dicts = {
        'all':all,
        'active':active,
        'process':process,
        'cancell':cancell
    }
    return dicts

def chartSaleIndex(request):
    # Obtener la fecha y hora actual
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Calcular inicio y fin del mes actual
    start_of_month = timezone.make_aware(datetime(current_year, current_month, 1), timezone.get_current_timezone())
    last_day_of_month = calendar.monthrange(current_year, current_month)[1]
    end_of_month = timezone.make_aware(
        datetime(current_year, current_month, last_day_of_month, 23, 59, 59), 
        timezone.get_current_timezone()
    )

    # Roles con acceso ampliado
    roleAuditar = ['S', 'Admin']

    # Construcción de la consulta basada en el rol del usuario
    if request.user.role in roleAuditar:
        # Para roles con acceso ampliado: consultar datos de todos los usuarios
        users_data = User.objects.annotate(
            obamacare_count=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__status_color=3,
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month
            ), distinct=True),
            obamacare_count_total=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month
            ), distinct=True),
            supp_count=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__status_color=3,
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month
            ), distinct=True), 0),
            supp_count_total=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month
            ), distinct=True), 0)
        ).values('username', 'obamacare_count', 'obamacare_count_total', 'supp_count', 'supp_count_total')

    elif request.user.role not in roleAuditar:
        # Para usuarios con rol 'A': consultar datos solo para el usuario actual
        users_data = User.objects.filter(id=request.user.id).annotate(
            obamacare_count=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__status_color=3,
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month,
                agent_sale_aca__agent=request.user.id,
                agent_sale_aca__is_active=True
            ), distinct=True),
            obamacare_count_total=Count('agent_sale_aca', filter=Q(
                agent_sale_aca__created_at__gte=start_of_month,
                agent_sale_aca__created_at__lt=end_of_month,
                agent_sale_aca__agent=request.user.id,
                agent_sale_aca__is_active=True
            ), distinct=True),
            supp_count=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__status_color=3,
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month,
                agent_sale_supp__agent=request.user.id,
                agent_sale_supp__is_active=True
            ), distinct=True), 0),
            supp_count_total=Coalesce(Count('agent_sale_supp', filter=Q(
                agent_sale_supp__created_at__gte=start_of_month,
                agent_sale_supp__created_at__lt=end_of_month,
                agent_sale_supp__agent=request.user.id,
                agent_sale_supp__is_active=True
            ), distinct=True), 0)
        ).values('username', 'obamacare_count', 'obamacare_count_total', 'supp_count', 'supp_count_total')

    # Convertir los datos a una lista de diccionarios para su uso
    combined_data = [
        {
            'username': user['username'],
            'obamacare_count': user['obamacare_count'],
            'obamacare_count_total': user['obamacare_count_total'],
            'supp_count': user['supp_count'],
            'supp_count_total': user['supp_count_total'],
        }
        for user in users_data
    ]

    return combined_data

def tableStatusObama(request):

    # Obtener la fecha y hora actual
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Obtener el primer y último día del mes actual (con zona horaria)
    start_of_month = timezone.make_aware(datetime(current_year, current_month, 1), timezone.get_current_timezone())
    end_of_month = timezone.make_aware(datetime(current_year, current_month + 1, 1), timezone.get_current_timezone()) if current_month < 12 else timezone.make_aware(datetime(current_year + 1, 1, 1), timezone.get_current_timezone())

    roleAuditar = ['S', 'C', 'AU', 'Admin']

    # Construcción de la consulta basada en el rol del usuario
    if request.user.role in roleAuditar:

        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = ObamaCare.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month).values('profiling').annotate(count=Count('profiling')).order_by('profiling')
    
    elif request.user.role == 'A':
        
        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = ObamaCare.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month).values('profiling').filter(agent=request.user.id).annotate(count=Count('profiling')).order_by('profiling')
    

    return result

def tableStatusSupp(request):

    # Obtener la fecha y hora actual
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    # Obtener el primer y último día del mes actual (con zona horaria)
    start_of_month = timezone.make_aware(datetime(current_year, current_month, 1), timezone.get_current_timezone())
    end_of_month = timezone.make_aware(datetime(current_year, current_month + 1, 1), timezone.get_current_timezone()) if current_month < 12 else timezone.make_aware(datetime(current_year + 1, 1, 1), timezone.get_current_timezone())

    # Roles con acceso ampliado
    roleAuditar = ['S', 'C', 'AU', 'Admin']

    # Construcción de la consulta basada en el rol del usuario
    if request.user.role in roleAuditar:
        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = Supp.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month,).values('status').annotate(count=Count('status')).order_by('status')

    elif request.user.role == 'A':

        # Realizamos la consulta y agrupamos por el campo 'profiling'
        result = Supp.objects.filter(created_at__gte=start_of_month, created_at__lt=end_of_month,).values('status').filter(agent=request.user.id).annotate(count=Count('status')).order_by('status')


    return result

@login_required(login_url='/login') 
def sale(request): 

    # Obtener los parámetros de fecha del request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Llamar a la función que procesa los datos de ventas y obtiene la información agrupada
    saleACA = saleObamaAgent(start_date, end_date)
    saleACAUsa = saleObamaAgentUsa(start_date, end_date)
    saleSupp = saleSuppAgent(start_date, end_date)
    saleSuppUsa = saleSuppAgentUsa(start_date, end_date)
    sales_data, total_status_color_1_obama, total_status_color_3_obama, total_status_color_1_supp, total_status_color_3_supp, total_sales = salesBonusAgent(start_date, end_date)

    # Calcular los totales por agente antes de pasar los datos a la plantilla
    for agent, data in sales_data.items():
        data['total'] = data['status_color_1_obama'] + data['status_color_3_obama'] + data['status_color_1_supp'] + data['status_color_3_supp']

    context = {
        'saleACA': saleACA,
        'saleACAUsa': saleACAUsa,
        'saleSupp': saleSupp,
        'saleSuppUsa': saleSuppUsa,
        'sales_data': sales_data,
        'total_status_color_1_obama': total_status_color_1_obama,
        'total_status_color_3_obama': total_status_color_3_obama,
        'total_status_color_1_supp': total_status_color_1_supp,
        'total_status_color_3_supp': total_status_color_3_supp,
        'total_sales': total_sales
    }

    return render (request, 'table/sale.html', context)

def saleObamaAgent(start_date=None, end_date=None):
    # Definir la consulta base para Supp, utilizando `select_related` para obtener el nombre del agente (User)
    sales_query = ObamaCare.objects.select_related('agent') \
        .values('agent__username', 'status_color') \
        .annotate(total_sales=Count('id')) \
        .order_by('agent', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_name = entry['agent__username']  # Ahora tenemos el nombre del agente
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_name not in agents_sales:
            agents_sales[agent_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[agent_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[agent_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[agent_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[agent_name]['status_color_4'] = total_sales

        agents_sales[agent_name]['total_sales'] += total_sales

    return agents_sales

def saleObamaAgentUsa(start_date=None, end_date=None):
    # Definir la consulta base para Supp, utilizando `values` para obtener el nombre del agente (agent_usa)
    sales_query = ObamaCare.objects.values('agent_usa', 'status_color') \
        .annotate(total_sales=Count('id')) \
        .order_by('agent_usa', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_name = entry['agent_usa']  # Ahora tenemos el nombre del agente usando el campo `agent_usa`
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_name not in agents_sales:
            agents_sales[agent_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[agent_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[agent_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[agent_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[agent_name]['status_color_4'] = total_sales

        agents_sales[agent_name]['total_sales'] += total_sales

    return agents_sales

def saleSuppAgent(start_date=None, end_date=None):
    # Definir la consulta base para Supp, utilizando `select_related` para obtener el nombre del agente (User)
    sales_query = Supp.objects.select_related('agent') \
        .values('agent__username', 'status_color') \
        .annotate(total_sales=Count('id')) \
        .order_by('agent', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_name = entry['agent__username']  # Ahora tenemos el nombre del agente
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_name not in agents_sales:
            agents_sales[agent_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[agent_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[agent_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[agent_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[agent_name]['status_color_4'] = total_sales

        agents_sales[agent_name]['total_sales'] += total_sales

    return agents_sales

def saleSuppAgentUsa(start_date=None, end_date=None):
    # Definir la consulta base para Supp, utilizando `values` para obtener el nombre del agente (agent_usa)
    sales_query = Supp.objects.values('agent_usa', 'status_color') \
        .annotate(total_sales=Count('id')) \
        .order_by('agent_usa', 'status_color')

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query = sales_query.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query = sales_query.filter(created_at__range=[start_date, end_date])

    # Crear un diccionario para almacenar los resultados por agente y status color
    agents_sales = {}
    status_colors = [1, 2, 3, 4]

    # Procesar los resultados y organizar los totales por agente
    for entry in sales_query:
        agent_name = entry['agent_usa']  # Ahora tenemos el nombre del agente usando el campo `agent_usa`
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_name not in agents_sales:
            agents_sales[agent_name] = {'status_color_1': 0, 'status_color_2': 0, 'status_color_3': 0, 'status_color_4': 0, 'total_sales': 0}

        if status_color == 1:
            agents_sales[agent_name]['status_color_1'] = total_sales
        elif status_color == 2:
            agents_sales[agent_name]['status_color_2'] = total_sales
        elif status_color == 3:
            agents_sales[agent_name]['status_color_3'] = total_sales
        elif status_color == 4:
            agents_sales[agent_name]['status_color_4'] = total_sales

        agents_sales[agent_name]['total_sales'] += total_sales

    return agents_sales

def salesBonusAgent(start_date=None, end_date=None):
    # Consulta para Supp
    sales_query_supp = Supp.objects.select_related('agent') \
        .values('agent__username', 'status_color') \
        .annotate(total_sales=Count('id'))

    # Consulta para ObamaCare
    sales_query_obamacare = ObamaCare.objects.select_related('agent') \
        .values('agent__username', 'status_color') \
        .annotate(total_sales=Count('id'))

    # Si no se proporcionan fechas, filtrar por el mes actual
    if not start_date and not end_date:
        today = timezone.now()
        first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            last_day_of_month = today.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month + 1) - timezone.timedelta(seconds=1))

        sales_query_supp = sales_query_supp.filter(created_at__range=[first_day_of_month, last_day_of_month])
        sales_query_obamacare = sales_query_obamacare.filter(created_at__range=[first_day_of_month, last_day_of_month])

    # Si se proporcionan fechas, filtrar por el rango de fechas
    elif start_date and end_date:
        start_date = timezone.make_aware(
            datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        )
        end_date = timezone.make_aware(
            datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        )

        sales_query_supp = sales_query_supp.filter(created_at__range=[start_date, end_date])
        sales_query_obamacare = sales_query_obamacare.filter(created_at__range=[start_date, end_date])

    # Diccionario para almacenar las ventas por agente
    sales_data = {}

    # Procesar los resultados de Supp
    for entry in sales_query_supp:
        agent_name = entry['agent__username']
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_name not in sales_data:
            sales_data[agent_name] = {
                'status_color_1_obama': 0,
                'status_color_3_obama': 0,
                'status_color_1_supp': 0,
                'status_color_3_supp': 0,
                'total_sales': 0
            }

        # Sumar las ventas solo por status_color_1 y status_color_3 en Supp
        if status_color == 1:
            sales_data[agent_name]['status_color_1_supp'] += total_sales
        elif status_color == 3:
            sales_data[agent_name]['status_color_3_supp'] += total_sales

    # Procesar los resultados de ObamaCare
    for entry in sales_query_obamacare:
        agent_name = entry['agent__username']
        status_color = entry['status_color']
        total_sales = entry['total_sales']

        if agent_name not in sales_data:
            sales_data[agent_name] = {
                'status_color_1_obama': 0,
                'status_color_3_obama': 0,
                'status_color_1_supp': 0,
                'status_color_3_supp': 0,
                'total_sales': 0
            }

        # Sumar las ventas solo por status_color_1 y status_color_3 en ObamaCare
        if status_color == 1:
            sales_data[agent_name]['status_color_1_obama'] += total_sales
        elif status_color == 3:
            sales_data[agent_name]['status_color_3_obama'] += total_sales

    # Sumar los totales generales solo para status_color_1 y status_color_3
    total_status_color_1_obama = sum([data['status_color_1_obama'] for data in sales_data.values()])
    total_status_color_3_obama = sum([data['status_color_3_obama'] for data in sales_data.values()])
    total_status_color_1_supp = sum([data['status_color_1_supp'] for data in sales_data.values()])
    total_status_color_3_supp = sum([data['status_color_3_supp'] for data in sales_data.values()])
    
    # Total general de las sumas de status_color_1 y status_color_3
    total_sales = total_status_color_1_obama + total_status_color_3_obama + total_status_color_1_supp + total_status_color_3_supp

    return sales_data, total_status_color_1_obama, total_status_color_3_obama, total_status_color_1_supp, total_status_color_3_supp, total_sales                                                                            

@login_required(login_url='/login')   
def liveViewWeekly(request):
    
    userRole = [ 'A' , 'C']
    users = User.objects.filter(role__in = userRole)
    context = {
        'users':users,
        'weeklySales': getSalesForWekkly()
    }
    return render(request, 'dashboard/liveView.html', context)

def getSalesForWekkly():

    # Inicializamos un diccionario por defecto para contar las instancias
    user_counts = defaultdict(lambda: {
        'lunes': {'obama': 0, 'supp': 0},
        'martes': {'obama': 0, 'supp': 0},
        'miercoles': {'obama': 0, 'supp': 0},
        'jueves': {'obama': 0, 'supp': 0},
        'viernes': {'obama': 0, 'supp': 0},
        'sabado': {'obama': 0, 'supp': 0}
    })

    # Mapeo de números a días de la semana
    dias_de_la_semana = {
        0: 'lunes',
        1: 'martes',
        2: 'miercoles',
        3: 'jueves',
        4: 'viernes',
        5: 'sabado'
    }

    # Contamos cuántos registros de ObamaCare tiene cada usuario por día
    userRole = [ 'A' , 'C']
    obama_counts = ObamaCare.objects.values('agent', 'created_at').filter(agent__role__in=userRole).annotate(obama_count=Count('id'))
    for obama in obama_counts:
        # Obtener el día de la semana (0=lunes, 1=martes, ..., 6=domingo)
        dia_semana = obama['created_at'].weekday()
        if dia_semana < 6:  # Excluimos el domingo
            dia = dias_de_la_semana[dia_semana]
            user_counts[obama['agent']][dia]['obama'] += obama['obama_count']

    # Contamos cuántos registros de Supp tiene cada usuario por día
    supp_counts = Supp.objects.values('agent', 'created_at').filter(agent__role__in=userRole).annotate(supp_count=Count('id'))
    for supp in supp_counts:
        # Obtener el día de la semana (0=lunes, 1=martes, ..., 6=domingo)
        dia_semana = supp['created_at'].weekday()
        if dia_semana < 6:  # Excluimos el domingo
            dia = dias_de_la_semana[dia_semana]
            user_counts[supp['agent']][dia]['supp'] += supp['supp_count']

    # Aseguramos que todos los usuarios estén en el diccionario, incluso si no tienen registros    
    for user in User.objects.filter(role__in = userRole):
        if user.id not in user_counts:
            user_counts[user.id] = {
                'lunes': {'obama': 0, 'supp': 0},
                'martes': {'obama': 0, 'supp': 0},
                'miercoles': {'obama': 0, 'supp': 0},
                'jueves': {'obama': 0, 'supp': 0},
                'viernes': {'obama': 0, 'supp': 0},
                'sabado': {'obama': 0, 'supp': 0}
            }

    # Convertimos los identificadores de usuario a nombres (si necesitas los nombres de los usuarios)
    user_names = {user.id: user.username for user in User.objects.all()}

    # Crear un diccionario con los nombres de los usuarios y los conteos por día
    final_counts = {user_names[user_id]: counts for user_id, counts in user_counts.items()}

    return final_counts

#Websocket
def notify_websocket(user_id):
    """
    Función que notifica al WebSocket de un cambio, llamando a un consumidor específico.
    """
    channel_layer = get_channel_layer()

    # Llamamos al WebSocket para notificar al usuario que su plan fue agregado
    async_to_sync(channel_layer.group_send)(
        "user_updates",  # El nombre del grupo de WebSocket
        {
            "type": "user_update",  # Tipo de mensaje que enviamos
            "user_id": user_id,  # ID del usuario al que notificamos
            "message": "Nuevo plan agregado"
        }
    )

def generar_reporte(request):
    form = ReporteSeleccionForm(request.GET)
    reporte_datos = None
           
    return render(request, 'generar_reporte.html', {'form': form, 'reporte_datos': reporte_datos})





