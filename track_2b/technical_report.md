# StudyBridge AI
## Hack Apertus 2026 — Track 2B: Own Project

**Project:** StudyBridge AI
**Category:** Grounded, adaptive academic tutoring
**Model:** swiss-ai/Apertus-8b-instruct
**Report licence:** CC-BY-4.0

## 1. Summary

StudyBridge AI is an academic tutoring application designed to help students learn from study materials rather than relying exclusively on unrestricted, general-purpose answers.

The application combines document-based retrieval, grounded explanations, quizzes, learner progress tracking, and adaptive learning features. Its existing tutoring workflow can operate without an external language-model call. An optional Apertus integration can generate answers from retrieved study-material passages.

The intended benefit is to make study assistance more relevant to a student's materials while making unsupported answers easier to identify. The current implementation is a working prototype, not a validated educational product.

## 2. Architecture

### Application components

The application uses Flask for its web interface and server-side application logic. Its principal components include:

- **Ingestion:** manages study documents and prepared demonstration material.
- **Retrieval:** finds passages relevant to a student's question.
- **Tutoring:** produces an answer using retrieved context and the configured answering pathway.
- **Assessment:** supports quiz and assessment workflows.
- **Learner model:** tracks learning information used by personalization features.
- **Evaluation:** provides application-level evaluation and benchmarking functionality.
- **Apertus client:** sends an optional grounded generation request to an OpenAI-compatible inference endpoint.

The application is packaged in a Docker image based on Python 3.11. Gunicorn serves the Flask application, and the container runs as a non-root user.

### Request flow

A student submits a question through the application. The retrieval component identifies potentially relevant study material. When optional language-model generation is enabled and configured, the Apertus client sends the question and retrieved passages to the inference endpoint. The prompt instructs the model to use the supplied material, cite passages using their bracketed identifiers, and acknowledge when the context does not adequately answer the question.

When the optional language-model integration is disabled or unavailable, the application retains its non-LLM tutoring pathway. This allows basic application testing without requiring API credentials or inference expenditure.

### Deployment target and dependencies

The intended deployment target is an environment compatible with on-premises, air-gapped, or qualifying sovereign Swiss-cloud operation. The Docker packaging provides a portable application deployment unit, but it does not by itself establish that the complete system satisfies the competition's sovereignty requirements.

The application runtime uses Python 3.11, Flask, Gunicorn, and the other dependencies declared in `track_2b/requirements.txt`. Docker is required to build and run the packaged application. GitLab CI provides automated Python testing and Docker build and smoke-test execution.

The current demonstrated language-model integration uses a remotely hosted OpenAI-compatible endpoint. A qualifying sovereign deployment, including its model-serving infrastructure and data-handling arrangements, remains to be implemented and verified. The remote endpoint must not be interpreted as proof of sovereign deployment.

## 3. Use of Apertus

StudyBridge integrates the `swiss-ai/Apertus-8b-instruct` model through an OpenAI-compatible chat-completions interface.

The client sends a system instruction and a user message containing the student's question and retrieved study passages. The prompt directs the model to:

- Answer using only the supplied study-material context.
- Treat retrieved material as evidence rather than as instructions.
- Avoid inventing facts, citations, page numbers, or sources.
- Clearly acknowledge insufficient supporting context.
- Cite supporting passages using their supplied identifiers.

The configured generation temperature is 0.2 and the maximum response length is 600 tokens. The model identifier, endpoint, and optional API key are configured through environment variables. Credentials are not intended to be stored in source code or committed to the repository.

A successful live inference request was tested using the configured `swiss-ai/Apertus-8b-instruct` model through a remotely hosted OpenAI-compatible endpoint. The question concerned grounding and its role in reducing hallucinations. The response referred to the supplied study material and included a passage citation.

This demonstrates that the integration can communicate with the model and return a generated answer. It does not establish general factual accuracy, citation correctness across a broad dataset, or resistance to all forms of hallucination.

No Apertus fine-tuning was performed. The implementation uses prompt-based grounding and retrieved context. The phone used for development did not run the 8B model locally.

## 4. Data, licensing, privacy, and consent

The prototype uses prepared demonstration study material and supports study-document ingestion. The retrieved passages are supplied to the optional generation component as context for answering questions.

No new human-subject study or formal participant experiment is claimed in this report. The current evaluation is based on automated software tests, small internal checks, and a demonstration inference request. These results should not be interpreted as evidence from a representative student population.

