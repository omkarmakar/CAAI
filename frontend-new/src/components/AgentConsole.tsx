"use client"

import React, { useEffect, useState } from 'react'
import api from '../lib/api'

type AgentMeta = Record<string, any>

export default function AgentConsole() {
  const [meta, setMeta] = useState<AgentMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)
  const [action, setAction] = useState<string | null>(null)
  const [formValues, setFormValues] = useState<Record<string, any>>({})
  const [output, setOutput] = useState<any>(null)

  useEffect(() => {
    api.get('/agents').then((r) => {
      setMeta(r.data)
    }).catch((e) => {
      console.error(e)
    }).finally(() => setLoading(false))
  }, [])

  function setField(name: string, value: any) {
    setFormValues((s) => ({ ...s, [name]: value }))
  }

  async function uploadFile(file: File) {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    return res.data.path
  }

  async function submit() {
    if (!selected || !action) return
    setOutput(null)
    const agent = selected
    const act = action
    const params: any = {}
    const actionMeta = meta[selected].actions[action]
    for (const p of actionMeta.params || []) {
      const val = formValues[p.name]
      if (p.type === 'file' && val instanceof File) {
        try {
          const path = await uploadFile(val)
          params[p.name] = path
        } catch (e) {
          setOutput({ error: 'File upload failed' })
          return
        }
      } else {
        params[p.name] = val
      }
    }

    try {
      const res = await api.post('/agents/execute', { agent, action: act, params })
      setOutput(res.data)
    } catch (e: any) {
      setOutput({ error: e?.response?.data || e.message })
    }
  }

  if (loading) return <div>Loading agents...</div>
  if (!meta) return <div>No agents found</div>

  return (
    <div className="container">
      <h2 className="text-xl font-bold mb-4">Agent Console</h2>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <h3 className="font-semibold">Agents</h3>
          <ul>
            {Object.keys(meta).map((k) => (
              <li key={k}>
                <button className={`py-1 px-2 hover:bg-gray-100 w-full text-left ${selected===k? 'bg-gray-200':''}`} onClick={() => { setSelected(k); setAction(null); setFormValues({}) }}>{meta[k].display || k}</button>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-semibold">Actions</h3>
          {selected ? (
            <ul>
              {Object.keys(meta[selected].actions || {}).map((a) => (
                <li key={a}><button className={`py-1 px-2 hover:bg-gray-100 w-full text-left ${action===a? 'bg-gray-200':''}`} onClick={() => { setAction(a); setFormValues({}) }}>{meta[selected].actions[a].label || a}</button></li>
              ))}
            </ul>
          ) : <div>Select an agent</div>}
        </div>
        <div>
          <h3 className="font-semibold">Form</h3>
          {selected && action ? (
            <div>
              {(meta[selected].actions[action].params || []).map((p: any) => (
                <div key={p.name} className="mb-2">
                  <label className="block text-sm font-medium">{p.label}</label>
                  {p.type === 'file' ? (
                    <input type="file" onChange={(e) => setField(p.name, e.target.files?.[0])} />
                  ) : p.type === 'json' ? (
                    <textarea rows={4} className="w-full p-2 border" onChange={(e) => setField(p.name, JSON.parse(e.target.value || 'null'))} />
                  ) : (
                    <input className="w-full p-2 border" onChange={(e) => setField(p.name, p.type==='number'? Number(e.target.value) : e.target.value)} />
                  )}
                </div>
              ))}
              <button className="mt-2 px-4 py-2 bg-blue-600 text-white rounded" onClick={submit}>Run</button>
            </div>
          ) : <div>Select an action</div>}
        </div>
      </div>

      <div className="mt-6">
        <h3 className="font-semibold">Output</h3>
        <pre className="bg-black text-white p-4 rounded">{JSON.stringify(output, null, 2)}</pre>
      </div>
    </div>
  )
}
