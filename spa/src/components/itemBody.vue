<template>
	<div class="body">
		<h1 class="body-title">Neo4j - Application example</h1>
		<b-row>
			<b-col md="3" cols="12" style="padding-top: 10px; padding-bottom: 10px">
				<p>
					Select an origin and a destination and click "<i>Find my route</i>" to find the the shortest path.
				</p>
				<b-form @submit.prevent="getRoute">
					<b-form-group id="input-origin-group" label="Origin" label-for="input-origin">
						<b-form-select
							v-model="route.origin"
							:options="route.originSelection"
							required
							@change="updateDestination"
						/>
					</b-form-group>
					<b-form-group id="input-destination-group" label="Destination" label-for="input-destination">
						<b-form-select
							v-model="route.destination"
							:options="route.destinationSelection"
							required
							@change="updateOrigin()"
						/>
					</b-form-group>
					<b-button type="submit" class="body-button" block>Find my route</b-button>
				</b-form>
				<b-alert variant="info" show class="body-info">
					Please note, that the programm will not take account of transfer time. Since transfer times need to
					take account of multiple constraints (e.g. departure time, arrival time, walking speed, ...) the
					resulting algorithm will be pretty complicated. This requirement would result in creating custom
					algorithms, either in Neo4J or in the application.
				</b-alert>
			</b-col>
			<b-col md="9" cols="12" style="padding-top: 10px; padding-bottom: 10px">
				<b-row>
					<b-col md="4" cols="12">
						<b-button class="body-button" block id="zoom-in">
							<fa-icon icon="fa-magnifying-glass-plus" />&nbsp;Zoom in
						</b-button>
					</b-col>
					<b-col md="4" cols="12">
						<b-button class="body-button" block id="zoom-out">
							<fa-icon icon="fa-magnifying-glass-minus" />&nbsp;Zoom out
						</b-button>
					</b-col>
					<b-col md="4" cols="12">
						<b-button class="body-button" block id="zoom-reset">
							<fa-icon icon="fa-magnifying-glass" />&nbsp;Reset zoom
						</b-button>
					</b-col>
				</b-row>
				<b-card class="body-chart">
					<div id="chart" />
				</b-card>
				<div class="body-route-details" v-if="route.segments.length > 0">
					<h3>Route details</h3>
					<b-card v-for="s of route.segments" :key="s" class="body-route-details-item">
						<b-card-title>
							<div class="start">
								<p>{{ getRouteDetail(s).start().name }}</p>
								<fa-icon icon="fa-location-pin" class="color-grey" />
							</div>
							<div class="end">
								<p>{{ getRouteDetail(s).end().name }}</p>
								<fa-icon icon="fa-bullseye" class="color-grey" />
							</div>
						</b-card-title>
						<div class="line" />
						<div class="train">
							<p><fa-icon icon="fa-train" class="color-grey" />&nbsp;{{ getRouteDetail(s).train() }}</p>
							<p>
								<fa-icon icon="fa-clock" class="color-grey" />&nbsp;{{
									getRouteDetail(s).duration()
								}}
								Minutes
							</p>
						</div>
						<div class="start">
							<p>Departure<br />{{ getRouteDetail(s).departure() }}</p>
						</div>
						<div class="end">
							<p>Arrival<br />{{ getRouteDetail(s).arrival() }}</p>
						</div>
						<div></div>
						<div class="features">
							<b-badge pill variant="success" v-if="getRouteDetail(s).property().bicycle">
								<fa-icon icon="fa-bicycle" />&nbsp;Bicycle
							</b-badge>
							<b-badge pill variant="success" v-if="getRouteDetail(s).property().bistro">
								<fa-icon icon="fa-utensils" />&nbsp;Bord bistro
							</b-badge>
							<b-badge pill variant="success" v-if="getRouteDetail(s).property().restautant">
								<fa-icon icon="fa-utensils" />&nbsp;Bord restaurant
							</b-badge>
						</div>
					</b-card>
				</div>
			</b-col>
		</b-row>
	</div>
</template>

<script>
import * as d3 from "d3";
import _ from "lodash";

