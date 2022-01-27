from django.dispatch import receiver
from django.db.models import signals

# from .emails import EmailSender

# @receiver(signals.post_save, sender=Account)
# def is_account_registered(sender, instance, created, **kwargs):
#     if created:
#         print(instance)
#         print('ACCOUNT REGISTERED')
#         user = instance
#         to = instance.email
#         sender = EmailSender()
#         if not user.is_superuser:
#             print(sender.send_user_activation_email_to_user(user, to))

#             print(sender.send_user_activation_email_to_staff(user))

#         # if instance.get_account_type() == 'Operator':
#         #     sender.send_new_user_registered_email_to_staff(user)

#         return instance

#     print(instance)
#     print('ACCOUNT UPDATED')