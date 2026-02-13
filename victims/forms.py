from django import forms

from .models import Submission, Victim


class SubmissionForm(forms.ModelForm):
    details = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6, "class": "form-control"}),
        help_text="Provide the correction or additional information.",
    )
    source_urls = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        help_text="List sources (one per line).",
    )

    class Meta:
        model = Submission
        fields = ["victim", "submitter_name", "submitter_email", "details", "source_urls"]
        widgets = {
            "victim": forms.Select(attrs={"class": "form-select"}),
            "submitter_name": forms.TextInput(attrs={"class": "form-control"}),
            "submitter_email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        proposed_data = {
            "victim_id": cleaned.get("victim").id if cleaned.get("victim") else None,
            "details": cleaned.get("details"),
            "source_urls": [
                line.strip()
                for line in (cleaned.get("source_urls") or "").splitlines()
                if line.strip()
            ],
        }
        self.instance.proposed_data = proposed_data
        return cleaned


class VictimFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    city = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    verification_status = forms.ChoiceField(
        required=False,
        choices=[("", "All"), *Victim.VerificationStatus.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    age_min = forms.IntegerField(
        required=False, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    age_max = forms.IntegerField(
        required=False, min_value=0, widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    tag = forms.CharField(required=False)
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ("recent", "Most recent"),
            ("alpha", "Alphabetical"),
            ("age", "Age"),
            ("date", "Date of death"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
