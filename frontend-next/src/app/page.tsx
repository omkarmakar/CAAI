"use client";
import React, { useEffect, useMemo, useState } from 'react'
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip,
  ResponsiveContainer, BarChart, Bar
} from 'recharts'
import styles from './page.module.css'

// Configure backend origin (default to same host:8000 assumption)
const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

type AgentParam = {
  name: string;
  label?: string;
  type: 'string'|'number'|'text'|'file'|'files'|'select'|'json';
  placeholder?: string;
  required?: boolean;
  options?: string[];
}

type AgentAction = {
  label?: string;
  params?: AgentParam[];
}

type AgentMeta = {
  display?: string;
  active?: boolean;
  hint?: string;
  actions: Record<string, AgentAction>;
}

export default function Page() {
  // Tabs
  type Tab = 'overview'|'agents'|'analytics'|'activity'
  const [tab, setTab] = useState<Tab>('overview')

  const [agents, setAgents] = useState<Record<string, AgentMeta>>({})
  const [loading, setLoading] = useState(false)
  const [current, setCurrent] = useState<{ name: string|null; action: string|null }>({ name: null, action: null })
  const [formState, setFormState] = useState<Record<string, any>>({})
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string|null>(null)
  const [toggling, setToggling] = useState<Record<string, boolean>>({})

  // Overview / Metrics / Activity / Analytics state
  const [overview, setOverview] = useState<any>(null)
  const [metrics, setMetrics] = useState<{ metrics: { name: string; active: boolean; executions: number; errors: number; last_ts?: string|null }[] } | null>(null)
  const [activity, setActivity] = useState<{ events: any[] } | null>(null)
  const [salesData, setSalesData] = useState<any>(null)
  const [purchasesData, setPurchasesData] = useState<any>(null)

  const currentMeta = useMemo(() => current.name ? agents[current.name] : undefined, [agents, current])
  const currentAction = useMemo(() => (currentMeta && current.action) ? currentMeta.actions[current.action] : undefined, [currentMeta, current])

  async function fetchAgents() {
    try {
      const r = await fetch(`${BACKEND}/agents`)
      const j = await r.json()
      setAgents(j)
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => { fetchAgents() }, [])

  // Fetch helpers for new tabs
  async function fetchOverview() {
    try { const r = await fetch(`${BACKEND}/overview`); setOverview(await r.json()) } catch {}
  }
  async function fetchMetrics() {
    try { const r = await fetch(`${BACKEND}/agents/metrics`); setMetrics(await r.json()) } catch {}
  }
  async function fetchActivity() {
    try { const r = await fetch(`${BACKEND}/activity?limit=100`); setActivity(await r.json()) } catch {}
  }
  async function fetchAnalytics() {
    try {
      const [s, p] = await Promise.all([
        fetch(`${BACKEND}/data/sales`).then(r => r.json()),
        fetch(`${BACKEND}/data/purchases`).then(r => r.json())
      ])
      setSalesData(s); setPurchasesData(p)
    } catch {}
  }

  // Initial load for overview/metrics/activity/analytics
  useEffect(() => {
    fetchOverview(); fetchMetrics(); fetchActivity(); fetchAnalytics()
    const id = setInterval(() => { fetchOverview(); fetchMetrics(); fetchActivity() }, 30000)
    return () => clearInterval(id)
  }, [])

  async function setActive(name: string, active: boolean) {
    // Optimistic update and disable while in-flight
    setToggling(prev => ({ ...prev, [name]: true }))
    setAgents(prev => ({ ...prev, [name]: { ...prev[name], active } }))
    try {
      const url = `${BACKEND}/agents/${encodeURIComponent(name)}/activate?active=${encodeURIComponent(String(active))}`
      const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ active }) })
      if (!r.ok) {
        console.warn('Activation toggle failed', r.status)
      }
    } catch (e) {
      console.warn('Activation error', e)
    } finally {
      await fetchAgents()
      setToggling(prev => ({ ...prev, [name]: false }))
    }
  }

  async function onUpload(file: File) {
    const fd = new FormData(); fd.append('file', file)
    const r = await fetch(`${BACKEND}/upload`, { method: 'POST', body: fd })
    return r.json()
  }

  async function run() {
    if (!current.name || !current.action) return
    setLoading(true); setError(null); setResult(null)
    try {
      const payload = { agent: current.name, action: current.action, params: formState }
      const r = await fetch(`${BACKEND}/agents/execute`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      })
      const j = await r.json()
      setResult(j)
      if (!j || j.status === 'error' || j.error) setError(j.message || j.error || 'Execution failed')
    } catch (e: any) {
      setError(String(e))
    } finally { setLoading(false) }
  }

  function onParamChange(p: AgentParam, v: any) {
    setFormState((s: Record<string, any>) => ({ ...s, [p.name]: v }))
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>CA AI Agent Dashboard</h1>
        <span className={styles.status}>Backend: {Object.keys(agents).length ? 'online' : 'connecting…'}</span>
      </header>
      <div className={styles.tabs}>
        {renderTab('overview', 'Overview', tab, setTab)}
        {renderTab('agents', 'AI Agents', tab, setTab)}
        {renderTab('analytics', 'Data Analytics', tab, setTab)}
        {renderTab('activity', 'Recent Activity', tab, setTab)}
      </div>
      <main className={styles.main}>
        {tab === 'overview' && (
          <OverviewPanel overview={overview} metrics={metrics} />
        )}

        {tab === 'agents' && (
        <div className={styles.row}>
          <section className={styles.agents}>
            {Object.entries(agents as Record<string, AgentMeta>).map(([name, meta]) => (
            <div key={name} className={styles.card}>
              <div className={styles.cardTitle}>{meta.display || name}</div>
              {meta.hint && <div className={styles.hint}>{meta.hint}</div>}
              <div className={styles.cardActions}>
                <label className={styles.switch}>
                  <input type="checkbox" checked={!!meta.active} disabled={!!toggling[name]} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setActive(name, e.target.checked)} />
                  <span className={styles.slider}></span>
                </label>
                <button className={styles.btn} disabled={!meta.active} onClick={() => { if (!agents[name]?.active) return; setCurrent({ name, action: null }); setFormState({}); setResult(null); setError(null); }}>Open</button>
              </div>
              {/* Tiny metrics for the agent */}
              {metrics && (
                <div className={styles.subtle}>
                  {(() => {
                    const m = metrics.metrics.find(x => x.name === name)
                    if (!m) return null
                    return <span>Exec: {m.executions} · Err: {m.errors} {m.last_ts ? `· Last: ${new Date(m.last_ts).toLocaleString()}` : ''}</span>
                  })()}
                </div>
              )}
            </div>
            ))}
          </section>
          <section className={styles.panel}>
            <h2>{currentMeta ? (currentMeta.display || current.name) : 'Select an active agent'}</h2>
            {currentMeta && (
              <div className={styles.actionsList}>
                {Object.entries(currentMeta.actions || {}).map(([action, info]) => (
                  <div key={action}
                       className={`${styles.pill} ${current.action===action ? styles.pillActive : ''}`}
                       onClick={() => { setCurrent(c => ({ ...c, action })); setFormState({}); setResult(null); setError(null); }}>
                    {info.label || action}
                  </div>
                ))}
              </div>
            )}

            {currentAction && (
              <div className={styles.formGrid}>
                {(currentAction.params || []).map((p) => (
                  <div key={p.name} className={styles.formRow}>
                    <label>{p.label || p.name}</label>
                    {p.type === 'file' && (
                      <input type="file" onChange={async (e) => {
                        const f = e.target.files?.[0]; if (!f) return;
                        const up = await onUpload(f); onParamChange(p, up.path);
                      }} />
                    )}
                    {p.type === 'files' && (
                      <input type="file" multiple onChange={async (e) => {
                        const files = Array.from(e.target.files || []);
                        const paths: string[] = []
                        for (const f of files) { const up = await onUpload(f); paths.push(up.path); }
                        onParamChange(p, paths)
                      }} />
                    )}
                    {p.type === 'select' && (
                      <select onChange={e => onParamChange(p, e.target.value)}>
                        {(p.options||[]).map(opt => <option key={opt} value={opt}>{opt}</option>)}
                      </select>
                    )}
                    {p.type === 'number' && (
                      <input type="number" onChange={e => onParamChange(p, parseFloat(e.target.value))} />
                    )}
                    {p.type === 'text' && (
                      <textarea rows={3} placeholder={p.placeholder||''} onChange={e => onParamChange(p, e.target.value)} />
                    )}
                    {/* default string */}
                    {(!['file','files','select','number','text'].includes(p.type)) && (
                      <input type="text" placeholder={p.placeholder||''} onChange={e => onParamChange(p, e.target.value)} />
                    )}
                  </div>
                ))}
                <button className={styles.runBtn} onClick={run} disabled={loading}>{loading ? 'Running…' : 'Run'}</button>
              </div>
            )}

            {/* Result */}
            <div className={styles.result}>
              {error && <div className={styles.errorBox}>{error}</div>}
              {result && <RichResult agent={current.name!} action={current.action!} data={result} />}
            </div>
          </section>
        </div>
        )}

        {tab === 'analytics' && (
          <AnalyticsPanel sales={salesData} purchases={purchasesData} />
        )}

        {tab === 'activity' && (
          <ActivityPanel activity={activity} />
        )}
      </main>
      <footer className={styles.footer}><small>Tip: Toggle agents on/off. Click an active agent to view actions.</small></footer>
    </div>
  )
}

