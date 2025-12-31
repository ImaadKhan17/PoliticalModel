import { redis } from "../../lib/redis";
import politicians from "../../../private-data/politicians.json";

export async function update(state = null) {
  const raw = await redis.set("politicians:v1", politicians);
}
