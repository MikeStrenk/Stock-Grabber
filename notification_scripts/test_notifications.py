import matplotlib.pyplot as plt
import strenkcloud
# from email_template import text_template, html_template


data = [1, 2, 3, 4]
title = 'some numbers'


def generate_jpg(img_name, data, title):
    plt.plot(data)
    plt.ylabel(title)
    plt.savefig(f'{img_name}.png')


generate_jpg('img1', data, title)

img1 = 'img1.png'

# Email template setup
text_template = '''Hi!\nThis is a test email\nI hope it is working!'''

html_template = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title></title>
  <style type="text/css">
    #outlook a {padding:0;}
    body{width:100% !important; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; margin:0; padding:0;} /* force default font sizes */
    .ExternalClass {width:100%;} .ExternalClass, .ExternalClass p, .ExternalClass span, .ExternalClass font, .ExternalClass td, .ExternalClass div {line-height: 100%;} /* Hotmail */
    table td {border-collapse: collapse;}
    @media only screen and (min-width: 600px) { .maxW { width:600px !important; } }
  </style>
</head>
<body style="margin: 0px; padding: 0px; -webkit-text-size-adjust:none; -ms-text-size-adjust:none;" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0" bgcolor="#FFFFFF"><table bgcolor="#CCCCCC" width="100%" border="0" align="center" cellpadding="0" cellspacing="0"><tr><td valign="top">
<!--[if (gte mso 9)|(IE)]>
<table width="600" align="center" cellpadding="0" cellspacing="0" border="0"><tr><td valign="top">
<![endif]-->
<table width="100%" class="maxW" style="max-width: 600px; margin: auto;" border="0" align="center" cellpadding="0" cellspacing="0"><tr><td valign="top" align="center">

<img src="cid:image1">




</td></tr></table>
<!--[if (gte mso 9)|(IE)]>
</td></tr></table>
<![endif]-->
</td></tr></table></body></html>'''


strenkcloud.send_email_notification(
    subject='testing this stuff', text_template=text_template, html_template=html_template, image=img1)
