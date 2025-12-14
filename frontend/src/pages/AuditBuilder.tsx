import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { auditApi, questionnaireApi } from '../services/api'
import GuidancePanel from '../components/AuditBuilder/GuidancePanel'
import QuestionEditor from '../components/AuditBuilder/QuestionEditor'
import QuestionTypeSelector from '../components/AuditBuilder/QuestionTypeSelector'
import {
  AuditDraft,
  QuestionDraft,
  QuestionType,
  QuestionnaireDraft,
  makeDefaultQuestion,
  nextQuestionCode,
  slugifyVariableName,
  defaultVariableType,
} from '../components/AuditBuilder/types'

type ApiErrorShape = {
  detail?: string
  errors?: any
  request_id?: string
}

function isoFromDateInput(date: string | undefined): string | undefined {
  if (!date) return undefined
  // HTML date input gives YYYY-MM-DD; JS parses it as UTC midnight.
  const d = new Date(date)
  if (Number.isNaN(d.getTime())) return undefined
  return d.toISOString()
}

function safeErrorMessage(err: any): string {
  const data: ApiErrorShape | undefined = err?.response?.data
  const status = err?.response?.status
  const reqId = data?.request_id ? ` (request_id: ${data.request_id})` : ''

  if (data?.detail) return `${data.detail}${reqId}`
  if (typeof err?.message === 'string' && err.message) return `${err.message}${reqId}`
  if (status) return `Request failed (HTTP ${status})${reqId}`
  return `Request failed${reqId}`
}

function downloadJson(filename: string, data: any) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function normalizeQuestionDraft(q: Partial<QuestionDraft>, fallbackCode: string): QuestionDraft {
  const questionType = (q.question_type as QuestionType) || 'text_short'
  const code = q.question_code || fallbackCode
  const variableName = q.variable_name || slugifyVariableName(code)

  const choiceTypes = new Set<QuestionType>(['categorical_single', 'categorical_multiple', 'ordinal'])
  const wantsChoices = choiceTypes.has(questionType)
  const rawChoices = (q.options as any)?.choices
  const choices = Array.isArray(rawChoices) ? rawChoices : wantsChoices ? [''] : []

  return {
    id: (q as any).id || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    question_code: code,
    question_text: q.question_text || '',
    question_type: questionType,
    help_text: q.help_text || '',
    clinical_guidance: q.clinical_guidance || '',
    required: q.required ?? true,
    options: wantsChoices ? { choices: choices.map((c: any) => String(c)) } : null,
    validation: (q.validation as any) ?? null,
    conditional_logic: (q.conditional_logic as any) ?? null,
    variable_name: variableName,
    variable_type: q.variable_type || defaultVariableType(questionType),
    variable_description: q.variable_description || '',
    validated_instrument: q.validated_instrument || '',
  }
}

function mapQuestionDraftToApi(q: QuestionDraft) {
  const trimmedChoices = q.options?.choices?.map((c) => c.trim()).filter((c) => c.length > 0) ?? []
  const isChoiceType =
    q.question_type === 'categorical_single' ||
    q.question_type === 'categorical_multiple' ||
    q.question_type === 'ordinal'

  return {
    question_code: q.question_code,
    question_text: q.question_text,
    question_type: q.question_type,
    help_text: q.help_text || null,
    clinical_guidance: q.clinical_guidance || null,
    required: q.required,
    options: isChoiceType ? { choices: trimmedChoices } : null,
    validation: q.validation && Object.keys(q.validation).length > 0 ? q.validation : null,
    conditional_logic: q.conditional_logic && Object.keys(q.conditional_logic).length > 0 ? q.conditional_logic : null,
    variable_name: q.variable_name || slugifyVariableName(q.question_code),
    variable_type: q.variable_type || defaultVariableType(q.question_type),
    variable_description: q.variable_description || null,
    validated_instrument: q.validated_instrument || null,
  }
}

