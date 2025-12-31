import { getAllPoliticians } from "@/lib/politicians";
import { NextResponse } from "next/server";

export async function GET(req:Request){
    let pols = await getAllPoliticians();
    const {searchParams } = new URL(req.url);

    const state  = searchParams.get("state")

    if (state) {
      pols = pols.filter((p) => p.state === state);
    }

     return NextResponse.json({
       politicians:pols,
     });

}