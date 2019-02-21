from report_builder import Email

sample_report = Email(debug=True)

html_template = 'sample_email.html'
sample_report.append_html(html_template)

sample_report.send()
