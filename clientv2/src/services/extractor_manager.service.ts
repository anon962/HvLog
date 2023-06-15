import { AttributeExtractor, BaseExtractor, ExtractorGroup } from "@/classes/logs/extractor"
import { HttpClient } from "@angular/common/http"
import { Injectable } from "@angular/core"


@Injectable({
    providedIn: 'root'
})
export class AttributeManager extends ExtractorGroup {
    extractors: {[name: string]: AttributeExtractor} = {}

    constructor(private http: HttpClient) {
        super()
    }

    get_extractor(name: keyof typeof AttributeManager.extrs): AttributeExtractor {
        console.log('creating', name)
        return new AttributeExtractor(name, this.http)
    }
}

// DEFAULT_EXTRACTORS defined in server/classes/database/extractors
export namespace AttributeManager {
    export enum extrs {
        EXP  = "exp",
        PROF = "prof",
        MOB  = "monster",
        EQ   = "equips",
        CREDITS = "credits",
    }
}