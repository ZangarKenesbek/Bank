from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserAccount

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = UserAccount
        fields = ['username', 'email', 'password1', 'password2']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

class TransferForm(forms.Form):
    receiver = forms.ModelChoiceField(queryset=UserAccount.objects.none(), label="Получатель")
    amount = forms.DecimalField(label="Сумма", min_value=0.01, decimal_places=2)

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user')
        super().__init__(*args, **kwargs)
        self.fields['receiver'].queryset = UserAccount.objects.exclude(id=current_user.id)
