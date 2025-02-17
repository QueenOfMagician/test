from django.contrib.auth import login
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .serializers import SigninSerializer, SignupSerializer

# Create your views here.

def page404NotFound(request, exception):
    return render(request, '404.html', status=404)


class SigninView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def post(self, request):
        serializer = SigninSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            # Generate JWT token
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'id': user.id,
                'username': user.username,
            }, status=status.HTTP_200_OK)
        return Response({"status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)


class SignupView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "SUCCESS Created"}, status=status.HTTP_201_CREATED
            )
        return Response({"status": "Gagal Membuat Akun", "message": "Akun tidak dapat dibuat karena ada kesalahan pada input data."}, status=status.HTTP_400_BAD_REQUEST)