export default {
	data: () => {
		return {
			neo4j: {
				protocol: "bolt",
				host: "localhost",
				port: "7687",
				username: "neo4j",
				password: "admin",
			},
			graph: {
				stations: [],
				trains: [],
				county: [],
				size: {
					width: 250,
					height: 300,
				},
				svg: null,
				g: null,
				projGeoAlbers: null,
				zoom: null,
				tooltip: null,
			},
			route: {
				origin: null,
				originSelection: [],
				destination: null,
				destinationSelection: [],
				start: null,
				segments: [],
				end: null,
			},
		};
	},
	methods: {
		getConnection() {
			return this.$neo4j.connect(
				this.neo4j.protocol,
				this.neo4j.host,
				this.neo4j.port,
				this.neo4j.username,
				this.neo4j.password
			);
		},
		getDriver() {
			return this.$neo4j.getDriver();
		},
		setDatabase() {
			this.$neo4j.setDatabase("deutschebahn");
		},
		getQuery(query) {
			// get session
			let session = this.$neo4j.getSession();

			// run query
			return session.run(query);
		},
		setSvg() {
			// set zoom element
			this.graph.zoom = d3.zoom().on("zoom", this.zoomed);

			// svg element
			this.graph.svg = d3
				.select("#chart")
				.append("svg")
				.attr("preserveAspectRatio", "xMinYMin meet")
				.attr("viewBox", `0 0 ${this.graph.size.width + 40} ${this.graph.size.height + 40}`)
				.call(this.graph.zoom);

			// append g element
			this.graph.g = this.graph.svg.append("g");

			// register zoom buttons
			d3.select("#zoom-in").on("click", () =>
				this.graph.zoom.scaleBy(this.graph.svg.transition().duration(500), 1.5)
			);
			d3.select("#zoom-out").on("click", () => {
				this.graph.zoom.scaleBy(this.graph.svg.transition().duration(500), 0.8);
			});
			d3.select("#zoom-reset").on("click", () => {
				this.graph.svg.transition().duration(750).call(this.graph.zoom.transform, d3.zoomIdentity);
			});

			// set tooltip
			this.graph.tooltip = d3.select("#chart").append("div").style("opacity", 0).classed("body-tooltip", true);
		},
		zoomed(event) {
			this.graph.g.attr("transform", event.transform);
		},
		async setGermanyMap() {
			// get data
			let germanyJson = require("../assets/VG250_KRS.geo.json");
			let counties = await this.getQuery(`MATCH (county:County) RETURN county`);

			// map data into new structures
			for (let county of counties.records) {
				let data = {};
				data.identity = this.rangeToInt(county._fields[0].identity);
				data.countyId = county._fields[0].properties.countyId;
				data.properties = county._fields[0].properties;

				// convert some properties from Object to Integer
				data.properties.gdp = this.rangeToInt(data.properties.gdp);
				data.properties.gdpPerCapita = this.rangeToInt(data.properties.gdpPerCapita);
				data.properties.population = this.rangeToInt(data.properties.population);

				// append to array
				this.graph.county.push(data);
			}

			// get geoBounds
			let [bottomLeft, topRight] = d3.geoBounds(germanyJson);
			let lambda = -(topRight[0] + bottomLeft[0]) / 2;
			let center = [(topRight[0] + bottomLeft[0]) / 2 + lambda, (topRight[1] + bottomLeft[1]) / 2];
			let scale = Math.min(
				this.graph.size.width / (topRight[0] + bottomLeft[0]),
				this.graph.size.height / (topRight[1] - bottomLeft[1])
			);

			// create projection object
			this.graph.projGeoAlbers = d3
				.geoAlbers()
				.parallels([bottomLeft[1], topRight[1]])
				.translate([(this.graph.size.width + 40) / 2, (this.graph.size.height + 40) / 2])
				.rotate([lambda, 0, 0])
				.center(center)
				.scale(scale * 200);

			// create map of german
			this.graph.g
				.selectAll("path")
				.data(germanyJson.features)
				.join("path")
				.attr("d", d3.geoPath().projection(this.graph.projGeoAlbers))
				.classed("body-graph-area", true)
				.on("mouseover", (d) => {
					// get element data
					let data = d.srcElement.__data__;

					// set tooltip - position and presence
					this.graph.tooltip.transition().duration(250).style("opacity", 1);
					this.graph.tooltip.style("left", `${d.layerX}px`);
					this.graph.tooltip.style("top", `${d.layerY}px`);

					// get county details
					let cDetails = this.getCountyDetail(data.properties.ARS);

					// set tooltip information
					let tInfo = this.toHtml();
					tInfo.add(cDetails.name(), "h1", "header");
					tInfo.div(undefined, "text");
					tInfo.add(`ARS key: ${cDetails._countyId()}`, "p");
					tInfo.add(`Area size: ${this.numberToExt(cDetails.areaSize())}km²`, "p");
					tInfo.add(`GDP: ${this.numberToExt(Math.round(cDetails.gdp() / 1000))} Mio. EUR`, "p");
					tInfo.add(`GDP per capita: ${this.numberToExt(cDetails.gdpPerCapita())} EUR`, "p");
					tInfo.add(`Population: ${this.numberToExt(cDetails.population())}`, "p");
					tInfo.add(`Unemployment rate: ${this.numberToExt(cDetails.unemploymentRate())} %`, "p");
					tInfo.div(true);
					this.graph.tooltip.html(tInfo.get());
				})
				.on("mousemove", (d) => {
					this.graph.tooltip.style("left", `${d.layerX}px`);
					this.graph.tooltip.style("top", `${d.layerY}px`);
				})
				.on("mouseout", () => {
					this.graph.tooltip.transition().duration(250).style("opacity", 0);
				});
		},
		async setStations() {
			// get data
			let stations = await this.getQuery(`MATCH (stations:Station) RETURN stations`);

			// we need to process the data - stations
			for (let station of stations.records) {
				// map data into new structure
				let data = {};
				data.id = this.rangeToInt(station._fields[0].identity);
				data.properties = station._fields[0].properties;

				// convert properties.IBNR from Object to Integer
				data.properties.IBNR = this.rangeToInt(data.properties.IBNR);

				// append to array + selection options
				this.graph.stations.push(data);
				this.route.originSelection.push({ value: data.id, text: data.properties.name, disabled: false });
				this.route.destinationSelection.push({ value: data.id, text: data.properties.name, disabled: false });
			}

			// set stations as nodes
			this.graph.g
				.selectAll("circle")
				.data(this.graph.stations)
				.join("circle")
				.classed("body-graph-station", true)
				.attr("id", (d) => `station-${d.id}`)
				.attr("r", 2)
				.attr("transform", (d) => {
					return `translate(${this.graph.projGeoAlbers([d.properties.longitude, d.properties.latitude])})`;
				})
				.on("mouseover", (d) => {
					// get element data
					let data = d.srcElement.__data__;

					// set tooltip - position and presence
					this.graph.tooltip.transition().duration(250).style("opacity", 1);
					this.graph.tooltip.style("left", `${d.layerX}px`);
					this.graph.tooltip.style("top", `${d.layerY}px`);

					// set tooltip information
					let tInfo = this.toHtml();
					tInfo.add(_.find(this.graph.stations, { id: data.id }).properties.name, "h1", "header");
					this.graph.tooltip.html(tInfo.get());
				})
				.on("mousemove", (d) => {
					this.graph.tooltip.style("left", `${d.layerX}px`);
					this.graph.tooltip.style("top", `${d.layerY}px`);
				})
				.on("mouseout", () => {
					this.graph.tooltip.transition().duration(250).style("opacity", 0);
				});

			// order train stations by name (only dropdown lists)
			this.route.originSelection = _.orderBy(this.route.originSelection, "text", "asc");
			this.route.destinationSelection = _.orderBy(this.route.destinationSelection, "text", "asc");

			// add empty select options
			this.route.originSelection.unshift({ value: null, text: "Select an origin", disabled: false });
			this.route.destinationSelection.unshift({ value: null, text: "Select a destination", disabled: false });
		},
		async setTrains() {
			// get data -> all stations (nodes) and all trains (relations), germanyMap
			let trains = await this.getQuery(`MATCH ()-[trains:TRAIN]->() RETURN trains`);

			// we need to process the data - trains
			for (let train of trains.records) {
				// map data into new structure
				let newStructure = {};
				newStructure.source = this.rangeToInt(train._fields[0].start);
				newStructure.target = this.rangeToInt(train._fields[0].end);
				newStructure.identity = this.rangeToInt(train._fields[0].identity);
				newStructure.properties = train._fields[0].properties;

				// convert some properties from Object to Integer
				newStructure.properties.duration = this.rangeToInt(newStructure.properties.duration);
				newStructure.properties.lag = this.rangeToInt(newStructure.properties.lag);

				// append to array
				this.graph.trains.push(newStructure);
			}

			// append lines
			this.graph.g
				.selectAll("line")
				.data(this.graph.trains)
				.join("line")
				.classed("body-graph-train", true)
				.attr("id", (d) => `line-${d.identity}`)
				.attr("x1", (d) => this.graph.projGeoAlbers(this.getCoordinatesForId(d.source))[0])
				.attr("y1", (d) => this.graph.projGeoAlbers(this.getCoordinatesForId(d.source))[1])
				.attr("x2", (d) => this.graph.projGeoAlbers(this.getCoordinatesForId(d.target))[0])
				.attr("y2", (d) => this.graph.projGeoAlbers(this.getCoordinatesForId(d.target))[1])
				.on("mouseover", (d) => {
					// get element data
					let data = d.srcElement.__data__;

					// set tooltip - position and presence
					this.graph.tooltip.transition().duration(250).style("opacity", 1);
					this.graph.tooltip.style("left", `${d.layerX}px`);
					this.graph.tooltip.style("top", `${d.layerY}px`);

					// set tooltip information
					let tInfo = this.toHtml();
					tInfo.add(this.getRouteDetail(data.identity).train(), "h1", "header");
					tInfo.div(undefined, "text");
					tInfo.add(`Start: ${this.getRouteDetail(data.identity).start().name}`, "p");
					tInfo.add(`End: ${this.getRouteDetail(data.identity).end().name}`, "p");
					tInfo.div(true);
					this.graph.tooltip.html(tInfo.get());
				})
				.on("mousemove", (d) => {
					this.graph.tooltip.style("left", `${d.layerX}px`);
					this.graph.tooltip.style("top", `${d.layerY}px`);
				})
				.on("mouseout", () => {
					this.graph.tooltip.transition().duration(250).style("opacity", 0);
				});
		},
		rangeToInt: (range) => range.low,
		getCoordinatesForId(id) {
			return [
				_.find(this.graph.stations, { id: id }).properties.longitude,
				_.find(this.graph.stations, { id: id }).properties.latitude,
			];
		},
		updateOrigin() {
			// reset all disabled data
			if (_.find(this.route.originSelection, { disabled: true })) {
				_.find(this.route.originSelection, { disabled: true }).disabled = false;
			}

			// update selected value on origin selection
			if (this.route.destination !== null) {
				_.find(this.route.originSelection, { value: this.route.destination }).disabled = true;
			}
		},
		updateDestination() {
			// reset all disabled data
			if (_.find(this.route.destinationSelection, { disabled: true })) {
				_.find(this.route.destinationSelection, { disabled: true }).disabled = false;
			}

			// update selected value on destination selection
			if (this.route.origin !== null) {
				_.find(this.route.destinationSelection, { value: this.route.origin }).disabled = true;
			}
		},
		async getRoute() {
			// reset some variables
			this.route.start = null;
			this.route.segments = [];
			this.route.end = null;

			// reset route in SVG
			d3.selectAll(".train-active").classed("train-active", false);
			d3.selectAll(".station-active").classed("station-active", false);

			// get IBNR number
			let ibnrOrigin = _.find(this.graph.stations, { id: this.route.origin }).properties.IBNR;
			let ibnrDestination = _.find(this.graph.stations, { id: this.route.destination }).properties.IBNR;

			// create query
			let query = `MATCH (origin:Station {IBNR:${ibnrOrigin}}), (destination:Station {IBNR:${ibnrDestination}}) 
						 CALL apoc.algo.dijkstra(origin, destination, 'TRAIN>', 'duration')
						 YIELD path, weight
						 RETURN path, weight`;

			// get query results
			let route = await this.getQuery(query);

			// get start
			this.route.start = this.rangeToInt(route.records[0]._fields[0].start.identity);
			this.route.end = this.rangeToInt(route.records[0]._fields[0].end.identity);

			// transform route seagments to specific format
			for (let segment of route.records[0]._fields[0].segments) {
				this.route.segments.push(this.rangeToInt(segment.relationship.identity));
			}

			// update svg (route for route)
			for (let segment of this.route.segments) {
				// update train segment by id
				d3.select(`#line-${segment}`).classed("train-active", true).raise();

				// get route details
				let routeDetails = this.getRouteDetail(segment);

				// update train stations (start, end)
				d3.select(`#station-${routeDetails.start().id}`).classed("station-active", true).raise();
				d3.select(`#station-${routeDetails.end().id}`).classed("station-active", true).raise();
			}
		},
		getRouteDetail(id) {
			// get route
			let train = _.find(this.graph.trains, { identity: id });

			// return some functions
			return {
				start: () => {
					return {
						id: train.source,
						name: _.find(this.graph.stations, { id: train.source }).properties.name,
					};
				},
				end: () => {
					return {
						id: train.target,
						name: _.find(this.graph.stations, { id: train.target }).properties.name,
					};
				},
				train: () => train.properties.trainNumber,
				trainType: () => train.properties.trainType,
				departure: () => train.properties.depTime,
				arrival: () => train.properties.arrTime,
				duration: () => train.properties.duration,
				property: () => {
					return {
						bicycle: train.properties.bicycle,
						bistro: train.properties.bordbistro,
						restaurant: train.properties.bordrestaurant,
					};
				},
			};
		},
		getCountyDetail(id) {
			// get county
			let county = _.find(this.graph.county, { countyId: id });

			// return some functions
			return {
				_identity: () => county.identity,
				_countyId: () => county.countyId,
				areaSize: () => county.properties.areaSize,
				gdp: () => county.properties.gdp,
				gdpPerCapita: () => county.properties.gdpPerCapita,
				name: () => county.properties.name,
				population: () => county.properties.population,
				unemploymentRate: () => county.properties.unemploymentRate,
			};
		},
		toHtml() {
			let data = [];
			let html;

			// return some functions
			return {
				add: (content, elem, cls) => {
					data.push({ elem: elem, class: cls, content: content });
				},
				div: (closing = false, cls) => {
					data.push({ elem: `div`, class: cls, close: closing });
				},
				get: () => {
					// process every item in data
					for (let elem of data) {
						let elemHtml;
						//generate html for elem
						if (elem.elem === `div`) {
							elemHtml = elem.close ? `</div>` : `<div ${elem.class ? `class="${elem.class}"` : ""}>`;
						} else {
							if (elem.class) {
								elemHtml = `<${elem.elem} class="${elem.class}">${elem.content}</${elem.elem}>`;
							} else {
								elemHtml = `<${elem.elem}>${elem.content}</${elem.elem}>`;
							}
						}
						// add to previuos html
						html = html ? html + elemHtml : elemHtml;
					}

					// return html
					return html;
				},
			};
		},
		numberToExt: (number) => new Intl.NumberFormat("de").format(number),
	},
	mounted() {
		this.getConnection();
		this.getDriver();
		this.setDatabase();
		this.setSvg();
		this.setGermanyMap();
		this.setTrains();
		this.setStations();
	},
};
</script>

