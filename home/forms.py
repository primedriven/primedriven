from django import forms
from .models import EntryLIST, Member


class JoinListForm(forms.ModelForm):
    class Meta:
        model = EntryLIST
        fields = ["full_name", "email", "contact_preference"]


class JoinMemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "email", "entry_number", "ss"]
