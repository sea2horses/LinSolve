<script lang="ts">
	import MatrixInput from '$lib/components/MatrixInput.svelte';
	import NumberInput from '$lib/components/NumberInput.svelte';
	import OutputBox from '$lib/components/OutputBox.svelte';
	import { inversaAdjunta, inversaGaussJordan } from '$lib/services/algebra';
	import Icon from '@iconify/svelte';

	type Metodo = 'gauss-jordan' | 'adjunta';

	const metodoInfo: Record<Metodo, { title: string; desc: string; badge: string; icon: string }> = {
		'gauss-jordan': {
			title: 'Gauss-Jordan',
			desc: 'Aumenta con identidad y reduce a I para leer A^-1.',
			badge: 'Identidad aumentada',
			icon: 'tabler:stairs'
		},
		adjunta: {
			title: 'Adjunta',
			desc: 'Calcula cofactores, adjunta y multiplica por 1/det(A).',
			badge: 'Adj(A) / det(A)',
			icon: 'tabler:frame'
		}
	};

	const metodos: Metodo[] = ['gauss-jordan', 'adjunta'];

	let metodo: Metodo = $state('gauss-jordan');
	let dimension: number = $state(3);
	let matrix: string[][] = $state([]);
	let latexOutput: string | null = $state(null);
	let errorMessage: string | null = $state(null);
	let loading: boolean = $state(false);

	const headers = $derived(Array.from({ length: dimension }, (_, i) => `c${i + 1}`));

	const hayDatos = $derived(
		matrix.slice(0, dimension).some((row) => row?.some((cell) => cell?.trim()))
	);

	const calcular = async () => {
		if (loading) return;
		errorMessage = null;
		latexOutput = null;

		if (dimension < 1) {
			errorMessage = 'La dimension debe ser mayor a 0.';
			return;
		}

		loading = true;
		try {
			const spec = { rows: dimension, columns: dimension, values: matrix };
			if (metodo === 'adjunta') {
				latexOutput = await inversaAdjunta(spec);
			} else {
				latexOutput = await inversaGaussJordan(spec);
			}
		} catch (err) {
			errorMessage =
				err instanceof Error ? err.message : 'No se pudo calcular la inversa. Intenta de nuevo.';
		} finally {
			loading = false;
		}
	};
</script>

<main class="min-h-screen w-full px-6 py-8">
	<section class="mb-8 space-y-2">
		<p class="text-sm font-semibold uppercase tracking-wide text-primary">Matriz inversa</p>
		<h1 class="text-3xl font-bold">Adjunta o Gauss-Jordan en un solo lugar</h1>
		<p class="text-sm text-base-content/70 max-w-2xl">
			Ingresa una matriz cuadrada y elige el metodo. El backend en Python genera el desarrollo en
			LaTeX paso a paso para pegar directo en tu reporte.
		</p>
	</section>

	<section class="grid gap-6 lg:grid-cols-[1fr_0.95fr]">
		<div class="space-y-4">
			<div class="card-border card gap-3 p-5">
				<div class="flex flex-wrap gap-2">
					{#each metodos as m}
						<button
							type="button"
							class={`btn ${metodo === m ? 'btn-primary' : 'btn-soft'}`}
							onclick={() => (metodo = m)}
						>
							<Icon icon={metodoInfo[m].icon} class="size-4" />
							{metodoInfo[m].title}
						</button>
					{/each}
				</div>

				<div class="grid gap-3 sm:grid-cols-[160px_1fr] sm:items-center">
					<NumberInput bind:value={dimension} min={1} max={6} label="Dimension (n x n)" />
					<p class="text-xs text-base-content/60">
						Acepta decimales o fracciones en LaTeX. Celdas vacias se toman como 0.
					</p>
				</div>

				<div class="rounded-xl border border-base-300 bg-base-200/50 p-4 space-y-3">
					<div class="flex items-center gap-2">
						<span class="badge badge-outline">{metodoInfo[metodo].badge}</span>
						<p class="font-semibold">{metodoInfo[metodo].title}</p>
					</div>
					<p class="text-sm text-base-content/70">{metodoInfo[metodo].desc}</p>
					{#if metodo === 'gauss-jordan'}
						<p class="text-xs text-base-content/60">
							Se arma [A | I] y se reduce a identidad; la parte derecha queda como A^-1.
						</p>
					{:else}
						<p class="text-xs text-base-content/60">
							Calcula cofatores, adjunta y multiplica por 1/det(A). Falla si det(A) = 0.
						</p>
					{/if}
				</div>

				<div class="card-border card p-4 space-y-3">
					<p class="text-sm font-semibold text-base-content/70">Matriz A (n x n)</p>
					<MatrixInput Headers={headers} Rows={dimension} bind:value={matrix} />
				</div>

				<div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
					<p class="text-xs text-base-content/60">
						{hayDatos ? 'Listo para calcular.' : 'Tip: llena al menos una celda para empezar.'}
					</p>
					<button
						class="btn btn-primary min-w-36 justify-center"
						type="button"
						onclick={calcular}
						disabled={loading}
					>
						{#if loading}
							<Icon icon="line-md:loading-loop" class="size-4.5" />
						{/if}
						Calcular inversa
					</button>
				</div>
			</div>
		</div>

		<div class="space-y-4">
			<div class="card card-border bg-base-200/60 p-4">
				<h2 class="text-lg font-semibold">Resumen rapido</h2>
				<ul class="mt-2 space-y-1 text-sm text-base-content/70">
					<li>- Metodo: {metodoInfo[metodo].title}</li>
					<li>- Dimension: {dimension} x {dimension}</li>
					<li>- Backend: Python (cofactores, adjunta, Gauss-Jordan)</li>
				</ul>
			</div>
			<OutputBox bind:value={latexOutput} bind:error={errorMessage} className="w-full" />
		</div>
	</section>
</main>
