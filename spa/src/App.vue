<template>
	<div id="app" :style="returnHeightVariables">
		<ItemHeader ref="appHeader" />
		<ItemBody class="app-container" />
		<ItemFooter ref="appFooter" />
	</div>
</template>

<script>
import ItemBody from "./components/itemBody.vue";
import ItemFooter from "./components/itemFooter.vue";
import ItemHeader from "./components/itemHeader.vue";

export default {
	name: "App",
	data: function () {
		return {
			contentTitle: this.$root.contentTitle,
			computedHeightHeader: null,
			computedHeightFooter: null,
		};
	},
	methods: {
		calculateHeightFooter() {
			this.computedHeightFooter = this.$refs.appFooter.$el.clientHeight;
		},
		calculateHeightHeader() {
			this.computedHeightHeader = this.$refs.appHeader.$el.clientHeight;
		},
	},
	computed: {
		returnHeightVariables() {
			return {
				"--height-footer": `${this.computedHeightFooter}px`,
				"--height-header": `${this.computedHeightHeader}px`,
			};
		},
	},
	mounted: function () {
		this.calculateHeightHeader();
		this.calculateHeightFooter();
	},
	components: {
		ItemBody,
		ItemFooter,
		ItemHeader,
	},
};
</script>

<style lang="scss">
#app {
	font-family: Avenir, Helvetica, Arial, sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	text-align: center;
	color: #2c3e50;
}

.app-container {
	min-height: calc(100vh - var(--height-header) - var(--height-footer));
}
</style>