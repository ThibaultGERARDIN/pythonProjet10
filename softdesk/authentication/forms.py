from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import MyUser


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nom d'utilisateur"
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmer le mot de passe"
        for field in self.fields:
            self.fields[str(field)].widget.attrs["placeholder"] = self.fields[str(field)].label
            self.fields[str(field)].help_text = None

        self.label_suffix = ""

    class Meta:
        model = MyUser
        fields = ["username", "date_of_birth", "password1", "password2"]


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = MyUser
        fields = ("username",)


class CustomAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nom d'utilisateur"
        self.fields["password"].label = "Mot de passe"
        for field in self.fields:
            self.fields[str(field)].widget.attrs["placeholder"] = self.fields[str(field)].label
            self.fields[str(field)].help_text = None

        self.label_suffix = ""

    class Meta:
        model = MyUser
        fields = ["username", "password"]
