import 'reflect-metadata'
// import 'es6-shim'

import { createApp } from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueAxios from 'vue-axios'


// config
const app= createApp(App)
app.use(VueAxios, axios)

// start
app.mount('#app')
