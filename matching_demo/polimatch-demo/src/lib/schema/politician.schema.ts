import * as z from "zod";

export const IssueStanceSchema = z.object({
  stance: z
    .number()
    .min(-1)
    .max(1)
    .describe("Conservative stance score: -1 (liberal) to 1 (conservative)"),
});


export const issueKeys = [
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

export type IssueKey = (typeof issueKeys)[number];

const IssuesSchema = z.object({
  Economy: IssueStanceSchema,
  Healthcare: IssueStanceSchema,
  Immigration: IssueStanceSchema,
  Climate: IssueStanceSchema,
  Energy: IssueStanceSchema,
  Education: IssueStanceSchema,
  CivilRights: IssueStanceSchema,
  Crime: IssueStanceSchema,
  Defense: IssueStanceSchema,
  Tech: IssueStanceSchema,
  Housing: IssueStanceSchema,
  Labor: IssueStanceSchema,
});

export const PoliticianSchema = z.object({
  id: z.string(),
  name: z.string().min(1),
  party: z.enum(["R", "D", "I"]),
  chamber: z.enum(["House", "Senate"]),
  state: z.string().length(2).uppercase(),
  district: z.string().regex(/^\d+$/).nullable(),
  issues: IssuesSchema,
  topPriorities: z.array(z.string()).min(1),
  tags: z.array(z.string().min(1)).min(1),
  blurb: z.string().min(20),
});

export type Politician = z.infer<typeof PoliticianSchema>;
