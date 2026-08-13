from django import forms

from .choices import (
    CATEGORY_CHOICES,
    CITY_CHOICES,
    ExperienceLevel,
    JobType,
)
from .models import Application, Company, Job


class SearchForm(forms.Form):
    q = forms.CharField(required=False, label="Keyword")
    city = forms.ChoiceField(required=False, choices=[("", "All cities")] + CITY_CHOICES)
    job_type = forms.ChoiceField(
        required=False, choices=[("", "All types")] + JobType.choices
    )
    experience = forms.ChoiceField(
        required=False, choices=[("", "All levels")] + ExperienceLevel.choices
    )
    category = forms.ChoiceField(required=False, choices=[("", "All categories")] + CATEGORY_CHOICES)

    def clean_q(self):
        return self.cleaned_data.get("q", "").strip()


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = (
            "title",
            "category",
            "job_type",
            "experience_level",
            "city",
            "is_remote",
            "salary_min",
            "salary_max",
            "salary_period",
            "description",
            "responsibilities",
            "requirements",
            "skills",
            "apply_method",
            "apply_email",
            "apply_url",
            "deadline",
        )
        widgets = {
            "city": forms.Select(),
            "category": forms.Select(),
            "job_type": forms.Select(),
            "experience_level": forms.Select(),
            "salary_period": forms.Select(),
            "apply_method": forms.Select(),
            "description": forms.Textarea(attrs={"rows": 6}),
            "responsibilities": forms.Textarea(attrs={"rows": 4}),
            "requirements": forms.Textarea(attrs={"rows": 4}),
            "skills": forms.TextInput(attrs={"placeholder": "Django, Python, SQL"}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("apply_method") == "email" and not cleaned.get("apply_email"):
            self.add_error("apply_email", "Provide an email for candidates to apply to.")
        if cleaned.get("apply_method") == "url" and not cleaned.get("apply_url"):
            self.add_error("apply_url", "Provide the external application URL.")
        if cleaned.get("salary_min") and cleaned.get("salary_max") and cleaned.get("salary_min") > cleaned.get("salary_max"):
            self.add_error("salary_min", "Minimum salary cannot exceed maximum.")
        return cleaned


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = (
            "name",
            "logo",
            "tagline",
            "description",
            "industry",
            "website",
            "email",
            "phone",
            "city",
            "founded",
            "employees",
        )
        widgets = {
            "industry": forms.Select(),
            "city": forms.TextInput(),
            "description": forms.Textarea(attrs={"rows": 5}),
            "founded": forms.NumberInput(),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("email", "phone", "cover_letter", "resume")
        widgets = {
            "cover_letter": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Why are you a good fit for this role?"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["email"].initial = user.email
            profile = getattr(user, "seeker_profile", None)
            if profile:
                self.fields["phone"].initial = user.phone
                if profile.resume and not self.initial.get("resume"):
                    self.initial["resume"] = profile.resume

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume:
            allowed = {"pdf", "doc", "docx"}
            ext = resume.name.rsplit(".", 1)[-1].lower() if "." in resume.name else ""
            if ext not in allowed:
                raise forms.ValidationError("Only PDF, DOC or DOCX files are allowed.")
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Resume must be under 5 MB.")
        return resume