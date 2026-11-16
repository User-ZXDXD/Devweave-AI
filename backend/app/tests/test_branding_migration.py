"""Renaming synthetic demo data must retain identity and related records."""
import importlib.util
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.models import Base,Issue,Repository,WorkflowRun

spec=importlib.util.spec_from_file_location("seed_branding_migration",Path(__file__).resolve().parents[3]/"scripts/seed_demo_data.py")
seed=importlib.util.module_from_spec(spec);spec.loader.exec_module(seed)

def test_existing_demo_rename_preserves_repository_and_related_data():
    engine=create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        old=Repository(owner="course-demo",name="old-example",full_name="course-demo/devflow-sample-api",default_branch="main")
        db.add(old);db.flush();identity=old.id
        issue=Issue(repo_id=identity,number=9,title="Existing issue",state="open")
        run=WorkflowRun(repo_id=identity,name="ci",status="completed",html_url="https://github.com/"+seed.LEGACY_DEMO_FULL_NAME+"/actions/runs/301")
        db.add_all([issue,run]);db.commit()
        renamed=seed.ensure_demo_repository(db)
        assert renamed.id==identity and renamed.full_name==seed.DEMO_FULL_NAME
        assert db.query(Issue).one().repo_id==identity
        assert seed.DEMO_FULL_NAME in db.query(WorkflowRun).one().html_url
        assert seed.ensure_demo_repository(db).id==identity and db.query(Repository).count()==1
    engine.dispose()

def test_new_demo_name_is_idempotent():
    engine=create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        identity=seed.ensure_demo_repository(db).id
        assert seed.ensure_demo_repository(db).id==identity
        assert db.query(Repository).count()==1
        assert db.query(Repository).one().name=="devweave-sample-api"
    engine.dispose()
