import { AgeFilter } from "@/classes/logs/filters/age"
import { Injectable } from "@angular/core"
import { LogList } from "../list.service"
import { FilterCategory } from "@/classes/logs/filters/manager"


@Injectable({
    providedIn: 'root'
})
export class AgeOf extends FilterCategory {
    filters: {[id:number]: AgeFilter} = {}

    constructor(private list: LogList) {
        super()
    }

    // dynamically create filter
    get_filter(id: number)  {
        this.filters[id] = this.filters[id] || new AgeFilter(id, this.list.subject$)
        return this.filters[id]
    }

    get_add$(id: number) { return this.get_filter(id).on_add$ }
    get_remove$(id: number) { return this.get_filter(id).on_remove$ }

    get_name(id: number) { return `age_${Math.trunc(id)}` }
}