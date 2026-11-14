"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api";

type Overview={mode:string;data_kind:string;counts:Record<string,number>;configuration:Record<string,boolean|string>;scenarios:{id:string;title:string;url:string;question:string;outputs:string[]}[];boundaries:string[]};

export default function Showcase(){
  const [data,setData]=useState<Overview|null>(null);
  const [error,setError]=useState("");
  useEffect(()=>{apiGet<Overview>("/api/product/overview").then(setData).catch(err=>setError(String(err)));},[]);
  return <div className="mx-auto max-w-6xl space-y-6 p-3 md:p-7">
    <section className="rounded-2xl border border-teal-100 bg-gradient-to-br from-white to-teal-50 p-8 md:p-10">
      <div className="text-xs font-semibold tracking-[0.2em] text-teal-700">DEVWEAVE AI · PRODUCT WALKTHROUGH</div>
      <h1 className="mt-5 text-3xl font-semibold leading-snug text-slate-900 md:text-4xl">让研发上下文，变成有依据的下一步。</h1>
      <p className="mt-4 max-w-3xl text-base leading-8 text-slate-600">连接 Issue、PR、CI 与项目知识，把散落信息收集成可审阅的判断和动作草稿。建议、证据与人工确认分开，让协作过程可追踪。</p>
      <div className="mt-6 flex flex-wrap gap-3"><Link href="/" className="rounded-lg bg-teal-700 px-5 py-3 text-sm text-white">进入协作工作台 →</Link><Link href="/evals" className="rounded-lg border border-slate-200 bg-white px-5 py-3 text-sm text-slate-700">查看评测入口</Link></div>
    </section>
    {error&&<div role="alert" className="rounded-lg bg-red-50 p-4 text-sm text-red-700">后端暂不可访问：{error}。请先启动演示后端。</div>}
    {!data&&!error&&<div className="p-6 text-sm text-slate-500">正在读取当前数据与运行配置…</div>}
    {data&&<>
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-7 text-amber-900">
        <strong>{data.mode==="offline_demo"?"当前是无密钥离线演示":"当前使用已配置的运行环境"}</strong> · {data.data_kind==="synthetic"?"页面数据为明确构造的示例，不是生产收益。":"请按当前仓库数据来源解释结果。"}
        {data.mode==="offline_demo"&&<div>规则分析可以验证流程、结构化输出和人工确认；真实LLM、GitHub同步和向量召回需要在完整模式中分别验证。</div>}
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[["示例仓库",data.counts.repositories],["Issue",data.counts.issues],["PR",data.counts.pull_requests],["CI记录",data.counts.workflow_runs]].map(([label,count])=><div key={label} className="rounded-xl border border-slate-200 bg-white p-5"><div className="text-xs text-slate-500">{label}</div><div className="mt-3 text-3xl font-semibold text-slate-800">{count}</div></div>)}</div>
      <section><h2 className="mb-4 text-xl font-semibold text-slate-900">三条可以当场演示的业务路径</h2><div className="grid gap-5 lg:grid-cols-3">{data.scenarios.map((item,i)=><article key={item.id} className="flex flex-col rounded-xl border border-slate-200 bg-white p-6"><span className="text-xs font-semibold text-teal-700">0{i+1} / 业务任务</span><h3 className="mt-3 text-lg font-semibold text-slate-800">{item.title}</h3><p className="mt-3 text-sm leading-7 text-slate-500">{item.question}</p><ul className="my-5 space-y-2 text-sm text-slate-600">{item.outputs.map(output=><li key={output}>✓ {output}</li>)}</ul><Link href={item.url} className="mt-auto pt-3 text-sm font-medium text-teal-700">打开实际功能 →</Link></article>)}</div></section>
      <div className="grid gap-5 lg:grid-cols-2"><article className="rounded-xl border border-slate-200 bg-white p-6"><h2 className="text-lg font-semibold text-slate-800">从单一问答到受控的Agent协作</h2><p className="mt-3 text-sm leading-7 text-slate-600">工具调用解决按需取证；RAG补充项目资料；Planner组织任务，专用Agent执行，Observer检查缺口，最终综合结果。执行轨迹与动作草稿让用户能追问和确认。</p><div className="mt-5 flex gap-5 text-sm text-teal-700"><Link href="/workflow-runs">执行记录 →</Link><Link href="/action-drafts">安全草稿 →</Link><Link href="/rag">RAG工作室 →</Link></div></article><article className="rounded-xl border border-slate-200 bg-white p-6"><h2 className="text-lg font-semibold text-slate-800">什么已经可用，什么需要配置？</h2><dl className="mt-4 space-y-3 text-sm">{Object.entries(data.configuration).map(([key,value])=><div key={key} className="flex justify-between gap-4 border-b border-slate-100 pb-2"><dt className="text-slate-500">{key}</dt><dd className="font-medium text-slate-800">{typeof value==="boolean"?(value?"已配置 / 已启用":"未配置 / 未启用"):value}</dd></div>)}</dl></article></div>
      <section className="rounded-xl border border-slate-200 bg-slate-50 p-6"><h2 className="text-base font-semibold text-slate-800">使用边界</h2><ul className="mt-3 space-y-2 text-sm leading-6 text-slate-600">{data.boundaries.map(line=><li key={line}>• {line}</li>)}</ul></section>
    </>}
  </div>;
}
