import type { ChangeEvent } from 'react'
import { QuestionDraft, QuestionType } from './types'

function numberOrUndefined(value: string): number | undefined {
  if (value.trim() === '') return undefined
  const n = Number(value)
  if (Number.isNaN(n)) return undefined
  return n
}

export default function ValidationBuilder({
  questionType,
  question,
  onChange,
}: {
  questionType: QuestionType
  question: QuestionDraft
  onChange: (patch: Partial<QuestionDraft>) => void
}) {
  const validation = question.validation ?? {}

  const setValidation = (next: Record<string, any>) => {
    const cleaned = Object.keys(next).length === 0 ? null : next
    onChange({ validation: cleaned })
  }

  const setField = (key: string, value: any) => {
    const next = { ...validation }
    if (value === undefined || value === '' || value === null) {
      delete next[key]
    } else {
      next[key] = value
    }
    setValidation(next)
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold">Validation</h4>
        <span className="text-xs text-gray-500">Optional</span>
      </div>

      {questionType === 'numeric' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-600">Min</label>
            <input
              className="input"
              inputMode="numeric"
              value={validation.min ?? ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setField('min', numberOrUndefined(e.target.value))
              }
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">Max</label>
            <input
              className="input"
              inputMode="numeric"
              value={validation.max ?? ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setField('max', numberOrUndefined(e.target.value))
              }
            />
          </div>
        </div>
      )}

      {(questionType === 'text_short' || questionType === 'text_long') && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-600">Max length</label>
            <input
              className="input"
              inputMode="numeric"
              value={validation.max_length ?? ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setField('max_length', numberOrUndefined(e.target.value))
              }
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">Regex pattern</label>
            <input
              className="input"
              value={validation.pattern ?? ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setField('pattern', e.target.value)}
              placeholder="Optional"
            />
          </div>
        </div>
      )}

      {(questionType === 'categorical_single' ||
        questionType === 'categorical_multiple' ||
        questionType === 'ordinal') && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-600">Min selections</label>
            <input
              className="input"
              inputMode="numeric"
              value={validation.min_selections ?? ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setField('min_selections', numberOrUndefined(e.target.value))
              }
              placeholder="Optional"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">Max selections</label>
            <input
              className="input"
              inputMode="numeric"
              value={validation.max_selections ?? ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setField('max_selections', numberOrUndefined(e.target.value))
              }
              placeholder="Optional"
            />
          </div>
        </div>
      )}

      {(questionType === 'date' || questionType === 'time' || questionType === 'datetime') && (
        <div className="text-xs text-gray-600">
          Date/time validation not configured in MVP.
        </div>
      )}

      {questionType === 'boolean' && (
        <div className="text-xs text-gray-600">No extra validation needed.</div>
      )}

      <button
        type="button"
        className="btn btn-secondary px-3 py-2"
        onClick={() => onChange({ validation: null })}
        disabled={!question.validation || Object.keys(question.validation).length === 0}
      >
        Clear validation
      </button>
    </div>
  )
}
