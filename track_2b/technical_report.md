# StudyBridge AI — Technical Report

- **Track:** Track 2B — Own Project
- **Event:** Hack Apertus 2026, Online
- **Team:** StudyBridge
- **Member:** Oghenefejiro Duke
- **Demo:** To be added after recording and uploading the demonstration video.

## 1. Summary

StudyBridge AI is an educational assistant designed to help students learn from their study materials. It combines document retrieval, source-aware tutoring, quizzes, learner-progress tracking, and adaptive learning features. The Apertus integration sends a student question and retrieved study passages to an Apertus model through an OpenAI-compatible inference endpoint. The tutor prompt instructs the model to answer from the supplied context, cite supporting passages, and acknowledge when the context is insufficient. A local fallback allows the application to operate without making external inference requests. The project has 75 passing automated tests in its current test suite. These tests establish software behaviour, not independent proof of model factual accuracy.

## 2. Architecture

StudyBridge separates the web application, retrieval, assessment, learner modelling, and language-model inference.

1. The Flask application accepts student requests and serves the user interface.
2. The ingestion and retrieval components provide relevant study passages.
3. The tutor constructs a prompt containing the student's question and retrieved context.
4. When explicitly enabled and configured, the Apertus client sends the prompt to an OpenAI-compatible chat-completions endpoint.
5. The tutor returns the generated response with passage references. When inference is not enabled or configured, the application uses its local tutoring path.
6. Assessment and learner-model components support quizzes, progress tracking, and personalization.

### Target architecture

**Target: on-premises deployment.**

The intended production arrangement is to run the StudyBridge application and an Apertus-compatible inference service on infrastructure administered by the deploying organisation. The application is containerized, and its inference client accepts a configurable endpoint so an organisation can direct requests to its own service.

This is a target architecture, not a verified deployment result. The development demonstration used a hosted inference endpoint. We have not yet verified a complete on-premises Apertus serving setup or demonstrated that all runtime traffic stays within an organisation's infrastructure. An external endpoint alone does not establish sovereign or on-premises compliance.

### Dependencies

**Build time:** Python base image, Python package installation, and Docker image construction.

**Runtime:** Python, Flask, Gunicorn, the project's application dependencies, and optionally a configured OpenAI-compatible Apertus endpoint. External inference requires network access and an API credential. Without inference enabled, the application can use its local tutoring path.

The Dockerfile uses a non-root application user. Docker execution must be verified on a Docker-capable runner because the development environment used for this work is Termux on Android and does not provide a working local Docker build environment.

## 3. Use of Apertus

- **Model:** `swiss-ai/apertus-v1.5-8b`
- **Use:** Inference.
- **Fine-tuning:** None.
- **Where it ran during development:** Hosted OpenAI-compatible inference endpoint.
- **Model weights:** Not bundled in the repository.
- **Serving configuration:** The endpoint, model name, and API credential are supplied through environment variables.

The client uses `LLM_BASE_URL`, `LLM_NAME`, and `LLM_API_KEY`. The application requires `STUDYBRIDGE_ENABLE_LLM` to be explicitly enabled before automatically configuring inference. This prevents accidental external requests during tests or normal local use.

The prompt instructs Apertus to use only the supplied study-material context, treat that context as evidence rather than instructions, avoid inventing facts or sources, acknowledge insufficient evidence, and cite passages using bracketed reference numbers. Requests use temperature 0.2 and a maximum of 600 generated tokens.

One live development query about grounding and hallucination reduction returned an answer citing a retrieved study passage. This demonstrates that the client can communicate with the configured endpoint; it is not a comprehensive factuality, safety, or comparative model evaluation. API credentials are not included in the repository.

## 4. Data

The application uses demonstration study material and retrieved passages to support tutoring. Its seed content is generated or bundled for demonstration. Users may also supply their own study documents through the application's document-ingestion features.

No human-subject study or consent-based dataset was used for the reported software tests. Personal, private, or non-redistributable user documents should not be committed to the repository. Generated learner-progress files, processed runtime data, local environment files, and credentials are excluded from version control.

The application can process uploaded material, so deployment operators must apply appropriate access controls and retention practices. This project does not claim that every possible uploaded document has been checked for redistribution rights.

## 5. Evaluation

The evaluation combines automated software tests, existing internal functional checks, and a limited live inference smoke test.

| Setup | Metric | Result |
|---|---|---|
| Automated project test suite | Tests passing | 75 passed in the reported run |
| Internal tutor benchmark | Predefined questions passing | 3/3 in the existing internal evaluation |
| Learner simulation | Weak-topic consistency checks | 2/2 in the existing internal evaluation |
| Apertus integration smoke test | Successful response from configured endpoint | One successful development query |

The automated tests cover application behaviour, retrieval and tutoring logic, assessment, learner modelling, and the mocked Apertus client. The Apertus client tests use mocks rather than spending API credits.

These results are functional checks, not an independent evaluation of educational outcomes or language-model quality. No controlled head-to-head experiment has established that Apertus outperforms the local fallback. The live smoke test does not establish factual accuracy, citation entailment, robustness, or production readiness.

## 6. Limitations

- The complete Docker build and clean-container run still require verification on a Docker-capable runner.
- The intended on-premises Apertus serving architecture has not yet been demonstrated end to end.
- A hosted inference endpoint introduces an external dependency and may require network access, credentials, and paid credits.
- Generated answers can still be incorrect even when prompted to use retrieved context.
- Citation formatting does not guarantee that a cited passage logically supports every claim.
- The internal evaluation is small and does not establish learning gains or performance across a representative student population.
- Performance, concurrency, accessibility, security, and large-document behaviour require further testing.

## 7. Reproducibility

The repository includes the application source, test suite, dependency list, Dockerfile, and Makefiles. From a clean checkout on a machine with Docker and Make installed, the intended entry point is `make run` from the repository root. The image is built from `track_2b/Dockerfile` and the application is exposed on port 5000 by default.

Run the automated tests with:

`PYTHONPATH=track_2b/src python -m pytest -q track_2b/tests`

Tests should be run without inference credentials or the inference-enable flag so the suite remains deterministic and does not make external requests.

Development and test work was performed using Termux on an Android device. The container image targets Python 3.11. A Docker-capable CI runner must verify dependency installation and container startup before the submission can claim a reproducible successful container run.

**Submission commit:** To be recorded after the final reviewed changes are committed.

## 8. Next steps

1. Run the tests and Docker build in continuous integration.
2. Verify the complete application in a clean container.
3. Demonstrate an Apertus-compatible service deployed on organisation-controlled infrastructure.
4. Expand evaluation with a larger question set, explicit answer-support checks, and a documented local-fallback comparison.
5. Test failure handling, uploaded-document edge cases, and runtime privacy controls.
6. Record a demonstration video of no more than two minutes and add its URL.

## License

The project is intended to be released under the Creative Commons Attribution 4.0 International (CC-BY-4.0) license, subject to checking that all included code, dependencies, and assets can be distributed under the selected terms.

## References

- Hack Apertus project template: https://github.com/HackApertus/project-template
- Apertus v1.5 8B model: https://huggingface.co/swiss-ai/Apertus-v1.5-8B
- Hack Apertus submission information: https://hackapertus.ch/online-hack/submissions