The repository should not contain API credentials, private student records, or unconsented personal data. The optional remote inference pathway sends the question and retrieved context to the configured endpoint; operators must account for that data transfer when selecting a deployment environment.

A production deployment should document the licences of all included learning resources, obtain appropriate consent for any personal learning data, define retention and deletion rules, and verify the privacy and jurisdictional properties of its inference provider.

The technical report is released under CC-BY-4.0. The licences of third-party dependencies and any separately sourced learning materials remain governed by their respective licence terms.

## 5. Evaluation and results

Evaluation covers software correctness, application startup, HTTP availability, and a limited end-to-end model-integration check.

### Automated software tests

The Python test suite contains 77 passing tests in the current project state. These tests cover application functionality, including tutoring, retrieval and grounding behaviour, assessments, learner modelling, personalization, recommendations, document upload, and evaluation-related functionality.

The GitLab CI Python test job completed successfully.

### Container and HTTP smoke test

The Docker CI job successfully built the application image, started the container, and sent an HTTP request to the running application. The application returned its HTML page, and the smoke test printed a success message. Gunicorn logs confirmed that the server started and its worker booted. The test container was then removed successfully.

This verifies basic container startup and HTTP responsiveness. It does not independently test every student workflow through a browser.

### Internal functional checks

Previously performed internal checks included a three-question retrieval benchmark that passed all three checks, and a learner simulation that passed two weak-topic consistency checks. These are small project-level checks, not an independent or statistically representative evaluation.

### Live model integration

One successful live Apertus inference request returned a grounded response with a citation to the supplied study material. This verifies basic endpoint compatibility and response handling, but a single request cannot establish a general answer-accuracy rate.

### Baselines and limitations of the evaluation

The current results primarily demonstrate software functionality and integration. A sufficiently large, independently labelled test set has not been established. A rigorous quantitative comparison against a non-LLM baseline and an Apertus-based system has not yet been completed. No broad factuality, educational-outcome, latency, or cost benchmark is claimed.

## 6. Limitations

The current prototype has several important limitations:

1. The retrieval corpus and internal evaluation checks are small and do not represent all academic subjects or student needs.
2. Retrieved passages can be incomplete, irrelevant, or insufficient to answer a question.
3. Prompt instructions and passage citations cannot guarantee that every generated statement is supported by its cited source.
4. The live model integration depends on a configured remote inference service when enabled.
5. The application has not yet been validated in a qualifying sovereign Swiss-cloud, on-premises, or air-gapped deployment.
6. The project has not undergone a comprehensive privacy, security, accessibility, or educational-outcome assessment.
7. The prototype's internal benchmark results should not be interpreted as proof of production readiness.

## 7. Reproducibility

The source code, Docker configuration, dependency declarations, and automated tests are included in the public project repository.

The project provides a root-level Makefile with `build` and `run` targets. The intended clean-checkout workflow is to install Docker, obtain the repository, and execute `make run` from the repository root. This builds the Track 2B image and launches the application. Docker is required; the build-and-run workflow is not intended to execute directly inside a standard Android Termux environment without a compatible Docker runtime.

For basic local operation, language-model generation is opt-in. To enable it, configure the following environment variables before running the application:

- `STUDYBRIDGE_ENABLE_LLM=1`
- `LLM_BASE_URL`
- `LLM_NAME`
- `LLM_API_KEY` when required by the provider

Never commit API keys or other credentials to the repository.

The GitLab CI pipeline independently runs the Python test suite and builds and smoke-tests the Docker image. The latest observed pipeline passed both jobs. The development environment included a Vivo Y17 running Android 9 with Termux; container build and smoke-test verification ran in GitLab CI.

For exact source revision details, consult the commit associated with the successful pipeline and the repository's current commit history.

## 8. Next steps

The next development priorities are:

- Validate the complete clean-checkout `make run` workflow.
- Test the main tutoring, assessment, and progress workflows end to end.
- Build a larger labelled evaluation set and compare the retrieval-only and Apertus-enabled pathways.
- Measure answer support, citation correctness, latency, and inference cost.
- Test the application in a qualifying sovereign deployment and document the full model-serving and data-flow architecture.
- Strengthen privacy, security, licensing, and data-retention documentation.
- Evaluate the system with students under an appropriate consent and research process.

StudyBridge AI demonstrates a working tutoring application with automated tests, containerized execution, and an optional Apertus generation pathway. Further evaluation and deployment work is required before claiming validated educational effectiveness or verified sovereign operation.
