"""No-key local demo. Run from any directory; no real provider config is imported."""
from pathlib import Path
import argparse,importlib.util,os,subprocess,sys

ROOT=Path(__file__).resolve().parents[1]
def demo_environment():
    data=ROOT/'.demo';data.mkdir(exist_ok=True)
    environment=dict(os.environ)
    environment.update({'APP_ENV':'development','APP_NAME':'DevWeave AI · Offline Demo',
        'DATABASE_URL':'sqlite:///'+(data/'devflow.db').as_posix(),
        'DEMO_MODE':'true','OFFLINE_DEMO':'true','LLM_API_KEY':'','GITHUB_TOKEN':'','RAG_LLM_ENABLED':'false',
        'RAGAS_ENABLED':'false','MILVUS_ENABLED':'false','AUTO_SYNC_ENABLED':'false',
        'EMBEDDING_PROVIDER':'deterministic','EMBEDDING_DIMENSIONS':'384',
        'TOKEN_ENCRYPTION_KEY':'offline-demo-placeholder-not-for-production',
        'REPO_CHECKOUT_DIR':str(data/'repos'),'UPLOAD_DIR':str(data/'uploads'),
        'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','PYTHONDONTWRITEBYTECODE':'1',
        'NEXT_PUBLIC_API_BASE_URL':'http://127.0.0.1:8801','NEXT_PUBLIC_DEMO_MODE':'1'})
    environment.update({'CORS_ORIGINS':'http://127.0.0.1:3301,http://localhost:3301',
        'NO_PROXY':'127.0.0.1,localhost,::1','no_proxy':'127.0.0.1,localhost,::1',
        'NEXT_TELEMETRY_DISABLED':'1'})
    return environment

def main():
    parser=argparse.ArgumentParser(description='DevWeave AI无密钥演示：8801后端、3301前端。')
    parser.add_argument('service',choices=['backend','frontend','seed','check'])
    args=parser.parse_args()
    env=demo_environment()
    if args.service=='frontend':
        npm='npm.cmd' if os.name=='nt' else 'npm'
        raise SystemExit(subprocess.call([npm,'run','dev','--','--hostname','127.0.0.1','--port','3301'],cwd=ROOT/'frontend',env=env))
    os.environ.update(env)
    os.chdir(ROOT/'backend')
    sys.path.insert(0,str(ROOT/'backend'))
    sys.path.insert(0,str(ROOT/'scripts'))
    if args.service in ('backend','seed','check'):
        from seed_demo_data import main as seed
        seed()
    if args.service=='seed':return
    if args.service=='check':
        from fastapi.testclient import TestClient
        from app.main import app
        with TestClient(app) as client:
            assert client.get('/health').status_code==200
            overview=client.get('/api/product/overview').json()
            assert overview['mode']=='offline_demo' and overview['configuration']['llm_configured'] is False
            assert overview['counts']['issues']>=3
            print(overview)
        return
    import uvicorn
    uvicorn.run('app.main:app',host='127.0.0.1',port=8801,log_level='info')

if __name__=='__main__':main()
