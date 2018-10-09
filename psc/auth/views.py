from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.contrib.auth import logout


from psc.auth.serializers import LoginSerializer, RegistrationSerializer


class LoginApiView(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def login(self, request):
        # Method for login users handling via API
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class RegistrationView(ViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def registration(self, request):
        # Method for user registration handling via API
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)


class Logout(ViewSet):

    def api_logout(self, request):
        # Method for user logout handling via API
        logout(request)
        return Response({'detail': "User was logged out"})
