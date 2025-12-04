<script lang="ts">
	import MatrixInput from '$lib/components/MatrixInput.svelte';
	import VectorInput from '$lib/components/VectorInput.svelte';
	import NumberInput from '$lib/components/NumberInput.svelte';
	import OutputBox from '$lib/components/OutputBox.svelte';
	import Icon from '@iconify/svelte';
	import { resolverCramer } from '$lib/services/algebra';

	let n: number = $state(3);
	let coeffs: string[][] = $state([]);
	let results: string[] = $state([]);
	let latexOutput: string | null = $state(null);
	let errorMessage: string | null = $state(null);
	let loading: boolean = $state(false);

	const headers = $derived(Array.from({ length: n }, (_, i) => `x${i + 1}`));

	const run = async () => {
		if (loading) return;
		loading = true;
		errorMessage = null;
		latexOutput = null;
		try {
			latexOutput = await resolverCramer(
				{ rows: n, columns: n, values: coeffs },
				{ dimension: n, values: results }
			);
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'No se pudo resolver con Cramer.';
		} finally {
			loading = false;
		}
	};
</script>

<main class="min-h-screen w-full px-6 py-10">
	<div class="max-w-5xl space-y-4">
		<header class="space-y-2">
			<p class="text-sm font-semibold uppercase tracking-wide text-primary">Cramer</p>
			<h1 class="text-3xl font-bold">Resolver sistema Ax = b</h1>
			<p class="text-base text-base-content/70">
				Ingresa la matriz de coeficientes (cuadrada) y el vector de resultados. El método de Cramer entrega la solución con detalles en LaTeX.
			</p>
		</header>

		<div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
			<div class="card card-border p-4 space-y-4">
				<div class="grid gap-3 sm:grid-cols-2">
					<NumberInput bind:value={n} min={1} max={6} label="Filas/Columnas" />
				</div>
				<div class="grid gap-4 lg:grid-cols-[3fr_1fr]">
					<div class="card card-border p-3">
						<p class="text-sm font-semibold text-base-content/70">Matriz A</p>
						<MatrixInput Rows={n} Headers={headers} bind:value={coeffs} />
					</div>
					<div class="card card-border p-3">
						<p class="text-sm font-semibold text-base-content/70">Vector b</p>
						<VectorInput Header="b" Dimension={n} bind:value={results} />
					</div>
				</div>
				<div class="flex justify-end">
					<button class="btn btn-primary" type="button" onclick={run} disabled={loading}>
						{#if loading}
							<Icon icon="line-md:loading-loop" class="size-5" />
						{/if}
						Resolver
					</button>
				</div>
			</div>

			<OutputBox bind:value={latexOutput} bind:error={errorMessage} className="w-full" />
		</div>
	</div>
</main>
