from .models import MyUser
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ("id", "username")


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ("id", "username", "age", "rgpd_consent")


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password], label="Mot de passe"
    )
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmation du mot de passe")

    class Meta:
        model = MyUser
        fields = ("username", "password", "password2", "date_of_birth", "can_be_contacted", "can_data_be_shared")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        today = timezone.now().date()
        age = int(
            today.year
            - (validated_data["date_of_birth"].year)
            - ((today.month, today.day) < (validated_data["date_of_birth"].month, validated_data["date_of_birth"].day))
        )
        if age < 15:
            raise serializers.ValidationError("Vous devez avoir au moins 15ans pour vous inscrire.")
        else:
            user = MyUser.objects.create(
                username=validated_data["username"],
                date_of_birth=validated_data["date_of_birth"],
                can_be_contacted=validated_data["can_be_contacted"],
                can_data_be_shared=validated_data["can_data_be_shared"],
            )

            user.set_password(validated_data["password"])
            user.save()

        return user
