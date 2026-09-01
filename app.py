import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
# from email.message import EmailMessage
from flask import Flask, render_template, request, send_from_directory
from data_manager import log_contact_message, LOG_FILE


load_dotenv()

app = Flask(__name__)

# --- EMAIL CONFIGURATION ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
MY_EMAIL = os.environ.get('MY_EMAIL')
MY_PASSWORD = os.environ.get('MY_PASSWORD')


def send_notification_email(downloader_name, downloader_email, trigger_type="CV Download"):
    """
    Dispatches a system alert with contact_messages.csv attached,
    utilizing your original, proven connection.sendmail() logic.
    """
    try:
        # Create a Multipart Container to hold text and your attachment together
        msg = MIMEMultipart()
        msg["Subject"] = f"Website Alert: {trigger_type}!"
        msg["From"] = MY_EMAIL
        msg["To"] = MY_EMAIL

        # Define the body message text
        body_content = (
            f"Hello Raheel,\n\n"
            f"Your portfolio portal recorded a new interaction:\n\n"
            f"Type: {trigger_type}\n"
            f"Name: {downloader_name}\n"
            f"Email: {downloader_email}\n\n"
            f"The complete system connection log database backup file (.csv) "
            f"has been attached to this email notice.\n\n"
            f"Best regards,\n"
            f"Your Digital Portfolio App 🤖"
        )
        msg.attach(MIMEText(body_content, "plain"))

        # ATTACHMENT SUBSYSTEM
        if os.path.isfile(LOG_FILE):
            with open(LOG_FILE, "rb") as file_asset:
                attachment_part = MIMEApplication(file_asset.read(), Name=os.path.basename(LOG_FILE))

            attachment_part['Content-Disposition'] = f'attachment; filename="{os.path.basename(LOG_FILE)}"'
            msg.attach(attachment_part)
            print("📎 Local log backup file payload mounted cleanly onto MIME stream layer.")

        with smtplib.SMTP("smtp.gmail.com", 465) as connection:
            connection.starttls()
            connection.login(MY_EMAIL, MY_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=MY_EMAIL,
                msg=msg.as_string()
            )

        print("✉️ Notification alert with attachment dispatched successfully via sendmail!")
        return True
    except Exception as e:
        print(f"❌ Failed to dispatch system email alert bundle: {e}")
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

        # Log the downloader into your local database text row tracker
        log_contact_message(name, email, "Triggered direct download of curriculum vitae PDF.")

        # Fire the background email pipeline with the database attachment file
        send_notification_email(name, email, trigger_type="CV Download Tracking")

        # Serve the file block back to browser client instantly
        return send_from_directory(directory='static', path='Raheel_Ali_CV.pdf', as_attachment=True)

    return render_template('download_cv.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message_sent = False
    if request.method == 'POST':
        visitor_name = request.form.get('name')
        visitor_email = request.form.get('email')
        visitor_message = request.form.get('message')

        # Store contact context inside local system tracking logs database
        log_success = log_contact_message(visitor_name, visitor_email, visitor_message)

        # Fire identical framework module package dispatch carrying attached logs database
        send_notification_email(visitor_name, visitor_email, trigger_type="New Website Contact Message")

        if log_success:
            message_sent = True

    return render_template('contact.html', message_sent=message_sent)


if __name__ == '__main__':
    app.run(debug=True)
