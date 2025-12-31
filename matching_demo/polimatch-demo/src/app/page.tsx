"use client";


const US_STATES = [
  { value: "", label: "Select a state (optional)" },
  { value: "AL", label: "Alabama" },
  { value: "AK", label: "Alaska" },
  { value: "AZ", label: "Arizona" },
  { value: "AR", label: "Arkansas" },
  { value: "CA", label: "California" },
  { value: "CO", label: "Colorado" },
  { value: "CT", label: "Connecticut" },
  { value: "DE", label: "Delaware" },
  { value: "FL", label: "Florida" },
  { value: "GA", label: "Georgia" },
  { value: "HI", label: "Hawaii" },
  { value: "ID", label: "Idaho" },
  { value: "IL", label: "Illinois" },
  { value: "IN", label: "Indiana" },
  { value: "IA", label: "Iowa" },
  { value: "KS", label: "Kansas" },
  { value: "KY", label: "Kentucky" },
  { value: "LA", label: "Louisiana" },
  { value: "ME", label: "Maine" },
  { value: "MD", label: "Maryland" },
  { value: "MA", label: "Massachusetts" },
  { value: "MI", label: "Michigan" },
  { value: "MN", label: "Minnesota" },
  { value: "MS", label: "Mississippi" },
  { value: "MO", label: "Missouri" },
  { value: "MT", label: "Montana" },
  { value: "NE", label: "Nebraska" },
  { value: "NV", label: "Nevada" },
  { value: "NH", label: "New Hampshire" },
  { value: "NJ", label: "New Jersey" },
  { value: "NM", label: "New Mexico" },
  { value: "NY", label: "New York" },
  { value: "NC", label: "North Carolina" },
  { value: "ND", label: "North Dakota" },
  { value: "OH", label: "Ohio" },
  { value: "OK", label: "Oklahoma" },
  { value: "OR", label: "Oregon" },
  { value: "PA", label: "Pennsylvania" },
  { value: "RI", label: "Rhode Island" },
  { value: "SC", label: "South Carolina" },
  { value: "SD", label: "South Dakota" },
  { value: "TN", label: "Tennessee" },
  { value: "TX", label: "Texas" },
  { value: "UT", label: "Utah" },
  { value: "VT", label: "Vermont" },
  { value: "VA", label: "Virginia" },
  { value: "WA", label: "Washington" },
  { value: "WV", label: "West Virginia" },
  { value: "WI", label: "Wisconsin" },
  { value: "WY", label: "Wyoming" },
];

export default function Home() {
  const handleFindMatches = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // TODO: implement later
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center bg-white py-24 px-6 dark:bg-black sm:px-16">
        <div className="w-full">

          <div className="mb-10 space-y-3 text-center sm:text-left">
            <h1 className="text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
              Find matches based on what you care about.
            </h1>
            <p className="max-w-xl text-lg leading-8 text-zinc-600 dark:text-zinc-400">
              Describe your priorities and optionally choose a state. Then hit{" "}
              <span className="font-medium text-zinc-950 dark:text-zinc-50">
                Find Matches
              </span>
              .
            </p>
          </div>

          <form onSubmit={handleFindMatches} className="w-full space-y-6">
            <div className="space-y-2">
              <label
                htmlFor="priorities"
                className="text-sm font-medium text-zinc-950 dark:text-zinc-50"
              >
                Describe your priorities
              </label>
              <textarea
                id="priorities"
                name="priorities"
                placeholder="Example: I care most about affordability, housing, reducing climate change..."
                rows={6}
                className="w-full resize-y rounded-2xl border border-black/[.08] bg-white px-4 py-3 text-base text-zinc-950 shadow-sm outline-none transition focus:border-black/20 focus:ring-2 focus:ring-black/10 dark:border-white/[.145] dark:bg-black dark:text-zinc-50 dark:focus:border-white/30 dark:focus:ring-white/10"
              />
              <p className="text-sm text-zinc-500 dark:text-zinc-400">
                Be as specific as you want
              </p>
            </div>

            <div className="space-y-2">
              <label
                htmlFor="state"
                className="text-sm font-medium text-zinc-950 dark:text-zinc-50"
              >
                State (optional)
              </label>
              <select
                id="state"
                name="state"
                defaultValue=""
                className="w-full appearance-none rounded-2xl border border-black/[.08] bg-white px-4 py-3 text-base text-zinc-950 shadow-sm outline-none transition focus:border-black/20 focus:ring-2 focus:ring-black/10 dark:border-white/[.145] dark:bg-black dark:text-zinc-50 dark:focus:border-white/30 dark:focus:ring-white/10"
              >
                {US_STATES.map((s) => (
                  <option key={s.value || "none"} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              className="flex h-12 w-full items-center justify-center rounded-full bg-foreground px-6 text-base font-medium text-background transition-colors hover:bg-[#383838] dark:hover:bg-[#ccc] sm:w-auto"
            >
              Find Matches
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