export default function AuditBuilder() {
  const { auditId } = useParams()
  const navigate = useNavigate()

  const [audit, setAudit] = useState<AuditDraft>({
    title: '',
    description: '',
    clinical_domain: '',
    population: '',
    start_date: new Date().toISOString().slice(0, 10),
    end_date: '',
    governance_body: '',
    data_protection_level: 'no_pii',
    is_public: false,
    require_consent: false,
    retention_days: 3650,
  })

  const [questionnaire, setQuestionnaire] = useState<QuestionnaireDraft>({
    title: 'Questionnaire v1',
    description: '',
    questions: [],
  })

  const [selectedQuestionId, setSelectedQuestionId] = useState<string | null>(null)
  const selectedQuestion = useMemo(
    () => questionnaire.questions.find((q) => q.id === selectedQuestionId),
    [questionnaire.questions, selectedQuestionId]
  )

  const [pageLoading, setPageLoading] = useState(false)
  const [savingAudit, setSavingAudit] = useState(false)
  const [savingQuestionnaire, setSavingQuestionnaire] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [draggingId, setDraggingId] = useState<string | null>(null)

  const importInputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    if (!auditId) return
    let cancelled = false
    setPageLoading(true)
    setError(null)

    const load = async () => {
      try {
        const auditRes = await auditApi.get(auditId)
        if (cancelled) return
        const a = auditRes.data
        setAudit({
          title: a.title ?? '',
          description: a.description ?? '',
          clinical_domain: a.clinical_domain ?? '',
          population: a.population ?? '',
          start_date: (a.start_date ? String(a.start_date).slice(0, 10) : new Date().toISOString().slice(0, 10)) as any,
          end_date: a.end_date ? String(a.end_date).slice(0, 10) : '',
          governance_body: a.governance_body ?? '',
          data_protection_level: a.data_protection_level ?? 'no_pii',
          is_public: !!a.is_public,
          require_consent: !!a.require_consent,
          retention_days: typeof a.retention_days === 'number' ? a.retention_days : 3650,
        })

        const versionsRes = await questionnaireApi.list(auditId)
        if (cancelled) return

        const versions = Array.isArray(versionsRes.data) ? versionsRes.data : []
        if (versions.length === 0) {
          setQuestionnaire({ title: 'Questionnaire v1', description: '', questions: [] })
          setSelectedQuestionId(null)
          return
        }

        const latestVersion = versions[0]?.version
        if (typeof latestVersion !== 'number') {
          setQuestionnaire({ title: 'Questionnaire v1', description: '', questions: [] })
          setSelectedQuestionId(null)
          return
        }

        const qRes = await questionnaireApi.get(auditId, latestVersion)
        if (cancelled) return
        const q = qRes.data
        const qs = Array.isArray(q.questions) ? q.questions : []

        const mapped: QuestionDraft[] = qs.map((raw: any, idx: number) =>
          normalizeQuestionDraft(raw, raw.question_code || `Q${idx + 1}`)
        )
        setQuestionnaire({
          title: q.title ?? `Questionnaire v${latestVersion}`,
          description: q.description ?? '',
          questions: mapped,
        })
        setSelectedQuestionId(mapped[0]?.id ?? null)
      } catch (e: any) {
        if (cancelled) return
        setError(safeErrorMessage(e))
      } finally {
        if (cancelled) return
        setPageLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [auditId])

  const canSaveAudit = useMemo(() => {
    return (
      audit.title.trim().length > 0 &&
      audit.clinical_domain.trim().length > 0 &&
      audit.population.trim().length > 0 &&
      audit.start_date.trim().length > 0
    )
  }, [audit])

  const canSaveQuestionnaire = useMemo(() => {
    return questionnaire.title.trim().length > 0 && questionnaire.questions.length > 0 && !!auditId
  }, [questionnaire.title, questionnaire.questions.length, auditId])

  const addQuestion = (type: QuestionType) => {
    const code = nextQuestionCode(questionnaire.questions)
    const q = makeDefaultQuestion(code, type)
    setQuestionnaire((prev) => ({ ...prev, questions: [...prev.questions, q] }))
    setSelectedQuestionId(q.id)
  }

  const updateSelectedQuestion = (next: QuestionDraft) => {
    setQuestionnaire((prev) => ({
      ...prev,
      questions: prev.questions.map((q) => (q.id === next.id ? next : q)),
    }))
  }

  const deleteSelectedQuestion = () => {
    if (!selectedQuestion) return
    setQuestionnaire((prev) => {
      const nextQuestions = prev.questions.filter((q) => q.id !== selectedQuestion.id)
      const nextSelected = nextQuestions[0]?.id ?? null
      setSelectedQuestionId(nextSelected)
      return { ...prev, questions: nextQuestions }
    })
  }

  const moveQuestion = (fromIdx: number, toIdx: number) => {
    setQuestionnaire((prev) => {
      const next = [...prev.questions]
      const [item] = next.splice(fromIdx, 1)
      next.splice(toIdx, 0, item)
      return { ...prev, questions: next }
    })
  }

  const onDragStart = (id: string) => setDraggingId(id)

  const onDropOn = (targetId: string) => {
    if (!draggingId) return
    if (draggingId === targetId) return

    const fromIdx = questionnaire.questions.findIndex((q) => q.id === draggingId)
    const toIdx = questionnaire.questions.findIndex((q) => q.id === targetId)
    if (fromIdx < 0 || toIdx < 0) return
    moveQuestion(fromIdx, toIdx)
    setDraggingId(null)
  }

  const saveAudit = async () => {
    setError(null)
    setSavingAudit(true)

    try {
      const fallbackStart = new Date().toISOString()
      const payload = {
        title: audit.title,
        description: audit.description || null,
        clinical_domain: audit.clinical_domain,
        population: audit.population,
        start_date: isoFromDateInput(audit.start_date) || fallbackStart,
        end_date: isoFromDateInput(audit.end_date || undefined) ?? null,
        governance_body: audit.governance_body || null,
        data_protection_level: audit.data_protection_level,
        is_public: audit.is_public,
        require_consent: audit.require_consent,
        retention_days: audit.retention_days,
      }

      if (!auditId) {
        const res = await auditApi.create(payload)
        const createdId = res.data?.id
        if (createdId && questionnaire.questions.length > 0) {
          const qPayload = {
            title: questionnaire.title,
            description: questionnaire.description || null,
            questions: questionnaire.questions.map(mapQuestionDraftToApi),
          }
          await questionnaireApi.create(createdId, qPayload)
        }
        if (createdId) navigate(`/audits/${createdId}/edit`, { replace: true })
      } else {
        await auditApi.update(auditId, {
          title: payload.title,
          description: payload.description,
          end_date: payload.end_date,
          is_public: payload.is_public,
        })
      }
    } catch (e: any) {
      setError(safeErrorMessage(e))
    } finally {
      setSavingAudit(false)
    }
  }

  const saveQuestionnaireAsNewVersion = async () => {
    if (!auditId) return
    setError(null)
    setSavingQuestionnaire(true)

    try {
      const payload = {
        title: questionnaire.title,
        description: questionnaire.description || null,
        questions: questionnaire.questions.map(mapQuestionDraftToApi),
      }
      await questionnaireApi.create(auditId, payload)
    } catch (e: any) {
      setError(safeErrorMessage(e))
    } finally {
      setSavingQuestionnaire(false)
    }
  }

  const exportTemplate = () => {
    downloadJson('audit_template.json', {
      audit,
      questionnaire,
    })
  }

  const importTemplateFromFile = async (file: File) => {
    setError(null)
    try {
      const text = await file.text()
      const parsed = JSON.parse(text)
      const a = parsed?.audit
      const q = parsed?.questionnaire

      if (!a || !q) {
        setError('Invalid template: expected { audit, questionnaire }')
        return
      }

      setAudit((prev) => ({
        ...prev,
        title: a.title ?? prev.title,
        description: a.description ?? prev.description,
        clinical_domain: a.clinical_domain ?? prev.clinical_domain,
        population: a.population ?? prev.population,
        start_date: a.start_date ?? prev.start_date,
        end_date: a.end_date ?? prev.end_date,
        governance_body: a.governance_body ?? prev.governance_body,
        data_protection_level: a.data_protection_level ?? prev.data_protection_level,
        is_public: !!a.is_public,
        require_consent: !!a.require_consent,
        retention_days: typeof a.retention_days === 'number' ? a.retention_days : prev.retention_days,
      }))

      const rawQuestions = Array.isArray(q.questions) ? q.questions : []
      const mapped = rawQuestions.map((raw: any, idx: number) =>
        normalizeQuestionDraft(raw, raw.question_code || `Q${idx + 1}`)
      )
      setQuestionnaire({
        title: q.title ?? 'Imported questionnaire',
        description: q.description ?? '',
        questions: mapped,
      })
      setSelectedQuestionId(mapped[0]?.id ?? null)
    } catch (e: any) {
      setError(e?.message ? `Import failed: ${e.message}` : 'Import failed')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Audit Builder</h1>
          <p className="text-gray-600">
            {auditId ? `Editing audit ${auditId}` : 'Create a new audit and design its questionnaire.'}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <input
            ref={importInputRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) importTemplateFromFile(file)
              if (e.target) e.target.value = ''
            }}
          />
          <button type="button" className="btn btn-secondary px-4 py-2" onClick={() => importInputRef.current?.click()}>
            Import JSON
          </button>
          <button type="button" className="btn btn-secondary px-4 py-2" onClick={exportTemplate}>
            Export JSON
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 p-4 text-sm text-gray-900">
          <div className="font-semibold text-destructive">Error</div>
          <div className="mt-1">{error}</div>
        </div>
      )}

      {pageLoading ? (
        <div className="card p-6">Loading audit…</div>
      ) : (
        <div className="grid grid-cols-12 gap-6">
          {/* Left: metadata + add question */}
          <div className="col-span-12 lg:col-span-3 space-y-4">
            <div className="card p-4 space-y-3">
              <h2 className="text-sm font-semibold">Audit metadata</h2>

              <div>
                <label className="text-xs text-gray-600">Title</label>
                <input className="input" value={audit.title} onChange={(e) => setAudit((p) => ({ ...p, title: e.target.value }))} />
              </div>

              <div>
                <label className="text-xs text-gray-600">Description</label>
                <textarea
                  className="input h-20"
                  value={audit.description ?? ''}
                  onChange={(e) => setAudit((p) => ({ ...p, description: e.target.value }))}
                />
              </div>

              <div>
                <label className="text-xs text-gray-600">Clinical domain</label>
                <input
                  className="input"
                  value={audit.clinical_domain}
                  onChange={(e) => setAudit((p) => ({ ...p, clinical_domain: e.target.value }))}
                  placeholder="e.g. orthopaedics"
                />
              </div>

              <div>
                <label className="text-xs text-gray-600">Population</label>
                <textarea
                  className="input h-20"
                  value={audit.population}
                  onChange={(e) => setAudit((p) => ({ ...p, population: e.target.value }))}
                  placeholder="Who is included?"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-600">Start date</label>
                  <input
                    type="date"
                    className="input"
                    value={audit.start_date}
                    onChange={(e) => setAudit((p) => ({ ...p, start_date: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-600">End date</label>
                  <input
                    type="date"
                    className="input"
                    value={audit.end_date ?? ''}
                    onChange={(e) => setAudit((p) => ({ ...p, end_date: e.target.value }))}
                  />
                </div>
              </div>

              <div>
                <label className="text-xs text-gray-600">Governance body</label>
                <input
                  className="input"
                  value={audit.governance_body ?? ''}
                  onChange={(e) => setAudit((p) => ({ ...p, governance_body: e.target.value }))}
                  placeholder="Optional"
                />
              </div>

              <div>
                <label className="text-xs text-gray-600">Data protection level</label>
                <select
                  className="input"
                  value={audit.data_protection_level}
                  onChange={(e) => setAudit((p) => ({ ...p, data_protection_level: e.target.value as any }))}
                >
                  <option value="no_pii">No PII</option>
                  <option value="pseudonymised">Pseudonymised</option>
                  <option value="pii_required">PII required</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-600">Retention (days)</label>
                  <input
                    className="input"
                    inputMode="numeric"
                    value={String(audit.retention_days)}
                    onChange={(e) =>
                      setAudit((p) => ({
                        ...p,
                        retention_days: Number(e.target.value || 0) || 0,
                      }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 mt-6">
                    <input
                      type="checkbox"
                      checked={audit.require_consent}
                      onChange={(e) => setAudit((p) => ({ ...p, require_consent: e.target.checked }))}
                    />
                    <span className="text-sm">Require consent</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={audit.is_public}
                      onChange={(e) => setAudit((p) => ({ ...p, is_public: e.target.checked }))}
                    />
                    <span className="text-sm">Public template</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <button
                  type="button"
                  className="btn btn-primary px-4 py-2"
                  onClick={saveAudit}
                  disabled={!canSaveAudit || savingAudit}
                >
                  {savingAudit ? (auditId ? 'Saving…' : 'Creating…') : auditId ? 'Save audit' : 'Create audit'}
                </button>
                {!auditId && (
                  <span className="text-xs text-gray-600">Create the audit to enable questionnaire versioning.</span>
                )}
              </div>
            </div>

            <div className="card p-4 space-y-3">
              <h2 className="text-sm font-semibold">Questionnaire</h2>
              <div>
                <label className="text-xs text-gray-600">Title</label>
                <input
                  className="input"
                  value={questionnaire.title}
                  onChange={(e) => setQuestionnaire((p) => ({ ...p, title: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-xs text-gray-600">Description</label>
                <textarea
                  className="input h-20"
                  value={questionnaire.description ?? ''}
                  onChange={(e) => setQuestionnaire((p) => ({ ...p, description: e.target.value }))}
                />
              </div>
              <button
                type="button"
                className="btn btn-primary px-4 py-2"
                onClick={saveQuestionnaireAsNewVersion}
                disabled={!canSaveQuestionnaire || savingQuestionnaire}
              >
                {savingQuestionnaire ? 'Saving…' : 'Save questionnaire (new version)'}
              </button>
            </div>

            <QuestionTypeSelector onSelect={addQuestion} />
          </div>

          {/* Middle: designer list + editor */}
          <div className="col-span-12 lg:col-span-6 space-y-4">
            <div className="card p-4 space-y-3">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold">Questionnaire designer</h2>
                <div className="text-xs text-gray-600">Drag to reorder</div>
              </div>

              {questionnaire.questions.length === 0 ? (
                <div className="text-sm text-gray-600">Add your first question using the panel on the left.</div>
              ) : (
                <ul className="space-y-2">
                  {questionnaire.questions.map((q, idx) => {
                    const isSelected = q.id === selectedQuestionId
                    return (
                      <li
                        key={q.id}
                        className={`rounded-md border p-3 bg-background ${isSelected ? 'ring-2 ring-ring' : ''}`}
                        draggable
                        onDragStart={() => onDragStart(q.id)}
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={() => onDropOn(q.id)}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <button
                            type="button"
                            className="text-left flex-1"
                            onClick={() => setSelectedQuestionId(q.id)}
                          >
                            <div className="text-sm font-medium">
                              {q.question_code}{' '}
                              <span className="text-gray-500 font-normal">
                                {q.question_text ? `— ${q.question_text}` : '(no question text)'}
                              </span>
                            </div>
                            <div className="text-xs text-gray-600">{q.variable_name}</div>
                          </button>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              className="btn btn-secondary px-3 py-2"
                              onClick={() => idx > 0 && moveQuestion(idx, idx - 1)}
                              disabled={idx === 0}
                            >
                              Up
                            </button>
                            <button
                              type="button"
                              className="btn btn-secondary px-3 py-2"
                              onClick={() => idx < questionnaire.questions.length - 1 && moveQuestion(idx, idx + 1)}
                              disabled={idx === questionnaire.questions.length - 1}
                            >
                              Down
                            </button>
                          </div>
                        </div>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>

            {selectedQuestion ? (
              <QuestionEditor
                question={selectedQuestion}
                allQuestions={questionnaire.questions}
                onChange={updateSelectedQuestion}
                onDelete={deleteSelectedQuestion}
              />
            ) : (
              <div className="card p-6 text-sm text-gray-600">Select a question to edit it.</div>
            )}
          </div>

          {/* Right: guidance */}
          <div className="col-span-12 lg:col-span-3">
            <GuidancePanel questions={questionnaire.questions} selected={selectedQuestion} />
          </div>
        </div>
      )}
    </div>
  )
}
