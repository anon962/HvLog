import ENV from "@/env"
import axios from 'axios'
import { AttributeExtractor } from "./attribute_extractor"
import 'reflect-metadata'
import { Expose, plainToClass } from 'class-transformer'
import { Subject } from "rxjs"


class LogList {
    summaries: { [id: number]: LogSummary } = {}
    extractors: { [name: string]: AttributeExtractor } = {}
    last_fetch: number = 0

    subject: Subject<LogSummary> = new Subject<LogSummary>()

    async fetch(start: number|null = null): Promise<void> {
        start = start || this.last_fetch

        let target = `${ENV.server}/test/logs`
        let params = { start }
        let resp = (await axios.get(target, {params})).data

        resp.forEach( (r:object) => {
            let summ = plainToClass(LogSummary, r)
            this.summaries[summ.start] = summ
            this.subject.next(summ)
        })
        this.last_fetch = Math.floor(Date.now() / 1000)
    }
}

class LogSummary {
    start: number;
    round_end: number;
    round_max: number;
    battle_type: string;
}


export { LogList, LogSummary }