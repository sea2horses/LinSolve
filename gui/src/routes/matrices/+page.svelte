<script lang="ts">
import MatrixInput from '$lib/components/MatrixInput.svelte';
import NumberInput from '$lib/components/NumberInput.svelte';
import OutputBox from '$lib/components/OutputBox.svelte';
import Icon from '@iconify/svelte';
import { onMount } from 'svelte';
import {
	sumarMatrices,
	restarMatrices,
	multiplicarMatrices,
	determinanteCofactores,
		determinanteSarrus
	} from '$lib/services/algebra';

	type Op = 'suma' | 'resta' | 'multiplicacion' | 'det-cof' | 'det-sarrus';

	let op: Op = $state('suma');
	let rowsA: number = $state(3);
	let colsA: number = $state(3);
	let rowsB: number = $state(3);
	let colsB: number = $state(3);
let matrixA: string[][] = $state([]);
let matrixB: string[][] = $state([]);
let latexOutput: string | null = $state(null);
let errorMessage: string | null = $state(null);
let loading: boolean = $state(false);

const opInfo: Record<Op, { title: string; desc: string; badge: string }> = {
	suma: { title: 'Suma A + B', desc: 'Requiere mismas dimensiones en A y B.', badge: 'A + B' },
	resta: { title: 'Resta A - B', desc: 'Requiere mismas dimensiones en A y B.', badge: 'A - B' },
	multiplicacion: {
		title: 'Producto A × B',
		desc: 'Columnas de A deben igualar filas de B.',
		badge: 'A × B'
	},
	'det-cof': { title: 'Determinante (cofactores)', desc: 'Matriz cuadrada.', badge: '|A|' },
	'det-sarrus': { title: 'Determinante (Sarrus)', desc: 'Solo para 3×3.', badge: '|A|' }
};

const headersA = $derived(Array.from({ length: colsA }, (_, i) => `A${i + 1}`));
const headersB = $derived(Array.from({ length: colsB }, (_, i) => `B${i + 1}`));

const syncHash = () => {
	const hash = typeof window !== 'undefined' ? window.location.hash.replace('#', '') : '';
	if (hash && opInfo[hash as Op]) {
		op = hash as Op;
	}
};

onMount(() => {
	syncHash();
	const handler = () => syncHash();
	window.addEventListener('hashchange', handler);
	return () => window.removeEventListener('hashchange', handler);
});

const run = async () => {
	if (loading) return;
	loading = true;
	errorMessage = null;
	latexOutput = null;

	try {
		if (op === 'suma' || op === 'resta') {
			if (rowsA !== rowsB || colsA !== colsB) {
				throw new Error('Para suma o resta, ambas matrices deben tener las mismas filas y columnas.');
			}
		}

		if (op === 'multiplicacion') {
			if (colsA !== rowsB) {
				throw new Error('Para multiplicar, columnas de A deben igualar filas de B.');
			}
		}

		if (op === 'det-cof' || op === 'det-sarrus') {
			if (rowsA !== colsA) throw new Error('La matriz debe ser cuadrada.');
			if (op === 'det-sarrus' && (rowsA !== 3 || colsA !== 3)) {
				throw new Error('El método de Sarrus solo aplica para matrices 3x3.');
			}
		}

		switch (op) {
			case 'suma':
				latexOutput = await sumarMatrices(
					{ rows: rowsA, columns: colsA, values: matrixA },
					{ rows: rowsB, columns: colsB, values: matrixB }
					);
					break;
				case 'resta':
					latexOutput = await restarMatrices(
						{ rows: rowsA, columns: colsA, values: matrixA },
						{ rows: rowsB, columns: colsB, values: matrixB }
					);
					break;
				case 'multiplicacion':
					latexOutput = await multiplicarMatrices(
						{ rows: rowsA, columns: colsA, values: matrixA },
						{ rows: rowsB, columns: colsB, values: matrixB }
					);
					break;
				case 'det-cof':
					latexOutput = await determinanteCofactores({
						rows: rowsA,
						columns: colsA,
						values: matrixA
					});
					break;
				case 'det-sarrus':
					latexOutput = await determinanteSarrus({
						rows: rowsA,
						columns: colsA,
						values: matrixA
					});
					break;
			}
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'No se pudo completar la operacion.';
		} finally {
			loading = false;
		}
	};
</script>

