<template>

<div class="bg-white w-full dark:bg-gray-800 p-4 rounded-lg">
    <br/><br/><br/>
    <h2 class="text-2xl mb-4 font-header">Text Selection</h2>    
    <label for="text-select" class="block mb-2 text-lg font-semibold">Select a text:
    <select v-model="selectedText" @change="bubbleUp" class="bg-gray-100 border border-gray-300 rounded p-2 dark:text-gray-900 dark:bg-gray-300" style="max-width: 100%;">   
        <option v-for="text in textData" :key="text.id" :value="text.text">
            {{ text.id }}
        </option>

    </select>
</label>
</div>

<div>
    <label for="text-area" class="block mb-2 text-lg font-semibold dark:text-gray-300 dark:bg-gray-800">Selected Text:</label>
    <textarea v-model="selectedText" rows="20" cols="100" readonly class="bg-gray-100 border border-gray-300 rounded p-2 dark:text-gray-300 dark:bg-gray-800" style="max-width: 100%;">
        {{ selectedText }}
    </textarea>
</div>
</template>
<script setup lang="ts">
// load data from a json file
import { ref, onMounted } from 'vue';
interface TextWithId {
  id: string;
  text: string;
}

const textData = ref([] as TextWithId[]);
const selectedText = ref('');

onMounted(async () => {
  const response = await fetch('/frontend_data.json');
    if (!response.ok) {
        console.error('Failed to fetch data:', response.statusText);
        return;
    }
    const data = await response.json();
    textData.value = data["texts"];
});

function bubbleUp() {
    // emit an event with the selected id to parent
    const selectedId = textData.value.find((text) => text.text === selectedText.value)?.id;
    if (selectedId) {
        const event = new CustomEvent('text-selected', { detail: selectedId });
        window.dispatchEvent(event);
    }
}
</script>

<style scoped>
</style>