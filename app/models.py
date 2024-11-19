from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    
    class Meta:
        db_table = 'users'

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

    class Meta:
        db_table = 'clients'

class Dependent(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    apply = models.CharField(max_length=200)
    sex = models.CharField(max_length=1)
    kinship = models.CharField(max_length=100,null=True)
    date_birth = models.DateField(null=True)
    migration_status = models.CharField(max_length=50)
    type_police = models.CharField(max_length=50)

    class Meta:
        db_table = 'dependents'

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
    profiling_agent = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.OneToOneField(Client, on_delete=models.CASCADE,null=True)
    taxes = models.IntegerField()
    plan_name = models.CharField(max_length=200)
    carrier = models.CharField(max_length=200)
    profiling = models.CharField(max_length=200,null=True)
    profiling_date = models.DateField(null=True)
    subsidy = models.BigIntegerField()
    ffm = models.BigIntegerField(null=True)
    required_bearing = models.BooleanField(default=False,null=True)
    date_bearing = models.DateField(null=True)
    doc_icon = models.BooleanField(default=False,null=True)
    doc_migration = models.BooleanField(default=False,null=True)
    status = models.CharField(max_length=50)
    status_color = models.IntegerField(null = True)
    work = models.CharField(max_length=50)
    npm = models.BigIntegerField(null=True)
    img = models.FileField(null=True)
    date_effective_coverage = models.DateField(null=True)
    date_effective_coverage_end = models.DateField(null=True)
    apply = models.CharField(max_length=50)
    observation = models.TextField(null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'obamacare'

class Supp(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    profiling_agent = models.ForeignKey(User, on_delete=models.CASCADE)    
    effective_date = models.DateField()
    company = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=100)
    premium = models.DecimalField(max_digits=10, decimal_places=2,)
    preventive = models.CharField(max_length=100)
    coverage = models.IntegerField()
    deducible = models.IntegerField()
    status = models.CharField(max_length=50,null=True)
    date_effective_coverage = models.DateField(null=True)
    date_effective_coverage_end = models.DateField(null=True)
    payment_type = models.CharField(max_length=50,null=True)
    observation = models.TextField(null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'supp'

class ObservationAgent(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    id_obamaCare = models.ForeignKey(ObamaCare, on_delete=models.CASCADE)
    id_supp = models.ForeignKey(Supp, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = 'observations_agents'

class ObservationCustomer(models.Model):
    id_client = models.ForeignKey(Client, on_delete=models.CASCADE)
    content = models.TextField()

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
