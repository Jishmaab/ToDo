from datetime import timedelta, timezone

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from rest_framework import exceptions, filters, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_api_key.permissions import HasAPIKey

from utils.exceptions import CustomException, fail, success

from .models import Task, TaskCategory, User
from .permissions import IsTaskOwner
from .serializers import (CategorySerializer, TaskSerializer, UserSerializer,
                          validate_password)


class LoginView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(fail(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        validate_password(password)
        user = authenticate(username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            expiration_date = token.created + timedelta(days=1)

            if expiration_date <= timezone.now():
                token.delete()
                token = Token.objects.create(user=user)

            user_serializer = UserSerializer(user)
            response_data = {
                "token": token.key,
                "user": user_serializer.data,
            }

            return Response(success(response_data), status=status.HTTP_200_OK)

        raise AuthenticationFailed("Invalid username or password")


class SignupView(APIView):

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                validate_email(email)
            except ValidationError as email_error:
                raise CustomException(
                    {"status": "Invalid email format", "detail": email_error.detail})

            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                raise CustomException(
                    {"status": "Username or email already in use"})
            user = serializer.create(serializer.validated_data)
            serializer = UserSerializer(user, context={'request': request})
            return Response(
                success(serializer.data),
                status=status.HTTP_201_CREATED,
            )
        raise CustomException(serializer.errors)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, HasAPIKey]

    def post(self, request: Request, format=None) -> Response:
        try:
            user = request.user
            token = request.user.auth_token
            token.delete()

            return Response(
                success("Logged out successfully"),
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            raise CustomException(str(e))


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsTaskOwner,HasAPIKey]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def mark_task_completed(self, request, pk=None):
        try:
            task = self.get_object()
            task.status = Task.StatusChoices.completed
            task.save()
            return Response(
                success(" Marked as Completed "),
                status=status.HTTP_200_OK,)
        except Exception as e:
            raise CustomException(str(e))

    def mark_task_incomplete(self, request, pk=None):
        try:
            task = self.get_object()
            task.status = Task.StatusChoices.incomplete
            task.save()
            return Response(
                success("Marked as Incomplete"),
                status=status.HTTP_200_OK, )
        except Exception as e:
            raise CustomException(str(e))


class CategoryViewSet(ModelViewSet):
    queryset = TaskCategory.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class UserProfileView(UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            print(serializer.validated_data)
            self.perform_update(serializer)

            return Response(
                success(" Profile updated successfully"),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            raise exceptions.APIException(str(e))


class TaskSearchView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['category', 'due_date', 'priority']
