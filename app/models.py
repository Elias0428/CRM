from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):

    ROLES_CHOICES = (
        ('A', 'Agent'),
        ('S', 'Supervisor'),
        ('C', 'Customer'),
        ('SUPP', 'Supplementary'),
        ('AU', 'Auditor'),
        ('TV', 'Tv'),
        ('Admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    
    class Meta:
        db_table = 'users'
        
    def _str_(self):
        return self.username

class Client(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    agent_usa = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField()
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)    
    address = models.CharField(max_length=255)
    zipcode = models.IntegerField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    county = models.CharField(max_length=100)
    sex = models.CharField(max_length=1)
    old = models.IntegerField()    
    date_birth = models.DateField()
    migration_status = models.CharField(max_length=100)
    type_sales = models.CharField(max_length=100)    
    is_active = models.BooleanField(default=True)  
    apply = models.BooleanField()

    class Meta:
        db_table = 'clients'

class Call(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_agent = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    create_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'calls'

class Typification(models.Model):
    id_call = models.ForeignKey(Call, on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'typifications'

class ObamaCare(models.Model):
    profiling_agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiling_agent_aca' ,null=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE,related_name='agent_sale_aca')
    client = models.OneToOneField(Client, on_delete=models.CASCADE,null=True)
    agent_usa = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)  
    taxes = models.IntegerField()
    plan_name = models.CharField(max_length=200)
    carrier = models.CharField(max_length=200)
    profiling = models.CharField(max_length=200,default='NO')
    profiling_date = models.DateField(null=True)
    subsidy = models.BigIntegerField()
    ffm = models.BigIntegerField(null=True)
    required_bearing = models.BooleanField(default=False,null=True)
    date_bearing = models.DateField(null=True)
    doc_income = models.BooleanField(default=False,null=True)
    doc_migration = models.BooleanField(default=False,null=True)
    status = models.CharField(max_length=50,null=True)
    status_color = models.IntegerField(null = True)
    work = models.CharField(max_length=50)
    npm = models.BigIntegerField(null=True)
    img = models.FileField(null=True)
    date_effective_coverage = models.DateField(null=True)
    date_effective_coverage_end = models.DateField(null=True)
    observation = models.TextField(null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'obamacare'

class Dependent(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    obamacare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE, null=True)  # Relación de muchos a uno
    name = models.CharField(max_length=200)
    apply = models.CharField(max_length=200)
    sex = models.CharField(max_length=1)
    kinship = models.CharField(max_length=100,null=True)
    date_birth = models.DateField(null=True)
    migration_status = models.CharField(max_length=50)
    type_police = models.TextField()

    class Meta:
        db_table = 'dependents'

class Supp(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_sale_supp')
    dependent = models.ForeignKey(Dependent, on_delete=models.CASCADE, null=True)
    agent_usa = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)  
    effective_date = models.DateField()
    company = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=100)
    premium = models.DecimalField(max_digits=10, decimal_places=2,)
    preventive = models.CharField(max_length=100)
    coverage = models.IntegerField()
    deducible = models.IntegerField()
    status = models.CharField(max_length=50,null=True)
    status_color = models.IntegerField(null = True)
    date_effective_coverage = models.DateField(null=True)
    date_effective_coverage_end = models.DateField(null=True)
    payment_type = models.CharField(max_length=50,null=True)
    observation = models.TextField(null=True)
    is_active = models.BooleanField(default=True)

    dependents = models.ManyToManyField(Dependent, related_name='SuppDependents')

    class Meta:
        db_table = 'supp'

class ObservationAgent(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_obamaCare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE, null=True, blank=True)
    id_supp = models.ForeignKey(Supp, on_delete=models.CASCADE, null=True, blank=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = 'observations_agents'

class ObservationCustomer(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)  
    type_police = models.CharField(max_length=20) 
    typeCall = models.CharField(max_length=20)   
    id_plan = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True) 
    typification = models.TextField()
    content = models.TextField()
    is_active = models.BooleanField(default=True) 

    class Meta:
        db_table = 'observations_customers'

class CustomerTracking(models.Model):
    id_obama = models.ForeignKey(ObamaCare, on_delete=models.CASCADE, null=True)
    id_supp = models.ForeignKey(Supp, on_delete=models.CASCADE, null=True)
    cs4h = models.BooleanField(default=False)
    cs8d = models.BooleanField(default=False)
    cs3w = models.BooleanField(default=False)
    cs5w = models.BooleanField(default=False)
    activo = models.BooleanField(default=False)
    gossip = models.BooleanField(default=False)

    class Meta:
        db_table = 'customer_tracking'

class Log(models.Model):
    id_agent = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=255)

    class Meta:
        db_table = 'logs'

class Motivation(models.Model):
    content = models.TextField()

    class Meta:
        db_table = 'motivation'

class ClientAlert(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    name_client = models.CharField(max_length=255)
    phone_number = models.BigIntegerField()
    datetime = models.DateField()
    content = models.TextField()
    is_active = models.BooleanField(default=True)  

    class Meta:
        db_table = 'client_alert'

class DropDownList(models.Model):
    profiling_obama = models.CharField(max_length=255,null=True)
    profiling_supp = models.CharField(max_length=255,null=True)

    class Meta:
        db_table = 'drop_down_list'

class ExcelFileMetadata(models.Model):
    file_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ExcelFileMetadata'


class BdExcel(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255,null=True)
    phone = models.BigIntegerField()
    address = models.CharField(max_length=255,null=True)
    city = models.CharField(max_length=200,null=True)
    state = models.CharField(max_length=200,null=True)
    zipCode = models.IntegerField(null=True)
    agent_id = models.IntegerField(null=True)
    excel_metadata = models.ForeignKey('ExcelFileMetadata',on_delete=models.CASCADE,related_name='records')


    class Meta:
        db_table = 'bd_excel'


class ControlQuality(models.Model):
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE, related_name='created_controls' )
    agent = models.ForeignKey(User,on_delete=models.CASCADE, related_name='assigned_controls')
    category = models.CharField(max_length=200, null=True)
    amount = models.BigIntegerField(null= True)
    date = models.DateField()
    findings = models.TextField(null= True)
    observation = models.TextField(null= True)
    is_active = models.BooleanField(default=True)  

    class Meta:
        db_table = 'ControlQuality'


class ControlCall(models.Model):
    agent_create = models.ForeignKey(User,on_delete=models.CASCADE, related_name='created_controls_call' )
    agent = models.ForeignKey(User,on_delete=models.CASCADE, related_name='assigned_controls_call',)
    daily = models.BigIntegerField()
    answered = models.BigIntegerField()
    mins = models.BigIntegerField()
    date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ControlCall'
     


