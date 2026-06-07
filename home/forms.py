from django import forms
from .models import EntryLIST, Member


class JoinListForm(forms.ModelForm):
    class Meta:
        model = EntryLIST
        fields = ["full_name", "email", "contact_preference","phone"]


class JoinMemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["full_name", "email", "entry_number", "ss"]


from django import forms
from .models import PrizeClaim


ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "pdf"]
MAX_FILE_SIZE_MB   = 10


class PrizeClaimForm(forms.ModelForm):

    class Meta:
        model  = PrizeClaim
        fields = [
            "full_name",
            "entry_number",
            "id_type",
            "id_file",
        ]

    def clean_entry_number(self):
        value = self.cleaned_data.get("entry_number", "").strip()
        # strip leading # if present
        return value.lstrip("#").strip()

    def clean_id_file(self):
        file = self.cleaned_data.get("id_file")

        if not file:
            raise forms.ValidationError("Please upload a valid ID document.")

        # check extension
        ext = file.name.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f"File type not allowed. Please upload a JPG, PNG or PDF."
            )

        # check size
        if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(
                f"File is too large. Maximum size is {MAX_FILE_SIZE_MB}MB."
            )

        return file

 
 