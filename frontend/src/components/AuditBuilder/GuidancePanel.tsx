import { QuestionDraft, QuestionType, QUESTION_TYPE_LABELS } from './types'

type GuidanceResult = {
  hasWarnings: boolean
  warnings: string[]
  suggestions: string[]
}

type QuestionnaireScores = {
  methodological_quality_score: number
  analysability_score: number
  structure_percentage: number
  validation_percentage: number
  instrument_percentage: number
  naming_percentage: number
  completeness_score: number
  missing_domains: string[]
}

const VALIDATED_INSTRUMENTS = {
  eq5d: { name: 'EQ-5D-5L', description: 'Quality of life measure' },
  barthel: { name: 'Barthel Index', description: 'Activities of daily living' },
  phq9: { name: 'PHQ-9', description: 'Depression screening' },
  gad7: { name: 'GAD-7', description: 'Anxiety screening' },
} as const

function analyzeQuestion(question: QuestionDraft): GuidanceResult {
  const warnings: string[] = []
  const suggestions: string[] = []

  if (question.question_type === 'text_short' || question.question_type === 'text_long') {
    warnings.push('Free text is difficult to analyze quantitatively')
    suggestions.push('Consider categorical options or validated scales where possible')
  }

  if (
    question.question_type === 'categorical_single' ||
    question.question_type === 'categorical_multiple' ||
    question.question_type === 'ordinal'
  ) {
    const options = question.options?.choices?.filter((c) => c.trim().length > 0) ?? []
    if (options.length < 2) warnings.push('Categorical questions need at least 2 options')
    if (options.length > 10) warnings.push('Too many options may confuse respondents')
  }

  if (question.question_type === 'numeric') {
    const v = question.validation ?? {}
    if (v.min === undefined && v.max === undefined) {
      warnings.push('Numeric questions should have min/max validation')
      suggestions.push('Set plausible clinical ranges to catch data entry errors')
    }
  }

  if (!question.variable_name || question.variable_name.trim().length === 0) {
    warnings.push('Variable name is missing')
    suggestions.push('Add a clear variable name for analysis/export')
  }

  const text = (question.question_text || '').toLowerCase()
  Object.values(VALIDATED_INSTRUMENTS).forEach((inst) => {
    const tokens = inst.name.toLowerCase().split(/\s+/)
    if (tokens.some((t) => t.length >= 3 && text.includes(t))) {
      suggestions.push(`Consider using the validated ${inst.name} instrument (${inst.description})`)
    }
  })

  return { hasWarnings: warnings.length > 0, warnings, suggestions }
}

function computeScores(questions: QuestionDraft[]): QuestionnaireScores {
  const total = questions.length
  if (total === 0) {
    return {
      methodological_quality_score: 0,
      analysability_score: 0,
      structure_percentage: 0,
      validation_percentage: 0,
      instrument_percentage: 0,
      naming_percentage: 0,
      completeness_score: 0,
      missing_domains: ['demographics', 'clinical_presentation', 'intervention', 'outcomes', 'process_metrics'],
    }
  }

  const structuredCount = questions.filter(
    (q) => q.question_type !== 'text_short' && q.question_type !== 'text_long'
  ).length

  const validatedCount = questions.filter((q) => q.validation && Object.keys(q.validation).length > 0).length
  const instrumentCount = questions.filter((q) => (q.validated_instrument || '').trim().length > 0).length
  const namingCount = questions.filter((q) => (q.variable_name || '').trim().length > 0).length

  const structure = (structuredCount / total) * 100
  const validation = (validatedCount / total) * 100
  const instrument = (instrumentCount / total) * 100
  const naming = (namingCount / total) * 100

  const methodologicalQuality = structure * 0.4 + validation * 0.3 + instrument * 0.2 + naming * 0.1
  const analysability = structure * 0.6 + validation * 0.3 + naming * 0.1

  const domainsCovered = {
    demographics: false,
    clinical_presentation: false,
    intervention: false,
    outcomes: false,
    process_metrics: false,
  }

  for (const q of questions) {
    const t = (q.question_text || '').toLowerCase()
    if (['age', 'sex', 'gender', 'ethnicity'].some((w) => t.includes(w))) domainsCovered.demographics = true
    if (['diagnosis', 'symptom', 'presentation'].some((w) => t.includes(w))) domainsCovered.clinical_presentation = true
    if (['treatment', 'surgery', 'procedure', 'intervention'].some((w) => t.includes(w))) domainsCovered.intervention = true
    if (['outcome', 'complication', 'mortality', 'readmission'].some((w) => t.includes(w))) domainsCovered.outcomes = true
    if (['time', 'delay', 'waiting', 'duration'].some((w) => t.includes(w))) domainsCovered.process_metrics = true
  }

  const completenessScore =
    (Object.values(domainsCovered).filter(Boolean).length / Object.keys(domainsCovered).length) * 100

  const missingDomains = Object.entries(domainsCovered)
    .filter(([, covered]) => !covered)
    .map(([k]) => k)

  const round2 = (n: number) => Math.round(n * 100) / 100

  return {
    methodological_quality_score: round2(methodologicalQuality),
    analysability_score: round2(analysability),
    structure_percentage: round2(structure),
    validation_percentage: round2(validation),
    instrument_percentage: round2(instrument),
    naming_percentage: round2(naming),
    completeness_score: round2(completenessScore),
    missing_domains: missingDomains,
  }
}

