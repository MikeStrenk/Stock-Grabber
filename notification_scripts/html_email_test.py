import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from config import sender, username, password

from email_template import text_template, html_template

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Test Strenk Cloud Email Notification System"
msg['From'] = sender
msg['To'] = sender

# Create the body of the message (a plain-text and an HTML version).
# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text_template, 'plain')
part2 = MIMEText(html_template, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# This example assumes the image is in the current directory
# fp = open('test.jpg', 'rb')
# msgImage = MIMEImage(fp.read())
# fp.close()

# Define the image's ID as referenced above
# msgImage.add_header('Content-ID', '<image1>')
# msg.attach(msgImage)

# Send the message via local SMTP server.
mail = smtplib.SMTP('smtp.gmail.com', 587)
mail.ehlo()
mail.starttls()

mail.login(username, password)
mail.sendmail(sender, sender, msg.as_string())
mail.quit()
