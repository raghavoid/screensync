from django import forms
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

class JoinRoomForm(forms.Form):
    room_id = forms.UUIDField(label='Room ID')
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)