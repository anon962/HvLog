import { BSTree } from "typescript-collections"
import { LogList, LogSummary } from "./log_list"


// filter log ids by LogSummary attributes
class LogFilter {
    index: BSTree<number> = new BSTree()
    conds: object: {}

    constructor(public list: LogList) {
        // filter all existing logs

        // subscribe
        this.list.subject.subscribe(this.push)
    }

    push(log: LogSummary) {
        if(this.filter(log)) {
            this.index.add(log.start)
        }
    }

    filter(log: LogSummary) {

    }

    /* filter conds */ 

}

interface FilterConds {
    type: null|string|RegExp
    recency: number
}