// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import settings from "./settings"
import '../static/css/style.css'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import axios from 'axios'
import store from './store'

Vue.config.productionTip = false
Vue.prototype.$settings = settings
Vue.prototype.$axios = axios

/* eslint-disable no-new */
Vue.use(ElementUI)

require('video.js/dist/video-js.css');
require('vue-video-player/src/custom-theme.css');
import VideoPlayer from 'vue-video-player'
Vue.use(VideoPlayer);

new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})
