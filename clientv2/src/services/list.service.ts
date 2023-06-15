import ENV from "@env"
import { from, Observable, ReplaySubject, Subject } from "rxjs"
import { tap, switchMap, map } from 'rxjs/operators'
import { Injectable } from "@angular/core"
import { HttpClient } from "@angular/common/http"
import { SummaryData, SummaryResponse } from "@/classes/logs/summary_data"


@Injectable({
    providedIn: 'root'
})
export class LogList {
    // inits
    summaries: { [id: number]: SummaryData } = {}
    last_fetch: number = 0
    subject$ = new ReplaySubject<SummaryData>()

    constructor(private http_client: HttpClient) {}

    // fetch and notify of new log summaries
    fetch(start: number|null = null): Observable<SummaryData> {
        // setup
        start = start || this.last_fetch
        this.last_fetch = Math.floor(Date.now() / 1000)
        let params = { start }

        // request
        return this._fetch(params).pipe( 
            // unravel
            switchMap(lst => {
                return from(lst)
            }),

            // cache
            tap(summ => {
                this.summaries[summ.id] = summ
            }),

            // emit
            tap(summ => this.subject$.next(summ))
        )
    }

    _fetch(params: {}) {
        let target = `${ENV.server}/test/logs`
        let resp = this.http_client.get<any>(target, { params }).pipe(
            // json to objects
            map(resp => resp.logs.map(
                (x: SummaryResponse) => {
                    return new SummaryData(x.start, x.round_end, x.round_max, x.battle_type)
                }
            ))
        )
        return resp as Observable<SummaryData[]>
    }
}

