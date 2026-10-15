# StudyBridge AI

**Hack Apertus 2026 — Track 2B: Own Project**

StudyBridge AI helps students explore course materials, ask questions,
practise through assessments, and track learning progress.

It combines document ingestion, retrieval, tutoring, assessments, and
learner-progress features. An optional Apertus integration generates
answers using retrieved study passages as context.

## Problem

Students can struggle to find relevant explanations in lengthy course
materials and identify topics that need further practice. StudyBridge
aims to make learning materials easier to explore and understand.

## Features

- Ask questions about study materials.
- Retrieve relevant passages for tutoring.
- Optionally generate answers through an Apertus-compatible endpoint.
- Retain local tutoring behaviour when external inference is disabled.
- Practise through assessments and quizzes.
- Track learner progress.
- Run the application in Docker.

## Architecture

Flask serves the web application. Separate components handle retrieval,
tutoring, assessments, and learner modelling.

When explicitly enabled, the tutoring component sends the question and
retrieved passages to a configured Apertus-compatible inference endpoint.

External inference is disabled by default.

See docs/ARCHITECTURE.md and docs/EVALUATION.md for further details.

## Requirements

- Docker Engine
- GNU Make
- Network access for the initial image build
- An Apertus-compatible endpoint and credentials if remote inference is used

## Run

From the repository root, execute: make run

The application is configured to use port 5000 by default.
Open http://localhost:5000 in your browser.

To change the host port, execute: make run PORT=8080

## Optional Apertus configuration

Set the following environment variables before running the application:

- STUDYBRIDGE_ENABLE_LLM=1
- LLM_BASE_URL=<your approved Apertus endpoint>
- LLM_NAME=swiss-ai/apertus-v1.5-8b
- LLM_API_KEY=<your secret API key>

Use an endpoint and model identifier supported by your deployment.
Never commit API keys, passwords, or other secrets.

The endpoint must be configured for your actual deployment. A public
API endpoint does not automatically satisfy the competition's
sovereign-deployment requirement.

## Testing

Run the tests from the repository root with:

PYTHONPATH=track_2b/src python -m pytest -q track_2b/tests

Apertus client tests mock HTTP responses and do not require a live
endpoint or consume API credits.

## Data and privacy

Do not commit private student information, uploaded documents,
credentials, or generated learner records.

When remote inference is enabled, questions and retrieved passages may
leave the application process. Assess endpoint security, retention,
access controls, and jurisdiction before using real student data.

The intended privacy-conscious target is an on-premises Apertus service
controlled by the deploying organisation. End-to-end deployment has
not yet been verified.

## Limitations

- Retrieval quality depends on available study materials.
- Generated answers can still be incorrect or incomplete.
- Grounding and citation quality need systematic evaluation.
- Performance under large workloads has not been established.
- GitLab CI successfully built the Docker image and passed the HTTP smoke test. Deployment in a qualifying sovereign Swiss environment remains unverified.

## Competition

- Event: Hack Apertus 2026
- Track: Track 2B — Own Project
- Model family: Apertus
- Source code licence: Apache-2.0
- Documentation and report licence: CC-BY-4.0, where applicable


## Licences

- Source code: Apache License 2.0, consistent with the repository's root `LICENSE`.
- Original documentation and technical report: Creative Commons Attribution 4.0 International (CC-BY-4.0), where applicable.
- Third-party dependencies, datasets, and learning materials retain their respective licences. Their terms must be respected.

These distinctions follow the Hack Apertus Terms and Conditions, section 6. Check that any included third-party content is compatible with the applicable licence before submission.
