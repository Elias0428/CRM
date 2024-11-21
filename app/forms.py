from django import forms
from app.models import *


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        exclude = ['agent']

class ObamaForm(forms.ModelForm):
    class Meta:
        model = ObamaCare
        fields = '__all__'
        exclude = ['client','profiling_agent','profiling','profiling_date','ffm','required_bearing','date_bearing','status','npm','date_effective_coverage','date_effective_coverage_end','img']

class SuppForm(forms.ModelForm):
    class Meta:
        model = Supp
        fields = '__all__'
        exclude = ['client','status','date_effective_coverage','date_effective_coverage_end','payment_type']

class DepentForm(forms.ModelForm):
    class Meta:
        model = Dependent
        fields = '__all__'
        exclude = ['client']

class ClientAlertForm(forms.ModelForm):
    class Meta:
        model = ClientAlert
        fields = '__all__'
        exclude = ['agent']