import { Observable, ReplaySubject, Subject, timer } from "rxjs";


// subset of numeric ids from whatever source
export abstract class BaseFilter {
    index = new Set<number>()
    on_add$ = new ReplaySubject<SourceData>() // notify of new data
    on_remove$ = new ReplaySubject<SourceData>()

    // listen for new source values (which must contain at least an id property)
    constructor(private target: Observable<SourceData>) {
        this.target.subscribe(this.process.bind(this))
    }
    
    // process source emissions
    process(data: SourceData) {
        let info = this.get_info(data)
        if(this.filter(data, info)) {
            this.index.add(data.id)
            this.on_add$.next(data)
            this.set_expiration(data)
        }
    }
    
    // override this
    // generate additional info about data before filtering
    // should NOT modify data
    get_info(data: SourceData): any {
        return null
    }

    // override this
    // check if value passes filter
    abstract filter(data: SourceData, info: any): boolean

    // remove data after some delay
    set_expiration(data: SourceData) {
        let expiry = this.get_expiration(data)
        if(expiry) {
            timer(expiry).subscribe(_ => {
                this.index.delete(data.id)
                this.on_remove$.next(data)
            })
        }
    }

    // override this
    // returns delay (ms) before the data is to be removed
    get_expiration(data: SourceData): number|void {}
}

export interface SourceData {
    id: number
    [other:string]: any
}