"""
Idempotent data migration seeding a demo account with sample job postings
and candidates, so the app is immediately explorable after `migrate`
without any manual setup.

Embeddings are computed at seed time via the same apps.common.ai.get_embedding
function used everywhere else (stub vectors if OPENAI_API_KEY isn't set,
which is expected/fine for this build - see apps/common/ai.py).

Guarded against duplicate inserts: re-running `migrate` (e.g. after a
`--fake` reset, or being re-applied in a squashed migration) will not
create a second demo user or duplicate rows, because the user is fetched
with get_or_create() and the job/candidate inserts are skipped entirely if
that user already has rows.
"""
from django.contrib.auth.hashers import make_password
from django.db import migrations

from apps.common.ai import get_embedding

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo12345"

JOB_POSTINGS = [
    {
        "title": "Backend Engineer",
        "description": (
            "We are looking for a Backend Engineer to design and maintain the REST "
            "APIs that power our product. You will work primarily in Python and "
            "Django, modelling data in PostgreSQL and writing clean, well-tested "
            "service code. Requirements: 3+ years building production REST APIs, "
            "strong SQL and relational database design skills, experience with "
            "Docker and CI/CD pipelines, and familiarity with cloud deployment on "
            "AWS. Bonus: experience with asynchronous task processing and API "
            "authentication/authorization patterns such as JWT."
        ),
    },
    {
        "title": "Data Analyst",
        "description": (
            "We are hiring a Data Analyst to turn raw operational data into "
            "actionable insight for our leadership team. You will write complex "
            "SQL queries against our data warehouse, build dashboards in Tableau "
            "or Power BI, and present findings to non-technical stakeholders. "
            "Requirements: advanced SQL, a solid grounding in statistics, "
            "experience with Python (pandas) for data cleaning, and the ability "
            "to clearly communicate quantitative findings in writing and in "
            "meetings. Experience with A/B testing analysis is a strong plus."
        ),
    },
    {
        "title": "Product Manager",
        "description": (
            "We are seeking a Product Manager to own the roadmap for our core "
            "platform. You will run user research, write clear product "
            "requirements, and work daily with engineering and design to ship "
            "features that solve real customer problems. Requirements: 4+ years "
            "of product management experience, a track record of shipping "
            "software products end to end, strong stakeholder communication "
            "skills, and comfort using prioritization frameworks (RICE, "
            "MoSCoW, etc.) to make trade-off decisions under ambiguity."
        ),
    },
    {
        "title": "Frontend Engineer",
        "description": (
            "We need a Frontend Engineer to build and maintain our customer-facing "
            "web application using React and TypeScript. You will own component "
            "architecture, state management, and performance, and you will care "
            "about accessibility as a first-class concern, not an afterthought. "
            "Requirements: 3+ years of production React experience, strong "
            "TypeScript skills, experience with modern build tooling (Vite or "
            "Webpack), and a working knowledge of WCAG accessibility guidelines. "
            "Experience with design systems is a plus."
        ),
    },
    {
        "title": "DevOps / Site Reliability Engineer",
        "description": (
            "We are looking for a DevOps / Site Reliability Engineer to help us "
            "run reliable, observable infrastructure at scale. You will manage "
            "our Kubernetes clusters, build and maintain CI/CD pipelines, and be "
            "part of an on-call rotation responding to production incidents. "
            "Requirements: hands-on experience with Kubernetes and Docker, "
            "infrastructure-as-code with Terraform, strong Linux fundamentals, "
            "and experience setting up monitoring/alerting (Prometheus, Grafana, "
            "or similar). Scripting ability in Python or Bash is required."
        ),
    },
]

