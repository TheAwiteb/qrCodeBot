import os
from time import sleep
import telebot
from config import TOKEN, VERSION
import qrcode
import cv2
import requests
from string import ascii_lowercase
from random import choice

bot = telebot.TeleBot(TOKEN)
bot_id = bot.get_me().id
bot_username = '@'+bot.get_me().username
bot_url = "https://t.me/"+bot.get_me().username

# Random name with 9 lowercase letters
random_name = lambda: ''.join(choice(ascii_lowercase) for i in range(9))

def make_qr_code(text:str):
    """ mkae QR code for text and saving image

    Args:
        text (str): text you want make QR code by.

    Returns:
        [str]: image name after saving.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_name = random_name()+'.jpeg'
    img.save(img_name,"JPEG")
    return img_name

def read_img(url):
    """ read image from url and Extract the content of the QR code

    Args:
        url (str): url of image

    Returns:
        str: content of the QR code
    """
    img_name = random_name()+'.jpeg'
    with open(img_name, 'wb') as f:
        f.write(requests.get(url).content)
    image = cv2.imread(img_name)
    detector = cv2.QRCodeDetector()
    data, vertices_array, binary_qrcode = detector.detectAndDecode(image)
    os.remove(img_name)
    if vertices_array is not None:
        return data
    else:
        return "لم يتم التعرف على QR code في الصورة"



def send_qr(chat_id:str, msg_id:str, img_name:str, photo:bool, text:str, caption="QR code for [ {} ]"):    
    """ send QR code for chat_id

    Args:
        chat_id (str): chat id to send for.
        msg_id (str): message id to reply for.
        img_name (str): QR code you want send for chat id.
        photo (bool): send QR code like photo if true else send like sticker.
        text (str): text of QR code.
        caption (str, optional): caption of message. Defaults to "QR code for [ {} ]".
    """
    with open(img_name, 'rb') as f:
        if photo:
            bot.send_photo(chat_id, f,caption.format(text if text else ''), msg_id)
        else:
            bot.send_sticker(chat_id, f,msg_id)
    os.remove(img_name)

@bot.message_handler(func=lambda msg: msg.text and msg.text.startswith('/'))
def command_handler(message):
    chat_id = message.chat.id
    msg_id = message.id
    text = message.text.lower()
    split_text = text.split()
    if text.startswith('/qr'):
        if len(split_text) >= 3:
            qr_text = ' '.join(split_text[2:])
            qr_type = split_text[1]
            if qr_type in ('p', 's'):
                qr_img_name = make_qr_code(text=qr_text)
                send_qr(chat_id=chat_id, msg_id=msg_id, img_name=qr_img_name,
                            text=qr_text, photo=qr_type== 'p')
            else:
                bot.reply_to(message,f"لايوجد نوع بهذا الاسم '{qr_type}' يمكنك استخدام p او s\nللتفاصيل:\n/help{bot_username}")
        else:
            example_command = f"""
            \rيوجد خطأ في تكوين الامر مثال صحيح للامر:
            \rلمعرفة طريقة الاستخدام ارسل /help{bot_username}
            """
            bot.reply_to(message, example_command)
    elif text.startswith('/help'):
        help_message = f"""
        \rاهلا,
        \rتوجد طريقتين لاستخدام البوت وهي ارسال ال qr كصورة او ارساله ك ستيكير
        \r/qr{bot_username} p|s النص هنا
        
        \rحيث يتم استخدام s لارساله ك ستيكير او استخدام p لارساله كصورة
        
        \rمثال:
        \r/qr{bot_username} p Hello World!
        """
        bot.reply_to(message, help_message)
    elif text.startswith('/start'):
        start_message = f"""
        \rاهلا,
        \rانا بوت استطيع تحويل النص او الرابط الذي ترسله لي الى QR Code
        \rيمكنك مشاركة البوت عبر QR Code الذي في الاعلى 
        \rلمعرفة طريقة الاستخدام ارسل /help{bot_username}
        \r الاصدار: {VERSION}
        """
        img_name = make_qr_code(bot_url)
        send_qr(chat_id, msg_id, img_name, True, None, start_message)

@bot.message_handler(func=lambda msg: msg.caption and msg.caption.startswith('/qr'), content_types=['photo'])
def photo_handler(message):
    photo_id = message.photo[-1].file_id
    file_url = bot.get_file_url(photo_id)
    text = read_img(file_url)
    bot.reply_to(message, text)

# Run bot
while True:
    print(f"Start {bot.get_me().first_name}")
    try:
        bot.polling(none_stop=True, interval=0, timeout=0)
    except Exception as err:
        print(err)
        sleep(10)