import smtplib, ssl
from internal import log_to_file

smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "testmail.mariko@gmail.com"
password = "jdoh qmgr bgng cpcy"
receiver_email = "vovakorben@gmail.com"


# Create a secure SSL context
context = ssl.create_default_context()


def send_email(message: str, recipients: list):
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        # server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        # server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        # TODO: Send email here
        for receiver_email in recipients:
            server.sendmail(sender_email, receiver_email, message)
    except Exception as e:
        # Print any error messages to stdout
        log_to_file(e)
    finally:
        server.quit()
