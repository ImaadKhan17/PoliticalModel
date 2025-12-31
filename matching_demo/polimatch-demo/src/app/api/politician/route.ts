import { getAllPoliticians } from "@/lib/politicians";
import { NextResponse } from "next/server";

export async function GET(req:Request){
    let pols = await getAllPoliticians();
    const {searchParams } = new URL(req.url);

    const id  = searchParams.get("id")

    if (id) {
      return NextResponse.json({
        politicians: pols.find(pol => pol.id === id),
      });
    }else{
        return NextResponse.json(
            {error:"Missing ID"}, {status:400}
        );
    }

     

}