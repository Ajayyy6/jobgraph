# JobGraph

JobGraph is a graph-based job recommendation application that connects a candidate's skills with relevant jobs, companies, related skills, and learning opportunities.

The application uses Flask for the web application and CognoDB/Neo4j for storing and querying the career graph.

## Features

- Candidate skill profile
- Skill-based job recommendations
- Job match percentage
- Matching skills identification
- Missing skill identification
- Related skill recommendations
- Recommended learning opportunities
- Company and job relationships
- Interactive career graph
- Dashboard with career statistics
- Multiple skill selection
- Empty-selection validation

## Technology Stack

- Python
- Flask
- CognoDB / Neo4j
- Cypher
- HTML
- CSS
- JavaScript
- Cytoscape.js
- python-dotenv

## Project Structure

```text
jobgraph/
│
├── app.py
│
├── database/
│   ├── seed.py
│   └── candidate.py
│
├── templates/
│   └── index.html
│
├── .gitignore
├── .env
├── README.md
└── venv/