import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection


app = Flask(__name__)
def normalize_branch(branch):
    if not branch:
        return ""

    value = " ".join(branch.strip().upper().split())

    aliases = {
        "CSE": "COMPUTER SCIENCE ENGINEERING",
        "COMPUTER SCIENCE ENGINEERING": "COMPUTER SCIENCE ENGINEERING",

        "ECE": "ELECTRONICS AND COMMUNICATION ENGINEERING",
        "ELECTRONICS AND COMMUNICATION ENGINEERING":
            "ELECTRONICS AND COMMUNICATION ENGINEERING",

        "EEE": "ELECTRICAL AND ELECTRONICS ENGINEERING",
        "ELECTRICAL AND ELECTRONICS ENGINEERING":
            "ELECTRICAL AND ELECTRONICS ENGINEERING",

        "IE": "INSTRUMENTATION ENGINEERING",
        "INSTRUMENTATION ENGINEERING":
            "INSTRUMENTATION ENGINEERING",
    }

    return aliases.get(value, value)

# Secret key for sessions and flash messages
app.secret_key = "placement-management-secret-key"


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# STUDENT LOGIN
# =========================================================

@app.route("/student/login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("student_login"))

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM students
                WHERE institute_email = %s
            """, (email,))

            student = cursor.fetchone()

            if student is None:
                flash(
                    "Invalid institute email or password.",
                    "danger"
                )
                return redirect(url_for("student_login"))

            if not check_password_hash(
                student["password"],
                password
            ):
                flash(
                    "Invalid institute email or password.",
                    "danger"
                )
                return redirect(url_for("student_login"))

            session.clear()
            session["student_id"] = student["id"]

            if student["profile_completed"]:
                return redirect(url_for("student_dashboard"))

            return redirect(url_for("student_profile"))

        except Exception as e:

            print("STUDENT LOGIN ERROR:", e)

            flash(
                "Something went wrong. Please try again.",
                "danger"
            )

            return redirect(url_for("student_login"))

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("student_login.html")


# =========================================================
# STUDENT REGISTRATION
# =========================================================

@app.route("/student/register", methods=["GET", "POST"])
def student_register():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash(
                "Email and password are required.",
                "danger"
            )
            return redirect(url_for("student_register"))

        if not email.endswith("@nits.ac.in"):
            flash(
                "Please use your NITS institute email.",
                "danger"
            )
            return redirect(url_for("student_register"))

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )
            return redirect(url_for("student_register"))

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id
                FROM students
                WHERE institute_email = %s
            """, (email,))

            existing_student = cursor.fetchone()

            if existing_student:

                flash(
                    "This institute email is already registered.",
                    "danger"
                )

                return redirect(
                    url_for("student_register")
                )

            hashed_password = generate_password_hash(password)

            cursor.execute("""
                INSERT INTO students
                (
                    institute_email,
                    password
                )
                VALUES
                (
                    %s,
                    %s
                )
            """, (
                email,
                hashed_password
            ))

            connection.commit()

            flash(
                "Registration successful! Please login.",
                "success"
            )

            return redirect(
                url_for("student_login")
            )

        except Exception as e:

            if connection:
                connection.rollback()

            print(
                "STUDENT REGISTRATION ERROR:",
                e
            )

            flash(
                f"Registration failed: {e}",
                "danger"
            )

            return redirect(
                url_for("student_register")
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("student_register.html")


# =========================================================
# STUDENT PROFILE
# =========================================================

@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        gmail = request.form.get("gmail", "").strip()
        cgpa = request.form.get("cgpa", "").strip()
        tenth = request.form.get("tenth", "").strip()
        twelfth = request.form.get("twelfth", "").strip()
        branch = request.form.get("branch", "").strip()
        graduation_year = request.form.get(
            "graduation_year",
            ""
        ).strip()
        preferred_roles = request.form.get(
            "preferred_roles",
            ""
        ).strip()
        skills = request.form.get(
            "skills",
            ""
        ).strip()
        resume_link = request.form.get(
            "resume_link",
            ""
        ).strip()

        if not name or not phone or not gmail:

            flash(
                "Name, phone and Gmail are required.",
                "danger"
            )

            return redirect(
                url_for("student_profile")
            )

        if not cgpa or not tenth or not twelfth:

            flash(
                "Please enter your academic details.",
                "danger"
            )

            return redirect(
                url_for("student_profile")
            )

        if not branch or not graduation_year:

            flash(
                "Branch and graduation year are required.",
                "danger"
            )

            return redirect(
                url_for("student_profile")
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE students
                SET
                    name = %s,
                    phone = %s,
                    gmail = %s,
                    cgpa = %s,
                    tenth_percentage = %s,
                    twelfth_percentage = %s,
                    branch = %s,
                    graduation_year = %s,
                    preferred_roles = %s,
                    skills = %s,
                    resume_link = %s,
                    profile_completed = TRUE
                WHERE id = %s
            """, (
                name,
                phone,
                gmail,
                cgpa,
                tenth,
                twelfth,
                branch,
                graduation_year,
                preferred_roles,
                skills,
                resume_link,
                student_id
            ))

            connection.commit()

            flash(
                "Profile completed successfully!",
                "success"
            )

            return redirect(
                url_for("student_dashboard")
            )

        except Exception as e:

            if connection:
                connection.rollback()

            print(
                "PROFILE UPDATE ERROR:",
                e
            )

            flash(
                f"Profile update failed: {e}",
                "danger"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("student_profile.html")


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/student/dashboard")
def student_dashboard():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM students
            WHERE id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:
            session.clear()
            return redirect(url_for("student_login"))

        cursor.execute("""
            SELECT
                jobs.*,
                companies.name AS company_name
            FROM jobs
            JOIN companies
                ON jobs.company_id = companies.id
            WHERE jobs.status = 'Open'
            ORDER BY jobs.created_at DESC
        """)

        jobs = cursor.fetchall()

        for job in jobs:
            eligible = True
            reason = ""

            if job["min_cgpa"] is not None:
                if (
                    student["cgpa"] is None
                    or student["cgpa"] < job["min_cgpa"]
                ):
                    eligible = False
                    reason = (
                        "Your CGPA is below "
                        "the required CGPA."
                    )

            if eligible and job["min_10th"] is not None:
                if (
                    student["tenth_percentage"] is None
                    or student["tenth_percentage"] < job["min_10th"]
                ):
                    eligible = False
                    reason = (
                        "Your 10th percentage is below "
                        "the required percentage."
                    )

            if eligible and job["min_12th"] is not None:
                if (
                    student["twelfth_percentage"] is None
                    or student["twelfth_percentage"] < job["min_12th"]
                ):
                    eligible = False
                    reason = (
                        "Your 12th percentage is below "
                        "the required percentage."
                    )

            if (
                eligible
                and job["graduation_year"] is not None
            ):
                if (
                    student["graduation_year"] is None
                    or student["graduation_year"] != job["graduation_year"]
                ):
                    eligible = False
                    reason = "Your graduation year does not match."

            if eligible and job["eligible_branches"]:
                branches = [
                    normalize_branch(branch)
                    for branch in job["eligible_branches"].split(",")
                ]

                student_branch = normalize_branch(student["branch"])

                if student_branch not in branches:
                    eligible = False
                    reason = (
                        "Your branch is not eligible "
                        "for this job."
                    )

            if not student["profile_completed"]:
                eligible = False
                reason = "Please complete your profile."

            job["eligible"] = eligible
            job["eligibility_reason"] = reason

        cursor.execute("""
            SELECT
                applications.id,
                applications.status,
                applications.applied_at,
                applications.job_id,
                jobs.role,
                companies.name AS company_name
            FROM applications
            JOIN jobs
                ON applications.job_id = jobs.id
            JOIN companies
                ON jobs.company_id = companies.id
            WHERE applications.student_id = %s
            ORDER BY applications.applied_at DESC
        """, (student_id,))

        applications = cursor.fetchall()

        applied_job_ids = [
            application["job_id"]
            for application in applications
        ]

        return render_template(
            "student_dashboard.html",
            student=student,
            jobs=jobs,
            applications=applications,
            applied_job_ids=applied_job_ids
        )

    except Exception as e:
        print(
            "STUDENT DASHBOARD ERROR:",
            e
        )

        flash(
            f"Could not load dashboard: {e}",
            "danger"
        )

        return redirect(
            url_for("student_login")
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# STUDENT JOB DETAILS
# =========================================================

@app.route("/student/job/<int:job_id>")
def student_job_details(job_id):

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM students
            WHERE id = %s
        """, (session["student_id"],))

        student = cursor.fetchone()

        if student is None:

            session.clear()

            return redirect(
                url_for("student_login")
            )

        cursor.execute("""
            SELECT
                jobs.*,
                companies.name AS company_name,
                companies.location AS company_location,
                companies.website AS company_website
            FROM jobs
            JOIN companies
                ON jobs.company_id = companies.id
            WHERE jobs.id = %s
        """, (job_id,))

        job = cursor.fetchone()

        if job is None:

            flash(
                "Job not found.",
                "danger"
            )

            return redirect(
                url_for("student_dashboard")
            )

        cursor.execute("""
            SELECT
                id,
                status,
                applied_at,
                updated_at
            FROM applications
            WHERE student_id = %s
            AND job_id = %s
        """, (
            session["student_id"],
            job_id
        ))

        application = cursor.fetchone()

        eligible = True
        eligibility_reasons = []

        if not student["profile_completed"]:

            eligible = False

            eligibility_reasons.append(
                "Please complete your profile first."
            )

        if job["min_cgpa"] is not None:

            if student["cgpa"] is None:

                eligible = False

                eligibility_reasons.append(
                    "CGPA is required."
                )

            elif student["cgpa"] < job["min_cgpa"]:

                eligible = False

                eligibility_reasons.append(
                    f"Minimum CGPA required: "
                    f"{job['min_cgpa']}"
                )

        if job["min_10th"] is not None:

            if student["tenth_percentage"] is None:

                eligible = False

                eligibility_reasons.append(
                    "10th percentage is required."
                )

            elif (
                student["tenth_percentage"]
                < job["min_10th"]
            ):

                eligible = False

                eligibility_reasons.append(
                    f"Minimum 10th percentage required: "
                    f"{job['min_10th']}%"
                )

        if job["min_12th"] is not None:

            if student["twelfth_percentage"] is None:

                eligible = False

                eligibility_reasons.append(
                    "12th percentage is required."
                )

            elif (
                student["twelfth_percentage"]
                < job["min_12th"]
            ):

                eligible = False

                eligibility_reasons.append(
                    f"Minimum 12th percentage required: "
                    f"{job['min_12th']}%"
                )

        if job["graduation_year"] is not None:

            if student["graduation_year"] is None:

                eligible = False

                eligibility_reasons.append(
                    "Graduation year is required."
                )

            elif (
                student["graduation_year"]
                != job["graduation_year"]
            ):

                eligible = False

                eligibility_reasons.append(
                    f"Graduation year must be "
                    f"{job['graduation_year']}."
                )

        if job["eligible_branches"]:

            eligible_branches = [
                normalize_branch(branch)
                for branch in
                job["eligible_branches"].split(",")
            ]

            student_branch = normalize_branch(
                student["branch"]
            )

            if student_branch not in eligible_branches:

                eligible = False

                eligibility_reasons.append(
                    "Your branch is not eligible "
                    "for this job."
                )

        if job["status"] != "Open":

            eligible = False

            eligibility_reasons.append(
                "This placement drive is closed."
            )

        return render_template(
            "job_details.html",
            job=job,
            student=student,
            application=application,
            eligible=eligible,
            eligibility_reasons=eligibility_reasons
        )

    except Exception as e:

        print(
            "JOB DETAILS ERROR:",
            e
        )

        flash(
            f"Could not load job details: {e}",
            "danger"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# STUDENT APPLY
# =========================================================

@app.route(
    "/student/apply/<int:job_id>",
    methods=["POST"]
)
def student_apply(job_id):

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM students
            WHERE id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:

            session.clear()

            return redirect(
                url_for("student_login")
            )

        cursor.execute("""
            SELECT *
            FROM jobs
            WHERE id = %s
        """, (job_id,))

        job = cursor.fetchone()

        if job is None:

            flash(
                "Job not found.",
                "danger"
            )

            return redirect(
                url_for("student_dashboard")
            )

        if not student["profile_completed"]:

            flash(
                "Please complete your profile before applying.",
                "warning"
            )

            return redirect(
                url_for("student_profile")
            )

        if job["status"] != "Open":

            flash(
                "This job is no longer accepting applications.",
                "danger"
            )

            return redirect(
                url_for(
                    "student_job_details",
                    job_id=job_id
                )
            )

        eligible = True

        if job["min_cgpa"] is not None:

            if (
                student["cgpa"] is None
                or student["cgpa"] < job["min_cgpa"]
            ):
                eligible = False

        if job["min_10th"] is not None:

            if (
                student["tenth_percentage"] is None
                or
                student["tenth_percentage"]
                < job["min_10th"]
            ):
                eligible = False

        if job["min_12th"] is not None:

            if (
                student["twelfth_percentage"] is None
                or
                student["twelfth_percentage"]
                < job["min_12th"]
            ):
                eligible = False

        if job["graduation_year"] is not None:

            if (
                student["graduation_year"] is None
                or
                student["graduation_year"]
                != job["graduation_year"]
            ):
                eligible = False

        if job["eligible_branches"]:

            branches = [
                normalize_branch(branch)
                for branch in
                job["eligible_branches"].split(",")
            ]

            student_branch = normalize_branch(
                student["branch"]
            )

            if student_branch not in branches:
                eligible = False

        if not eligible:

            flash(
                "You are not eligible for this job.",
                "danger"
            )

            return redirect(
                url_for(
                    "student_job_details",
                    job_id=job_id
                )
            )

        cursor.execute("""
            SELECT id
            FROM applications
            WHERE student_id = %s
            AND job_id = %s
        """, (
            student_id,
            job_id
        ))

        existing_application = cursor.fetchone()

        if existing_application:

            flash(
                "You have already applied for this job.",
                "info"
            )

            return redirect(
                url_for(
                    "student_job_details",
                    job_id=job_id
                )
            )

        cursor.execute("""
            INSERT INTO applications
            (
                student_id,
                job_id,
                status
            )
            VALUES
            (
                %s,
                %s,
                'Applied'
            )
        """, (
            student_id,
            job_id
        ))

        connection.commit()

        flash(
            "Application submitted successfully!",
            "success"
        )

        return redirect(
            url_for(
                "student_job_details",
                job_id=job_id
            )
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "APPLICATION ERROR:",
            e
        )

        flash(
            f"Application failed: {e}",
            "danger"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# STUDENT APPLICATIONS
# =========================================================

@app.route("/student/applications")
def student_applications():

    if "student_id" not in session:
        return redirect(url_for("student_login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                applications.id AS application_id,
                applications.status,
                applications.applied_at,
                applications.updated_at,

                jobs.id AS job_id,
                jobs.role,
                jobs.job_type,
                jobs.package,
                jobs.location,
                jobs.deadline,
                jobs.status AS job_status,

                companies.name AS company_name

            FROM applications

            JOIN jobs
                ON applications.job_id = jobs.id

            JOIN companies
                ON jobs.company_id = companies.id

            WHERE applications.student_id = %s

            ORDER BY applications.applied_at DESC
        """, (
            session["student_id"],
        ))

        applications = cursor.fetchall()

        return render_template(
            "student_applications.html",
            applications=applications
        )

    except Exception as e:

        print(
            "STUDENT APPLICATIONS ERROR:",
            e
        )

        flash(
            f"Could not load applications: {e}",
            "danger"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# COORDINATOR REGISTRATION
# =========================================================

@app.route(
    "/coordinator/register",
    methods=["GET", "POST"]
)
def coordinator_register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not password:

            flash(
                "All fields are required.",
                "danger"
            )

            return redirect(
                url_for("coordinator_register")
            )

        if "@" not in email:

            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(
                url_for("coordinator_register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("coordinator_register")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("coordinator_register")
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            cursor.execute("""
                SELECT id
                FROM coordinators
                WHERE email = %s
            """, (email,))

            existing_coordinator = cursor.fetchone()

            if existing_coordinator:

                flash(
                    "This email is already registered.",
                    "danger"
                )

                return redirect(
                    url_for("coordinator_register")
                )

            hashed_password = generate_password_hash(
                password
            )

            cursor.execute("""
                INSERT INTO coordinators
                (
                    name,
                    email,
                    password
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
            """, (
                name,
                email,
                hashed_password
            ))

            connection.commit()

            flash(
                "Coordinator account created successfully! Please login.",
                "success"
            )

            return redirect(
                url_for("coordinator_login")
            )

        except Exception as e:

            if connection:
                connection.rollback()

            print(
                "COORDINATOR REGISTRATION ERROR:",
                e
            )

            flash(
                f"Registration failed: {e}",
                "danger"
            )

            return redirect(
                url_for("coordinator_register")
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "coordinator_register.html"
    )


# =========================================================
# COORDINATOR LOGIN
# =========================================================

@app.route(
    "/coordinator/login",
    methods=["GET", "POST"]
)
def coordinator_login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Email and password are required.",
                "danger"
            )

            return redirect(
                url_for("coordinator_login")
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute("""
                SELECT *
                FROM coordinators
                WHERE email = %s
            """, (email,))

            coordinator = cursor.fetchone()

            if coordinator is None:

                flash(
                    "Invalid email or password.",
                    "danger"
                )

                return redirect(
                    url_for("coordinator_login")
                )

            if not check_password_hash(
                coordinator["password"],
                password
            ):

                flash(
                    "Invalid email or password.",
                    "danger"
                )

                return redirect(
                    url_for("coordinator_login")
                )

            session.clear()

            session["coordinator_id"] = (
                coordinator["id"]
            )

            session["coordinator_name"] = (
                coordinator["name"]
            )

            return redirect(
                url_for("coordinator_dashboard")
            )

        except Exception as e:

            print(
                "COORDINATOR LOGIN ERROR:",
                e
            )

            flash(
                "Something went wrong. Please try again.",
                "danger"
            )

            return redirect(
                url_for("coordinator_login")
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "coordinator_login.html"
    )


# =========================================================
# COORDINATOR DASHBOARD
# =========================================================

@app.route("/coordinator/dashboard")
def coordinator_dashboard():

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    return render_template(
        "coordinator_dashboard.html",
        coordinator_name=session.get(
            "coordinator_name"
        )
    )


# =========================================================
# ADD COMPANY
# =========================================================

@app.route(
    "/coordinator/company/add",
    methods=["GET", "POST"]
)
def add_company():

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        website = request.form.get(
            "website",
            ""
        ).strip()

        if not name:

            flash(
                "Company name is required.",
                "danger"
            )

            return redirect(
                url_for("add_company")
            )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO companies
                (
                    name,
                    location,
                    website
                )
                VALUES
                (
                    %s,
                    %s,
                    %s
                )
            """, (
                name,
                location,
                website
            ))

            connection.commit()

            flash(
                "Company added successfully!",
                "success"
            )

            return redirect(
                url_for("company_list")
            )

        except Exception as e:

            if connection:
                connection.rollback()

            print(
                "ADD COMPANY ERROR:",
                e
            )

            flash(
                f"Failed to add company: {e}",
                "danger"
            )

            return redirect(
                url_for("add_company")
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "add_company.html"
    )


# =========================================================
# COMPANY LIST
# =========================================================

@app.route("/coordinator/companies")
def company_list():

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT *
            FROM companies
            ORDER BY created_at DESC
        """)

        companies = cursor.fetchall()

        return render_template(
            "company_list.html",
            companies=companies
        )

    except Exception as e:

        print(
            "COMPANY LIST ERROR:",
            e
        )

        flash(
            f"Could not load companies: {e}",
            "danger"
        )

        return redirect(
            url_for("coordinator_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# ADD JOB
# =========================================================

@app.route(
    "/coordinator/job/add",
    methods=["GET", "POST"]
)
def add_job():

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT
                id,
                name
            FROM companies
            ORDER BY name
        """)

        companies = cursor.fetchall()

        if request.method == "POST":

            company_id = request.form.get(
                "company_id"
            )

            role = request.form.get(
                "role",
                ""
            ).strip()

            job_type = request.form.get(
                "job_type",
                ""
            ).strip()

            package = request.form.get(
                "package",
                ""
            ).strip()

            location = request.form.get(
                "location",
                ""
            ).strip()

            min_cgpa = request.form.get(
                "min_cgpa",
                ""
            ).strip()

            min_10th = request.form.get(
                "min_10th",
                ""
            ).strip()

            min_12th = request.form.get(
                "min_12th",
                ""
            ).strip()

            eligible_branches = request.form.get(
                "eligible_branches",
                ""
            ).strip()

            graduation_year = request.form.get(
                "graduation_year",
                ""
            ).strip()

            required_skills = request.form.get(
                "required_skills",
                ""
            ).strip()

            description = request.form.get(
                "description",
                ""
            ).strip()

            selection_process = request.form.get(
                "selection_process",
                ""
            ).strip()

            deadline = request.form.get(
                "deadline",
                ""
            ).strip()

            if not company_id or not role:

                flash(
                    "Company and job role are required.",
                    "danger"
                )

                return redirect(
                    url_for("add_job")
                )

            if (
                not min_cgpa
                or not min_10th
                or not min_12th
            ):

                flash(
                    "Please enter all academic eligibility criteria.",
                    "danger"
                )

                return redirect(
                    url_for("add_job")
                )

            if not eligible_branches:

                flash(
                    "Please enter at least one eligible branch.",
                    "danger"
                )

                return redirect(
                    url_for("add_job")
                )

            if not graduation_year:

                flash(
                    "Graduation year is required.",
                    "danger"
                )

                return redirect(
                    url_for("add_job")
                )

            cursor.execute("""
                INSERT INTO jobs
                (
                    company_id,
                    role,
                    job_type,
                    package,
                    location,
                    min_cgpa,
                    min_10th,
                    min_12th,
                    eligible_branches,
                    graduation_year,
                    required_skills,
                    description,
                    selection_process,
                    deadline,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'Open'
                )
            """, (
                company_id,
                role,
                job_type,
                package if package else None,
                location,
                min_cgpa,
                min_10th,
                min_12th,
                eligible_branches,
                graduation_year,
                required_skills,
                description,
                selection_process,
                deadline if deadline else None
            ))

            connection.commit()

            flash(
                "Job posted successfully!",
                "success"
            )

            return redirect(
                url_for("job_list")
            )

        return render_template(
            "add_job.html",
            companies=companies
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "ADD JOB ERROR:",
            e
        )

        flash(
            f"Failed to post job: {e}",
            "danger"
        )

        return redirect(
            url_for("coordinator_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# JOB LIST
# =========================================================

@app.route("/coordinator/jobs")
def job_list():

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT
                jobs.*,
                companies.name AS company_name,

                (
                    SELECT COUNT(*)
                    FROM applications
                    WHERE applications.job_id = jobs.id
                ) AS applicant_count

            FROM jobs

            JOIN companies
                ON jobs.company_id = companies.id

            ORDER BY jobs.created_at DESC
        """)

        jobs = cursor.fetchall()

        return render_template(
            "job_list.html",
            jobs=jobs
        )

    except Exception as e:

        print(
            "JOB LIST ERROR:",
            e
        )

        flash(
            f"Could not load jobs: {e}",
            "danger"
        )

        return redirect(
            url_for("coordinator_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# EDIT JOB
# =========================================================

@app.route(
    "/coordinator/job/<int:job_id>/edit",
    methods=["GET", "POST"]
)
def edit_job(job_id):

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT
                id,
                name
            FROM companies
            ORDER BY name
        """)

        companies = cursor.fetchall()

        cursor.execute("""
            SELECT *
            FROM jobs
            WHERE id = %s
        """, (job_id,))

        job = cursor.fetchone()

        if job is None:

            flash(
                "Job not found.",
                "danger"
            )

            return redirect(
                url_for("job_list")
            )

        if request.method == "POST":

            company_id = request.form.get(
                "company_id"
            )

            role = request.form.get(
                "role",
                ""
            ).strip()

            job_type = request.form.get(
                "job_type",
                ""
            ).strip()

            package = request.form.get(
                "package",
                ""
            ).strip()

            location = request.form.get(
                "location",
                ""
            ).strip()

            min_cgpa = request.form.get(
                "min_cgpa",
                ""
            ).strip()

            min_10th = request.form.get(
                "min_10th",
                ""
            ).strip()

            min_12th = request.form.get(
                "min_12th",
                ""
            ).strip()

            eligible_branches = request.form.get(
                "eligible_branches",
                ""
            ).strip()

            graduation_year = request.form.get(
                "graduation_year",
                ""
            ).strip()

            required_skills = request.form.get(
                "required_skills",
                ""
            ).strip()

            description = request.form.get(
                "description",
                ""
            ).strip()

            selection_process = request.form.get(
                "selection_process",
                ""
            ).strip()

            deadline = request.form.get(
                "deadline",
                ""
            ).strip()

            if not company_id or not role:

                flash(
                    "Company and job role are required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "edit_job",
                        job_id=job_id
                    )
                )

            if (
                not min_cgpa
                or not min_10th
                or not min_12th
            ):

                flash(
                    "Please enter all academic eligibility criteria.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "edit_job",
                        job_id=job_id
                    )
                )

            if not eligible_branches:

                flash(
                    "Please enter at least one eligible branch.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "edit_job",
                        job_id=job_id
                    )
                )

            if not graduation_year:

                flash(
                    "Graduation year is required.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "edit_job",
                        job_id=job_id
                    )
                )

            cursor.execute("""
                UPDATE jobs
                SET
                    company_id = %s,
                    role = %s,
                    job_type = %s,
                    package = %s,
                    location = %s,
                    min_cgpa = %s,
                    min_10th = %s,
                    min_12th = %s,
                    eligible_branches = %s,
                    graduation_year = %s,
                    required_skills = %s,
                    description = %s,
                    selection_process = %s,
                    deadline = %s
                WHERE id = %s
            """, (
                company_id,
                role,
                job_type,
                package if package else None,
                location,
                min_cgpa,
                min_10th,
                min_12th,
                eligible_branches,
                graduation_year,
                required_skills,
                description,
                selection_process,
                deadline if deadline else None,
                job_id
            ))

            connection.commit()

            flash(
                "Job updated successfully!",
                "success"
            )

            return redirect(
                url_for("job_list")
            )

        return render_template(
            "edit_job.html",
            job=job,
            companies=companies
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "EDIT JOB ERROR:",
            e
        )

        flash(
            f"Failed to update job: {e}",
            "danger"
        )

        return redirect(
            url_for("job_list")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# CLOSE JOB
# =========================================================

@app.route(
    "/coordinator/job/<int:job_id>/close",
    methods=["POST"]
)
def close_job(job_id):

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE jobs
            SET status = 'Closed'
            WHERE id = %s
        """, (job_id,))

        connection.commit()

        flash(
            "Placement drive closed successfully.",
            "success"
        )

        return redirect(
            url_for("job_list")
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "CLOSE JOB ERROR:",
            e
        )

        flash(
            f"Could not close job: {e}",
            "danger"
        )

        return redirect(
            url_for("job_list")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# VIEW APPLICANTS
# =========================================================

@app.route(
    "/coordinator/job/<int:job_id>/applicants"
)
def view_applicants(job_id):

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    search = request.args.get(
        "search",
        ""
    ).strip()

    branch = request.args.get(
        "branch",
        ""
    ).strip()

    status = request.args.get(
        "status",
        ""
    ).strip()

    min_cgpa = request.args.get(
        "min_cgpa",
        ""
    ).strip()

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT
                jobs.*,
                companies.name AS company_name
            FROM jobs
            JOIN companies
                ON jobs.company_id = companies.id
            WHERE jobs.id = %s
        """, (job_id,))

        job = cursor.fetchone()

        if not job:

            flash(
                "Job not found.",
                "danger"
            )

            return redirect(
                url_for("job_list")
            )

        query = """
            SELECT
                applications.id AS application_id,
                applications.status,
                applications.applied_at,
                applications.updated_at,

                students.id AS student_id,
                students.name,
                students.institute_email,
                students.gmail,
                students.phone,
                students.cgpa,
                students.tenth_percentage,
                students.twelfth_percentage,
                students.branch,
                students.graduation_year,
                students.skills,
                students.preferred_roles,
                students.resume_link

            FROM applications

            JOIN students
                ON applications.student_id = students.id

            WHERE applications.job_id = %s
        """

        params = [job_id]

        if search:

            query += """
                AND (
                    students.name LIKE %s
                    OR students.institute_email LIKE %s
                    OR students.gmail LIKE %s
                )
            """

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
                search_value
            ])

        if branch:

            query += """
                AND students.branch = %s
            """

            params.append(branch)

        if status:

            query += """
                AND applications.status = %s
            """

            params.append(status)

        if min_cgpa:

            try:

                cgpa_value = float(
                    min_cgpa
                )

                query += """
                    AND students.cgpa >= %s
                """

                params.append(
                    cgpa_value
                )

            except ValueError:
                pass

        query += """
            ORDER BY applications.applied_at DESC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        applicants = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT branch
            FROM students
            WHERE branch IS NOT NULL
            AND branch != ''
            ORDER BY branch
        """)

        branches = cursor.fetchall()

        return render_template(
            "applicants.html",
            job=job,
            applicants=applicants,
            branches=branches,
            search=search,
            selected_branch=branch,
            selected_status=status,
            min_cgpa=min_cgpa
        )

    except Exception as e:

        print(
            "VIEW APPLICANTS ERROR:",
            e
        )

        flash(
            f"Could not load applicants: {e}",
            "danger"
        )

        return redirect(
            url_for("job_list")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# UPDATE APPLICATION STATUS
# =========================================================

@app.route(
    "/coordinator/application/<int:application_id>/status",
    methods=["POST"]
)
def update_application_status(application_id):

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    new_status = request.form.get(
        "status",
        ""
    ).strip()

    allowed_statuses = [
        "Applied",
        "Shortlisted",
        "Assessment",
        "Interview",
        "Selected",
        "Rejected",
        "Withdrawn"
    ]

    if new_status not in allowed_statuses:

        flash(
            "Invalid application status.",
            "danger"
        )

        return redirect(
            url_for("job_list")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT job_id
            FROM applications
            WHERE id = %s
        """, (application_id,))

        application = cursor.fetchone()

        if application is None:

            flash(
                "Application not found.",
                "danger"
            )

            return redirect(
                url_for("job_list")
            )

        cursor.execute("""
            UPDATE applications
            SET status = %s
            WHERE id = %s
        """, (
            new_status,
            application_id
        ))

        connection.commit()

        flash(
            "Application status updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "view_applicants",
                job_id=application["job_id"]
            )
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "STATUS UPDATE ERROR:",
            e
        )

        flash(
            f"Could not update status: {e}",
            "danger"
        )

        return redirect(
            url_for("job_list")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PLACEMENT STATISTICS
# =========================================================

@app.route("/coordinator/statistics")
def placement_statistics():

    if "coordinator_id" not in session:

        return redirect(
            url_for("coordinator_login")
        )

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT COUNT(*) AS total_students
            FROM students
            WHERE profile_completed = TRUE
        """)

        total_students = (
            cursor.fetchone()["total_students"]
            or 0
        )

        cursor.execute("""
            SELECT COUNT(DISTINCT student_id)
            AS placed_students
            FROM applications
            WHERE status = 'Selected'
        """)

        placed_students = (
            cursor.fetchone()["placed_students"]
            or 0
        )

        unplaced_students = (
            total_students - placed_students
        )

        if unplaced_students < 0:
            unplaced_students = 0

        if total_students > 0:

            placement_percentage = round(
                (
                    placed_students
                    / total_students
                ) * 100,
                2
            )

        else:

            placement_percentage = 0

        cursor.execute("""
            SELECT DISTINCT branch
            FROM students
            WHERE profile_completed = TRUE
            AND branch IS NOT NULL
            AND branch != ''
            ORDER BY branch
        """)

        branch_list = cursor.fetchall()

        branch_statistics = []

        for branch_row in branch_list:

            branch = branch_row["branch"]

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM students
                WHERE profile_completed = TRUE
                AND branch = %s
            """, (branch,))

            total = (
                cursor.fetchone()["total"]
                or 0
            )

            cursor.execute("""
                SELECT COUNT(DISTINCT s.id) AS eligible

                FROM students s

                JOIN jobs j
                    ON j.status IN ('Open', 'Closed')

                WHERE s.profile_completed = TRUE
                AND s.branch = %s

                AND (
                    j.min_cgpa IS NULL
                    OR s.cgpa >= j.min_cgpa
                )

                AND (
                    j.min_10th IS NULL
                    OR s.tenth_percentage >= j.min_10th
                )

                AND (
                    j.min_12th IS NULL
                    OR s.twelfth_percentage >= j.min_12th
                )

                AND (
                    j.graduation_year IS NULL
                    OR s.graduation_year = j.graduation_year
                )

                AND (
                    j.eligible_branches IS NULL
                    OR j.eligible_branches = ''
                    OR FIND_IN_SET(
                        UPPER(s.branch),
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(
                                        UPPER(j.eligible_branches),
                                        'CSE',
                                        'COMPUTER SCIENCE ENGINEERING'
                                    ),
                                    'ECE',
                                    'ELECTRONICS AND COMMUNICATION ENGINEERING'
                                ),
                                'EEE',
                                'ELECTRICAL AND ELECTRONICS ENGINEERING'
                            ),
                            'IE',
                            'INSTRUMENTATION ENGINEERING'
                        )
                    )
                )
            """, (branch,))

            eligible = (
                cursor.fetchone()["eligible"]
                or 0
            )

            cursor.execute("""
                SELECT COUNT(DISTINCT a.student_id)
                AS placed

                FROM applications a

                JOIN students s
                    ON a.student_id = s.id

                WHERE s.branch = %s
                AND a.status = 'Selected'
            """, (branch,))

            placed = (
                cursor.fetchone()["placed"]
                or 0
            )

            unplaced = eligible - placed

            if unplaced < 0:
                unplaced = 0

            if total > 0:

                percentage = round(
                    (
                        placed / total
                    ) * 100,
                    2
                )

            else:

                percentage = 0

            branch_statistics.append({
                "branch": branch,
                "total": total,
                "eligible": eligible,
                "placed": placed,
                "unplaced": unplaced,
                "percentage": percentage
            })

        cursor.execute("""
            SELECT
                companies.name AS company_name,
                jobs.role,

                COUNT(
                    DISTINCT applications.id
                ) AS total_applications,

                COUNT(
                    DISTINCT CASE
                        WHEN applications.status = 'Selected'
                        THEN applications.student_id
                    END
                ) AS selected_students

            FROM jobs

            JOIN companies
                ON jobs.company_id = companies.id

            LEFT JOIN applications
                ON jobs.id = applications.job_id

            GROUP BY
                companies.id,
                companies.name,
                jobs.id,
                jobs.role

            ORDER BY selected_students DESC
        """)

        company_statistics = cursor.fetchall()

        return render_template(
            "placement_statistics.html",
            total_students=total_students,
            placed_students=placed_students,
            unplaced_students=unplaced_students,
            placement_percentage=placement_percentage,
            branch_statistics=branch_statistics,
            company_statistics=company_statistics
        )

    except Exception as e:

        print(
            "PLACEMENT STATISTICS ERROR:",
            e
        )

        flash(
            f"Could not load statistics: {e}",
            "danger"
        )

        return redirect(
            url_for("coordinator_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )