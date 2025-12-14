import ValidationBuilder from './ValidationBuilder'
import {
  ConditionalLogic,
  QuestionDraft,
  QuestionType,
  QUESTION_TYPE_LABELS,
  defaultVariableType,
  slugifyVariableName,
} from './types'

function isChoiceType(t: QuestionType): boolean {
  return t === 'categorical_single' || t === 'categorical_multiple' || t === 'ordinal'
}

function updateChoices(question: QuestionDraft, idx: number, value: string): { choices: string[] } {
  const current = question.options?.choices ?? []
  const next = [...current]
  next[idx] = value
  return { choices: next }
}

function removeChoice(question: QuestionDraft, idx: number): { choices: string[] } {
  const current = question.options?.choices ?? []
  const next = current.filter((_, i) => i !== idx)
  return { choices: next.length === 0 ? [''] : next }
}

function normalizeConditionalLogic(logic: ConditionalLogic): ConditionalLogic {
  if (!logic) return null
  const cleaned: any = { ...logic }
  if (!cleaned.depends_on) delete cleaned.depends_on
  if (!cleaned.operator) delete cleaned.operator
  if (!cleaned.value) delete cleaned.value
  return Object.keys(cleaned).length === 0 ? null : cleaned
}

export default function QuestionEditor({
  question,
  allQuestions,
  onChange,
  onDelete,
}: {
  question: QuestionDraft
  allQuestions: QuestionDraft[]
  onChange: (next: QuestionDraft) => void
  onDelete: () => void
}) {
  const set = (patch: Partial<QuestionDraft>) => onChange({ ...question, ...patch })

  const controllerOptions = allQuestions
    .filter((q) => q.id !== question.id)
    .map((q) => ({ value: q.question_code, label: `${q.question_code}: ${q.question_text || '(no text)'}` }))

  return (
    <div className="card p-4 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold">Question editor</h3>
          <p className="text-xs text-gray-600">Configure the selected question.</p>
        </div>
        <button type="button" className="btn btn-secondary px-3 py-2" onClick={onDelete}>
          Delete
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-600">Question code</label>
          <input
            className="input"
            value={question.question_code}
            onChange={(e) => {
              const code = e.target.value
              set({
                question_code: code,
                variable_name: question.variable_name ? question.variable_name : slugifyVariableName(code),
              })
            }}
            placeholder="e.g. Q1"
          />
        </div>
        <div>
          <label className="text-xs text-gray-600">Type</label>
          <select
            className="input"
            value={question.question_type}
            onChange={(e) => {
              const t = e.target.value as QuestionType
              set({
                question_type: t,
                options: isChoiceType(t) ? (question.options ?? { choices: [''] }) : null,
                variable_type: question.variable_type || defaultVariableType(t),
              })
            }}
          >
            {Object.entries(QUESTION_TYPE_LABELS).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="text-xs text-gray-600">Question text</label>
        <textarea
          className="input h-24"
          value={question.question_text}
          onChange={(e) => set({ question_text: e.target.value })}
          placeholder="What should the user answer?"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-600">Variable name</label>
          <input
            className="input"
            value={question.variable_name}
            onChange={(e) => set({ variable_name: slugifyVariableName(e.target.value) })}
            placeholder="analysis_ready_variable"
          />
        </div>
        <div>
          <label className="text-xs text-gray-600">Variable type</label>
          <input
            className="input"
            value={question.variable_type}
            onChange={(e) => set({ variable_type: e.target.value })}
            placeholder="categorical / numeric / string"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-600">Validated instrument (optional)</label>
          <input
            className="input"
            value={question.validated_instrument ?? ''}
            onChange={(e) => set({ validated_instrument: e.target.value })}
            placeholder="e.g. EQ-5D-5L"
          />
        </div>
        <div>
          <label className="text-xs text-gray-600">Required</label>
          <div className="flex items-center gap-2 mt-2">
            <input
              type="checkbox"
              checked={question.required}
              onChange={(e) => set({ required: e.target.checked })}
            />
            <span className="text-sm">This field must be completed</span>
          </div>
        </div>
      </div>

      <div>
        <label className="text-xs text-gray-600">Help text (optional)</label>
        <textarea
          className="input h-20"
          value={question.help_text ?? ''}
          onChange={(e) => set({ help_text: e.target.value })}
          placeholder="Guidance for data entry"
        />
      </div>

      <div>
        <label className="text-xs text-gray-600">Clinical guidance (optional)</label>
        <textarea
          className="input h-20"
          value={question.clinical_guidance ?? ''}
          onChange={(e) => set({ clinical_guidance: e.target.value })}
          placeholder="Clinical context / best practice note"
        />
      </div>

      <div>
        <label className="text-xs text-gray-600">Variable description (optional)</label>
        <textarea
          className="input h-20"
          value={question.variable_description ?? ''}
          onChange={(e) => set({ variable_description: e.target.value })}
          placeholder="Data dictionary description"
        />
      </div>

      {isChoiceType(question.question_type) && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold">Options</h4>
            <button
              type="button"
              className="btn btn-secondary px-3 py-2"
              onClick={() => set({ options: { choices: [...(question.options?.choices ?? ['']), ''] } })}
            >
              Add option
            </button>
          </div>

          <div className="space-y-2">
            {(question.options?.choices ?? []).map((choice, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <input
                  className="input"
                  value={choice}
                  onChange={(e) => set({ options: updateChoices(question, idx, e.target.value) })}
                  placeholder={`Option ${idx + 1}`}
                />
                <button
                  type="button"
                  className="btn btn-secondary px-3 py-2"
                  onClick={() => set({ options: removeChoice(question, idx) })}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <ValidationBuilder
        questionType={question.question_type}
        question={question}
        onChange={(patch) => set(patch)}
      />

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold">Conditional logic</h4>
          <span className="text-xs text-gray-500">Optional</span>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="text-xs text-gray-600">Depends on</label>
            <select
              className="input"
              value={question.conditional_logic?.depends_on ?? ''}
              onChange={(e) =>
                set({
                  conditional_logic: normalizeConditionalLogic({
                    ...(question.conditional_logic ?? {}),
                    depends_on: e.target.value || undefined,
                  }),
                })
              }
            >
              <option value="">(none)</option>
              {controllerOptions.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-600">Operator</label>
            <select
              className="input"
              value={question.conditional_logic?.operator ?? ''}
              onChange={(e) =>
                set({
                  conditional_logic: normalizeConditionalLogic({
                    ...(question.conditional_logic ?? {}),
                    operator: (e.target.value as any) || undefined,
                  }),
                })
              }
              disabled={!question.conditional_logic?.depends_on}
            >
              <option value="">(select)</option>
              <option value="equals">equals</option>
              <option value="not_equals">not equals</option>
              <option value="in">in (comma-separated)</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-600">Value</label>
            <input
              className="input"
              value={question.conditional_logic?.value ?? ''}
              onChange={(e) =>
                set({
                  conditional_logic: normalizeConditionalLogic({
                    ...(question.conditional_logic ?? {}),
                    value: e.target.value || undefined,
                  }),
                })
              }
              disabled={!question.conditional_logic?.depends_on || !question.conditional_logic?.operator}
              placeholder="e.g. Yes"
            />
          </div>
        </div>

        <button
          type="button"
          className="btn btn-secondary px-3 py-2"
          onClick={() => set({ conditional_logic: null })}
          disabled={!question.conditional_logic}
        >
          Clear conditional logic
        </button>
      </div>
    </div>
  )
}
