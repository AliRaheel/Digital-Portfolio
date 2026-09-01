import os
import smtplib
import threading
import requests
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from flask import Flask, render_template, request, send_from_directory
from data_manager import log_contact_message, LOG_FILE


load_dotenv()

app = Flask(__name__)

# --- EMAIL CONFIGURATION ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get('MY_PASSWORD')
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN") # e.g., sandbox123.mailgun.org


def email_worker_task(downloader_name, downloader_email, trigger_type):
    """
   Sends email alerts and attaches the local contact_messages.csv log database
   using Mailgun's HTTPS Web API over port 443 to bypass cloud firewall blocks.
   """
    try:
        url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        auth = ("api", MAILGUN_API_KEY)

        data = {
            "from": f"Portfolio Web Engine <postmaster@{MAILGUN_DOMAIN}>",
            "to": [MY_EMAIL],
            "subject": f"🚨 {trigger_type} Alert: {downloader_name}",
            "text": (
                f"Hello Raheel,\n\n"
                f"Your portfolio dashboard recorded a transaction:\n\n"
                f"📁 Type: {trigger_type}\n"
                f"👤 Name: {downloader_name}\n"
                f"📧 Email: {downloader_email}\n\n"
                f"Best regards,\nYour Python Web Engine App 🤖"
            )
        }

        # THE ATTACHMENT FIX: Read the local CSV file directly into Mailgun's files tuple parameter
        files = {}
        # Make sure your data_manager path is accessible (usually 'contact_messages.csv')
        log_file_path = "contact_messages.csv"

        if os.path.isfile(log_file_path):
            # Open the tracking file in raw binary ('rb') mode
            files = {"attachment": (os.path.basename(log_file_path), open(log_file_path, "rb"))}
            print("📎 Local log backup file payload mounted onto Mailgun HTTP form-data.")

        # 🚀 BYPASSES FIREWALLS: Standard HTTPS POST request over web port 443
        response = requests.post(url, auth=auth, data=data, files=files, timeout=15)

        # Cleanly close the file handler stream right after the transmission maps out
        if files:
            files["attachment"].close()

        if response.status_code == 200:
            print("✉️ Mailgun API successfully delivered the email alert with the CSV attachment!")
        else:
            print(f"⚠️ Mailgun API rejected delivery request: {response.text}")

    except Exception as e:
        print(f"❌ Background Web API pipeline error: {e}")


def send_notification_email(downloader_name, downloader_email, trigger_type="CV Download"):
    """Spawns an independent non-blocking thread to offload network delivery from the route."""
    try:
        # Spawn the parallel thread to execute the Mailgun HTTP Web request
        email_thread = threading.Thread(
            target=email_worker_task,
            args=(downloader_name, downloader_email, trigger_type)
        )
        email_thread.daemon = True
        email_thread.start()

        print("🚀 Background Mailgun thread spawned successfully. Returning control to route instantly.")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize background email pipeline: {e}")
        return False

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/experience')
def experience():
    return render_template('experience.html')


@app.route('/statement')
def statement():
    return render_template('statement.html')


@app.route('/download-cv', methods=['GET', 'POST'])
def download_cv():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')

        # Append the downloader transaction details to the local system tracker
        log_contact_message(name, email, "Triggered direct download of curriculum vitae PDF.")

        # Fires the non-blocking background threading alert module
        # This handshakes with port 465 silently without delaying the user!
        send_notification_email(name, email, trigger_type="CV Download Tracking")

        # Serve the file block back to the recruiter's browser instantly
        return send_from_directory(directory='static', path='Raheel_Ali_CV.pdf', as_attachment=True)

    return render_template('download_cv.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message_sent = False
    if request.method == 'POST':
        visitor_name = request.form.get('name')
        visitor_email = request.form.get('email')
        visitor_message = request.form.get('message')

        # Store the user parameters inside the local CSV spreadsheet row
        log_success = log_contact_message(visitor_name, visitor_email, visitor_message)

        # Fire the background email alert module
        send_notification_email(visitor_name, visitor_email, trigger_type="New Website Contact Message")

        # show the success banner if the local Database write succeede!
        if log_success:
            message_sent = True

    return render_template('contact.html', message_sent=message_sent)

if __name__ == '__main__':
    app.run(debug=True)