<main class="min-h-screen w-full px-6 py-8">
	<header class="mb-6 space-y-2">
		<p class="text-sm font-semibold uppercase tracking-wide text-primary">Matrices</p>
		<h1 class="text-3xl font-bold">Operaciones con LaTeX</h1>
		<p class="text-sm text-base-content/70">
			Llena las entradas, elige la operacion y obtén el resultado en LaTeX listo para copiar.
		</p>
	</header>

	<section class="space-y-4">
		<div class="flex flex-wrap gap-2">
			<span id="suma"></span><span id="resta"></span><span id="multiplicacion"></span><span id="det-cof"></span><span id="det-sarrus"></span>
			<button class={`btn ${op === 'suma' ? 'btn-primary' : 'btn-soft'}`} onclick={() => (op = 'suma')}>
				<Icon icon="tabler:sum" class="size-4" /> Suma
			</button>
			<button class={`btn ${op === 'resta' ? 'btn-primary' : 'btn-soft'}`} onclick={() => (op = 'resta')}>
				<Icon icon="gg:math-minus" class="size-4" /> Resta
			</button>
			<button
				class={`btn ${op === 'multiplicacion' ? 'btn-primary' : 'btn-soft'}`}
				onclick={() => (op = 'multiplicacion')}
			>
				<Icon icon="mdi:multiply" class="size-4" /> Multiplicacion
			</button>
			<button
				class={`btn ${op === 'det-cof' ? 'btn-primary' : 'btn-soft'}`}
				onclick={() => (op = 'det-cof')}
			>
				<Icon icon="mdi:alpha-d-box" class="size-4" /> Determinante (cofactores)
			</button>
			<button
				class={`btn ${op === 'det-sarrus' ? 'btn-primary' : 'btn-soft'}`}
				onclick={() => (op = 'det-sarrus')}
			>
				<Icon icon="mdi:alpha-s-box" class="size-4" /> Determinante (Sarrus)
			</button>
		</div>

		<div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
			<div class="space-y-4">
				<div class="card-border card space-y-4 p-4">
					<h2 class="text-lg font-semibold">Matriz A</h2>
					<div class="grid gap-3 sm:grid-cols-2">
						<NumberInput bind:value={rowsA} min={1} max={6} label="Filas" />
						<NumberInput bind:value={colsA} min={1} max={6} label="Columnas" />
					</div>
					<MatrixInput Headers={headersA} Rows={rowsA} bind:value={matrixA} />
				</div>

				{#if op !== 'det-cof' && op !== 'det-sarrus'}
					<div class="card-border card space-y-4 p-4">
						<h2 class="text-lg font-semibold">Matriz B</h2>
						<div class="grid gap-3 sm:grid-cols-2">
							<NumberInput bind:value={rowsB} min={1} max={6} label="Filas" />
							<NumberInput bind:value={colsB} min={1} max={6} label="Columnas" />
						</div>
						<MatrixInput Headers={headersB} Rows={rowsB} bind:value={matrixB} />
					</div>
				{/if}

				<div class="flex items-center justify-between gap-3">
					<p class="text-xs text-base-content/60">Admite decimales y fracciones en LaTeX (\frac12).</p>
					<button class="btn btn-primary" type="button" onclick={run} disabled={loading}>
						{#if loading}
							<Icon icon="line-md:loading-loop" class="size-5" />
						{/if}
						Calcular
					</button>
				</div>
			</div>

			<div class="card card-border bg-base-200/50 p-4 space-y-4">
				<div class="flex items-center gap-3">
					<span class="badge badge-primary">{opInfo[op].badge}</span>
					<div>
						<p class="text-lg font-semibold">{opInfo[op].title}</p>
						<p class="text-xs text-base-content/60">{opInfo[op].desc}</p>
						<p class="text-[11px] text-base-content/50">
							Resultado esperado: {op === 'multiplicacion' ? rowsA : rowsA}×{op === 'multiplicacion' ? colsB : colsA}
						</p>
					</div>
				</div>
				<div class="rounded-xl border border-base-300 bg-base-100/80 p-3 text-sm text-base-content/70 space-y-1">
					<p class="font-semibold text-base-content">Resumen</p>
					<ul class="list-disc pl-4 space-y-1">
						<li>Filas A: {rowsA}, Columnas A: {colsA}</li>
						{#if op !== 'det-cof' && op !== 'det-sarrus'}
							<li>Filas B: {rowsB}, Columnas B: {colsB}</li>
						{/if}
					</ul>
				</div>
				<OutputBox bind:value={latexOutput} bind:error={errorMessage} className="w-full" />
			</div>
		</div>
	</section>
</main>
