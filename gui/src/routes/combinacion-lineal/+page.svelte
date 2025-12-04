<script lang="ts">
	import VectorInput from '$lib/components/VectorInput.svelte';
	import NumberInput from '$lib/components/NumberInput.svelte';
	import OutputBox from '$lib/components/OutputBox.svelte';
	import Icon from '@iconify/svelte';
	import { combinacionLineal } from '$lib/services/algebra';

	let dim: number = $state(3);
	let cantidad: number = $state(3);
	let vectores: string[][] = $state([]);
	let objetivo: string[] = $state([]);
	let latexOutput: string | null = $state(null);
	let errorMessage: string | null = $state(null);
	let loading: boolean = $state(false);

	const ensureVectors = () => {
		while (vectores.length < cantidad) vectores.push([]);
		if (vectores.length > cantidad) vectores.length = cantidad;
		for (let i = 0; i < cantidad; i++) {
			if (!Array.isArray(vectores[i])) vectores[i] = [];
			while (vectores[i].length < dim) vectores[i].push('');
			if (vectores[i].length > dim) vectores[i].length = dim;
		}
		while (objetivo.length < dim) objetivo.push('');
		if (objetivo.length > dim) objetivo.length = dim;
	};

	$effect(() => {
		ensureVectors();
	});
	ensureVectors();

	const run = async () => {
		if (loading) return;
		loading = true;
		errorMessage = null;
		latexOutput = null;
		try {
			latexOutput = await combinacionLineal(
				vectores.map((v) => ({ dimension: dim, values: v })),
				{ dimension: dim, values: objetivo }
			);
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'No se pudo calcular la combinación.';
		} finally {
			loading = false;
		}
	};
</script>

<main class="min-h-screen w-full px-6 py-10">
	<div class="max-w-5xl space-y-4">
		<header class="space-y-2">
			<p class="text-sm font-semibold uppercase tracking-wide text-primary">Combinación lineal</p>
			<h1 class="text-3xl font-bold">Expresa un vector como combinación de otros</h1>
			<p class="text-base text-base-content/70">Define la dimensión, los vectores base y el vector objetivo. Obtendrás la solución en LaTeX.</p>
		</header>

		<div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
			<div class="card card-border p-4 space-y-4">
				<div class="grid gap-3 sm:grid-cols-2">
					<NumberInput bind:value={dim} min={1} max={6} label="Dimensión" />
					<NumberInput bind:value={cantidad} min={1} max={6} label="Cantidad de vectores" />
				</div>

				<div class="space-y-4">
					{#each Array(cantidad) as _, i}
						<div class="card card-border p-3">
							<p class="text-sm font-semibold text-base-content/70">Vector v{i + 1}</p>
							<VectorInput Header={`v${i + 1}`} Dimension={dim} bind:value={vectores[i]} />
						</div>
					{/each}
				</div>

				<div class="card card-border p-3">
					<p class="text-sm font-semibold text-base-content/70">Vector objetivo</p>
					<VectorInput Header="b" Dimension={dim} bind:value={objetivo} />
				</div>

				<div class="flex justify-end">
					<button class="btn btn-primary" type="button" onclick={run} disabled={loading}>
						{#if loading}
							<Icon icon="line-md:loading-loop" class="size-5" />
						{/if}
						Calcular
					</button>
				</div>
			</div>

			<OutputBox bind:value={latexOutput} bind:error={errorMessage} className="w-full" />
		</div>
	</div>
</main>
