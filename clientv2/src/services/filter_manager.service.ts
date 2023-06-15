import { BaseFilterManager } from "@/classes/logs/filters/manager";
import { PropertyCategory } from "@/classes/logs/filters/property";
import { Injectable } from "@angular/core";
import { AgeOf } from "./filters/age.service";
import { LogList } from "./list.service";


@Injectable({
    providedIn: 'root'
})
export class FilterManager extends BaseFilterManager {
    constructor(list: LogList) {
        super()
        
        this.categories[FilterManager.cats.AGE] = new AgeOf(list)

        this.categories[FilterManager.cats.MONTH] = new PropertyCategory(
            'month',
            (id,month) => id === month,
            list
        )

        this.categories[FilterManager.cats.DAY] = new PropertyCategory(
            'weekday',
            (id,day) => id === day,
            list
        )
        
        this.categories[FilterManager.cats.TYPE] = new PropertyCategory(
            'battle_type',
            (id,type) => id === type,
            list
        )
    }
}

export namespace FilterManager {
    export enum cats {
        AGE,
        MONTH,
        DAY,
        TYPE
    }
}