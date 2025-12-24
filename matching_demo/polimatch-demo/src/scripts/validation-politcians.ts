import * as z from "zod";
import { PoliticianSchema } from "@/lib/schema/politician.schema";
import politicians from '../../private-data/politicians.json';

for (const pol of politicians['house']){
    try{
    PoliticianSchema.parse(pol);
    }
    catch(error){
    
    console.log(pol);
    process.exit(0);
    }
}