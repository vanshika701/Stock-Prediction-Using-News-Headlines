# Person 2 - Pipeline Results and How to Run

What I implemented for Person 2 (based on `README_FOR_PERSON2.txt`):

- `person2_pipeline.py`: Loads the provided preprocessed JSON files and:
  - Computes a per-article sentiment score using lemmatized tokens and
    `features.financial_keywords`.
  - Maps scores to Buy / Sell / Hold recommendations using thresholds.
  - Produces a confidence score per article and per-ticker aggregate.
  - Aggregates ticker-level sentiment across up to the 50 most recent
    articles and weights recent articles more heavily.
  - Writes results to `person2_results.json` in the same directory.

Output:

- `exports_for_person2/person2_results.json` — contains per-article scores and
  per-ticker aggregates with recommendations and confidence.

Notes and assumptions:

- The implementation is intentionally lightweight and local (no external
  models). It uses a small lexicon plus the provided financial keywords. You
  can swap `POSITIVE_WORDS` / `NEGATIVE_WORDS` or plug a model in
  `compute_article_score` if you prefer.
- If per-ticker files are present (e.g. `aapl_preprocessed.json`), they are
  used for per-ticker aggregation; otherwise the script groups articles from
  `all_articles_preprocessed.json`.


What I did:

- Tuned and expanded the positive / negative lexicon and exposed
  thresholds in `person2_pipeline.py` (see `THRESHOLD_BUY` / `THRESHOLD_SELL`).
- Added optional integration with VADER (`vaderSentiment`) if available; the
  pipeline will use VADER's compound score when the package is installed.
- Added unit tests at `tests/test_person2_pipeline.py` using Python's
  builtin `unittest`. Run them with:

How to run (from repository root on Windows PowerShell):

```powershell
python .\exports_for_person2\person2_pipeline.py
```