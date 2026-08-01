import smtplib
import secrets
from dotenv import load_dotenv
import os


EMAIL = os.environ["GMAIL_ADDRESS"]
PASSWORD = os.environ["GMAIL_APP_PASSWORD"]


def otpgensignup(recver):
    otp = secrets.randbelow(900000) + 100000

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(
   EMAIL,
    PASSWORD
)

    server.sendmail(
    "echonet.team@gmail.com",
    recver,
    f"Subject: OTP for Verification\n\nYour OTP for signup verification is: {otp}\nIf this wasnt requested by you, please ignore!"
)
    server.quit()
    print("Email sent")
    return otp
    