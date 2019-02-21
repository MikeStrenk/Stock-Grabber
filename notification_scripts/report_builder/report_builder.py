import pandas as pd
import os
import datetime as dt
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from config import sender, username, password


class Email(object):
    '''
    Instantiates an Email body object
    '''

    def __init__(self, debug=False):
        self.debug = debug
        self.date = dt.date.today().strftime("%m-%m-%y")
        self.subject = f'Standard Report {self.date}'
        self.from_address = sender
        self.to_address = sender
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
            cwd = os.path.dirname(os.path.abspath(__file__))
            absolute_filepath = os.path.join(cwd, filepath)
            html_file = open(absolute_filepath, 'r')
            self.html_body += html_file.read()
            html_file.close()

            if self.debug:
                print(f'{filepath} has been appended to the html body')

        else:
            raise TypeError('Function argument not a string')

    def insert_image(self):
        pass

    def send(self, image=False):
        '''
        This function drives the StrenkCloud email notifications
        '''
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.from_address
        msg['To'] = self.to_address

        # Create the body of the message (a plain-text and an HTML version).
        # Record the MIME types of both parts - text/plain and text/html.
        print(type(self.html_body))
        # part1 = MIMEText("nothing in the plain text email", 'plain')
        part2 = MIMEText(self.html_body, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.

        msg.attach(part2)

        # This example assumes the image is in the current directory
        # if image == True:
        #     cwd = os.path.dirname(os.path.abspath(__file__))
        #     image_path = os.path.join(cwd, image)
        #     print(image_path)
        #     fp = open(image_path, 'rb')
        #     msgImage = MIMEImage(fp.read())
        #     fp.close()

        #     # Define the image's ID as referenced above
        #     msgImage.add_header('Content-ID', '<image1>')
        #     msg.attach(msgImage)

        # Send the message via local SMTP server.

        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()

        mail.login(username, password)
        mail.sendmail(self.from_address, self.from_address,
                      msg.as_string())
        mail.quit()

        if self.debug:
            print(f'\n--> Email sent with subject: "{self.subject}"\n')

    def send_notification(self, text, image=False):
        notification = Email(debug=True)
        notification.subject = text
        notification.send(image)

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


# def send(subject, text_template=None, html_template=None, image=None):
#     '''
#     This function drives the StrenkCloud email notifications
#     '''
#     msg = MIMEMultipart('alternative')
#     msg['Subject'] = subject
#     msg['From'] = sender
#     msg['To'] = sender

#     # Create the body of the message (a plain-text and an HTML version).
#     # Record the MIME types of both parts - text/plain and text/html.
#     part1 = MIMEText(text_template, 'plain')
#     part2 = MIMEText(html_template, 'html')

#     # Attach parts into message container.
#     # According to RFC 2046, the last part of a multipart message, in this case
#     # the HTML message, is best and preferred.
#     msg.attach(part1)
#     msg.attach(part2)

#     # This example assumes the image is in the current directory
#     fp = open(image, 'rb')
#     msgImage = MIMEImage(fp.read())
#     fp.close()

#     # Define the image's ID as referenced above
#     msgImage.add_header('Content-ID', '<image1>')
#     msg.attach(msgImage)

#     # Send the message via local SMTP server.

#     mail = smtplib.SMTP('smtp.gmail.com', 587)

#     mail.ehlo()

#     mail.starttls()

#     mail.login(username, password)
#     mail.sendmail(sender, sender, msg.as_string())
#     mail.quit()

if __name__ == '__main__':
    print('\nTest Mode')
    test_report = Email(debug=True)
