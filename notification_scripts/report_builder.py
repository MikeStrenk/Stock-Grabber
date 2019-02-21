import smtplib
import matplotlib.pyplot as plt
import datetime as dt

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from config import sender, username, password


class Email(object):
    '''
    Instantiates and Email body object
    '''

    def __init__(self, debug=False):
        self.debug = debug
        self.date = dt.date.today().strftime("%m-%m-%y")
        self.subject = f'Standard Report {self.date}'
        self.html_body = ''
        self.html_header = ''
        self.html_footer = ''

        if self.debug:
            print(f"{'-'*45}\nSubject: {self.subject}")

    def append_html(self, filepath):
        '''
        Reads .html files from a relative filepath (String) and returns the file
        '''
        if type(filepath) is str:
            file_object = open(filepath, 'r')
            self.html_body += file_object.read()
            file_object.close()

            if self.debug:
                print(f'{filepath} has been appended to the html body')

        else:
            raise TypeError('Function argument not a string')

    def send(self):
        '''
        Sends the email
        '''
        if self.debug:
            print('\nEmail Sent!\n')


# class Chart(name, title):
#     '''
#     '''

#     def __init__(self, name, title):
#         self.filename = name
#         # instance_var1 is a instance variable
#         self.title = title
#         # instance_var2 is a instance variable
#     xlabel = 'xlabel test'
#     ylabel = 'ylabel test'

#     def make_bar(data):
#         plt.bar(data)
#         plt.xlabel(xlabel)
#         plt.ylabel(ylabel)
#         plt.savefig(f'{filename}.png')

#         filename = f'{filename}.png'

#     def make_line( data, xlabel='', ylabel=''):
#         plt.plot(data)
#         plt.xlabel(xlabel)
#         plt.ylabel(ylabel)
#         plt.savefig(f'{filename}.png')

#         filename = f'{filename}.png'


def send(subject, text_template=None, html_template=None, image=None):
    '''
    This function drives the StrenkCloud email notifications
    '''
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
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
    fp = open(image, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)

    # Send the message via local SMTP server.

    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(username, password)
    mail.sendmail(sender, sender, msg.as_string())
    mail.quit()
