<template>
    <div class="header bg-gray-100/75 dark:bg-gray-900/75">
        <div class="header-content">
            <h1 class="text-2xl font-header">Impersonal data</h1>
            <p class="text-sm">Your data, your way</p>            
        </div>
    </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.header {
    
    padding: 10px;
    text-align: center;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 1000;
    backdrop-filter: blur(5px);
}
</style>