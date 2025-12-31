// src/app/api/match/route.ts
import { NextResponse } from "next/server";
import { z } from "zod";

import { UserVectorSchema } from "@/lib/schema/uservector.schema";
import { getAllPoliticians } from "@/lib/politicians";
import { issueKeys } from "@/lib/schema/politician.schema";


const MatchRequestSchema = z
  .object({
    userVector: UserVectorSchema,
    state: z.string().length(2).optional(), 
  })
  .strict();

function clamp01(n: number) {
  if (n < 0) return 0;
  if (n > 1) return 1;
  return n;
}

export async function POST(req: Request) {
  // 1) Read body
  const body = await req.json().catch(() => null);
  if (!body) {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }


  // 2) Validate wrapper + userVector
  const parsed = MatchRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { error: "Invalid input", details: parsed.error.flatten() },
      { status: 400 }
    );
  }

  const { userVector, state } = parsed.data;

  // 3) Load politicians
  let politicians = await getAllPoliticians();

  if(state){
    politicians = politicians.filter(p => p.state === state)
  }
 const scores = [];

 for (const p of politicians) {
   const pIssues = p.issues; // object: { Economy: { stance }, ... }
   const uIssues = userVector; // object: { Economy: { stance, importance }, ... }

   let weightedSum = 0;
   let importanceSum = 0;
   let Alignmnets = [];

   // iterate over issue KEYS (strings), not the issues object itself
   for (const issueKey of issueKeys) {
     const userStance = uIssues[issueKey].stance;
     const importance = uIssues[issueKey].importance;

     if (importance <= 0) continue;

     const polStance = pIssues[issueKey].stance;

     // similarity in [0,1]
     const similarity = 1 - Math.abs(userStance - polStance) / 2;

     weightedSum += similarity * importance;
     Alignmnets.push({issue: issueKey, strength: similarity * importance})

     importanceSum += importance;
   }
   let topAlignments = Alignmnets.sort((a,b) => b.strength - a.strength).slice(0,3);
   const returnAlignments = []
   for (let i = 0; i<topAlignments.length;i++){
        returnAlignments.push(topAlignments[i].issue);
   }
   const score01 = importanceSum > 0 ? weightedSum / importanceSum : 0;
   const score = Math.round(score01 * 100);

   scores.push({ id: p.id, name:p.name, party:p.party, state:p.state, chamber:p.chamber, district:p.district,blurb:p.blurb, score, topAlignments: returnAlignments });
 }

 return NextResponse.json({data:scores.sort((a,b)=> b.score-a.score).slice(0,10)});
  
}
