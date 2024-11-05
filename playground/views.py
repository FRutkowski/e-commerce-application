# from django.core.mail import EmailMessage, BadHeaderError
from django.shortcuts import render
import logging
from rest_framework.views import APIView
import requests

# from templated_mail.mail import BaseEmailMessage

logger = logging.getLogger(__name__)  # playground.views


class HelloView(APIView):
    def get(self, request):
        try:
            logger.info("Calling httpbin")
            response = requests.get("https://httpbin.org/delay/2")
            logger.info("Received the response")
        except request.ConnectionError:
            logger.critical("httpbin is off!")
        data = response.json()
        return render(request, "hello.html", {"name": data})
