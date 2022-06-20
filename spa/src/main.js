import Vue from 'vue';

// import plugins
import { BootstrapVue } from 'bootstrap-vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import VueNeo4j from 'vue-neo4j'

// import components
import App from './App.vue';

// Style imports
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-vue/dist/bootstrap-vue.min.css';

// import icons
import { faBicycle, faBullseye, faChartSimple, faClock, faDatabase, faFontAwesome, faLink, faLocationPin, faMagnifyingGlassPlus, faMagnifyingGlassMinus, faMagnifyingGlass, faTrain, faUtensils } from '@fortawesome/free-solid-svg-icons';
import { faBootstrap, faGithub, faPython, faVuejs } from '@fortawesome/free-brands-svg-icons';
library.add(faBicycle, faBootstrap, faBullseye, faChartSimple, faClock, faDatabase, faFontAwesome, faGithub, faLink, faLocationPin, faMagnifyingGlassPlus, faMagnifyingGlassMinus, faMagnifyingGlass, faPython, faTrain, faUtensils, faVuejs);

// Vue use
Vue.use(BootstrapVue);
Vue.use(VueNeo4j);

// custom components
Vue.component('fa-icon', FontAwesomeIcon);

// Vue settings
Vue.config.productionTip = false;

// Vue mounting
new Vue({
	render: h => h(App),
}).$mount('#app');
