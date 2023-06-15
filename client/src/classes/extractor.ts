import { request_extract } from "@/utils/request_utils"
import { LogList } from "./log_list"


// mostly a cache for server response
class BaseExtractor {
    cache: { [log_id: number]: any } = {}
    name: string = ""

    constructor(public id: string) { }

    async get_log(log_id: number): Promise<any> {
        if(!this.cache[log_id]) {
            const response = await request_extract(log_id, [this.id])
            this.cache[log_id] = this.handle_response(response[this.id])
        }
        
        return this.cache[log_id]
    }

    handle_response(resp: any): any {
        throw Error("not implemented")
    }
}

// collection of BaseExtractors that watch for changes to a LogList
class ExtractorGroup {
    log_list: LogList
    extractors: { [name: string]: BaseExtractor }
    cache: { [name: string]: any } = {} // list of logs checked for each extractor

    constructor(log_list: LogList) {
        this.log_list = log_list
        this.extractors = {}
    }

    extract(extractor: string, filters: any) {
        let extr = this.extractors[extractor]
        
    }

    _extract() {

    }
}


export { BaseExtractor, ExtractorGroup }