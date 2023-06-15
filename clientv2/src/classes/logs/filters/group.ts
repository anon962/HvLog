import { Observable } from "rxjs"
import { SummaryData } from "../summary_data"
import { BaseFilter } from "./filter"


// essentially a collection of filters that share a cache
export abstract class FilterGroup<T> {
    info_cache: ICache<T> = {}
    abstract filters: {[id:number]: FilterGroupMember<T>}
}

export abstract class FilterGroupMember<T> extends BaseFilter {
    constructor(
        public id: number, 
        public info_cache: ICache<T>,
        target: Observable<SummaryData>
    ) {
        super(target)
    }

    get_info(data: SummaryData) {
        return this.info_cache[this.id] || this.get_cache_value(data)
    }

    abstract get_cache_value(data: SummaryData): T
}


interface ICache<T> {
    [id: number]: T
}