<template>
	<div class="footer">
		<b-container fluid>
			<div class="footer-header">
				<h3>Additional information</h3>
			</div>
			<b-row>
				<b-col cols="12" md="1" />
				<b-col cols="12" md="5">
					<b-card class="footer-card" no-body>
						<template #header>
							<h5>This project was created by:</h5>
						</template>
						<b-list-group class="footer-list-item" flush>
							<b-list-group-item href="https://github.com/Ehrete" target="_blank">
								<fa-icon icon="fa-brands fa-github" />&nbsp;Engelbert Ehret (ehrete)
							</b-list-group-item>
							<b-list-group-item href="https://github.com/SacrumDeus" target="_blank">
								<fa-icon icon="fa-brands fa-github" />&nbsp;Adrian Weiss (SacrumDeus)
							</b-list-group-item>
						</b-list-group>
					</b-card>
					<b-card class="footer-card" no-body>
						<template #header>
							<h5>Our data sources are:</h5>
						</template>
						<b-list-group class="footer-list-item" flush>
							<b-list-group-item href="https://developer.deutschebahn.com/" target="_blank">
								<fa-icon icon="fa-train" />&nbsp;Deutsche Bahn
							</b-list-group-item>
							<b-list-group-item href="https://www.destatis.de/" target="_blank">
								<fa-icon icon="fa-chart-simple" />&nbsp;Statistisches Bundesamt - DESTATIS
							</b-list-group-item>
							<b-list-group-item href="https://www.regionalstatistik.de/" target="_blank">
								<fa-icon icon="fa-chart-simple" />&nbsp;Statistische Ämter der Länder -
								Regionalstatistik
							</b-list-group-item>
						</b-list-group>
					</b-card>
				</b-col>
				<b-col cols="12" md="5">
					<b-card class="footer-card" no-body>
						<template #header>
							<h5>This demo application was created by using the following packages:</h5>
						</template>
						<b-list-group class="footer-list-item" flush>
							<b-list-group-item href="https://fontawesome.com/" target="_blank">
								<fa-icon icon="fa-font-awesome" />&nbsp;Fontawesome
							</b-list-group-item>
							<b-list-group-item href="https://d3js.org/" target="_blank">
								<fa-icon icon="fa-brands fa-github" />&nbsp;D3.js
							</b-list-group-item>
							<b-list-group-item href="https://github.com/adam-cowley/vue-neo4j" target="_blank">
								<fa-icon icon="fa-brands fa-github" />&nbsp;vue-neo4j
							</b-list-group-item>
							<b-list-group-item href="https://bootstrap-vue.org/" target="_blank">
								<fa-icon icon="fa-brands fa-bootstrap" />&nbsp;Bootstrap / Bootstrap-Vue
							</b-list-group-item>
							<b-list-group-item href="https://lodash.com/" target="_blank">
								<fa-icon icon="fa-link" />&nbsp;Lodash
							</b-list-group-item>
							<b-list-group-item href="https://vuejs.org/" target="_blank">
								<fa-icon icon="fa-brands fa-vuejs" />&nbsp;Vue.js
							</b-list-group-item>
						</b-list-group>
					</b-card>
					<b-card class="footer-card" no-body>
						<template #header>
							<h5>Additional technologies used:</h5>
						</template>
						<b-list-group class="footer-list-item" flush>
							<b-list-group-item href="https://neo4j.com/" target="_blank">
								<fa-icon icon="fa-database" />&nbsp;Neo4j
							</b-list-group-item>
							<b-list-group-item href="https://www.python.org/" target="_blank">
								<fa-icon icon="fa-brands fa-python" />&nbsp;Python
							</b-list-group-item>
						</b-list-group>
					</b-card>
				</b-col>
				<b-col cols="12" md="1" />
			</b-row>
		</b-container>
	</div>
</template>

<script>
export default {};
</script>

<style lang="scss">
@import "../variables.scss";

.footer {
	background-color: $color-grey;
	color: $color-red;
}

.footer-header {
	padding-top: 20px;
	padding-bottom: 20px;
}

.footer-card {
	margin-bottom: 25px;
	border-color: $color-red !important;
	border-width: 2px !important;

	> .card-header {
		background-color: $color-grey;
		border-color: $color-red;
	}

	> .card-body {
		background-color: $color-grey;
	}
}

.footer-list-item {
	> .list-group-item {
		background-color: $color-grey;
		color: $color-red;
		border-color: $color-red;
	}

	> .list-group-item:hover {
		background-color: $color-red;
		color: $color-grey;
	}
}
</style>