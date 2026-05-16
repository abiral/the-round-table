interface TimeBucketHeaderProps {
  label: string
}

export function TimeBucketHeader({ label }: TimeBucketHeaderProps) {
  return (
    <div className="text-[11px] font-semibold tracking-[0.08em] uppercase text-text-subtle px-2 mt-4 mb-1 first:mt-0">
      {label}
    </div>
  )
}
