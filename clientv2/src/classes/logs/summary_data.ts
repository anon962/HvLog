import { Subject } from "rxjs"


export class SummaryData implements SummaryResponse {
    id: number
    _cache: {[key: string]: any} = {}

    types = new Set()
    on_new_type$ = new Subject<string>()

    constructor(
        public start: number, // seconds
        public round_end: number,
        public round_max: number,
        public battle_type: string,
    ) {
        this.id = start
        this.types.add(battle_type)
    }


    /* derived props */
    get weekday() {
        let key = "weekday"
        this._cache[key] = this._cache[key] || new Date(this.start*1000).getUTCDay()
        return this._cache[key]
    }
    get month() {
        let key = "month"
        this._cache[key] = this._cache[key] || new Date(this.start*1000).getUTCMonth()
        return this._cache[key]
    }
}

export interface SummaryResponse {
    start: number // seconds
    round_end: number
    round_max: number
    battle_type: string
}