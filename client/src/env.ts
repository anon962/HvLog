import defaults from "@/environments/defaults"
import dev from "@/environments/env.dev"
import prod from "@/environments/env.prod"


let ENV
const MODE= process.env.VUE_APP_MODE

if(MODE === "DEV") {
    ENV= {...defaults, ...dev} 
} else if(MODE === "PROD") {
    ENV= {...defaults, ...prod} 
}


export default { ...ENV }