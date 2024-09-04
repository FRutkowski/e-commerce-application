# from django.core.mail import EmailMessage, BadHeaderError
from django.shortcuts import render
from .tasks import notify_customers

# from templated_mail.mail import BaseEmailMessage


def say_hello(request):
    # try:
    # do normalnego wysyłania tekstowych maili można skorzystać z gotowych funkcji,
    # jednak do wysyłania mailów z plików trzeba samemu utworzyć obiekt i załączyć pliki
    # send_mail("subject", "message", "hello@hello.com", ["frutkowski80@gmail.com"])
    # mail_admins("subject", "message", html_message="message")
    # message = EmailMessage(
    #     "subject", "message", "hello@hello.com", ["frutkowski80@gmail.com"]
    # )
    # message.attach_file("playground/static/images/dog.jpg")
    # message.send()
    #     message = BaseEmailMessage(
    #         template_name="emails/hello.html",
    #         context={"name": "Filip"},
    #     )
    #     message.send(["frutkowski80@gmail.com"])
    # except BadHeaderError:
    #     pass
    # return render(request, "hello.html", {"name": "Mosh"})
    notify_customers.delay("Hello")
    return render(request, "hello.html", {"name": "Mosh"})
