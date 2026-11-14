from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.routes.product import router
from app.core.config import settings
from app.db.models import Base,Issue,PullRequest,Repository,WorkflowRun
from app.db.session import get_db

@pytest.fixture
def client():
    engine=create_engine('sqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        app=FastAPI();app.include_router(router,prefix='/api/product')
        app.dependency_overrides[get_db]=lambda:session
        yield TestClient(app),session
    engine.dispose()

def test_empty_overview_does_not_claim_connected_or_sample_data(client,monkeypatch):
    browser,db=client
    monkeypatch.setattr(settings,'llm_api_key',None)
    monkeypatch.setattr(settings,'github_token',None)
    monkeypatch.setattr(settings,'demo_mode',True)
    payload=browser.get('/api/product/overview').json()
    assert payload['data_kind']=='empty' and payload['mode']=='offline_demo'
    assert payload['counts']=={'repositories':0,'issues':0,'pull_requests':0,'workflow_runs':0}
    assert payload['configuration']['llm_configured'] is False

def test_overview_counts_actual_database_rows(client,monkeypatch):
    browser,db=client
    repo=Repository(owner='demo',name='sample',full_name='demo/sample',default_branch='main')
    db.add(repo);db.flush()
    db.add(Issue(repo_id=repo.id,number=1,title='A bug',state='open',labels=[],assignees=[]))
    db.add(PullRequest(repo_id=repo.id,number=2,title='A patch',state='open'))
    db.add(WorkflowRun(repo_id=repo.id,name='tests',status='completed',conclusion='failure'))
    db.commit()
    payload=browser.get('/api/product/overview').json()
    assert payload['data_kind']=='synthetic'
    assert payload['counts']=={'repositories':1,'issues':1,'pull_requests':1,'workflow_runs':1}
    assert len(payload['scenarios'])==3

def test_configuration_is_not_provider_health_or_secret_disclosure(client,monkeypatch):
    browser,db=client
    monkeypatch.setattr(settings,'llm_api_key','fixture-secret-not-to-return')
    monkeypatch.setattr(settings,'github_token','fixture-gh-secret')
    response=browser.get('/api/product/overview')
    assert response.json()['mode']=='configured_runtime'
    assert 'fixture-secret' not in response.text and 'fixture-gh-secret' not in response.text
    assert response.json()['configuration']['llm_configured'] is True


def test_offline_demo_does_not_clone_a_remote_pr(client,monkeypatch):
    from app.services import worktree_manager
    from types import SimpleNamespace
    from uuid import uuid4
    monkeypatch.setattr(settings,'offline_demo',True)
    def forbidden_network(*args,**kwargs):
        raise AssertionError('Offline demo must not prepare a remote checkout')
    monkeypatch.setattr(worktree_manager,'_sync_checkout',forbidden_network)
    response=worktree_manager.prepare_pr_worktree(None,None,SimpleNamespace(id=uuid4(),number=42))
    assert response['status']=='offline_demo'
