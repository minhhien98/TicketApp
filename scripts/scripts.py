import os
import sys
import django
import gspread
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


    item_list = []
    # get all participants data
    participants = Participant.objects.all()
    count = participants.count()
    for participant in participants:
        item_array = []
        item_array.append(participant.date.timestamp())
        item_array.append(participant.user_id.last_name + ' ' + participant.user_id.first_name)
        item_array.append(participant.user_id.userextend.birthdate.strftime("%d/%m/%Y"))
        item_array.append(participant.user_id.userextend.phone_number)
        item_array.append(participant.user_id.email)
        item_array.append(participant.qrcode)
        item_array.append(participant.workshop_id.id)
        item_array.append("N")
        item_array.append(participant.user_id.userextend.parish)
        item_array.append(participant.user_id.userextend.address)
        item_array.append(participant.quantity)
        item_list.append(item_array)

    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]
    gc = gspread.service_account_from_dict(settings.GOOGLE_JSON_KEY,scopes=scope)
    # Get Spreadsheet
    sheet = gc.open_by_key(settings.SPREADSHEET_ID)
    participant_worksheet = sheet.worksheet('Participant')
    participant_worksheet.update("A2:K"+str(count+1),item_list)