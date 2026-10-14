# StudyBridge AI — Evaluation

## 1. Purpose

StudyBridge AI is evaluated for functional correctness, retrieval-grounded
tutoring, assessment reliability, learner-progress tracking, and personalized
study recommendations.

The evaluation combines automated software tests, a small predefined
tutoring benchmark, and a deterministic simulation of student profiles.

The results are intended to document implementation behavior and current
limitations. They are not proof of general AI accuracy or improved learning
outcomes.

## 2. Automated software tests

Run the test suite from the repository root:

    PYTHONPATH=track_2b/src python -m pytest -q track_2b/tests

The latest recorded full-suite result is **75 passing tests**.

The tests cover:

- Core application behavior and API routes.
- Quiz scoring, answer normalization, and invalid inputs.
- Retrieval grounding and unsupported questions.
- Learner mastery updates.
- Text and document uploads.
- Study recommendation priorities and matching materials.
- Personalization simulation and mastery changes.
- Question-exposure and repetition metrics.
- Evaluation-report integration and weak-topic consistency checks.
- Isolation of simulated learner progress from normal learner data.

The evaluation API was also checked using Flask's test client. The observed
result was HTTP 200, with the tutoring benchmark passing 3/3 cases, both
simulated learner profiles present, and the weak-topic consistency check
passing 2/2 cases.

These results verify the tested software paths. They do not establish that
all possible inputs work correctly or that the system produces educationally
valid mastery estimates.

Rerun the full test suite after code changes and update the recorded count
when the result changes.

## 3. Tutoring benchmark

The tutoring benchmark contains three predefined questions covering:

1. Cross-attention in multimodal AI.
2. Student mastery tracking.
3. Grounding and hallucination reduction.

For each question, the evaluator records whether the tutor marks its response
as supported and whether the answer contains a predefined expected phrase.

A case passes when both checks succeed.

Benchmark accuracy is the percentage of cases passing both checks. The
grounding score is the fraction of benchmark responses marked as supported
by the tutoring engine.

The latest recorded benchmark result is **3/3 passing cases**.

These are small, implementation-specific measurements. They are not
independent assessments of factual correctness, comprehensive retrieval-quality
measures, or evidence of general model accuracy.

Keyword matching may reject correct answers that use different wording. It
may also accept an answer containing the expected phrase without explaining
it correctly. The benchmark should be expanded and independently reviewed.

## 4. Learner modeling and recommendations

Learner progress is tracked by topic using quiz results and a persistent local
progress file. Recommendations prioritize topics according to recorded
mastery and can include matching indexed study materials.

Automated tests check representative mastery updates, recommendation ordering,
priority labels, matching materials, empty retrieval results, and bounded
mastery percentages.

These tests verify selected software behaviors. They do not establish that
mastery estimates accurately measure a student's understanding or that
recommendations improve learning outcomes.

## 5. Personalization simulation

The evaluation includes two deterministic simulated learner profiles:

- `grounding_focus`
- `learner_modeling_focus`

Each profile is evaluated over three sessions by default. The simulation
records session scores, initial and final topic mastery estimates, estimated
mastery changes, weakest topics, question exposures, and question repetition.

The latest recorded simulation produced the following observations:

- Two simulated learner profiles were evaluated.
- Each profile encountered nine question exposures across three sessions.
- Each profile encountered three unique questions.
- The resulting repeated-exposure rate was 66.7% for each profile.
- The weak-topic consistency check passed for both profiles (2/2).

The repetition rate is calculated as repeated exposures divided by total
question exposures. Repeated exposure means that a question is encountered
again; it does not by itself measure whether repetition is pedagogically
helpful or harmful.

The simulation is deterministic and reuses a fixed question set. Its results
are not observations from real students. The weak-topic consistency check
verifies consistency between the simulated profile's final weakest topic and
the reported topic; it is not an independent measure of recommendation
quality.

Mastery values are application estimates produced by the current learner
model. They are not validated using student outcomes, and their changes
should not be interpreted as measured learning gains.

The simulation uses an isolated temporary data directory so its progress
updates do not overwrite the application's normal learner-progress file.

## 6. Grounding and unsupported questions

The tutoring engine uses locally indexed course materials to retrieve evidence
for answers. When sufficiently relevant evidence is unavailable, the intended
behavior is to acknowledge that the available materials do not support a
reliable answer rather than invent a source.

Grounding tests exercise representative supported and unsupported queries.
They do not guarantee that every answer is correct or that every unsupported
question will be detected.

## 7. Current limitations

- The tutoring benchmark contains only three predefined questions.
- Expected-phrase matching is a limited measure of answer relevance.
- Retrieval uses local lexical matching rather than semantic embeddings.
- The personalization simulation reuses a small, fixed question set.
- The observed 66.7% repeated-exposure rate indicates that question
  deduplication and a larger assessment bank need further work.
- Scanned PDFs and image-only documents are not interpreted using OCR.
- The current system does not yet establish complete extraction and
  understanding of diagrams, figures, and lecture-video content.
- Mastery scores are application estimates, not validated educational
  measurements.
- No controlled user study has established improvements in learning outcomes.
- Results depend on the quality and coverage of indexed materials.

## 8. Future evaluation improvements

Future work should include:

- A larger benchmark with independently reviewed expected answers.
- Relevant, irrelevant, and unsupported questions across multiple topics.
- Checks that source references correspond to retrieved evidence.
- Retrieval precision and recall measurements on a labeled dataset.
- A larger assessment bank with topic, difficulty, and source metadata.
- Question-selection logic that reduces unintended repetition.
- Tests for malformed requests, empty documents, and unusual file inputs.
- Multimodal ingestion tests covering images, diagrams, and scanned pages.
- Simulated learner sessions with clearly defined expected adaptations.
- User testing focused on mobile usability and learning workflows.
