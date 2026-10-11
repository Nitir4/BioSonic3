"""Audio prediction API and contained frontend serving."""
import importlib
import logging
from pathlib import Path
import tempfile
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

LOGGER = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / 'static'
MAX_UPLOAD_BYTES = 25 * 1024 * 1024


def _module(name):
    return importlib.import_module(f'{__package__}.{name}' if __package__ else name)


def _load_model():
    return _module('model.predictor').load_model()


def _model_ready():
    return _module('model.predictor').is_model_ready()


def _run_pipeline(path):
    return _module('main').run_pipeline(path)


def create_app(static_dir=None, model_loader=None, pipeline=None, readiness=None):
    root = Path(static_dir if static_dir is not None else STATIC_DIR).resolve()
    model_loader = model_loader or _load_model
    pipeline = pipeline or _run_pipeline
    readiness = readiness or _model_ready

    def ready():
        try:
            return bool(readiness())
        except Exception:
            return False

    @asynccontextmanager
    async def lifespan(app):
        try:
            await run_in_threadpool(model_loader)
        except Exception:
            LOGGER.exception('Model initialization failed; predictions are unavailable.')
        yield

    app = FastAPI(title='BioSonic API', lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

    @app.get('/health')
    @app.head('/health')
    def health():
        available = ready()
        return JSONResponse({'status':'ok' if available else 'unavailable','model_ready':available},
                            status_code=200 if available else 503)

    @app.post('/predict')
    async def predict_audio(file: UploadFile = File(...)):
        if not ready():
            raise HTTPException(503, 'The audio model is unavailable. Please try again later.')
        suffix = Path(file.filename or 'audio.ogg').suffix or '.ogg'
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                temp_path = temp.name
                size = 0
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_UPLOAD_BYTES:
                        raise HTTPException(413, 'Audio uploads must be no larger than 25 MiB.')
                    temp.write(chunk)
            if size == 0:
                raise HTTPException(422, 'Choose a nonempty audio file.')
            try:
                return await run_in_threadpool(pipeline, temp_path)
            except ValueError:
                LOGGER.info('Invalid audio upload', exc_info=True)
                raise HTTPException(422, 'The upload is not valid audio.') from None
            except Exception:
                LOGGER.exception('Audio inference failed.')
                raise HTTPException(500, 'Audio prediction failed. Please try again later.') from None
        finally:
            if temp_path is not None:
                Path(temp_path).unlink(missing_ok=True)
            await file.close()

    def contained_file(relative):
        try:
            path = (root / relative).resolve()
        except (OSError, RuntimeError, ValueError):
            raise HTTPException(404, 'Not Found') from None
        if not path.is_relative_to(root):
            raise HTTPException(404, 'Not Found')
        return path

    def index_response():
        path = contained_file('index.html')
        if not path.is_file():
            raise HTTPException(503, 'The frontend build is unavailable.')
        return FileResponse(path)

    @app.get('/favicon.ico')
    async def favicon():
        path = contained_file('favicon.svg')
        if not path.is_file():
            raise HTTPException(404, 'Not Found')
        return FileResponse(path)

    @app.get('/')
    @app.head('/')
    async def serve_index():
        return index_response()

    assets = root / 'assets'
    if assets.is_dir() and assets.resolve().is_relative_to(root):
        app.mount('/assets', StaticFiles(directory=assets, follow_symlink=False), name='assets')

    @app.get('/{full_path:path}')
    async def catch_all(full_path: str):
        path = contained_file(full_path)
        if path.is_file():
            return FileResponse(path)
        return index_response()

    return app


app = create_app()
