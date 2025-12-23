from django.utils import timezone
from django.conf import settings

from engine.models import Gara


def get_gare():
    gare = Gara.objects.filter(inizio__isnull=False).order_by("-inizio", "-id")
    loraesatta = timezone.now()
    attive = []
    archivio = []
    for g in gare:
        if g.sospensione is not None:
            attive.append(g)
        elif g.get_ora_fine() < loraesatta:
            archivio.append(g)
        else:
            attive.append(g)
    da_iniziare = Gara.objects.filter(inizio__isnull=True).order_by("-id")
    return attive, archivio, da_iniziare


def gare(request):
    attive, archivio, da_iniziare = get_gare()
    return {
        "gare_attive": attive,
        "gare_archivio": archivio,
        "gare_da_iniziare": da_iniziare
    }


def export_settings(request):
    data = {
        "registration_open": settings.REGISTRATION_OPEN
    }
    return data
