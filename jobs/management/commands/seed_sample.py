import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from jobs.choices import (
    ApplyMethod,
    CATEGORY_CHOICES,
    CITY_CHOICES,
    ExperienceLevel,
    JobStatus,
    JobType,
    SalaryPeriod,
)
from jobs.models import Company, Job


class Command(BaseCommand):
    help = "Seed Resuma.pk with SAMPLE companies and jobs (marked as sample) for testing."

    SAMPLE_COMPANIES = [
        {
            "name": "Horizon Tech (Sample)",
            "tagline": "A sample software company — Lahore's growing product studio.",
            "industry": "Information Technology",
            "city": "Lahore",
            "website": "https://example.com",
            "employees": "51-200",
            "founded": 2018,
            "description": (
                "SAMPLE DATA — this company exists only to demonstrate Resuma.pk. "
                "Horizon Tech builds web products for clients across Pakistan and the Gulf."
            ),
        },
        {
            "name": "Karachi Mills Co. (Sample)",
            "tagline": "A sample textile & manufacturing group based in Karachi.",
            "industry": "Textiles / Fashion",
            "city": "Karachi",
            "website": "https://example.com",
            "employees": "201-1000",
            "founded": 1994,
            "description": (
                "SAMPLE DATA — this company exists only to demonstrate Resuma.pk. "
                "Karachi Mills is a diversified manufacturer with export operations."
            ),
        },
        {
            "name": "Islamabad Health Hub (Sample)",
            "tagline": "A sample healthcare provider serving the twin cities.",
            "industry": "Healthcare / Medical",
            "city": "Islamabad",
            "website": "https://example.com",
            "employees": "1-50",
            "founded": 2015,
            "description": (
                "SAMPLE DATA — this company exists only to demonstrate Resuma.pk. "
                "Islamabad Health Hub operates clinics and telehealth services."
            ),
        },
        {
            "name": "RiseEdge Ventures (Sample)",
            "tagline": "A sample e-commerce startup with remote-first culture.",
            "industry": "E-Commerce",
            "city": "Remote / Anywhere",
            "website": "https://example.com",
            "employees": "1-50",
            "founded": 2021,
            "description": (
                "SAMPLE DATA — this company exists only to demonstrate Resuma.pk. "
                "RiseEdge runs a remote-first e-commerce team across Pakistan."
            ),
        },
    ]

    SAMPLE_JOBS = [
        {
            "title": "Junior Django Developer",
            "company": 0,
            "category": "software",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.JUNIOR,
            "city": "Lahore",
            "salary_min": 100000,
            "salary_max": 150000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "We are building a Django-powered product platform and want a developer who loves clean, tested code."
            ),
            "responsibilities": "Build and maintain Django REST APIs\nWrite unit tests for new features\nCollaborate with designers on product features",
            "requirements": "1+ years of Python/Django experience\nSolid understanding of SQL\nBasic Git and teamwork skills",
            "skills": "Python, Django, SQL, Git",
            "apply_method": ApplyMethod.EMAIL,
            "apply_email": "careers@example.com",
            "is_featured": True,
        },
        {
            "title": "Senior Product Designer",
            "company": 3,
            "category": "design",
            "job_type": JobType.REMOTE,
            "experience_level": ExperienceLevel.SENIOR,
            "city": "Remote / Anywhere",
            "salary_min": 250000,
            "salary_max": 350000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "We are looking for a senior designer to own our design system end to end."
            ),
            "responsibilities": "Own the design system and component library\nRun user research and usability tests\nPrototype and ship features with engineering",
            "requirements": "5+ years of product design experience\nStrong portfolio with shipped products\nFluency in Figma and modern design tooling",
            "skills": "Figma, Design Systems, Prototyping, UI/UX",
            "apply_method": ApplyMethod.URL,
            "apply_url": "https://example.com/careers/designer",
            "is_featured": True,
        },
        {
            "title": "Sales Executive — B2B",
            "company": 3,
            "category": "sales",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.MID,
            "city": "Karachi",
            "salary_min": 80000,
            "salary_max": 120000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "We are expanding our B2B sales team and need an energetic closer."
            ),
            "responsibilities": "Hunt and qualify new B2B accounts\nRun product demos and negotiations\nMaintain pipeline hygiene in CRM",
            "requirements": "3+ years in B2B sales\nExcellent Urdu and English communication\nSelf-driven with strong follow-through",
            "skills": "Sales, CRM, Negotiation, Communication",
            "apply_method": ApplyMethod.EMAIL,
            "apply_email": "careers@example.com",
        },
        {
            "title": "Staff Nurse — OPD",
            "company": 2,
            "category": "health",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.FRESH,
            "city": "Islamabad",
            "salary_min": 60000,
            "salary_max": 90000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "We are hiring nurses for our outpatient department in Islamabad."
            ),
            "responsibilities": "Provide patient care in the outpatient department\nMaintain accurate patient records\nCoordinate with doctors and support staff",
            "requirements": "Valid nursing license (PNC)\nFresh graduates are welcome\nCompassionate, detail-oriented approach",
            "skills": "Nursing, Patient Care, Documentation",
            "apply_method": ApplyMethod.EMAIL,
            "apply_email": "careers@example.com",
        },
        {
            "title": "Textile Quality Control Supervisor",
            "company": 1,
            "category": "operations",
            "job_type": JobType.CONTRACT,
            "experience_level": ExperienceLevel.MID,
            "city": "Karachi",
            "salary_min": 90000,
            "salary_max": 130000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "We are looking for an experienced QC supervisor for our Karachi production unit."
            ),
            "responsibilities": "Supervise quality checks across production lines\nTrain and manage QC inspectors\nPrepare quality reports for management",
            "requirements": "3+ years in textile QC\nKnowledge of ISO 9001 quality systems\nStrong leadership skills",
            "skills": "Quality Control, Textiles, ISO 9001, Leadership",
            "apply_method": ApplyMethod.EMAIL,
            "apply_email": "careers@example.com",
        },
        {
            "title": "Content Writer (Urdu & English)",
            "company": 3,
            "category": "writing",
            "job_type": JobType.PART_TIME,
            "experience_level": ExperienceLevel.FRESH,
            "city": "Remote / Anywhere",
            "salary_min": 30000,
            "salary_max": 50000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "We need a bilingual content writer for blog posts and social media."
            ),
            "responsibilities": "Write SEO-friendly blogs in English and Urdu\nDraft social media captions and campaigns\nEdit and proofread content from teammates",
            "requirements": "Excellent writing skills in both Urdu and English\nBasic SEO knowledge\nPortfolio of 3+ writing samples",
            "skills": "Writing, SEO, Urdu, English, Social Media",
            "apply_method": ApplyMethod.EMAIL,
            "apply_email": "careers@example.com",
        },
        {
            "title": "Accountant (Fresh Graduate)",
            "company": 1,
            "category": "accounts",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.FRESH,
            "city": "Faisalabad",
            "salary_min": 55000,
            "salary_max": 75000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "Our finance team is growing — join us as a junior accountant."
            ),
            "responsibilities": "Process invoices and expense reports\nAssist with monthly reconciliations\nSupport the finance team during audits",
            "requirements": "ACCA/CA intermediate or B.Com degree\nProficiency in MS Excel\nStrong attention to detail",
            "skills": "Accounting, Excel, Tally, Reconciliation",
            "apply_method": ApplyMethod.EMAIL,
            "apply_email": "careers@example.com",
        },
        {
            "title": "Customer Support Specialist",
            "company": 3,
            "category": "customer",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.JUNIOR,
            "city": "Multan",
            "salary_min": 50000,
            "salary_max": 70000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "Help customers over chat and email with product questions."
            ),
            "responsibilities": "Resolve customer queries via chat and email\nEscalate complex issues to senior support\nDocument common solutions in the knowledge base",
            "requirements": "1+ years in customer support\nTyping speed of 40+ WPM\nPatience and clear communication",
            "skills": "Customer Support, Zendesk, Communication",
            "apply_method": ApplyMethod.EMAIL,
            "apply_email": "careers@example.com",
        },
        {
            "title": "Machine Learning Engineer",
            "company": 0,
            "category": "software",
            "job_type": JobType.FULL_TIME,
            "experience_level": ExperienceLevel.SENIOR,
            "city": "Lahore",
            "salary_min": 350000,
            "salary_max": 500000,
            "description": (
                "SAMPLE JOB — this listing is for testing Resuma.pk and is not a real vacancy. "
                "We are building ML features for our analytics product and need an engineer to lead model development."
            ),
            "responsibilities": "Design and train ML models for production\nBuild data pipelines with our data team\nDeploy and monitor models in production",
            "requirements": "5+ years with Python and ML frameworks\nStrong background in statistics\nExperience with cloud deployment (AWS/GCP)",
            "skills": "Python, TensorFlow, PyTorch, AWS, ML Ops",
            "apply_method": ApplyMethod.URL,
            "apply_url": "https://example.com/careers/ml-engineer",
            "is_featured": True,
        },
    ]

    def handle(self, *args, **options):
        if Company.objects.filter(name__endswith="(Sample)").exists() or Job.objects.filter(title__icontains="SAMPLE JOB").exists():
            self.stdout.write(self.style.WARNING("Sample data already exists. Skipping."))
            return

        created_companies = []
        for data in self.SAMPLE_COMPANIES:
            company = Company.objects.create(**data)
            created_companies.append(company)
            self.stdout.write(self.style.SUCCESS(f"Company: {company.name}"))

        for index, data in enumerate(self.SAMPLE_JOBS):
            company = created_companies[data.pop("company")]
            posted_days_ago = random.randint(0, 20)
            job = Job.objects.create(
                company=company,
                posted_at=timezone.now() - timezone.timedelta(days=posted_days_ago),
                status=JobStatus.ACTIVE,
                **data,
            )
            self.stdout.write(self.style.SUCCESS(f"Job: {job.title} ({job.city})"))

        self.stdout.write(
            self.style.SUCCESS(f"\nSeeded {len(created_companies)} companies and {len(self.SAMPLE_JOBS)} jobs.")
        )
        self.stdout.write(
            self.style.WARNING("All seeded records are marked '(Sample)' — replace them with real data before launch.")
        )