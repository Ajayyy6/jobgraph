import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

app = Flask(__name__)

# --------------------------------
# CognoDB connection
# --------------------------------

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


# --------------------------------
# Home page
# --------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------
# Candidate profile
# --------------------------------

@app.route("/candidate", methods=["GET"])
def get_candidate():

    try:

        with driver.session() as session:

            result = session.run(
                """
                MATCH
                    (c:Candidate)-[:HAS_SKILL]->(s:Skill)

                RETURN
                    c.name AS name,
                    c.experience_level AS experience_level,
                    collect(s.name) AS skills

                LIMIT 1
                """
            )

            record = result.single()

            if record is None:

                return jsonify({
                    "error": "Candidate not found."
                }), 404

            return jsonify({
                "name": record["name"],
                "experience_level":
                    record["experience_level"],
                "skills": record["skills"]
            })

    except Exception as e:

        print("Candidate error:", e)

        return jsonify({
            "error": "Unable to load candidate."
        }), 500


# --------------------------------
# Related skills
# --------------------------------

@app.route("/skill-path", methods=["GET"])
def skill_path():

    try:

        with driver.session() as session:

            result = session.run(
                """
                MATCH
                    (c:Candidate)-[:HAS_SKILL]->(s:Skill)
                    -[:RELATED_TO]->(related:Skill)

                RETURN DISTINCT
                    s.name AS current_skill,
                    related.name AS recommended_skill

                ORDER BY
                    current_skill,
                    recommended_skill
                """
            )

            recommendations = []

            for record in result:

                recommendations.append({
                    "current_skill":
                        record["current_skill"],

                    "recommended_skill":
                        record["recommended_skill"]
                })

            return jsonify({
                "recommendations":
                    recommendations
            })

    except Exception as e:

        print("Skill path error:", e)

        return jsonify({
            "error":
                "Unable to load related skills."
        }), 500


# --------------------------------
# Focused career graph
# --------------------------------

@app.route("/graph", methods=["GET"])
def graph_data():

    try:

        with driver.session() as session:

            nodes = []
            edges = []

            node_ids = set()
            edge_keys = set()


            def add_node(
                node_id,
                label,
                node_type
            ):

                if node_id not in node_ids:

                    nodes.append({
                        "id": node_id,
                        "label": label,
                        "type": node_type
                    })

                    node_ids.add(node_id)


            def add_edge(
                source,
                target,
                label
            ):

                key = (
                    source,
                    target,
                    label
                )

                if key not in edge_keys:

                    edges.append({
                        "from": source,
                        "to": target,
                        "label": label
                    })

                    edge_keys.add(key)


            # --------------------------------
            # Candidate and candidate skills
            # --------------------------------

            candidate_result = session.run(
                """
                MATCH
                    (c:Candidate)-[:HAS_SKILL]->(s:Skill)

                RETURN
                    c.name AS candidate,
                    s.name AS skill
                """
            )

            candidate_skills = []


            for record in candidate_result:

                candidate_name = record["candidate"]
                skill = record["skill"]

                candidate_skills.append(skill)

                add_node(
                    "candidate",
                    candidate_name,
                    "candidate"
                )

                skill_id = "skill_" + skill

                add_node(
                    skill_id,
                    skill,
                    "skill"
                )

                add_edge(
                    "candidate",
                    skill_id,
                    "HAS_SKILL"
                )


            # --------------------------------
            # Related skills of candidate skills
            # --------------------------------

            related_result = session.run(
                """
                MATCH
                    (s:Skill)-[:RELATED_TO]->(r:Skill)

                WHERE
                    s.name IN $skills

                RETURN
                    s.name AS skill,
                    r.name AS related
                """,
                skills=candidate_skills
            )


            for record in related_result:

                skill = record["skill"]
                related = record["related"]

                skill_id = "skill_" + skill

                related_id = "related_" + related

                add_node(
                    skill_id,
                    skill,
                    "skill"
                )

                add_node(
                    related_id,
                    related,
                    "related"
                )

                add_edge(
                    skill_id,
                    related_id,
                    "RELATED_TO"
                )


            # --------------------------------
            # Jobs requiring candidate skills
            # --------------------------------

            job_result = session.run(
                """
                MATCH
                    (j:Job)-[:REQUIRES]->(s:Skill)

                WHERE
                    s.name IN $skills

                RETURN DISTINCT
                    j.title AS job,
                    s.name AS skill
                """,
                skills=candidate_skills
            )


            relevant_jobs = []


            for record in job_result:

                job = record["job"]
                skill = record["skill"]

                relevant_jobs.append(job)

                job_id = "job_" + job

                skill_id = "skill_" + skill

                add_node(
                    job_id,
                    job,
                    "job"
                )

                add_node(
                    skill_id,
                    skill,
                    "skill"
                )

                add_edge(
                    job_id,
                    skill_id,
                    "REQUIRES"
                )


            # --------------------------------
            # Companies offering relevant jobs
            # --------------------------------

            company_result = session.run(
                """
                MATCH
                    (company:Company)-[:OFFERS]->(j:Job)

                WHERE
                    j.title IN $jobs

                RETURN
                    company.name AS company,
                    j.title AS job
                """,
                jobs=relevant_jobs
            )


            for record in company_result:

                company = record["company"]
                job = record["job"]

                company_id = (
                    "company_" +
                    company
                )

                job_id = (
                    "job_" +
                    job
                )

                add_node(
                    company_id,
                    company,
                    "company"
                )

                add_node(
                    job_id,
                    job,
                    "job"
                )

                add_edge(
                    company_id,
                    job_id,
                    "OFFERS"
                )


            return jsonify({

                "nodes": nodes,

                "edges": edges

            })


    except Exception as e:

        print(
            "Graph error:",
            e
        )

        return jsonify({

            "error":
                "Unable to load graph data."

        }), 500


