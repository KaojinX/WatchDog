import json
import os
import smtplib
import datetime
import schedule as SH
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
#Authentication HERE IS IMPORTANT FACTOR!
#Use this link\activate for yourself https://support.google.com/accounts/answer/185833?visit_id=638846722749099373-851972500&p=InvalidSecondFactor&rd=1
#Then use password generated from there here and it will work.

def SEND_MAIL(changed_files):
    
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    EMAIL_ADDRESS = 'mikolajsiwek@gmail.com' # PUT YOUR EMAIL ADRESS
    EMAIL_PASSWORD = 'owli iqpz tslt eqck'  # USE APLICATION PASSWORD
    RECIPIENT_EMAIL = 'mikolajsiwek@gmail.com' #HERE PUT YOUR EMAIL ADRESS TOO

    # Message creation
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "ALERT! Your File Changed"

    # Message itself
    changes = "\n".join([f"- {file}: {date}" for file, date in changed_files.items()])
    body = f"Hey, some of your files have changed:\n{changes}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Connection
    try:
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print("Mail sended succesfuly!")
        
    except Exception as e:
        print(f"Sending Error: {str(e)}")
        
    finally:
        if 'server' in locals():
            server.quit()
        


def job():
    json_path = os.path.join(os.path.dirname(__file__), 'ignored_files.json')
    if not os.path.exists(json_path):
        initial_files = ["ignored_files.json", "main.py"]
        with open(json_path, 'w') as f:
            json.dump({"files": initial_files, "checked_files": []}, f, indent=4)

    #localization of your folders to check
    folder_to_check = r"Put here full folder path to check"  
    files_to_check = os.listdir(folder_to_check)
    #print (files_to_check)
    try:
        with open (json_path, 'r', encoding='utf-8') as JsonFile:
            data = json.load(JsonFile)
        ignored_files = data['files']
        checked_files = data['checked_files']
           
    except json.JSONDecodeError:
        print("ERROR: JSON file is damaged. Creating new one...")
        data = {"files": [], "checked_files": []}
        ignored_files = []
        checked_files = []
    except KeyError:
        pass
        
        
    
    changed_files = {}
    if not checked_files:
        print ("First Launch.")
        for x in files_to_check:
            if os.path.basename(x) not in ignored_files:
                x_path = os.path.join(folder_to_check, x)
                mod_date = os.path.getmtime(x_path)
                checked_files[x] = datetime.datetime.fromtimestamp(mod_date).strftime("%y.%m.%d_%H:%M")
                with open (json_path, 'r', encoding='utf-8') as JsonFile:
                    data = json.load(JsonFile)
                data['checked_files'] = checked_files
                with open (json_path, 'w', encoding='utf-8') as JsonFile:
                    json.dump(data, JsonFile, indent=4)
    else:
        print ("Working...")
        with open (json_path, 'r', encoding='utf-8') as JsonFile:
            data = json.load(JsonFile)
            ToCheck = data.get('checked_files', {})
            
            
        for x in files_to_check:
            if os.path.basename(x) not in ignored_files:
                x_path = os.path.join(folder_to_check, x)
                mod_date = os.path.getmtime(x_path)
                checked_files[x] = datetime.datetime.fromtimestamp(mod_date).strftime("%y.%m.%d_%H:%M")
                
    for file, current_date in checked_files.items():
        if file not in ToCheck or ToCheck[file] != current_date:
            print(f"{file} not match (old date: {ToCheck.get(file)}, newdate: {current_date})")
            changed_files[file] = current_date

    if changed_files:
        print("Changed files:", changed_files)
        SEND_MAIL(changed_files)
    else:
        print("No file changed.")

    # Aktualizacja danych i zapis
    data['checked_files'] = checked_files
    with open(json_path, 'w', encoding='utf-8') as JsonFile:
        json.dump(data, JsonFile, indent=4)


SH.every(30).seconds.do(job)


while True:
    try:
        SH.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        print ("Stopped by hand.")
        exit()