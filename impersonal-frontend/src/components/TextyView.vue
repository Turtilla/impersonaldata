<template>
    <div class="items-center w-full">
        <br/><br/><br/>
      <h2 class="text-2xl mb-4 font-header">Texty view for text {{ textid }}</h2>
  
      <div class="flex flex-wrap flex-row gap-1">
        
        <div
          v-for="(svg, index) in svgs"
          :key="index"
          class="bg-white p-4 border border-gray-300 rounded shadow-md"
        >
          <span class="text-lg font-semibold mb-2">{{ svg['base'] }}</span>
          
        <img v-if="legend" :src="`/${svg['svg']}`" class="w-128"/>
      </div>
      </div>
      <!--
      <div>
        
         
        <table class="table-auto w-full border-separate border border-gray-300 border-spacing-2 rounded-lg">
          <thead>
            <tr>
                <th colspan="3">Statistics</th>
            </tr>
            <tr>
                <th></th>
              <th>BERT Classifier Label</th>
              <th>GV-PII-2.0 SweLLified Label</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in currentStats" :key="index">
              <th>{{ item["label"] }}</th>
              <td class="border border-gray-300">{{ item["bert_classifier_pct"] }}</td>
              <td class="border border-gray-300">{{ item["gv-pii-2.0_SweLLified_pct"] }}</td>
            </tr>
          </tbody>
        </table>

      </div>
      -->
    </div>
    <Legend v-if="legend" :categories="legend"></Legend>   
  </template>
  
  

<script setup lang="ts">
// declare props
import { defineProps, onBeforeMount } from 'vue';
import { ref } from 'vue';
import Legend from './Legend.vue';

const props = defineProps({
  textid: {
    type: Number,
    required: true
  }
});

interface Legend {
  [key: string]: string;
}

interface Svg {
  svg: string;
  base: string;
}

const svgs = ref([] as Svg[]);
const legend = ref({});
const currentStats = ref([] as any[]);

onBeforeMount(() => {
    fetch("/config.json")
        .then((response) => {
            if (!response.ok) {
                console.error('Failed to fetch data:', response.statusText);
                return;
            }
            return response.json();
        })
        .then((data) => {
            legend.value = data["categories"];
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
        })
        .then((data) => {
            const basefiles = data["base_files"];
            for (let i = 0; i < basefiles.length; i++) {
                const base = basefiles[i].split(".json")[0];
                const svg = base+"-"+props.textid+".svg";
                svgs.value.push({"svg": svg, "base": base});
            }
            const stats = data["stats_by_doc"];
            console.log(stats);
            currentStats.value = stats.filter((item: { document_id: number }) => item.document_id === props.textid);
            console.log(currentStats.value);
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
        });
});
</script>

<style scoped>
</style>