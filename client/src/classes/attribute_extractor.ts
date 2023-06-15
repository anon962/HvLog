import { sum_lst, zip_dicts } from "@/utils/misc_utils"
import { BaseExtractor } from "./extractor"


class AttributeExtractor extends BaseExtractor {
    cache: { [log_id: number]: LogAttributes } = {}

    handle_response(resp: Array<DataInterface>) {
        return new LogAttributes(resp)
    }
}

// holds extract data for a log
class LogAttributes extends Array<DataInterface> {
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

export { AttributeExtractor }