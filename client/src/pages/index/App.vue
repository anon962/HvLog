<template>
    <index/>
</template>

<script>
import index from '@/components/index.vue'

export default {
    components: {
        index,
    },

    created() {
        document.querySelector("#loading").remove()
    }
}
</script>

<style>
#app {
    text-align: center;
    font-family: Avenir, Helvetica, Arial, sans-serif;
    color: #2c3e50;
    margin-top: 60px;
}
</style>
