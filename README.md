## BioSonic

The unified Docker image builds the frontend and runs `backend/api.py`. For
local use, install `backend/requirements.txt`, build the frontend into
`backend/static`, and run `uvicorn backend.api:app` from the repository root
(or `uvicorn api:app` from `backend`).

Model defaults resolve relative to the predictor source directory. Override
`WEIGHTS_DIR`, `CLASS_NAMES_PATH`, and `ID_TO_NAME_PATH` for external artifacts.
All fold checkpoints must match the model architecture; failed or incomplete
loads do not publish a partially initialized ensemble. Reloading replaces the
ensemble rather than appending duplicate folds.

`GET /health` returns 200 only while class metadata and folds are ready;
otherwise it returns 503. `/predict` accepts audio up to 25 MiB and reports 422
for invalid audio, 413 for oversized uploads, 503 for unavailable models, and a
sanitized 500 for unexpected inference failures. Temporary uploads are removed
after success and failure. Inference runs off the event loop.

Static files, including symlinks and frontend fallbacks, must resolve inside
`backend/static`. A missing favicon returns 404, and a missing frontend build
returns 503 without exposing server filesystem paths.

Run `python -m pytest backend/tests -q` with `pytest`, `fastapi`, `httpx`, and
`python-multipart` installed. API and loader tests use disposable files and
model substitutes; they do not certify trained-model accuracy.
