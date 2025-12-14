import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Clinical Audit Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Open infrastructure for clinician-led clinical audits. Design, deploy, 
          and analyze audits with embedded methodological guidance and analysis-ready data capture.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/register"
            className="btn btn-primary px-8 py-3 text-lg"
          >
            Get Started
          </Link>
          <Link
            to="/library"
            className="btn btn-secondary px-8 py-3 text-lg"
          >
            Browse Library
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="grid md:grid-cols-3 gap-8">
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-3">Visual Audit Builder</h3>
          <p className="text-gray-600">
            Design questionnaires with structured data capture and real-time methodological guidance.
          </p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-3">Data Protection by Design</h3>
          <p className="text-gray-600">
            GDPR-compliant with PII segregation, encryption, and automated DPIA generation.
          </p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-3">Analysis-Ready Data</h3>
          <p className="text-gray-600">
            Export clean, normalized datasets with automatic data dictionaries and derived metrics.
          </p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-3">Interactive Dashboards</h3>
          <p className="text-gray-600">
            Real-time benchmarking, geographic comparisons, and longitudinal trend analysis.
          </p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-3">Open Audit Library</h3>
          <p className="text-gray-600">
            Public repository of reusable audit instruments and aggregated results.
          </p>
        </div>
        
        <div className="card p-6">
          <h3 className="text-xl font-semibold mb-3">Methodological Guidance</h3>
          <p className="text-gray-600">
            Embedded best-practice recommendations and validated instrument suggestions.
          </p>
        </div>
      </section>

      {/* Key Stats */}
      <section className="bg-nhs-blue text-white rounded-lg p-12">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">100%</div>
            <div className="text-nhs-lightBlue">Open Source</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">GDPR</div>
            <div className="text-nhs-lightBlue">Compliant</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">NHS</div>
            <div className="text-nhs-lightBlue">Compatible</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">Zero</div>
            <div className="text-nhs-lightBlue">Vendor Lock-in</div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="space-y-6">
        <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
        
        <div className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
              1
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Design Your Audit</h3>
              <p className="text-gray-600">
                Use the visual builder to create questionnaires with structured questions, 
                validation rules, and conditional logic.
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
              2
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Review Guidance</h3>
              <p className="text-gray-600">
                Get real-time methodological feedback and suggestions for validated instruments.
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
              3
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Collect Data</h3>
              <p className="text-gray-600">
                Clinicians enter data through auto-generated forms with real-time validation.
              </p>
            </div>
          </div>
          
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-primary-500 text-white rounded-full flex items-center justify-center font-bold">
              4
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Analyze Results</h3>
              <p className="text-gray-600">
                Export clean datasets, view interactive dashboards, and generate reports.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
