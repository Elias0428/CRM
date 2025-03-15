from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from storages.backends.s3boto3 import S3Boto3Storage

# Create your models here.
class Companies(models.Model):
    owner = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50)
    remaining_balance = models.DecimalField(max_digits=20, decimal_places=6)
    user_role = models.CharField(max_length=50)
    company_email = models.EmailField()
    language_preference = models.CharField(max_length=2)
    telephones = models.IntegerField()
    notified_at_10 = models.BooleanField(default=False)
    notified_at_5 = models.BooleanField(default=False)
    notified_at_1 = models.BooleanField(default=False)
    
    class Meta:
        managed = False 
        db_table = 'app_companies'  

class Numbers(models.Model):
    phone_number = models.BigIntegerField()
    
    class Meta:
        managed = False 
        db_table = 'app_numbers'

class Users(models.Model):  # ✅ Ahora es un modelo normal
    ROLES_CHOICES = (
        ('A', 'Agent'),
        ('S', 'Supervisor'),
        ('Admin', 'Admin'),
    )

    username = models.CharField(max_length=150)  # Agregar manualmente
    assigned_phone = models.ForeignKey(Numbers, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLES_CHOICES)
    company = models.ForeignKey(Companies, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'app_users'

    def __str__(self):
        return self.username
    
    def formatted_phone_number(self):
        if self.assigned_phone and self.assigned_phone.phone_number:
            phone_str = str(self.assigned_phone.phone_number)
            formatted = f"+{phone_str[0]} ({phone_str[1:4]}) {phone_str[4:7]} {phone_str[7:]}"
            return formatted
        return None
    
class Clients(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)  # Relación con la compañía
    name = models.CharField(max_length=50, null=True)
    phone_number = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField()

    class Meta:
        unique_together = ('company', 'phone_number')  # Restricción de unicidad por compañía y número de teléfono
        managed = False 
        db_table = 'app_clients'

    def __str__(self):
        return f'{self.name} - {self.phone_number} ({self.company.company_name})'


class SecretKey(models.Model):
    client = models.OneToOneField(Clients, on_delete=models.CASCADE)
    secretKey = models.CharField(max_length=200)
    
    class Meta:
        managed = False 
        db_table = 'app_secretkey'

class TemporaryURL(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    token = models.TextField()  # Guardar el token firmado
    expiration = models.DateTimeField()
    is_active = models.BooleanField(default=True)  # Para invalidar manualmente
    
    class Meta:
        managed = False 
        db_table = 'app_temporaryurl'

    def is_expired(self):
        return timezone.now() > self.expiration

    def __str__(self):
        return f"Temporary URL for {self.client.name} (Active: {self.is_active})"

class Chat(models.Model):
    agent = models.ForeignKey(Users, on_delete=models.CASCADE)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)  # Nueva relación
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('client', 'company')  # Restringe a un solo chat por cliente y compañía
        managed = False 
        db_table = 'app_chat'

    def __str__(self):
        return f'{self.agent.username} - {self.client.phone_number} ({self.company.company_name})'

class Messages(models.Model):
    SENDER_TYPE_CHOICES = (
        ('A', 'Agent'),
        ('C', 'Client'),
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender_type = models.CharField(max_length=20, choices=SENDER_TYPE_CHOICES)
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    message_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        managed = False 
        db_table = 'app_messages'

class Files(models.Model):
    file = models.FileField(
        upload_to='files',
        storage=S3Boto3Storage()
    )
    message = models.OneToOneField(Messages, on_delete=models.CASCADE)
    
    class Meta:
        managed = False 
        db_table = 'app_files'