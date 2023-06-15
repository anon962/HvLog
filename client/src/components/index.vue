<template>
    <overview_pane/>
     <p>{{log_list}}</p>
</template>


<script lang="ts">
    import { defineComponent } from "vue"
    import overview_pane from "@/components/overview/pane.vue"
    import { LogList, ExtractorGroup } from "@/classes/module"

    export default defineComponent({
        data() { return {
            log_list: 1 // new LogList(),
            extrs: [],
        }},

        created() {
            // this.log_list.fetch().then(_ => {
                // this.extrs = new ExtractorGroup(this.log_list)
            // })
        },


        components: {
            overview_pane
        },
    })
</script>