function badgeColor(type: 'ok' | 'warn'): string {
  return type === 'ok'
    ? 'bg-secondary text-secondary-foreground'
    : 'bg-destructive text-destructive-foreground'
}

function QuestionTypePill({ type }: { type: QuestionType }) {
  return (
    <span className="inline-flex items-center rounded-md border px-2 py-0.5 text-xs text-gray-700">
      {QUESTION_TYPE_LABELS[type]}
    </span>
  )
}

export default function GuidancePanel({
  questions,
  selected,
}: {
  questions: QuestionDraft[]
  selected?: QuestionDraft
}) {
  const scores = computeScores(questions)
  const selectedGuidance = selected ? analyzeQuestion(selected) : null

  return (
    <div className="card p-4 space-y-4">
      <div>
        <h3 className="text-sm font-semibold">Guidance</h3>
        <p className="text-xs text-gray-600">Real-time feedback to keep questionnaires analysis-ready.</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-md border p-3">
          <div className="text-xs text-gray-600">Methodological quality</div>
          <div className="text-lg font-semibold">{scores.methodological_quality_score}%</div>
        </div>
        <div className="rounded-md border p-3">
          <div className="text-xs text-gray-600">Analysability</div>
          <div className="text-lg font-semibold">{scores.analysability_score}%</div>
        </div>
        <div className="rounded-md border p-3">
          <div className="text-xs text-gray-600">Structured questions</div>
          <div className="text-lg font-semibold">{scores.structure_percentage}%</div>
        </div>
        <div className="rounded-md border p-3">
          <div className="text-xs text-gray-600">Validation coverage</div>
          <div className="text-lg font-semibold">{scores.validation_percentage}%</div>
        </div>
        <div className="rounded-md border p-3">
          <div className="text-xs text-gray-600">Validated instruments</div>
          <div className="text-lg font-semibold">{scores.instrument_percentage}%</div>
        </div>
        <div className="rounded-md border p-3">
          <div className="text-xs text-gray-600">Variable naming</div>
          <div className="text-lg font-semibold">{scores.naming_percentage}%</div>
        </div>
      </div>

      <div className="rounded-md border p-3">
        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-600">Completeness</div>
          <span
            className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs ${badgeColor(
              scores.missing_domains.length === 0 ? 'ok' : 'warn'
            )}`}
          >
            {scores.completeness_score}%
          </span>
        </div>
        {scores.missing_domains.length > 0 ? (
          <div className="mt-2 text-xs text-gray-700">
            Missing domains: {scores.missing_domains.join(', ')}
          </div>
        ) : (
          <div className="mt-2 text-xs text-gray-700">All core domains appear covered.</div>
        )}
      </div>

      <div className="border-t pt-4">
        <h4 className="text-sm font-semibold">Selected question</h4>
        {!selected ? (
          <div className="text-xs text-gray-600 mt-1">Select a question to see detailed guidance.</div>
        ) : (
          <div className="mt-2 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-medium truncate">{selected.question_code || 'Untitled'}</div>
              <QuestionTypePill type={selected.question_type} />
            </div>

            {selectedGuidance && selectedGuidance.warnings.length > 0 ? (
              <div className="rounded-md border border-destructive/30 bg-destructive/10 p-3">
                <div className="text-xs font-semibold text-destructive">Warnings</div>
                <ul className="mt-1 list-disc pl-5 text-xs text-gray-800 space-y-1">
                  {selectedGuidance.warnings.map((w, idx) => (
                    <li key={idx}>{w}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="rounded-md border bg-secondary/30 p-3 text-xs text-gray-700">
                No warnings detected for this question.
              </div>
            )}

            {selectedGuidance && selectedGuidance.suggestions.length > 0 && (
              <div className="rounded-md border p-3">
                <div className="text-xs font-semibold">Suggestions</div>
                <ul className="mt-1 list-disc pl-5 text-xs text-gray-800 space-y-1">
                  {selectedGuidance.suggestions.map((s, idx) => (
                    <li key={idx}>{s}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
