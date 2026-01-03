"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

type IssueKey =
  | "Economy"
  | "Healthcare"
  | "Immigration"
  | "Climate"
  | "Energy"
  | "Education"
  | "CivilRights"
  | "Crime"
  | "Defense"
  | "Tech"
  | "Housing"
  | "Labor";

const ISSUE_KEYS: IssueKey[] = [
  "Economy",
  "Healthcare",
  "Immigration",
  "Climate",
  "Energy",
  "Education",
  "CivilRights",
  "Crime",
  "Defense",
  "Tech",
  "Housing",
  "Labor",
];

type Politician = {
  id: string;
  name: string;
  party: string;
  chamber: string;
  state: string;
  district?: string | null;
  tags?: string[] | null;
  blurb?: string | null;
  topPriorities?: string[] | null;
  issues: Record<IssueKey, { stance: number }>;
};

function StanceBar({ stance }: { stance: number }) {
  const pct = Math.round(((stance + 1) / 2) * 100);

  return (
    <div className="w-full">
      <div className="h-2 w-full rounded-full bg-zinc-200 dark:bg-white/10">
        <div
          className="h-2 rounded-full bg-zinc-900 dark:bg-zinc-100"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="mt-1 flex justify-between text-xs text-zinc-500 dark:text-zinc-400">
        <span>-1</span>
        <span>{stance.toFixed(2)}</span>
        <span>+1</span>
      </div>
    </div>
  );
}

export default function PoliticianPage() {
  const searchParams = useSearchParams();
  const idParam = searchParams.get("id"); // string | null

  const [profile, setProfile] = useState<Politician | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const titleLine = useMemo(() => {
    if (!profile) return "";
    return `${profile.party} • ${profile.chamber} • ${profile.state}${
      profile.district ? `-${profile.district}` : ""
    }`;
  }, [profile]);

  useEffect(() => {
    let cancelled = false;

    async function run(id: string) {
      setLoading(true);
      setError(null);

      try {
        //  avoids encodeURIComponent(null) and handles encoding safely
        const url = new URL("/api/politician", window.location.origin);
        url.searchParams.set("id", id);

        const res = await fetch(url.toString());
        const json = await res.json().catch(() => null);

        if (!res.ok) {
          const msg =
            (json && (json.error || json.message)) ||
            `Request failed (${res.status})`;
          throw new Error(msg);
        }

        if (!cancelled) setProfile(json?.politicians ?? null);
      } catch (e: unknown) {
        const message =
          e instanceof Error ? e.message : "Failed to load profile";
        if (!cancelled) {
          setError(message);
          setProfile(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    if (!idParam) {
      // optional: clear state if someone navigates to /politician without id
      setProfile(null);
      setError(null);
      setLoading(false);
      return;
    }

    run(idParam);

    return () => {
      cancelled = true;
    };
  }, [idParam]);

  if (!idParam) {
    return (
      <div className="min-h-screen bg-zinc-50 p-6 dark:bg-black">
        <div className="mx-auto max-w-3xl rounded-2xl bg-white p-6 dark:bg-black">
          <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
            Missing id
          </h1>
          <p className="mt-2 text-zinc-600 dark:text-zinc-400">
            This page needs an <code>id</code> query parameter.
          </p>
          <Link href="/results" className="mt-4 inline-block underline">
            Back to results
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 p-6 dark:bg-black">
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="rounded-2xl bg-white p-6 dark:bg-black">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold text-black dark:text-zinc-50">
                {profile ? profile.name : loading ? "Loading..." : "Profile"}
              </h1>
              {profile ? (
                <p className="mt-1 text-zinc-600 dark:text-zinc-400">
                  {titleLine}
                </p>
              ) : null}
            </div>

            <Link
              href="/results"
              className="text-sm font-medium text-zinc-900 underline underline-offset-4 dark:text-zinc-100"
            >
              ← Results
            </Link>
          </div>

          {error ? (
            <p className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-200">
              {error}
            </p>
          ) : null}

          {profile?.blurb ? (
            <p className="mt-4 text-zinc-700 dark:text-zinc-300">
              {profile.blurb}
            </p>
          ) : null}

          {profile?.tags?.length ? (
            <div className="mt-4 flex flex-wrap gap-2">
              {profile.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-full border border-black/[.08] px-3 py-1 text-sm text-zinc-700 dark:border-white/[.145] dark:text-zinc-200"
                >
                  {t}
                </span>
              ))}
            </div>
          ) : null}

          {profile?.topPriorities?.length ? (
            <div className="mt-6">
              <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
                Top priorities
              </h2>
              <ul className="mt-2 list-inside list-disc text-zinc-700 dark:text-zinc-300">
                {profile.topPriorities.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>

        <div className="rounded-2xl bg-white p-6 dark:bg-black">
          <h2 className="text-lg font-semibold text-black dark:text-zinc-50">
            Issue stances
          </h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Stances are normalized from -1 to +1.
          </p>

          <div className="mt-6 space-y-4">
            {profile ? (
              ISSUE_KEYS.map((k) => (
                <div key={k} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
                      {k}
                    </div>
                  </div>

                  {/*  safe access even if issues is missing somehow */}
                  <StanceBar stance={profile.issues?.[k]?.stance ?? 0} />
                </div>
              ))
            ) : loading ? (
              <p className="text-zinc-600 dark:text-zinc-400">
                Loading stances…
              </p>
            ) : (
              <p className="text-zinc-600 dark:text-zinc-400">
                No profile loaded.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