<style lang="scss">
@import "../variables.scss";
.body {
	padding: 20px;
}

.body-graph-area {
	fill: $color-lightGrey;

	&:hover {
		fill: $color-red;
	}
}

.body-graph-train {
	stroke: $color-grey;
	stroke-width: 1px;
}

.body-graph-station {
	fill: $color-grey;
	stroke: $color-grey;

	&:hover {
		stroke: $color-red;
	}
}

.train-active {
	stroke: $color-red;
	stroke-width: 2px;
}

.station-active {
	fill: $color-red;
}

.body-button {
	&.btn-secondary {
		color: $color-white;
		background-color: $color-red;
		border-color: $color-red;
		border-width: 2px;
	}

	&.btn-secondary:hover {
		color: $color-red;
		background-color: $color-white;
		border-color: $color-red;
	}
}

.body-route-details-item {
	margin-top: 10px;
	margin-bottom: 5px;

	.start {
		width: 50%;
		float: left;
	}

	.end {
		width: 50%;
		float: right;
	}

	.line {
		display: inline-block;
		width: 50%;
		margin-left: 25%;
		margin-right: 25%;
		border: 1px solid $color-lightGrey;
	}

	.color-grey {
		color: $color-lightGrey;
	}

	.train > p {
		display: inline-block;
		padding: 5px;
	}
}

.body-chart {
	margin-top: 10px;
	margin-bottom: 10px;
	max-height: 700px;

	flex-direction: row !important;
	justify-content: center;

	> .card-body {
		max-width: 600px;
	}
}

.body-tooltip {
	position: absolute;
	border: 2px solid $color-red;
	border-radius: 5px;
	min-width: 100px;
	max-width: 400px;
	padding: 5px;
	pointer-events: none;
	background-color: $color-lightGrey;

	> .header {
		font-size: 1.25em;
		margin: 0;
		text-align: left;
	}

	> .text {
		text-align: left;
		font-size: 0.8em;
		margin: 0;
		margin-top: 5px;

		> p {
			margin: 0;
		}
	}
}

.features {
	> .badge {
		margin-right: 5px;
		margin-left: 5px;
	}
}

.body-info {
	margin-top: 10px;
}
</style>