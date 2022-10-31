import io
import os
import secrets
from django.conf import settings
import gspread
import pyqrcode
from PIL import Image, ImageDraw, ImageFont

from ticket.models import Participant

def generate_qrcode():
    while True:
        qrcode = secrets.token_urlsafe(16)
        qrcode_exist = Participant.objects.filter(qrcode = qrcode).exists()
        if qrcode_exist == False:
            return qrcode

# Generate QR Code
def generate_ticket(sFullCode, sFullName, sWorkshopID,ticket_template_path) :
    #Review Gsheet "List of registered user":
        # FullCode i sutilized to generate QRCode.
    bytes_qrcode = make_qr_code(sFullCode) # generate <sShortCode>.png in DEFAULT_IMAGE_PATH
    iTicketNo = int(sWorkshopID)
    # Use workshop 3 for the ones who do not choose workshop.
    # Ticket Template without qr code img
    sFullPathOfTicket = os.path.join(settings.STATIC_ROOT, 'ticket/img/ticket_template.png')
    #Ticket Template with qr code img
    #bytes_img_with_qr =add_image(sFullPathOfTicket, bytes_qrcode) # add QRCode image to ticket image -> final image temp.png in DEFAULT_IMAGE_PATH
    bytes_img_with_qr =add_image(ticket_template_path, bytes_qrcode)
    bytes_ticket = add_text(bytes_img_with_qr, sFullName)  # add <sFullName> to image of Ticket_with_QRCode
    return bytes_ticket

def make_qr_code(sFullCode) : # return bytes type of qr code img
    #sShortCode is utilized to create file name
    #sFullCode is utilized to create QRCode
    #sQRCodeFile = DEFAULT_IMAGE_PATH + QRCode_image_name + '.png'
    qrcode = pyqrcode.create(sFullCode, encoding = 'utf-8')
    
    buffer = io.BytesIO()
    qrcode.png(buffer,scale=7) 
    buffer.seek(0)  
    bytes_qrcode = buffer.getvalue()
    return bytes_qrcode

def add_image(sFullPathTicket, bytes_qrcode) : # insert QRcode image to the ticket
    imgTicket = Image.open(sFullPathTicket)
    imgQR_code = Image.open(io.BytesIO(bytes_qrcode)).resize((518,518))# need to resize because size of QR Code image depend on length of Code.

    back_im = imgTicket.copy()
    back_im.paste(imgQR_code, (102, 222))

    #Return bytes type of img with qr code img added
    buffer = io.BytesIO()
    back_im.save(buffer, format='PNG', quality=95)
    bytes_img_with_qr = buffer.getvalue()
    return bytes_img_with_qr

def add_text(bytes_img_with_qr, sText):
    imgTicket = Image.open(io.BytesIO(bytes_img_with_qr))
    draw = ImageDraw.Draw(imgTicket)
    font = ImageFont.truetype(os.path.join(settings.STATIC_ROOT + '/ticket/font/JetBrainsMono-Bold.ttf'), 35)
    sName = sText

    # Get Left Align for sName: supposed that 32 characters/letters fit the width of the ticket.
    if len(sName) > 27:     # supposed that 27 words fit to the box
        arrNames = sName.split(" ")
        sName = arrNames[len(arrNames)-2] + ' ' + arrNames[len(arrNames)-1]
    nLeftAlign = (32 - len(sName))/2

    draw.text((nLeftAlign*22, 1100), sName,(255,255,255),font=font)
    buffer = io.BytesIO()
    imgTicket.save(buffer, format='PNG')
    return buffer.getvalue()

# Google API
# scope = [
#         'https://www.googleapis.com/auth/drive',
#         'https://www.googleapis.com/auth/drive.file'
#         ]
# def add_participant_to_google_sheet(user_info): 
#     # Connect to google service account 
#     gc = gspread.service_account_from_dict(settings.GOOGLE_JSON_KEY,scopes=scope)
#     # Get Spreadsheet
#     sheet = gc.open_by_key(settings.SPREADSHEET_ID)
#     participant_worksheet = sheet.worksheet('Participant')
#     #Create new participant rows
#     row_count = len(participant_worksheet.get_all_values())
#     field_list = participant_worksheet.row_values(1)
#     col = 1
#     # Check if participant exist in spread, update exist participant and return
#     qr_exist = participant_worksheet.find(in_column=6,query=user_info.get('QRCode'))
#     if qr_exist is not None:
#         for field in field_list:       
#             participant_worksheet.update_cell(qr_exist.row,col,str(user_info.get(field)))
#             col +=1
#         return
#     # Add new Participant to google sheet
#     for field in field_list:       
#         participant_worksheet.update_cell(row_count + 1,col,str(user_info.get(field)))
#         col +=1
