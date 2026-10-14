# StudyBridge AI — Architecture

## 1. Project overview

StudyBridge AI is a web-based learning assistant for exploring course
materials, asking questions, practising assessments, and tracking
learner progress.

The project is submitted to Hack Apertus 2026, Track 2B — Own Project.
It combines a Flask application, local document retrieval, tutoring,
assessment, and learner-modelling components with optional Apertus
language-model inference.

## 2. Main components

### Web application

`src/app/main.py` provides the Flask application and HTTP endpoints.
The frontend is implemented with HTML, CSS, and JavaScript under
`src/app/templates/` and `src/app/static/`.

### Document ingestion

`src/app/ingestion.py` handles supported learning-material ingestion
and maintains indexed content for retrieval.

### Retrieval

`src/app/retrieval.py` identifies potentially relevant material for a
student's question. The current retrieval implementation relies on
local lexical matching rather than a dedicated vector database.

### Tutoring

`src/app/tutor.py` combines retrieval with answer generation. When
external inference is disabled, the application uses its existing
local tutoring behaviour.

When explicitly enabled and configured, the tutoring component can
send a question and retrieved passages to an Apertus-compatible
endpoint.

### Apertus client

`src/app/llm_client.py` implements an HTTP client for a chat-completions
endpoint compatible with the OpenAI API format.

Configuration is provided through environment variables:

- `STUDYBRIDGE_ENABLE_LLM`
- `LLM_BASE_URL`
- `LLM_NAME`
- `LLM_API_KEY`

The client does not itself host model weights. Actual model execution
takes place wherever the configured inference service runs.

### Assessments and learner modelling

The assessment and learner-model components provide quiz evaluation,
progress tracking, and learning-related feedback.

The resulting mastery values are application estimates, not validated
measurements of educational attainment.

## 3. Data flow

1. Learning materials are ingested into the application.
2. A student submits a question through the web interface.
3. The retrieval component searches available indexed materials.
4. The tutoring component uses the retrieved passages to formulate
   a supported response.
5. If enabled, the configured Apertus endpoint generates the response.
6. The application returns the answer and available source information.
7. Assessment results and learner progress are handled by their
   respective application components.

The quality of a response depends on retrieval quality, the available
source material, and model behaviour.

## 4. Deployment architecture

### Intended target: on-premises

The intended privacy-conscious deployment is an on-premises installation
under the deploying organisation's administration.

The application is packaged using a Dockerfile and Makefiles. In the
intended deployment, an Apertus inference service would run on
organisation-controlled infrastructure, and the application would use
that service through its configured endpoint.

For this target to be considered verified, the organisation must
establish where the model runs, control access to the service, and
confirm that student data does not leave the approved environment.

**Status:** The target architecture is documented, but the complete
on-premises deployment has not yet been verified end to end.

A public hosted inference endpoint does not, by itself, establish
compliance with the competition's sovereign-deployment requirement.

## 5. Build-time and runtime dependencies

### Build time

- Docker base image
- Python package installation
- Application source files

The initial image build requires access to the base image and package
repositories unless these dependencies are already available locally.

### Runtime

- Python
- Flask
- Gunicorn
- Application code and runtime data
- An Apertus-compatible inference service only when external inference
  is enabled

The application is configured to listen on port 5000 inside the
container.

## 6. Security and privacy considerations

API credentials must be supplied through the runtime environment and
must not be committed to source control.

When external inference is enabled, the question and retrieved passages
may be transmitted to the configured endpoint. Deployment operators
must assess endpoint security, data retention, jurisdiction, and access
controls before processing private student information.

Runtime data should not be committed to the repository.

## 7. Testing status

The latest recorded automated test run passed 75 tests in the Termux
development environment.

The tests cover existing application behaviour and offline tests for
the Apertus client. The client tests mock HTTP responses and do not
establish model accuracy.

A Docker build and clean-container end-to-end run still require
verification in an environment with Docker.

## 8. Known limitations

- Retrieval uses lexical matching rather than semantic embeddings.
- Generated answers may be incorrect or incomplete.
- The existing tutoring benchmark is small and uses predefined checks.
- Learner mastery estimates have not been validated against real
  student outcomes.
- Production-scale performance has not been established.
- On-premises inference deployment has not yet been demonstrated.
