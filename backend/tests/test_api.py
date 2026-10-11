import asyncio
from pathlib import Path

import httpx
import pytest

from backend import api


def exchange(app, requests):
    async def run():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://test') as client:
                return [await client.request(method,url,**kwargs) for method,url,kwargs in requests]
    return asyncio.run(run())


def test_static_routes_deny_traversal_and_symlinks(tmp_path):
    root=tmp_path/'static';root.mkdir()
    (root/'index.html').write_text('Frontend index')
    (root/'safe.txt').write_text('Public text')
    marker=tmp_path/'private.txt';marker.write_text('Private audit marker')
    (root/'leak.txt').symlink_to(marker)
    assets=root/'assets';assets.mkdir();(assets/'leak.txt').symlink_to(marker)
    app=api.create_app(root,model_loader=lambda:None,readiness=lambda:True)
    urls=['/','/safe.txt','/dashboard','/..%2Fprivate.txt','/%2F'+str(marker).lstrip('/'),'/leak.txt','/assets/leak.txt','/favicon.ico']
    responses=exchange(app,[('GET',url,{}) for url in urls])
    assert [r.status_code for r in responses]==[200,200,200,404,404,404,404,404]
    assert all('Private audit marker' not in r.text for r in responses)


def test_health_and_predict_reflect_missing_or_failed_models(tmp_path):
    called=[]
    def broken():raise RuntimeError('/private/model/checkpoint')
    app=api.create_app(tmp_path,model_loader=broken,readiness=lambda:False,pipeline=lambda path:called.append(path))
    responses=exchange(app,[('GET','/health',{}),('HEAD','/health',{}),('POST','/predict',{'files':{'file':('a.wav',b'audio')}})])
    assert [r.status_code for r in responses]==[503,503,503]
    assert responses[0].json()['model_ready'] is False
    assert not called
    assert '/private/' not in responses[-1].text


@pytest.mark.parametrize('error,status',[(None,200),(ValueError('/private/decoder'),422),(RuntimeError('/private/model'),500)])
def test_predict_cleanup_and_sanitized_errors(tmp_path,error,status):
    paths=[]
    def pipeline(path):
        paths.append(Path(path))
        assert Path(path).read_bytes()==b'Audio test'
        if error:raise error
        return {'species':'Test bird','confidence':.8}
    app=api.create_app(tmp_path,model_loader=lambda:None,readiness=lambda:True,pipeline=pipeline)
    response=exchange(app,[('POST','/predict',{'files':{'file':('sample.wav',b'Audio test')}})])[0]
    assert response.status_code==status
    assert len(paths)==1 and not paths[0].exists()
    assert '/private/' not in response.text


def test_empty_and_oversized_uploads_are_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(api,'MAX_UPLOAD_BYTES',8)
    called=[]
    app=api.create_app(tmp_path,model_loader=lambda:None,readiness=lambda:True,pipeline=lambda path:called.append(path))
    responses=exchange(app,[('POST','/predict',{'files':{'file':('a.wav',content)}}) for content in [b'',b'123456789']])
    assert [r.status_code for r in responses]==[422,413]
    assert not called


def test_missing_frontend_does_not_expose_paths(tmp_path):
    app=api.create_app(tmp_path,model_loader=lambda:None,readiness=lambda:True)
    response=exchange(app,[('GET','/',{})])[0]
    assert response.status_code==503 and str(tmp_path) not in response.text
