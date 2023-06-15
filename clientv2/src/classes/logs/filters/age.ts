import { Observable } from "rxjs";
import { BaseFilter, SourceData } from "./filter";
import { SummaryData } from "../summary_data";


export class AgeFilter extends BaseFilter {
    public age_ms: number

    // age in days
    constructor(public age: number, target: Observable<SummaryData>) {
        super(target)
        this.age_ms = 86400*1000*age
    }

    // check if elapsed time less than specified age
    // if age is <= 0, always return true
    filter(data: SummaryData) {
        if(this.age_ms > 0) {
            let elapsed = Date.now() - data.start*1000
            return elapsed <= this.age_ms
        } else {
            return true
        }
    }

    get_expiration(data: SummaryData) {
        return data.start*1000 + this.age_ms
    }
}