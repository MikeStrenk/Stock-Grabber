from report_builder import send_notification, Email

sample_report = Email(debug=True)

html_template = 'sample_email.html'
sample_report.append_html(html_template)

sample_report.send()

send_notification('Alert, we didnt send the email!')
