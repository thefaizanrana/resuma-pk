from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from jobs.models import Company, Job

User = get_user_model()


class AccountFlowsTests(TestCase):
    def setUp(self):
        self.seeker_data = {
            "first_name": "Ali",
            "email": "ali@example.com",
            "phone": "03001234567",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
            "accept_terms": "on",
        }
        self.employer_data = {
            **self.seeker_data,
            "email": "hiring@example.com",
            "company_name": "Test Corp",
            "industry": "Information Technology",
        }

    def test_seeker_registration_and_profile(self):
        response = self.client.post(reverse("accounts:register"), self.seeker_data)
        self.assertRedirects(response, reverse("accounts:seeker_dashboard"))
        user = User.objects.get(email="ali@example.com")
        self.assertTrue(user.is_seeker)
        self.assertTrue(hasattr(user, "seeker_profile"))

    def test_employer_registration_creates_company(self):
        response = self.client.post(reverse("accounts:register_employer"), self.employer_data)
        self.assertRedirects(response, reverse("accounts:company_setup"))
        user = User.objects.get(email="hiring@example.com")
        self.assertTrue(user.is_employer)
        self.assertEqual(user.managed_company.name, "Test Corp")

    def test_duplicate_email_rejected(self):
        self.client.post(reverse("accounts:register"), self.seeker_data)
        self.client.logout()
        response = self.client.post(reverse("accounts:register"), self.seeker_data)
        self.assertNotIn(302, [response.status_code])
        self.assertIn("already exists", response.content.decode())

    def test_login_logout(self):
        self.client.post(reverse("accounts:register"), self.seeker_data)
        self.client.get(reverse("accounts:logout"))
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "ali@example.com", "password": "SecurePass123!"},
        )
        self.assertRedirects(response, reverse("jobs:home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class EmployerFlowTests(TestCase):
    def setUp(self):
        employer = User.objects.create_user(
            username="emp@example.com", email="emp@example.com", password="SecurePass123!", role="employer"
        )
        self.company = Company.objects.create(owner=employer, name="Test Corp", slug="test-corp")
        self.client.login(username="emp@example.com", password="SecurePass123!")

    def test_post_job(self):
        response = self.client.post(
            reverse("accounts:job_create"),
            {
                "title": "Django Developer",
                "category": "software",
                "job_type": "full_time",
                "experience_level": "junior",
                "city": "Lahore",
                "salary_min": 100000,
                "salary_max": 150000,
                "salary_period": "monthly",
                "description": "Build web apps.",
                "apply_method": "email",
                "apply_email": "hr@example.com",
            },
        )
        self.assertRedirects(response, reverse("accounts:employer_dashboard"))
        job = Job.objects.get(title="Django Developer")
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.status, "active")
        self.assertEqual(job.salary_display, "Rs. 100,000 - Rs. 150,000 per month")

    def test_apply_method_validation(self):
        response = self.client.post(
            reverse("accounts:job_create"),
            {
                "title": "Bad Apply",
                "category": "software",
                "job_type": "full_time",
                "experience_level": "fresh",
                "city": "Karachi",
                "description": "Desc",
                "apply_method": "url",
            },
        )
        self.assertIn("Provide the external application URL", response.content.decode())


class JobSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        employer = User.objects.create_user(
            username="emp@example.com", email="emp@example.com", password="SecurePass123!", role="employer"
        )
        company = Company.objects.create(owner=employer, name="Tech Co", slug="tech-co")
        cls.job = Job.objects.create(
            company=company,
            title="Python Developer",
            category="software",
            job_type="full_time",
            experience_level="mid",
            city="Lahore",
            description="Python work",
            skills="Python, Django",
            status="active",
        )

    def test_search_by_keyword(self):
        response = self.client.get(reverse("jobs:job_list"), {"q": "python"})
        self.assertContains(response, "Python Developer")

    def test_search_by_city(self):
        response = self.client.get(reverse("jobs:job_list"), {"city": "Karachi"})
        self.assertNotContains(response, "Python Developer")

    def test_draft_jobs_hidden(self):
        self.job.status = "draft"
        self.job.save()
        response = self.client.get(reverse("jobs:job_list"))
        self.assertNotContains(response, "Python Developer")
        response = self.client.get(reverse("jobs:job_detail", kwargs={"slug": self.job.slug}))
        self.assertEqual(response.status_code, 404)

    def test_homepage_context(self):
        response = self.client.get(reverse("jobs:home"))
        self.assertContains(response, "Python Developer")


class ApplicationFlowTests(TestCase):
    def setUp(self):
        employer = User.objects.create_user(
            username="emp@example.com", email="emp@example.com", password="SecurePass123!", role="employer"
        )
        company = Company.objects.create(owner=employer, name="Tech Co", slug="tech-co", email="hr@tech.co")
        self.job = Job.objects.create(
            company=company,
            title="Django Developer",
            category="software",
            job_type="full_time",
            experience_level="fresh",
            city="Lahore",
            description="Build things.",
            apply_method="email",
            apply_email="hr@tech.co",
            status="active",
        )
        self.seeker = User.objects.create_user(
            username="seeker@example.com", email="seeker@example.com", password="SecurePass123!"
        )
        self.client.login(username="seeker@example.com", password="SecurePass123!")

    def test_apply_and_duplicate_rejected(self):
        response = self.client.post(
            reverse("jobs:apply_job", kwargs={"slug": self.job.slug}),
            {"email": "seeker@example.com", "phone": "03001112222", "cover_letter": "I am a great fit."},
        )
        self.assertRedirects(response, reverse("jobs:job_detail", kwargs={"slug": self.job.slug}))
        self.assertEqual(self.job.applications.count(), 1)
        response = self.client.post(
            reverse("jobs:apply_job", kwargs={"slug": self.job.slug}),
            {"email": "seeker@example.com"},
        )
        self.assertEqual(self.job.applications.count(), 1)

    def test_resume_file_validation(self):
        bad = SimpleUploadedFile("resume.exe", b"bad", content_type="application/octet-stream")
        response = self.client.post(
            reverse("jobs:apply_job", kwargs={"slug": self.job.slug}),
            {"email": "seeker@example.com", "resume": bad},
        )
        self.assertIn("Only PDF, DOC or DOCX", response.content.decode())
        self.assertEqual(self.job.applications.count(), 0)

    def test_save_and_unsave_job(self):
        url = reverse("jobs:save_job", kwargs={"slug": self.job.slug})
        self.client.post(url)
        self.assertEqual(self.job.saved_by.count(), 1)
        self.client.post(url)
        self.assertEqual(self.job.saved_by.count(), 0)

    def test_employer_status_update(self):
        app = self.job.applications.create(
            applicant=self.seeker, email=self.seeker.email, status="received"
        )
        self.client.logout()
        self.client.login(username="emp@example.com", password="SecurePass123!")
        response = self.client.post(
            reverse("accounts:application_status", kwargs={"pk": app.pk}), {"status": "shortlisted"}
        )
        self.assertEqual(response.status_code, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, "shortlisted")

    def test_employer_cannot_edit_others_job(self):
        self.client.logout()
        other = User.objects.create_user(
            username="other@example.com", email="other@example.com", password="SecurePass123!", role="employer"
        )
        Company.objects.create(owner=other, name="Other Co", slug="other-co")
        self.client.login(username="other@example.com", password="SecurePass123!")
        response = self.client.post(
            reverse("accounts:job_toggle_status", kwargs={"slug": self.job.slug})
        )
        self.assertEqual(response.status_code, 404)