# JobGraph

JobGraph is a graph-based job recommendation application that connects a candidate's skills with relevant jobs, companies, related skills, and learning opportunities.

The application is built using Flask and CognoDB as the graph database layer.

## Problem Statement

Finding a suitable job is not only about matching a candidate with a job title. A candidate's skills are connected to job requirements, related skills, companies, and learning opportunities.

JobGraph models these relationships as a graph and uses them to provide personalized job recommendations and skill-gap analysis.

## Why a Graph Database?

A graph database is a natural fit for JobGraph because the main problem is based on relationships between candidates, skills, jobs, companies, and learning opportunities.

The main graph relationships are:

```text
Candidate
   |
   | HAS_SKILL
   v
 Skill
   |
   | RELATED_TO
   v
Related Skill

Company
   |
   | OFFERS
   v
 Job
   |
   | REQUIRES
   v
 Skill