CANDIDATES = [
    {
        "name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "resume_text": (
            "Backend software engineer with 6 years of experience building REST "
            "APIs in Python and Django, backed by PostgreSQL. Led the migration "
            "of a monolithic billing service into smaller, well-tested Django "
            "apps with clear ownership boundaries. Comfortable with Docker, "
            "writing CI/CD pipelines, and deploying services to AWS (ECS, RDS, "
            "S3). Enjoys mentoring junior engineers on API design and database "
            "indexing strategy."
        ),
    },
    {
        "name": "Marcus Chen",
        "email": "marcus.chen@example.com",
        "resume_text": (
            "Backend engineer with 4 years of experience across Node.js and Go, "
            "specializing in microservices architecture and message-queue-based "
            "systems. Built a payments reconciliation service handling millions "
            "of transactions per day. Strong SQL skills (Postgres and MySQL), "
            "comfortable with Kubernetes for deployment, and experienced writing "
            "integration tests for distributed systems."
        ),
    },
    {
        "name": "Fatima Al-Rashid",
        "email": "fatima.alrashid@example.com",
        "resume_text": (
            "Data analyst with 5 years of experience turning messy operational "
            "data into clear dashboards and recommendations for leadership. "
            "Expert in SQL window functions and query optimization, builds "
            "dashboards in Tableau, and uses Python/pandas for ad hoc analysis. "
            "Ran the analysis behind three major pricing experiments, each "
            "presented directly to the executive team with clear statistical "
            "reasoning."
        ),
    },
    {
        "name": "David Okafor",
        "email": "david.okafor@example.com",
        "resume_text": (
            "Data scientist with 3 years of experience building machine learning "
            "models for churn prediction and demand forecasting. Proficient in "
            "Python (pandas, scikit-learn, numpy), SQL, and experiment design for "
            "A/B tests. Published an internal report on customer segmentation "
            "that directly shaped the product roadmap. Comfortable presenting "
            "statistical findings to non-technical stakeholders."
        ),
    },
    {
        "name": "Elena Petrova",
        "email": "elena.petrova@example.com",
        "resume_text": (
            "Product manager with 7 years of experience shipping consumer and "
            "B2B SaaS products end to end. Led a cross-functional team of "
            "engineers and designers to launch a self-serve onboarding flow that "
            "increased activation by 18 percent. Runs structured user research, "
            "writes clear product requirement documents, and uses RICE scoring "
            "to prioritize a crowded backlog. Comfortable communicating roadmap "
            "trade-offs to executives and customers alike."
        ),
    },
    {
        "name": "James Whitfield",
        "email": "james.whitfield@example.com",
        "resume_text": (
            "Growth-focused product manager with 4 years of experience in B2B "
            "SaaS, owning the acquisition and activation funnels for a mid-market "
            "analytics product. Partnered closely with engineering to instrument "
            "funnels and run rapid experimentation cycles. Strong stakeholder "
            "communicator, comfortable presenting roadmap decisions to the board "
            "and aligning sales, marketing, and engineering around a single plan."
        ),
    },
    {
        "name": "Sofia Martinez",
        "email": "sofia.martinez@example.com",
        "resume_text": (
            "Frontend engineer with 5 years of experience building production "
            "React and TypeScript applications. Rebuilt a legacy jQuery "
            "dashboard into a modern React + TypeScript app with a component "
            "library used across three product teams. Deeply cares about "
            "accessibility, regularly audits pages against WCAG 2.1 AA, and has "
            "led performance work that cut time-to-interactive by 40 percent."
        ),
    },
    {
        "name": "Tariq Hassan",
        "email": "tariq.hassan@example.com",
        "resume_text": (
            "Full-stack developer with 4 years of experience across React on the "
            "frontend and Django REST Framework on the backend. Built and shipped "
            "a customer support portal end to end, including the Postgres schema, "
            "REST API, and React UI. Comfortable owning a feature from design "
            "through deployment, with a strong eye for clean API contracts "
            "between frontend and backend."
        ),
    },
    {
        "name": "Natasha Ivanova",
        "email": "natasha.ivanova@example.com",
        "resume_text": (
            "DevOps engineer with 5 years of experience running Kubernetes "
            "clusters in production for a fast-growing SaaS company. Wrote and "
            "maintains the Terraform modules that provision all cloud "
            "infrastructure on AWS. Built CI/CD pipelines that cut deployment "
            "time from 40 minutes to under 5. Set up Prometheus and Grafana "
            "monitoring with actionable on-call alerting."
        ),
    },
    {
        "name": "Benjamin Okoye",
        "email": "benjamin.okoye@example.com",
        "resume_text": (
            "Site reliability engineer with 6 years of experience keeping "
            "high-traffic services online. Led incident response for a payments "
            "platform processing significant daily transaction volume, "
            "authoring blameless postmortems after every major incident. Strong "
            "Python and Bash scripting skills for automation, deep experience "
            "with Docker and Kubernetes, and comfortable being the primary "
            "on-call escalation point."
        ),
    },
    {
        "name": "Lucas Ferreira",
        "email": "lucas.ferreira@example.com",
        "resume_text": (
            "Junior backend developer with one year of professional experience "
            "plus a strong internship background building small Flask and "
            "Python services. Completed a six-month internship building "
            "internal tooling with Python and PostgreSQL, including a REST API "
            "used by the support team. Eager to grow into a full backend "
            "engineering role, comfortable with Git, basic Docker usage, and "
            "writing unit tests."
        ),
    },
    {
        "name": "Hannah Kim",
        "email": "hannah.kim@example.com",
        "resume_text": (
            "UX/UI designer with 5 years of experience designing web "
            "applications, with enough frontend fluency to implement her own "
            "designs in React and CSS when needed. Led the visual redesign of a "
            "SaaS dashboard, running usability testing sessions to validate "
            "design decisions before implementation. Skilled in Figma, design "
            "systems, and basic HTML/CSS/JavaScript, though not a dedicated "
            "software engineer."
        ),
    },
]


def seed_demo_data(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    JobPosting = apps.get_model("jobs", "JobPosting")
    Candidate = apps.get_model("candidates", "Candidate")

    # get_or_create (not create_user/set_password) because this runs against
    # the *historical* model via apps.get_model, which only has the fields
    # and managers captured in migration state - AbstractUser/AbstractBaseUser
    # methods like set_password() aren't available on it, so the password is
    # hashed directly with Django's hasher instead.
    User.objects.get_or_create(
        email=DEMO_EMAIL,
        defaults={
            "first_name": "Demo",
            "last_name": "User",
            "is_active": True,
            "password": make_password(DEMO_PASSWORD),
        },
    )
    user = User.objects.get(email=DEMO_EMAIL)

    if not JobPosting.objects.filter(user=user).exists():
        for job in JOB_POSTINGS:
            text = f"{job['title']}\n{job['description']}"
            JobPosting.objects.create(
                user=user,
                title=job["title"],
                description=job["description"],
                embedding=get_embedding(text),
            )

    if not Candidate.objects.filter(user=user).exists():
        for candidate in CANDIDATES:
            Candidate.objects.create(
                user=user,
                name=candidate["name"],
                email=candidate["email"],
                resume_text=candidate["resume_text"],
                embedding=get_embedding(candidate["resume_text"]),
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("jobs", "0001_initial"),
        ("candidates", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_demo_data, noop_reverse),
    ]
