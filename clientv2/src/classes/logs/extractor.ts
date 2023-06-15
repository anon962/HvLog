import { sum_lst, zip_dicts } from "@/utils/misc_utils"
import { HttpClient } from "@angular/common/http"
import { iif, merge, Observable, of } from "rxjs"
import ENV from "@env"
import { catchError, tap } from "rxjs/operators"


// mostly a cache for server response
export abstract class BaseExtractor {
    cache: { [log_id: number]: any } = {}

    constructor(
        public id: string,
        private http: HttpClient,
    ) {}

    // retrieve and cache data
    get_logs(log_ids: number[]): Observable<any> {
        return merge(...log_ids.map(id => {
            console.log('id', id)
            // if not cached, fetch
            if(!this.cache[id]) {
                return this._get_log(id).pipe(
                    tap(resp => this.cache[id] = this.handle_response(resp[this.id]))
                )
            // elif cached, get from cache
            } else {
                return of(this.cache[id]).pipe(tap(_=>console.log('cache', id, this.cache[id])),)
            }
        }))
    }

    // retrieve data
    _get_log(log_id: number): Observable<any> {
        const target = `${ENV.server}/test/extract`
        const params = {log_id, extractors: JSON.stringify([this.id])}
        console.log('fetching', target, params)

        return this.http.get(target, {params}).pipe(
            catchError(err => of(console.error('fetch error', err))),
            tap(data => console.log(target, params, data))
        )
    }

    abstract handle_response(resp: any): any
}


export class AttributeExtractor extends BaseExtractor {
    cache: {[log_id: number]: LogAttributes} = {}

    handle_response(resp: Array<DataInterface>) {
        console.log('handling', resp)
        return new LogAttributes(resp)
    }
}

// holds extract data for a log
export class LogAttributes extends Array<DataInterface> {
    cache: any = null

    constructor(public data: Array<DataInterface>) {
        super(...data)
    }

    get totals() {
        this.cache = this.cache || this._totals
        return this.cache
    }

    get _totals(): { [attr: string]: any } {
        const totals: { [x:string]: any } = {}

        const zipped = zip_dicts(this)
        Object.entries(zipped).forEach( ([attr, lst]) => {
            if (attr === "meta") return
            totals[attr]= sum_lst(lst)
        })

        return totals
    }
}


/* interfaces */
interface DataInterface {
    meta: {
        round: number,
        turn: number,
        event: number,
    }

    [attr_name: string]: any
}


// facilitates extractor requests by creating extractors on-demand
export abstract class ExtractorGroup {
    extractors: { [name: string]: BaseExtractor } = {}

    extract(log_ids: number[], extractor: string) {
        let extr = this.get_extractor(extractor)
        return extr.get_logs(log_ids)
    }

    abstract get_extractor(name: string): BaseExtractor
}