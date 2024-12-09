from ..models import ClientAlert  # Ajusta esto al modelo que estés utilizando para las alertas
from datetime import date

def alert_count(request):

    #(ALERT) Obtener las alertas vencidas (fechas menores o iguales a la fecha actual)
    expiredAlerts = ClientAlert.objects.filter(datetime__lte=date.today(), is_active=True)

    # Contar las alertas
    alertCount = expiredAlerts.count()

    return {'expiredAlerts': expiredAlerts, 'alertCount': alertCount}
