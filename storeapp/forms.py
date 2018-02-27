from django.contrib.auth.models import User
from django import forms
from .models import highscore
from .models import game
from django.contrib.auth.models import Group


#Form for user signup
class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput)
    developer = forms.BooleanField(required = False)
    confirm_password=forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name','email', 'username', 'password', 'confirm_password', 'developer']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for fieldname in ['username']:
            self.fields[fieldname].help_text = None

class highscore(forms.ModelForm):

    class Meta:
        model = highscore
        fields = ['playerID', 'score']

class manageGames(forms.ModelForm):

    class Meta:
        model = game
        fields = ['name','url', 'price', 'description']
