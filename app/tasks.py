import telnyx

from celery import shared_task
from datetime import datetime
from celery.utils.log import get_task_logger

from app.models import Client
from app.views import getCompanyPerAgent
from django.conf import settings



logger = get_task_logger(__name__)

@shared_task
def my_daily_task():
    now = datetime.now().date()

    # Filtramos los clientes que cumplen años hoy, ignorando el año
    birthdayClients = Client.objects.filter(
        date_birth__month=now.month,
        date_birth__day=now.day,
        is_active=True
    )

    for client in birthdayClients:
        lines = client.agent_usa.split("\n")
        agentFirstName = lines[0].split()[0] 

        telnyx.api_key = settings.TELNYX_API_KEY
        telnyx.Message.create(
            from_=f"+17869848406", # Your Telnyx number
            to=f'+{client.phone_number}',
            text= f'¡Feliz cumpleaños, {client.first_name} {client.last_name}! 🎉 De parte de todo el equipo de {getCompanyPerAgent(agentFirstName)}, le deseamos un año lleno de salud y bienestar. Recuerde que su agente de seguros, {client.agent_usa}, está siempre a su disposición para cualquier duda o apoyo con su póliza. ¡Que tenga un excelente día!'
        )

        # Log para verificar el envío
        logger.info(f"Mensaje enviado al numero {client.phone_number} - {client.first_name} {client.last_name}")