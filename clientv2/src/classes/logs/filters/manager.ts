import { join_and } from "@/utils/observable_utils";
import { merge, Observable } from "rxjs";
import { distinct } from "rxjs/operators";
import { BaseFilter, SourceData } from "./filter";


// facilitates interaction of components and (categories of) filters
// allows subscription to single observable for whatever filter combo
export abstract class BaseFilterManager {
    categories: {[cat:string]: FilterCategory} = {}

    // returns observable for new logs
    get_add$(opts: FilterOptions): Observable<SourceData> {
        // get emitters
        let adds = new Array<Observable<SourceData>>()
        Object.entries(opts).forEach(([name, arg]) => {
            let cat = this.categories[name]
            adds.push(cat.get_add$(arg))
        })

        // filter for logs that pass all filters
        return join_and(adds)
    }

    // returns observable for log removals
    get_remove$(opts: FilterOptions): Observable<SourceData> {
        // get emitters
        let removes = new Array<Observable<SourceData>>()
        Object.entries(opts).forEach(([name, arg]) => {
            let cat = this.categories[name]
            removes.push(cat.get_add$(arg))
        })

        // emit logs that are removed from any filter
        let on_remove$ = merge(...removes).pipe(distinct())

        // return
        return on_remove$
    }
}


// keys are FilterCategory ids, values are arguments to that category
export interface FilterOptions {
    [cat:string]: any
}

export abstract class FilterCategory {
    filters: {[id:number]: BaseFilter} | {[id:string]: BaseFilter} = {}
    get_name(id: any) { return String(id) }

    abstract get_add$(x: any): Observable<SourceData>
    abstract get_remove$(x: any): Observable<SourceData>
}