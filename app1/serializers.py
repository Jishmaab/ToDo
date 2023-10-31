from rest_framework import serializers
from .models import *
from .validators import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    profile_picture = serializers.FileField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password','first_name','last_name','user_type', 'profile_picture']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        user = User(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            user_type=validated_data.get('user_type'),
            profile_picture=validated_data.get('profile_picture')
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user
    

class TaskSerializer(serializers.ModelSerializer):
     class Meta:
        model = Task
        fields = ['name', 'category','due_date','status','priority','user']  


class CategorySerializer(serializers.ModelSerializer):
     class Meta:
        model = TaskCategory
        fields = ['name']          