from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


ESENDER = settings.EMAIL_SENDER


# class EmailSender():
#     '''
#     Module, that will send all kind of emails
#     For now it send activation email to user after creating accounts
#     '''
#     def send_user_activation_email_to_user(self, user, to):
#         '''
#         function to send activation emal.
#         get emails detail from settings,
#         use Django EmailMessage class
#         '''

#         subject = ESENDER['EMAIL_SUBJECTS'].get('activation_action_to_user')
#         sender = ESENDER['SENDER']
#         email_template = ESENDER['EMAIL_TEMPLATES'].get('activation_action_to_user')

#         domain = Site.objects.get_current().domain

#         email_context={
#             'site_name':  ESENDER['SITE_NAME'],
#             'protocol': ESENDER['PROTOCOL'],
#             'domain': domain,
#             'url': activation_url
#         }

#         # prepare email_template before sending
#         html_message = render_to_string(email_template, context=email_context)
#         # create message object, that will sended
#         msg = EmailMessage(
#             subject=subject,
#             body=html_message,
#             from_email=sender,
#             to=[to]
#             )
#         msg.content_subtype = "html"

#         # check if settings allow to send activation email and send email
#         if ESENDER['SEND_ACTIVATION_ACTION_EMIL_TO_USER'] == True:
#             try:
#                 msg.send()
#                 return 'ACTIVATION EMAIL SEND TO USER'
#             except Exception as e:
#                 print(e)
#                 return 'email not send, error'
#         return 'SEND_ACTIVATION_ACTION_EMIL_TO_USER = False'
