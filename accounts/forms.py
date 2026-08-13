from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from jobs.choices import CITY_CHOICES

from .models import JobSeekerProfile, User


class RoleChoiceForm(forms.Form):
    role = forms.ChoiceField(choices=User.Role.choices, widget=forms.HiddenInput)


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Full name")
    phone = forms.CharField(max_length=30, required=False)
    accept_terms = forms.BooleanField(required=True, label="I agree to the Terms of Service")

    class Meta:
        model = User
        fields = ("first_name", "email", "phone", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.role = self.cleaned_data.get("role", User.Role.JOB_SEEKER)
        if commit:
            user.save()
            if user.is_seeker:
                JobSeekerProfile.objects.get_or_create(user=user)
        return user


class SeekerRegistrationForm(UserRegistrationForm):
    role = forms.CharField(initial=User.Role.JOB_SEEKER, required=False, widget=forms.HiddenInput)

    def clean_role(self):
        return User.Role.JOB_SEEKER


class EmployerRegistrationForm(UserRegistrationForm):
    role = forms.CharField(initial=User.Role.EMPLOYER, required=False, widget=forms.HiddenInput)
    company_name = forms.CharField(max_length=150, label="Company name")
    industry = forms.CharField(max_length=80, required=False, label="Industry")

    def clean_role(self):
        return User.Role.EMPLOYER


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    def clean_username(self):
        return self.cleaned_data["username"].lower()


class JobSeekerProfileForm(forms.ModelForm):
    city = forms.ChoiceField(choices=CITY_CHOICES, required=False)

    class Meta:
        model = JobSeekerProfile
        fields = ("title", "city", "summary", "skills", "resume")
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 4}),
            "skills": forms.TextInput(attrs={"placeholder": "Python, Django, SQL, ..."}),
        }

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