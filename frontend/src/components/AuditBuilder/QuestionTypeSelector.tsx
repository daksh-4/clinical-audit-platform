import { QuestionType, QUESTION_TYPE_DESCRIPTIONS, QUESTION_TYPE_LABELS } from './types'

const ORDER: QuestionType[] = [
  'categorical_single',
  'categorical_multiple',
  'ordinal',
  'boolean',
  'numeric',
  'date',
  'time',
  'datetime',
  'text_short',
  'text_long',
]

export default function QuestionTypeSelector({
  onSelect,
}: {
  onSelect: (type: QuestionType) => void
}) {
  return (
    <div className="card p-4 space-y-3">
      <div>
        <h3 className="text-sm font-semibold">Add a question</h3>
        <p className="text-xs text-gray-600">Choose a type to insert a new question.</p>
      </div>

      <div className="space-y-2">
        {ORDER.map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => onSelect(type)}
            className="w-full text-left rounded-md border bg-background px-3 py-2 hover:bg-secondary"
          >
            <div className="text-sm font-medium">{QUESTION_TYPE_LABELS[type]}</div>
            <div className="text-xs text-gray-600">{QUESTION_TYPE_DESCRIPTIONS[type]}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
