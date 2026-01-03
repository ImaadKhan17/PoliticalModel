import { NextResponse } from "next/server";
import { z } from "zod";

import { groq } from "@/lib/groq"; // wherever your groq.ts is
import { UserVectorSchema } from "@/lib/schema/uservector.schema";

// 1) Validate input text (only sanity checks)
const ParseRequestSchema = z
  .object({
    text: z.string().trim().min(5, "Please add a bit more detail.").max(2000),
  })
  .strict();

// 2) Give the model an explicit JSON shape to follow (keys must match EXACTLY)
const ISSUE_KEYS = [
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
] as const;

function schemaReminder() {
  return `Return ONLY a single JSON object with exactly these 12 top-level keys: ${ISSUE_KEYS.join(
    ", "
  )}.

For each key, output an object:
{
  "stance": number in [-1, 1],
  "importance": number in [0, 1]
}

STANCE SCALE (USE DECIMALS OFTEN):
- stance = -1 means the user's preference is strongly liberal/left on that issue (more government action/regulation/redistribution/protections, depending on the issue).
- stance = +1 means the user's preference is strongly conservative/right on that issue (more market/individual responsibility/enforcement/tradition/national security, depending on the issue).
- stance = 0 means neutral / mixed / unclear.
- stance is continuous: it can be ANY number like -0.8, -0.3, 0, 0.4, 0.9 (not just -1 or +1).
- Use extremes ONLY when the user is very explicit or absolute.
  Examples of extreme language: "must", "ban", "zero tolerance", "always", "abolish", "fully", "no exceptions".
- Use moderate values for typical opinions:
  - strong lean:   -0.7 to -0.9 or +0.7 to +0.9
  - moderate lean: -0.3 to -0.6 or +0.3 to +0.6
  - slight lean:   -0.1 to -0.2 or +0.1 to +0.2
  - neutral/unclear: 0
- If the text gives mixed signals for an issue, choose a value closer to 0 (e.g., -0.2, 0.1, 0).


IMPORTANCE SCALE:
- importance = 1 means it's a top priority for the user.
- importance = 0 means the user does not care / did not mention it.
- Use 0 when the issue is not mentioned.
- If the issue is mentioned only briefly, use a low importance like 0.2–0.4.
- If the user emphasizes it (e.g., "most important", repeated, strong language), use 0.7–1.0.

RULES:
- You MUST include all 12 keys even if not mentioned (set stance=0, importance=0).
- No extra keys.
- No explanations, no markdown, no prose—JSON only.

IMPORTANT: Stance reflects direction; importance reflects priority.
Do NOT make stance extreme just because importance is high.
High importance can still have moderate stance (e.g., stance=0.4, importance=0.9).


`;
}


export async function POST(req: Request) {
  // Read JSON
  const body = await req.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  // Validate input
  const parsed = ParseRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Invalid input", details: parsed.error.flatten() },
      { status: 400 }
    );
  }

  const { text } = parsed.data;

  try {
    // Call Groq
    const completion = await groq.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      temperature: 0.2,
      messages: [
        {
          role: "system",
          content:
            "You are a strict JSON generator for a political preference vector.",
        },
        { role: "system", content: schemaReminder() },
        {
          role: "user",
          content: `User priorities:\n${text}\n\nGenerate the JSON now.`,
        },
      ],
      // JSON mode: ensures valid JSON output (older but very reliable)
      response_format: { type: "json_object" },
    });

    const content = completion.choices?.[0]?.message?.content;
    if (!content) {
      return NextResponse.json(
        { error: "No content returned from model" },
        { status: 502 }
      );
    }

    // Parse JSON
    const maybeVector = JSON.parse(content);

    // Validate output with your strict schema (ranges + 12 keys)
    const vectorParsed = UserVectorSchema.safeParse(maybeVector);
    if (!vectorParsed.success) {
      return NextResponse.json(
        {
          error: "Model returned invalid vector",
          details: vectorParsed.error.flatten(),
        },
        { status: 502 }
      );
    }

    return NextResponse.json({ userVector: vectorParsed.data });
  } catch (err: any) {
    return NextResponse.json(
      { error: "Groq parse failed", details: err?.message ?? String(err) },
      { status: 502 }
    );
  }
}
