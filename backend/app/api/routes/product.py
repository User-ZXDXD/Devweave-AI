"""Product entry: report actual local data and configuration, not business impact claims."""
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Issue,PullRequest,Repository,WorkflowRun
from app.db.session import get_db

router=APIRouter()

@router.get('/overview')
def overview(db:Session=Depends(get_db)):
    repos=db.query(Repository).all()
    return {'product':'DevWeave AI','mode':'offline_demo' if settings.demo_mode and not settings.llm_api_key else 'configured_runtime',
        'data_kind':'empty' if not repos else 'synthetic' if all(repo.owner in ('course-demo','demo') for repo in repos) else 'mixed_or_connected',
        'configuration':{'llm_configured':bool(settings.llm_api_key),'github_token_configured':bool(settings.github_token),
            'milvus_enabled':settings.milvus_enabled,'embedding_provider':settings.embedding_provider,'auto_sync_enabled':settings.auto_sync_enabled},
        'counts':{'repositories':len(repos),'issues':db.query(Issue).count(),'pull_requests':db.query(PullRequest).count(),'workflow_runs':db.query(WorkflowRun).count()},
        'scenarios':[
            {'id':'issue-triage','title':'从问题描述到行动项','url':'/issues','question':'JWT过期为什么返回500？应该怎样分级、补测试？','outputs':['问题分类与优先级','相关证据','可执行的下一步']},
            {'id':'pr-readiness','title':'判断PR是否具备合入条件','url':'/pull-requests','question':'PR变更是否覆盖Issue、CI和Review要求？','outputs':['变更摘要与风险','测试建议','待人工确认的动作']},
            {'id':'ci-investigation','title':'把失败日志转换为排障路径','url':'/ci','question':'CI失败来自测试、环境还是依赖？先检查哪里？','outputs':['失败类别','证据与排查步骤','不确定性与人工复核']},
        ],
        'boundaries':['离线演示使用规则与显式降级，不冒充已调用真实LLM。','配置存在不等于当前外部服务已经连接成功。','本地展示环境未提供生产多租户认证，不建议直接对公网开放。','合并、发布等外部写操作必须经过现有人工确认流程。']}
