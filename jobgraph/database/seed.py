import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


def seed_database():

    with driver.session() as session:

        # Clear existing graph
        session.run(
            "MATCH (n) DETACH DELETE n"
        )

        # -------------------------
        # Skills
        # -------------------------

        skills = [
            "Python",
            "SQL",
            "JavaScript",
            "React",
            "Java",
            "FastAPI",
            "Docker",
            "AWS",
            "Git",
            "Machine Learning"
        ]

        for skill in skills:

            session.run(
                """
                MERGE (s:Skill {name: $name})
                """,
                name=skill
            )


        # -------------------------
        # Companies
        # -------------------------

        companies = [
            "TechNova",
            "CloudWorks",
            "DataSphere",
            "CodeCraft",
            "FinEdge"
        ]

        for company in companies:

            session.run(
                """
                MERGE (c:Company {name: $name})
                """,
                name=company
            )


        # -------------------------
        # Jobs
        # -------------------------

        jobs = [
            ("Backend Developer", "TechNova"),
            ("Full Stack Developer", "CodeCraft"),
            ("Data Analyst", "DataSphere"),
            ("Cloud Engineer", "CloudWorks"),
            ("Software Engineer", "FinEdge")
        ]

        for job_name, company_name in jobs:

            session.run(
                """
                MATCH (c:Company {name: $company_name})

                MERGE (j:Job {title: $job_name})

                MERGE (c)-[:OFFERS]->(j)
                """,
                job_name=job_name,
                company_name=company_name
            )


        # -------------------------
        # Job requirements
        # -------------------------

        requirements = {

            "Backend Developer": [
                "Python",
                "SQL",
                "FastAPI",
                "Git"
            ],

            "Full Stack Developer": [
                "JavaScript",
                "React",
                "SQL",
                "Git"
            ],

            "Data Analyst": [
                "Python",
                "SQL",
                "Machine Learning"
            ],

            "Cloud Engineer": [
                "Python",
                "Docker",
                "AWS",
                "Git"
            ],

            "Software Engineer": [
                "Java",
                "SQL",
                "Git"
            ]
        }


        for job_title, required_skills in requirements.items():

            for skill_name in required_skills:

                session.run(
                    """
                    MATCH (j:Job {title: $job_title})

                    MATCH (s:Skill {name: $skill_name})

                    MERGE (j)-[:REQUIRES]->(s)
                    """,
                    job_title=job_title,
                    skill_name=skill_name
                )


        # -------------------------
        # Related skills
        # -------------------------

        related_skills = [

            ("Python", "FastAPI"),

            ("Python", "Machine Learning"),

            ("JavaScript", "React"),

            ("Python", "Docker"),

            ("Docker", "AWS"),

            ("SQL", "Machine Learning")
        ]


        for skill1, skill2 in related_skills:

            session.run(
                """
                MATCH (s1:Skill {name: $skill1})

                MATCH (s2:Skill {name: $skill2})

                MERGE (s1)-[:RELATED_TO]->(s2)
                """,
                skill1=skill1,
                skill2=skill2
            )


        # -------------------------
        # Courses
        # -------------------------

        courses = [

            (
                "FastAPI Backend Development",
                "FastAPI"
            ),

            (
                "Python Machine Learning Fundamentals",
                "Machine Learning"
            ),

            (
                "Modern React Development",
                "React"
            ),

            (
                "Docker for Developers",
                "Docker"
            ),

            (
                "AWS Cloud Fundamentals",
                "AWS"
            ),

            (
                "Advanced SQL for Data Analysis",
                "SQL"
            )
        ]


        for course_name, skill_name in courses:

            session.run(
                """
                MATCH (s:Skill {name: $skill_name})

                MERGE (c:Course {
                    name: $course_name
                })

                MERGE (c)-[:TEACHES]->(s)
                """,
                course_name=course_name,
                skill_name=skill_name
            )


        print(
            "JobGraph database seeded successfully!"
        )


try:

    driver.verify_connectivity()

    print(
        "Connected to CognoDB"
    )

    seed_database()


finally:

    driver.close()