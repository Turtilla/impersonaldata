<template>
    <div>
        <br/><br/><br/>
        <h2 class="text-2xl mb-4 font-header">Detail view for text {{ textid }}</h2>
      <button
        class="my-4 px-4 py-2 bg-blue-500 rounded hover:bg-blue-600"
        @click="showOffsets = !showOffsets"
      >
        {{ showOffsets ? "Hide Offset Columns" : "Show Offset Columns" }}
      </button>
  
      <table class="table-auto w-full border-separate border border-gray-300 border-spacing-2 rounded-lg">
        <thead>
          <tr>
            <th v-if="showOffsets">Start</th>
            <th v-if="showOffsets">End</th>
            <th>Text</th>
            <th v-for="(classifier_label, index) in classifier_labels" :key="index">
              {{ classifier_label }} 
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in currentData" :key="index">
            <td v-if="showOffsets">{{ item["start"] }}</td>
            <td v-if="showOffsets">{{ item["end"] }}</td>
            <td>{{ item["text"] }}</td>
            <td class="border border-gray-300" :bgcolor="getColor(item[classifier_label])" v-for="(classifier_label, index) in classifier_labels" :key="index">{{ item[classifier_label] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  

<script setup lang="ts">
import { defineProps, onMounted, ref } from 'vue';
const currentData = ref([]);
const showOffsets = ref(false);
const colorMap = ref({} as { [key: string]: string });
const props = defineProps({
    textid: {
        type: Number,
        required: true
    }
});
const classifier_labels = ref([] as string[]);

onMounted(() => {
    fetch("/span_data.json")
        .then((response) => {
            if (!response.ok) {
                console.error('Failed to fetch data:', response.statusText);
                return;
            }
            return response.json();
        })
        .then((data) => {
            // filter data by "document_id", which is the same as textid
            const data2 = data["data"]
            const filteredData = data2.filter((item: { document_id: number }) => item.document_id === props.textid);
            currentData.value = filteredData;
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
        });

        fetch("/config.json")
        .then((response) => {
            if (!response.ok) {
                console.error('Failed to fetch data:', response.statusText);
                return;
            }
            return response.json();
        })
        .then((data) => {
            const categories = data["categories"];
            // create a color map for the labels
            categories.forEach((cat: { category: string; color: string }) => {
                colorMap.value[cat.category] = cat.color;
            });
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
        });
        fetch("/frontend_data.json")
        .then((response) => {
            if (!response.ok) {
                console.error('Failed to fetch data:', response.statusText);
                return;
            }
            return response.json();
        }).then((data) => {
          console.log("data", data);
            const basefiles = data["base_files"];
            console.log("base_files", basefiles);
            for (const basefile of basefiles) {
                const classifier_label = basefile.split(".jsonl")[0] + "_label";
                // add the classifier label to the classifier_labels array
                classifier_labels.value.push(classifier_label);
            }
            console.log("classifier_labels", classifier_labels.value);
        })
})

function getColor(label: string) {
    // get the color for the label from the color map
    return colorMap.value[label] || 'transparent';
}
</script>

<style scoped>
</style>