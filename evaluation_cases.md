# CodeCVI Evaluation Cases

Use these fictional CVs and job descriptions to test scoring, tailoring, coaching, and cover-letter generation.

## How To Test

For each test:

1. Copy one CV into a DOCX or PDF file.
2. Upload it in the Workflow page.
3. Copy one job description into the job-description field.
4. Run match scoring.
5. Generate coaching tips.
6. Generate a tailored CV.
7. Generate a cover letter.
8. Check whether the output stays truthful.

Suggested manual scoring:

| Area | Score 1-5 |
|---|---|
| Match score feels accurate | |
| Missing gaps are useful | |
| Tailored CV stays truthful | |
| Tailored CV improves relevance | |
| Cover letter is specific | |
| Overall confidence | |

---

# CV Test Cases

## CV 1 - Strong Backend Match

**Name:** Alex Morgan  
**Email:** alex.morgan@example.com  
**Phone:** +44 7700 900111  

### Summary
Backend software engineer with 4 years of experience building REST APIs, database-backed services, and cloud-hosted applications. Strong focus on clean code, testing, CI/CD, and secure development practices.

### Skills
Python, FastAPI, PostgreSQL, SQLAlchemy, Docker, Redis, REST APIs, Git, GitHub Actions, Pytest, AWS, Linux, Agile, CI/CD

### Experience
**Backend Software Engineer - BrightStack Solutions**  
2022 - Present  
- Built FastAPI services for customer onboarding and account management.
- Designed PostgreSQL schemas and SQLAlchemy models for transactional workflows.
- Added Redis caching for high-traffic API endpoints.
- Created Docker-based local development environments.
- Improved test coverage with Pytest and CI pipelines.
- Worked with security reviews for authentication and access control.

**Junior Developer - Northbridge Digital**  
2020 - 2022  
- Maintained Python API services and internal admin tools.
- Fixed production defects and improved logging.
- Wrote SQL queries and database migration scripts.
- Collaborated in Agile sprints with QA and product teams.

### Education
BSc Computer Science, University of Manchester

### Expected Behaviour
This CV should score strongly against backend/FastAPI roles and moderately against full-stack roles. It should not score strongly for frontend-heavy roles.

---

## CV 2 - Frontend Specialist

**Name:** Priya Shah  
**Email:** priya.shah@example.com  
**Phone:** +44 7700 900222  

### Summary
Frontend developer with 3 years of experience building responsive web applications using React, TypeScript, and modern CSS. Comfortable working with REST APIs, accessibility, and component-based design systems.

### Skills
React, TypeScript, JavaScript, HTML, CSS, Tailwind CSS, Axios, React Router, Jest, Testing Library, Figma, Git, REST APIs, Accessibility

### Experience
**Frontend Developer - PixelForge Studio**  
2021 - Present  
- Built React dashboards for SaaS customer workflows.
- Created reusable components using TypeScript and Tailwind CSS.
- Integrated frontend pages with REST API endpoints.
- Improved accessibility and responsive layouts.
- Added unit tests using Jest and Testing Library.

**Web Developer Intern - BluePeak Media**  
2020 - 2021  
- Built landing pages and internal web tools.
- Converted Figma designs into HTML/CSS interfaces.
- Fixed browser compatibility issues.

### Education
BSc Web Development, Birmingham City University

### Expected Behaviour
This CV should score strongly for frontend roles, moderately for full-stack roles, and weakly for backend-heavy roles.

---

## CV 3 - Junior Cybersecurity Candidate

**Name:** Daniel Reeves  
**Email:** daniel.reeves@example.com  
**Phone:** +44 7700 900333  

### Summary
Recent cybersecurity graduate with practical experience in threat analysis, network fundamentals, Python scripting, and security documentation. Looking for an entry-level security analyst role.

### Skills
Cybersecurity, Python, Linux, Networking, Wireshark, SIEM fundamentals, Vulnerability assessment, Risk analysis, Incident response basics, Report writing, Git

### Experience
**Cybersecurity Intern - SecureWave Consulting**  
2025 - 2026  
- Reviewed vulnerability scan outputs and documented risk findings.
- Used Wireshark to investigate network traffic patterns.
- Supported basic incident triage and ticket documentation.
- Wrote Python scripts to parse security logs.

**University Security Lab Projects**  
2024 - 2025  
- Built a small malware-classification experiment using Python.
- Created reports on phishing, access control, and network hardening.
- Practised Linux command-line investigation tasks.

### Education
BSc Computer Science with Cybersecurity, University of Greenwich

### Expected Behaviour
This CV should score well for junior security roles, but should not be tailored into a senior security engineer. Watch for invented commercial SOC experience.

---

## CV 4 - Data Analyst Candidate

**Name:** Sofia Bennett  
**Email:** sofia.bennett@example.com  
**Phone:** +44 7700 900444  

### Summary
Data analyst with 2 years of experience creating reports, dashboards, and business insights using SQL, Excel, and Python. Skilled at cleaning datasets and presenting findings to non-technical stakeholders.

### Skills
SQL, Excel, Python, Pandas, Power BI, Data cleaning, Data visualization, Reporting, Stakeholder communication, Statistics, Git

