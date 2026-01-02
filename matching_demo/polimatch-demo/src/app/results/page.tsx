"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type MatchItem = {
  id: string;
  name: string;
  party: string;
  state: string;
  chamber: string;
  district?: string | null;
  blurb?: string | null;
  score: number;
  topAlignments: string[];
};

type MatchResponse = {
  data: MatchItem[];
};

export default function ResultsPage() {
  const [results, setResults] = useState<MatchResponse | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("match_data");
    if (!raw) return;

    try {
      const parsed = JSON.parse(raw) as MatchResponse;
      setResults(parsed);
    } catch {
      // If something got stored incorrectly, treat as empty
      setResults(null);
    }
  }, []);

  if (!results) {
    return (
      <div className="min-h-screen bg-zinc-50 p-6 dark:bg-black">
        <div className="mx-auto max-w-3xl rounded-2xl bg-white p-6 dark:bg-black">
          <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
            No results yet
          </h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            Go back and run a match first.
          </p>
          <Link
            href="/"
            className="mt-4 inline-flex rounded-full bg-foreground px-5 py-2 text-background hover:opacity-90"
          >
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 p-6 dark:bg-black">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="rounded-2xl bg-white p-6 dark:bg-black">
          <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
            Your top matches
          </h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            Ranked by alignment score (0–100).
          </p>
        </div>

        <div className="space-y-4">
          {results.data.map((m, idx) => (
            <div
              key={m.id}
              className="rounded-2xl border border-black/[.08] bg-white p-5 shadow-sm dark:border-white/[.145] dark:bg-black"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-sm text-zinc-500 dark:text-zinc-400">
                    #{idx + 1}
                  </div>
                  <div className="text-lg font-semibold text-black dark:text-zinc-50">
                    {m.name}
                  </div>
                  <div className="text-sm text-zinc-600 dark:text-zinc-400">
                    {m.party} • {m.chamber}
                    {m.state ? ` • ${m.state}` : ""}
                    {m.district ? `-${m.district}` : ""}
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-sm text-zinc-500 dark:text-zinc-400">
                    Score
                  </div>
                  <div className="text-2xl font-semibold text-black dark:text-zinc-50">
                    {m.score}
                  </div>
                </div>
              </div>

              {m.blurb ? (
                <p className="mt-3 text-sm text-zinc-600 dark:text-zinc-400">
                  {m.blurb}
                </p>
              ) : null}

              <div className="mt-4 flex flex-wrap gap-2">
                {m.topAlignments.map((issue) => (
                  <span
                    key={issue}
                    className="rounded-full border border-black/[.08] px-3 py-1 text-sm text-zinc-700 dark:border-white/[.145] dark:text-zinc-200"
                  >
                    {issue}
                  </span>
                ))}
              </div>

              <div className="mt-4">
                <Link
                  href={`/politician?id=${encodeURIComponent(m.id)}`}
                  className="text-sm font-medium text-zinc-900 underline underline-offset-4 dark:text-zinc-100"
                >
                  View profile →
                </Link>
              </div>
            </div>
          ))}
        </div>

        <div className="rounded-2xl bg-white p-6 dark:bg-black">
          <Link
            href="/"
            className="inline-flex rounded-full border border-black/[.08] px-5 py-2 text-zinc-900 hover:bg-zinc-50 dark:border-white/[.145] dark:text-zinc-100 dark:hover:bg-white/5"
          >
            Run another match
          </Link>
        </div>
      </div>
    </div>
  );
}
