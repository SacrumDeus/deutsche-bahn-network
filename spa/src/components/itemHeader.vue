<template>
	<div class="header">
		<b-navbar type="dark" toggleable="md">
			<b-col md="1" />
			<b-col md="10">
				<b-navbar-brand disabled> Deutsche Bahn network analysis </b-navbar-brand>
			</b-col>
			<b-col md="1" />
		</b-navbar>
	</div>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped>
@import "../variables.scss";

.header {
	background-color: $color-grey;

	& .navbar-brand {
		color: $color-red;
		padding-top: 2px;
		padding-bottom: 2px;
		padding-left: 20px;
		padding-right: 10px;
		text-decoration: none;
	}

	& .navbar-brand:hover {
		color: $color-red;
	}
}
</style>