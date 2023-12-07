from datetime import timedelta

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, HiddenInput, TimeInput, DateInput
from django.urls import reverse
from django_select2 import forms as s2forms

from main.models import (
    IncidentReport,
    Incident,
    NotificationPreference, Announcement,
)


class StationWidget(s2forms.ModelSelect2Widget):
    search_fields = ["name__icontains", "line_stations__station_code__icontains"]

class StationMultipleWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ["name__icontains", "line_stations__station_code__icontains"]

class ReportIncidentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("station"),
            Field("description"),
            Submit("submit", "Submit", css_class="button btn btn-primary"),
        )
    class Meta:
        model = IncidentReport
        fields = ("station", "description")
        widgets = {"station": StationWidget}


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("username"),
            Field("email"),
            Field("password1"),
            Field("password2"),
            Submit("submit", "Submit", css_class="button  btn btn-primary"),
        )
        self.fields["email"].widget.attrs["required"] = "required"
        self.fields["email"].label = "Email address*"

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already belongs to an existing user. Please log in instead.")
        return email

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class NotificationPreferenceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("day"),
            Field("specific_date"),
            Field("time"),
            Field("stations"),
            Field("rule"),
            Submit("submit", "Save", css_class="button  btn btn-primary"),
        )

    class Meta:
        model = NotificationPreference
        exclude = ("user",)
        widgets = {
            "stations": StationMultipleWidget, "time": TimeInput(attrs={'type': 'time'}),
            "specific_date": DateInput(attrs={"required": False, "type": "date"}),
        }


class UserSettingsForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "settingsForm"
        self.helper.layout = Layout(
            Field("username"),
            Field("email"),

        )
        self.fields["email"].widget.attrs["required"] = "required"
        self.fields["email"].label = "Email address*"

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already belongs to another user. ")
        return email

    class Meta:
        model = User
        fields = ["username", "email"]


class VerifyReportForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("content"),
            Submit("submit", "Save", css_class="button  btn btn-primary"),
        )

    class Meta:
        model = Announcement
        exclude = ("added_by", "incident")
