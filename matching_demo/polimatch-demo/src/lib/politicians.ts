import type { Politician } from "./schema/politician.schema";
import { redis } from "./redis";

let cachedPols: Politician[] | null = null; 
export async function getAllPoliticians() {
  const raw = await redis.get("politicians:v1");
  if (raw === null) {
    throw new Error("Data doesn't exist");
  }

  const typed = raw as { congressman: Politician[] };
  cachedPols = typed.congressman;

  return cachedPols;
}
