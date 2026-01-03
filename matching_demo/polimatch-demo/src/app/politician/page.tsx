import { Suspense } from "react";
import PoliticianClient from "./PoliticianClient";

export const dynamic = "force-dynamic";

export default function Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-zinc-50 p-6 dark:bg-black">
          <div className="mx-auto max-w-3xl rounded-2xl bg-white p-6 dark:bg-black">
            <p className="text-zinc-600 dark:text-zinc-400">Loading…</p>
          </div>
        </div>
      }
    >
      <PoliticianClient />
    </Suspense>
  );
}