function JSONBox({ title, data }: { title: string; data: any }) {
  return (
    <div className={styles.box}>
      <div className={styles.boxTitle}>{title}</div>
      <pre className={styles.pre}>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}

function Table({ rows, columns }: { rows: any[]; columns?: string[] }) {
  const cols = columns || Array.from(new Set((rows||[]).flatMap(r => Object.keys(r))))
  if (!rows || rows.length === 0) return <div className={styles.subtle}>No rows</div>
  return (
    <table className={styles.table}>
      <thead><tr>{cols.map(c => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>
      {rows.map((r, i) => (
        <tr key={i}>{cols.map(c => <td key={c}>{formatCell(r[c])}</td>)}</tr>
      ))}
      </tbody>
    </table>
  )
}

function KPI({ pairs }: { pairs: [string, any][] }) {
  return (
    <div className={styles.kpis}>
      {pairs.map(([k,v]) => (
        <div key={k} className={styles.kpi}><div className={styles.kpiLabel}>{k}</div><div className={styles.kpiVal}>{String(v)}</div></div>
      ))}
    </div>
  )
}

function RichResult({ agent, action, data }: { agent: string; action: string; data: any }) {
  if (!data || data.status === 'error' || data.error) {
    return <div className={styles.errorBox}>Error: {data?.message || data?.error || 'Execution failed'}</div>
  }

  const R = RENDERERS[agent]?.[action]
  if (R) {
    try { return <R data={data} /> } catch { /* fallthrough */ }
  }
  return <JSONBox title="Result" data={data} />
}

function formatCell(v: any) {
  if (v === null || v === undefined) return ''
  if (typeof v === 'object') return JSON.stringify(v)
  return String(v)
}

const RENDERERS: Record<string, Record<string, (props: { data: any }) => JSX.Element>> = {
  DocAuditAgent: {
    audit_document: ({ data }) => (
      <div className={styles.box}>
        <div className={styles.boxTitle}>Document Audit Findings</div>
        <ul className={styles.list}>
          {(data.findings||[]).map((f: string, i: number) => <li key={i}>{f}</li>)}
        </ul>
      </div>
    )
  },
  BookBotAgent: {
    categorize: ({ data }) => (
      <>
        <div className={styles.box}><div className={styles.boxTitle}>Top Categories</div><BarList items={data.top_categories||[]} labelKey="category" valueKey="rows" /></div>
        <div className={styles.box}><div className={styles.boxTitle}>Preview (first 25)</div><Table rows={data.preview||[]} /></div>
      </>
    ),
    pnl: ({ data }) => (
      <>
        <div className={styles.box}><div className={styles.boxTitle}>P&L by Category</div><Table rows={data.pnl_by_category||[]} /></div>
        <KPI pairs={[['Net Profit', data.net_profit]]} />
      </>
    ),
    journalize: ({ data }) => {
      const items = (data.journals||[]).slice(0, 50)
      return (
        <div className={styles.box}>
          <div className={styles.boxTitle}>Journal Entries (first 50 invoices)</div>
          {items.map((j: any, i: number) => (
            <div key={i} className={styles.subcard}>
              <div className={styles.subcardTitle}>Invoice {j.invoice_no}</div>
              <Table rows={(j.entry||[]).map((e: any) => ({ account: e.account, dr: e.dr, cr: e.cr }))} columns={["account","dr","cr"]} />
            </div>
          ))}
        </div>
      )
    }
  },
  InsightBotAgent: {
    summarize_period: ({ data }) => {
      const k = data.kpis || {}
      return (
        <>
          <div className={styles.box}><div className={styles.boxTitle}>Sales KPIs</div>{k.sales && <KPI pairs={Object.entries(k.sales) as any} />}</div>
          <div className={styles.box}><div className={styles.boxTitle}>Purchases KPIs</div>{k.purchases && <KPI pairs={Object.entries(k.purchases) as any} />}</div>
          <div className={styles.box}><div className={styles.boxTitle}>Net Tax Liability (proxy)</div>{k.net_tax_liability_proxy && <KPI pairs={Object.entries(k.net_tax_liability_proxy) as any} />}</div>
        </>
      )
    },
    top_customers: ({ data }) => <div className={styles.box}><div className={styles.boxTitle}>Top Customers</div><Table rows={data.top_customers||[]} /></div>,
    anomaly_scan: ({ data }) => (
      <>
        <div className={styles.box}><div className={styles.boxTitle}>Anomalies</div><Table rows={data.anomalies||[]} /></div>
        <div className={styles.box}><div className={styles.boxTitle}>Population Stats</div><KPI pairs={[["Mean", data.population_mean||0],["StdDev", data.population_stdev||0]]} /></div>
      </>
    ),
    ai_summary: ({ data }) => <JSONBox title="AI Summary" data={data} />,
    ai_explain_anomalies: ({ data }) => <JSONBox title="AI Explanation" data={data} />,
    ai_forecast: ({ data }) => <JSONBox title="AI Forecast" data={data} />,
    ai_query: ({ data }) => (
      <div className={styles.box}>
        <div className={styles.boxTitle}>AI Query Result</div>
        {data.rows && <Table rows={data.rows} />}
        {data.query && <div className={styles.subtle}>Query: {data.query}</div>}
      </div>
    )
  },
  ComplianceCheckAgent: {
    run_checks: ({ data }) => {
      const findings = data.findings || []
      const group: Record<string, any[]> = { HIGH: [], MEDIUM: [], LOW: [] }
      findings.forEach((f: any) => { (group[f.severity] || (group[f.severity] = [])).push(f) })
      return (
        <div className={styles.box}>
          <div className={styles.boxTitle}>Findings ({findings.length})</div>
          {Object.entries(group).map(([level, arr]) => (
            <div key={level} className={styles.subcard}>
              <div className={styles.subcardTitle}>Severity <Badge kind={level==='HIGH'?'danger':level==='MEDIUM'?'warning':'info'} text={level} /></div>
              <Table rows={arr.map((f: any) => ({ ledger: f.ledger, invoice_no: f.invoice_no, issue: f.issue, hint: f.hint||'' }))} />
            </div>
          ))}
        </div>
      )
    }
  },
  GSTAgent: {
    detect_anomalies: ({ data }) => <JSONBox title="GST Anomalies" data={data} />,
    query: ({ data }) => (
      <div className={styles.box}>
        <div className={styles.boxTitle}>GST Query Results</div>
        {data.results && <Table rows={data.results} />}
        {data.expression && <div className={styles.subtle}>Expr: {data.expression}</div>}
      </div>
    ),
    summarize: ({ data }) => <JSONBox title="GST Summary" data={data} />,
  },
  TaxBot: {
    extract: ({ data }) => (
      <>
        <div className={styles.box}><div className={styles.boxTitle}>Person</div><Table rows={[data.person||{}]} /></div>
        <div className={styles.box}><div className={styles.boxTitle}>Incomes</div><Table rows={data.incomes||[]} /></div>
      </>
    ),
    calculate: ({ data }) => {
      const s = data.summary || {}
      return <KPI pairs={[["Gross Income", s.gross_income],["Deductions", s.total_deductions],["Taxable Income", s.taxable_income],["Tax Before Rebate", s.tax_before_rebate],["Rebate", s.rebate],["Health Cess", s.health_cess],["Tax Payable", s.tax_payable],["Effective Rate %", s.effective_rate]]} />
    },
    'ai-summarize': ({ data }) => <JSONBox title="AI Summary" data={data} />,
    'ai-categorize': ({ data }) => <JSONBox title="AI Categorized" data={data} />,
  }
}

function Badge({ text, kind }: { text: string; kind: 'info'|'warning'|'danger' }) {
  return <span className={`${styles.badge} ${styles[kind]}`}>{text}</span>
}

function BarList({ items, labelKey, valueKey }: { items: any[]; labelKey: string; valueKey: string }) {
  const max = Math.max(...items.map(i => Number(i[valueKey])||0), 1)
  return (
    <div className={styles.bars}>
      {items.map((i, idx) => (
        <div key={idx} className={styles.barRow}>
          <div className={styles.barLabel}>{String(i[labelKey])}</div>
          <div className={styles.bar}><div className={styles.barFill} style={{ width: `${Math.round(((Number(i[valueKey])||0)/max)*100)}%` }} /></div>
          <div className={styles.barVal}>{String(i[valueKey])}</div>
        </div>
      ))}
    </div>
  )
}

function renderTab(key: string, label: string, active: string, setActiveTab: (t: any) => void) {
  const is = active === key
  return (
    <div className={`${styles.tab} ${is ? styles.tabActive : ''}`} onClick={() => setActiveTab(key)}>{label}</div>
  )
}

function OverviewPanel({ overview, metrics }: { overview: any; metrics: any }) {
  return (
    <section className={styles.grid}>
      <div className={styles.kpiCard}><div className={styles.kpiTitle}>Total Agents</div><div className={styles.kpiBig}>{overview?.total_agents ?? '-'}</div></div>
      <div className={styles.kpiCard}><div className={styles.kpiTitle}>Active</div><div className={styles.kpiBig} style={{color:'#2fb36e'}}>{overview?.active_agents ?? '-'}</div></div>
      <div className={styles.kpiCard}><div className={styles.kpiTitle}>Inactive</div><div className={styles.kpiBig} style={{color:'#ffadad'}}>{overview?.inactive_agents ?? '-'}</div></div>
      <div className={styles.kpiCard}><div className={styles.kpiTitle}>Health</div><div className={styles.kpiSmall}>{overview?.health?.backend||'?'}</div><div className={styles.kpiTiny}>{overview?.health?.time ? new Date(overview.health.time).toLocaleString() : ''}</div></div>

      <div className={styles.card} style={{gridColumn:'1 / -1'}}>
        <div className={styles.cardTitle}>Agent Metrics</div>
        {metrics?.metrics?.length ? (
          <Table rows={metrics.metrics} />
        ) : (<div className={styles.subtle}>No metrics yet</div>)}
      </div>
    </section>
  )
}

function AnalyticsPanel({ sales, purchases }: { sales: any; purchases: any }) {
  return (
    <section className={styles.grid2}>
      <div className={styles.card}>
        <div className={styles.cardTitle}>Sales Trend</div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={sales?.trend || []} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
              <CartesianGrid stroke="#22305c" />
              <XAxis dataKey="date" stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <YAxis stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#2fb36e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <KPI pairs={[["Total Sales", sales?.total ?? 0]] as any} />
      </div>

      <div className={styles.card}>
        <div className={styles.cardTitle}>Sales GST Rate Distribution</div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={sales?.rate_dist || []}>
              <CartesianGrid stroke="#22305c" />
              <XAxis dataKey="rate" stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <YAxis stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#2b8fff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className={styles.card}>
        <div className={styles.cardTitle}>Purchases Trend</div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={purchases?.trend || []} margin={{ top: 8, right: 12, bottom: 8, left: 0 }}>
              <CartesianGrid stroke="#22305c" />
              <XAxis dataKey="date" stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <YAxis stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#ffad3d" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <KPI pairs={[["Total Purchases", purchases?.total ?? 0]] as any} />
      </div>

      <div className={styles.card}>
        <div className={styles.cardTitle}>Purchases GST Rate Distribution</div>
        <div className={styles.chart}>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={purchases?.rate_dist || []}>
              <CartesianGrid stroke="#22305c" />
              <XAxis dataKey="rate" stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <YAxis stroke="#9aa5d1" tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#ab6fff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}

function ActivityPanel({ activity }: { activity: { events: any[] } | null }) {
  const events = activity?.events || []
  return (
    <section className={styles.card}>
      <div className={styles.cardTitle}>Recent Activity</div>
      {events.length === 0 ? <div className={styles.subtle}>No events yet</div> : (
        <div className={styles.timeline}>
          {events.map((e, idx) => (
            <div key={idx} className={styles.timelineItem}>
              <div className={styles.timelineMeta}>{e.ts ? new Date(e.ts).toLocaleString() : ''}</div>
              <div className={styles.timelineBody}>
                {e.type === 'agent_activation' && (
                  <div>Agent <b>{e.agent}</b> set to <b>{String(e.active)}</b></div>
                )}
                {e.type === 'agent_execute' && (
                  <div>Execute <b>{e.agent}</b>/<code>{e.action}</code> → <b>{e.status}</b>{e.error ? ` (${e.error})` : ''}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
