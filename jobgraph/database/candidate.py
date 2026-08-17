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


def create_candidate():

    with driver.session() as session:

        session.run(
            """
            MERGE (c:Candidate {
                name: $name,
                experience_level: $experience_level
            })

            WITH c

            UNWIND $skills AS skill_name

            MATCH (s:Skill {
                name: skill_name
            })

            MERGE (c)-[:HAS_SKILL]->(s)
            """,
            name="Ajay",
            experience_level="Fresher",
            skills=[
                "Python",
                "SQL",
                "Git"
            ]
        )

        print("Candidate created successfully!")


try:

    driver.verify_connectivity()

    print("Connected to CognoDB")

    create_candidate()

finally:

    driver.close()