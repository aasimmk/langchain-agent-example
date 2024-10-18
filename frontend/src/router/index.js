import { createRouter, createWebHistory } from 'vue-router';
import Chat from '@/components/ChatView.vue';

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: Chat,
  },
  // add more routes here
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
