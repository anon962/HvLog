import ENV from "@/env"
import axios from 'axios'

// returned object keys are extractor names
async function request_extract(log_id: number, extractors: Array<string>): Promise<{ [extractor: string]: any }> {
    const target= `${ENV.server}/test/extract`
    const params= {log_id, extractors: JSON.stringify(extractors) }

    console.log(target, params)
    const ret= (await axios.get(target, {params})).data
    console.log(target, params, ret)
    return ret
}


// create a summary of time-related stats for response (eg total rounds, total logs, etc)
// function count_response(response) {
//     const ret= {
//         logs: 0,
//         rounds: 0,
//     }

//     const entries= Object.entries(response)
//     ret.logs= entries.length

//     entries.forEach( ([start,log_info]) => {
//         ret.rounds+= log_info.log.round_end
//     })

//     return ret
// }



export {
    request_extract
}