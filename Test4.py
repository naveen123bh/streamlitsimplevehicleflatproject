import smtplib
from email.mime.text import MIMEText

sender_email = "your_email@gmail.com"
app_password = "your_app_password"
receiver_email = "7247navhhatt@gmail.com"

message = MIMEText("Test alert from Streamlit app")
message['Subject'] = "Test Email Alert"
message['From'] = sender_email
message['To'] = receiver_email

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, app_password)
        server.send_message(message)
    print("✅ Email sent successfully")
except Exception as e:
    print("❌ Failed:", e)
