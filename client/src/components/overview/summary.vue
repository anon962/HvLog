<template>
    <div id="root">
        <div id="summary">
            <div class="summary_card">
                
            </div>
        </div>

        <div id="log">
            <h3>list</h3>
            
        </div>
    </div>

    <pre v-if="debug"
    style="text-align:left;">
        <hr/>
        DEBUG:<br/>
    </pre>
</template>



<script lang="ts">
    import { defineComponent } from 'vue'
    import { LogList } from '@/classes/log_list'
    import { AttributeExtractor } from '@/classes/attribute_extractor'
    import ENV from "@/env"

    export default defineComponent({
        name: 'summary_tab',
        // inject: ['extrs']
        
        data() { return {
            debug: ENV.debug,
        }},

        created() {
            // console.log(this)
            // this.extrs.extractors['exp'] = new AttributeExtractor('exp')
        },

        methods: {
            
        },
    })
</script>



<style scoped>
    #root {
        display: grid;
        grid-template-columns: 2fr 1fr;
    }
</style>
