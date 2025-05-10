import telebot
import requests
import datetime
import gspread
import os
import speech_recognition as sr
from pydub import AudioSegment
from dotenv import load_dotenv


from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

BOT_TOKEN =os.environ.get("BOT_TOKEN")
SHEET_NAME = 'ScrapBack'
bot = telebot.TeleBot(BOT_TOKEN)

scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Apollo Lookup (Simulated)
def apollo_lookup(name):
    API_KEY = 'Qjcs3tTy-wLgjLhb14U8Zg'
    base_url = 'https://api.apollo.io/v1/people/match'

    params = {
        'api_key': API_KEY,
        'name': name
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if data.get('person'):
        person = data['person']
        return {
            'name': person.get('name', 'N/A'),
            'title': person.get('title', 'N/A'),
            'company': person.get('organization', {}).get('name', 'N/A'),
            'email': person.get('email', 'N/A'),
            'linkedin': person.get('linkedin_url', 'N/A')
        }
    else:
        return {
            'name': name,
            'title': 'Not Found',
            'company': 'Unknown',
            'email': 'Not Found',
            'linkedin': 'N/A'
        }





def extract_name(text):
    words = text.split()
    if "of" in words:
        idx = words.index("of")
        return ' '.join(words[idx + 1:])
    return text.strip()

def transcribe_voice(file_path):
    sound = AudioSegment.from_file(file_path)
    wav_path = file_path.replace(".ogg", ".wav")
    sound.export(wav_path, format="wav")
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    return r.recognize_google(audio, language="en-IN")

@bot.message_handler(content_types=['text', 'voice'])
def handle_message(message):
    try:
        if message.content_type == 'voice':
            file_info = bot.get_file(message.voice.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            ogg_file_path = f"voice_{message.chat.id}.ogg"
            with open(ogg_file_path, 'wb') as f:
                f.write(downloaded_file)

            user_input = transcribe_voice(ogg_file_path)
            os.remove(ogg_file_path)
        else:
            user_input = message.text

        name_to_lookup = extract_name(user_input)
        result = apollo_lookup(name_to_lookup)

        reply = f"👤 *{result['name']}*\n🏢 {result['title']} at {result['company']}\n📧 {result['email']}\n🔗 [LinkedIn]({result['linkedin']})"
        bot.reply_to(message, reply, parse_mode='Markdown')

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sheet.append_row([timestamp, user_input, result['name'], result['title'], result['company'], result['email'], result['linkedin']])
    
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

bot.polling()



