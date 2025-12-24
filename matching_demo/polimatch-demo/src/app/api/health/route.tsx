import { NextResponse } from "next/server";
import {redis} from "@/lib/redis";

export async function GET(){
    await redis.set(
        "healthcheck:v1",
        {
            ok:true,
            time: Date.now(),
            name: "Hasan",
        }
    );

    const value = await redis.get("healthcheck:v1");
    
    return NextResponse.json({
        status: "connected",
        value,
    });
}

