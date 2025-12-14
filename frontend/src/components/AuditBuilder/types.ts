export type QuestionType =
  | 'categorical_single'
  | 'categorical_multiple'
  | 'ordinal'
  | 'numeric'
  | 'date'
  | 'time'
  | 'datetime'
  | 'text_short'
  | 'text_long'
  | 'boolean'

export type ConditionalLogic = {
  depends_on?: string
  operator?: 'equals' | 'not_equals' | 'in'
  value?: string
} | null

export type QuestionDraft = {
  id: string
  question_code: string
  question_text: string
  question_type: QuestionType
  help_text?: string
  clinical_guidance?: string
  required: boolean
  options: { choices: string[] } | null
  validation: Record<string, any> | null
  conditional_logic: ConditionalLogic
  variable_name: string
  variable_type: string
  variable_description?: string
  validated_instrument?: string
}

export type QuestionnaireDraft = {
  title: string
  description?: string
  questions: QuestionDraft[]
}

export type AuditDraft = {
  title: string
  description?: string
  clinical_domain: string
  population: string
  start_date: string // YYYY-MM-DD
  end_date?: string // YYYY-MM-DD
  governance_body?: string
  data_protection_level: 'no_pii' | 'pseudonymised' | 'pii_required'
  is_public: boolean
  require_consent: boolean
  retention_days: number
}

export const QUESTION_TYPE_LABELS: Record<QuestionType, string> = {
  categorical_single: 'Categorical (single choice)',
  categorical_multiple: 'Categorical (multiple choice)',
  ordinal: 'Ordinal (ranked choices)',
  numeric: 'Numeric',
  date: 'Date',
  time: 'Time',
  datetime: 'Date & time',
  text_short: 'Short text',
  text_long: 'Long text',
  boolean: 'Yes / No',
}

export const QUESTION_TYPE_DESCRIPTIONS: Record<QuestionType, string> = {
  categorical_single: 'One answer from a list of options.',
  categorical_multiple: 'Multiple answers from a list of options.',
  ordinal: 'Ordered categories (e.g. mild/moderate/severe).',
  numeric: 'A number (e.g. age, time interval).',
  date: 'A calendar date.',
  time: 'A time of day.',
  datetime: 'A date and time.',
  text_short: 'Free text (short).',
  text_long: 'Free text (long).',
  boolean: 'A simple yes/no response.',
}

export function newId(): string {
  // Browser + modern Node
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const cryptoAny: any = (globalThis as any).crypto
  if (cryptoAny?.randomUUID) return cryptoAny.randomUUID()
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export function slugifyVariableName(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
}

export function defaultVariableType(questionType: QuestionType): string {
  switch (questionType) {
    case 'numeric':
      return 'numeric'
    case 'date':
      return 'date'
    case 'time':
      return 'time'
    case 'datetime':
      return 'datetime'
    case 'boolean':
      return 'boolean'
    case 'text_short':
    case 'text_long':
      return 'string'
    case 'ordinal':
    case 'categorical_single':
    case 'categorical_multiple':
      return 'categorical'
    default:
      return 'string'
  }
}

export function makeDefaultQuestion(nextCode: string, questionType: QuestionType): QuestionDraft {
  return {
    id: newId(),
    question_code: nextCode,
    question_text: '',
    question_type: questionType,
    help_text: '',
    clinical_guidance: '',
    required: true,
    options:
      questionType === 'categorical_single' ||
      questionType === 'categorical_multiple' ||
      questionType === 'ordinal'
        ? { choices: [''] }
        : null,
    validation: null,
    conditional_logic: null,
    variable_name: slugifyVariableName(nextCode),
    variable_type: defaultVariableType(questionType),
    variable_description: '',
    validated_instrument: '',
  }
}

export function nextQuestionCode(existing: QuestionDraft[]): string {
  const used = new Set(existing.map((q) => q.question_code))
  let i = existing.length + 1
  while (used.has(`Q${i}`)) i += 1
  return `Q${i}`
}
