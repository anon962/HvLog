import { LogList } from "@/services/list.service";
import { join_and } from "@/utils/observable_utils";
import { Observable } from "rxjs";
import { SummaryData } from "../summary_data";
import { BaseFilter } from "./filter";
import { FilterCategory } from "./manager";

type CompFn = (id: string, x: SummaryData[keyof SummaryData]) => boolean

export class PropertyFilter extends BaseFilter {
    constructor(
        public id: string,
        public prop: keyof SummaryData,
        public comp_fn: CompFn,
        target: Observable<SummaryData>
    ) {
        super(target)
    }

    filter(data: SummaryData) {
        let val = data[this.prop]
        return this.comp_fn(this.id, val)
    }
}

export class PropertyCategory extends FilterCategory  {
    filters: {[id: string]: PropertyFilter} = {}

    constructor(
        public prop_name: keyof SummaryData,
        public comp_fn: CompFn,
        private list: LogList,
    ) {
        super()
    }

    // dynamically create filter
    get_filter(id: string) {
        this.filters[id] = this.filters[id] || new PropertyFilter(id, this.prop_name, this.comp_fn, this.list.subject$)
        return this.filters[id]
    }

    get_add$(ids: string[]) {
        let adds = ids.map(id => this.get_filter(id).on_add$)
        return join_and(adds)
    }

    get_remove$(ids: string[]) {
        let rems = ids.map(id => this.get_filter(id).on_remove$)
        return join_and(rems)
    }
}