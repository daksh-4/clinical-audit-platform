export default function PageSkeleton() {
  return (
    <div className="space-y-6">
      <div className="animate-pulse space-y-3">
        <div className="h-8 w-1/3 rounded bg-gray-200" />
        <div className="h-4 w-2/3 rounded bg-gray-200" />
        <div className="h-4 w-1/2 rounded bg-gray-200" />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="animate-pulse h-28 rounded bg-gray-200" />
        <div className="animate-pulse h-28 rounded bg-gray-200" />
        <div className="animate-pulse h-28 rounded bg-gray-200" />
      </div>

      <div className="animate-pulse space-y-3">
        <div className="h-4 w-full rounded bg-gray-200" />
        <div className="h-4 w-5/6 rounded bg-gray-200" />
        <div className="h-4 w-2/3 rounded bg-gray-200" />
      </div>
    </div>
  )
}
