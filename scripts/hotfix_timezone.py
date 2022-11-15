import os
import sys
import django
from datetime import datetime, timedelta, timezone

# script upload all participants to spreadsheet
# use linux cron to run this script

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TicketApp.settings")
    django.setup()

    from ticket.models import Participant
    from django.conf import settings

    participants = Participant.objects.all()

    for participant in participants:
        participant.date += timedelta(hours=7)
        participant.save()