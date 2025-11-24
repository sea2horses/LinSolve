<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import SideBar from '$lib/components/SideBar.svelte';
	import { SideBarWidth } from '$lib/components/SideBar';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<main class="h-screen w-screen selection:bg-primary selection:text-base-100 grid grid-cols-[300px_1fr]">
	<SideBar />
	<div id="main-content" class="overflow-y-auto overflow-x-hidden">
		{@render children()}
	</div>
</main>