# --------------------------------
# Job recommendations
# --------------------------------

@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json()

    skills = data.get("skills", [])

    if not skills:

        return jsonify({
            "jobs": []
        })

    try:

        with driver.session() as session:

            result = session.run(
                """
                MATCH
                    (c:Company)-[:OFFERS]->(j:Job)

                MATCH
                    (j)-[:REQUIRES]->(required:Skill)

                WITH
                    j,
                    c,
                    collect(required.name)
                    AS required_skills

                WITH
                    j,
                    c,
                    required_skills,

                    [skill IN required_skills
                     WHERE skill IN $skills]
                    AS matching_skills

                WITH
                    j,
                    c,
                    required_skills,
                    matching_skills,

                    [skill IN required_skills
                     WHERE NOT skill IN $skills]
                    AS missing_skills

                OPTIONAL MATCH
                    (course:Course)-[:TEACHES]->(missing:Skill)

                WHERE
                    missing.name IN missing_skills

                WITH
                    j,
                    c,
                    required_skills,
                    matching_skills,
                    missing_skills,

                    collect(
                        DISTINCT {
                            name: course.name,
                            skill: missing.name
                        }
                    ) AS courses

                RETURN
                    j.title AS title,
                    c.name AS company,
                    matching_skills,
                    missing_skills,

                    size(required_skills)
                    AS total_skills,

                    CASE
                        WHEN size(required_skills) = 0
                        THEN 0

                        ELSE round(
                            100.0 *
                            size(matching_skills) /
                            size(required_skills)
                        )

                    END AS match_percentage,

                    courses

                ORDER BY
                    match_percentage DESC
                """,
                skills=skills
            )

            jobs = []

            for record in result:

                jobs.append({

                    "title":
                        record["title"],

                    "company":
                        record["company"],

                    "matching_skills":
                        record["matching_skills"],

                    "missing_skills":
                        record["missing_skills"],

                    "total_skills":
                        record["total_skills"],

                    "match_percentage":
                        record["match_percentage"],

                    "courses":
                        record["courses"]

                })

            return jsonify({
                "jobs": jobs
            })

    except Exception as e:

        print(
            "Database error:",
            e
        )

        return jsonify({

            "error":
                "Unable to connect to the database."

        }), 500


# --------------------------------
# Start application
# --------------------------------

if __name__ == "__main__":

    try:

        driver.verify_connectivity()

        print(
            "Connected to CognoDB successfully!"
        )

    except Exception as e:

        print(
            "Database connection failed:",
            e
        )

    app.run(debug=True)