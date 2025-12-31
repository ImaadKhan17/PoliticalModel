import { z } from "zod";

export const IssueKeySchema = z.enum([
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
]);

// One issue preference: stance + importance
export const UserIssuePreferenceSchema = z.object({
  stance: z.number().min(-1).max(1).describe("User stance from -1 to 1"),
  importance: z.number().min(0).max(1).describe("Importance from 0 to 1"),
});

// Full user vector (all 12 required). `.strict()` prevents extra keys.
export const UserVectorSchema = z
  .object({
    Economy: UserIssuePreferenceSchema,
    Healthcare: UserIssuePreferenceSchema,
    Immigration: UserIssuePreferenceSchema,
    Climate: UserIssuePreferenceSchema,
    Energy: UserIssuePreferenceSchema,
    Education: UserIssuePreferenceSchema,
    CivilRights: UserIssuePreferenceSchema,
    Crime: UserIssuePreferenceSchema,
    Defense: UserIssuePreferenceSchema,
    Tech: UserIssuePreferenceSchema,
    Housing: UserIssuePreferenceSchema,
    Labor: UserIssuePreferenceSchema,
  })
  .strict();

export type UserVector = z.infer<typeof UserVectorSchema>;
export type IssueKey = z.infer<typeof IssueKeySchema>;

// Optional: default neutral vector (useful for fallback)
export const DEFAULT_USER_VECTOR: UserVector = {
  Economy: { stance: 0, importance: 0 },
  Healthcare: { stance: 0, importance: 0 },
  Immigration: { stance: 0, importance: 0 },
  Climate: { stance: 0, importance: 0 },
  Energy: { stance: 0, importance: 0 },
  Education: { stance: 0, importance: 0 },
  CivilRights: { stance: 0, importance: 0 },
  Crime: { stance: 0, importance: 0 },
  Defense: { stance: 0, importance: 0 },
  Tech: { stance: 0, importance: 0 },
  Housing: { stance: 0, importance: 0 },
  Labor: { stance: 0, importance: 0 },
};
