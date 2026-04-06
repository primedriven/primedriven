from django import forms
from .models import EntryLIST


class JoinListForm(forms.ModelForm):
    class Meta:
        model = EntryLIST
        fields = ["full_name", "phone_number"]