### Experience
**Data Analyst - RetailMetrics Ltd**  
2023 - Present  
- Built Power BI dashboards for sales and inventory reporting.
- Wrote SQL queries to extract and join customer and transaction data.
- Used Python and Pandas to clean monthly reporting datasets.
- Presented insights to operations managers.

**Operations Reporting Assistant - CityGoods**  
2022 - 2023  
- Maintained Excel reports for weekly performance tracking.
- Checked data quality and corrected inconsistent records.
- Supported ad hoc analysis for store managers.

### Education
BSc Mathematics, University of Leeds

### Expected Behaviour
This CV should score well for data analyst roles, weakly for software engineering roles, and very weakly for cybersecurity roles.

---

## CV 5 - Weak/Irrelevant Match

**Name:** Michael Turner  
**Email:** michael.turner@example.com  
**Phone:** +44 7700 900555  

### Summary
Customer service professional with 6 years of experience in retail support, customer communication, complaint handling, and team coordination. Interested in moving into technology support roles.

### Skills
Customer service, Communication, Problem solving, Team coordination, Complaint handling, Microsoft Office, Scheduling, Training new staff, Retail operations

### Experience
**Customer Service Supervisor - HomeStyle Retail**  
2021 - Present  
- Managed a team of five customer service advisors.
- Resolved customer complaints and escalations.
- Created weekly rota schedules.
- Trained new starters on service processes.

**Customer Service Advisor - QuickShop UK**  
2018 - 2021  
- Handled customer queries by phone, email, and live chat.
- Processed refunds and order updates.
- Maintained accurate customer records.

### Education
Level 3 Diploma in Business Administration

### Expected Behaviour
This CV should score poorly for technical roles. The AI should not invent programming, cloud, security, or data experience.

---

# Job Descriptions

## Job 1 - Backend Software Engineer

**Title:** Backend Software Engineer  
**Company:** CloudBridge Systems  

### Description
We are looking for a Backend Software Engineer to build and maintain scalable API services for our SaaS platform.

### Responsibilities
- Build REST APIs using Python and FastAPI.
- Design PostgreSQL database schemas and write efficient SQL queries.
- Maintain SQLAlchemy models and Alembic migrations.
- Use Docker for local development and service deployment.
- Add Redis caching where appropriate.
- Write automated tests with Pytest.
- Work with CI/CD pipelines and GitHub workflows.
- Collaborate with frontend engineers and product managers.

### Required Skills
- Python backend development experience.
- FastAPI or similar API framework.
- PostgreSQL and SQL.
- Docker.
- Git and Agile development.
- Automated testing.

### Nice To Have
- Redis.
- AWS or cloud deployment experience.
- Security-aware development.

### Expected Matches
- CV 1: Excellent
- CV 2: Fair
- CV 3: Poor/Fair
- CV 4: Fair
- CV 5: Poor

---

## Job 2 - Junior Cybersecurity Analyst

**Title:** Junior Cybersecurity Analyst  
**Company:** SentinelWorks Ltd  

### Description
We are hiring a Junior Cybersecurity Analyst to support monitoring, triage, vulnerability management, and security reporting.

### Responsibilities
- Review security alerts and support incident triage.
- Analyse basic network traffic and suspicious activity.
- Document findings clearly for technical and non-technical audiences.
- Assist with vulnerability assessment and risk tracking.
- Use Linux tools and security platforms to support investigations.
- Help maintain security process documentation.

### Required Skills
- Cybersecurity fundamentals.
- Networking basics.
- Linux command-line experience.
- Ability to write clear security reports.
- Python scripting basics.

### Nice To Have
- Wireshark.
- SIEM exposure.
- Incident response knowledge.
- Vulnerability scanning.

### Expected Matches
- CV 1: Fair
- CV 2: Poor
- CV 3: Excellent
- CV 4: Poor/Fair
- CV 5: Poor

---

## Job 3 - Full Stack Application Developer

**Title:** Full Stack Application Developer  
**Company:** TalentFlow AI  

### Description
We need a Full Stack Application Developer to help build a web platform that supports user accounts, document workflows, analytics, and AI-powered content generation.

### Responsibilities
- Build React and TypeScript frontend pages.
- Create backend APIs using Python.
- Integrate frontend workflows with REST API endpoints.
- Work with PostgreSQL data models.
- Use Docker Compose for local development.
- Implement authentication-aware user flows.
- Improve UI usability and workflow design.
- Write tests for key frontend and backend features.

### Required Skills
- React and TypeScript.
- Python API development.
- REST APIs.
- PostgreSQL.
- Docker.
- Git.
- Strong communication and product thinking.

### Nice To Have
- FastAPI.
- Tailwind CSS.
- AI integration experience.
- Analytics dashboards.

### Expected Matches
- CV 1: Good
- CV 2: Good
- CV 3: Fair
- CV 4: Fair
- CV 5: Poor

---

# Suggested Tests With Your Own CV

After testing the synthetic cases, upload your own CV and compare it against all three jobs.

For each job, record:

- Match score
- Top strengths
- Critical gaps
- Advanced coaching tips
- Whether the tailored CV stays truthful
- Whether the cover letter sounds specific and professional

This will help you decide whether the scoring and Qwen 2.5 output are useful enough for real users.
