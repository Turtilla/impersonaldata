<script setup lang="ts">
import TextSelection from './components/TextSelection.vue';
import TextyView from './components/TextyView.vue';
import DetailView from './components/DetailView.vue';
import PageNotFound from './components/PageNotFound.vue';
import Footer from './components/Footer.vue';
import Header from './components/Header.vue';
import { ref } from 'vue';

const currentPage = ref(0);
const currentId = ref(0);

window.addEventListener('text-selected', (event: CustomEvent) => {
  currentId.value = event.detail;
});
</script>

<template>
  <Header></Header>
  <div v-if="currentPage==0" class="bg-white text-center w-full dark:bg-gray-800 p-4 rounded-lg">
    
    <TextSelection v-if="currentPage==0"/>
    
    <button @click="currentPage=1">Go to Texty View</button>
  </div>
  <div v-else-if="currentPage==1" class="bg-white text-center dark:bg-gray-800">
    <TextyView v-if="currentPage==1" :textid="currentId"/>
    <br/>
    <button @click="currentPage=0">Go to Text Selection</button>
    <button @click="currentPage=2">Go to Detail View</button>
  </div>
  <div v-else-if="currentPage==2" class="bg-white text-center dark:bg-gray-800">
    <DetailView v-if="currentPage==2" :textid="currentId"/>
    <br/>
    <button @click="currentPage=0">Go to Text Selection</button>
  </div>
  <div v-else class="bg-white text-center dark:bg-gray-800">
    <PageNotFound v-if="currentPage>2"/>
    <button @click="currentPage=0">Go to Text Selection</button>
  </div>
  <br/><br/>
  <Footer></Footer>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Alumni+Sans+Pinstripe:ital@0;1&family=Forum&family=Roboto+Serif:ital,opsz,wght@0,8..144,100..900;1,8..144,100..900&family=SUSE:wght@100..800&family=Saira:ital,wght@0,100..900;1,100..900&display=swap');

.font-header {
  font-family: 'SUSE', sans-serif;
}

body {
  font-family: 'Roboto', sans-serif;
}
</style>
