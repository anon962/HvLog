import { SourceData } from "@/classes/logs/filters/filter";
import { Observable, ReplaySubject } from "rxjs";


// filter for emits that are sent by all observables
export function join_and(lst: Observable<SourceData>[], debug=false) {
    let subj = new ReplaySubject<SourceData>()
    let partials: {[data:string]: boolean[]} = {}
    
    lst.forEach((obs,i) => {
        obs.subscribe(data => {
            // get row
            let hash = data.id
            partials[hash] = partials[hash] || new Array()

            // add to row
            partials[hash].push(true)
            if(debug) console.log(`pushed (${i+1}/${lst.length}) true`, partials[hash].length, data)

            // emit if all obs have emit true (tracked by number of pushes)
            if(partials[hash].length == lst.length) {
                if(debug) console.log(`join (${lst.length}) emitting`, data)
                subj.next(data)
                delete partials[hash]
            }
        })
    })

    return subj
}