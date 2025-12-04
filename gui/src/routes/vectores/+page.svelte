<script lang="ts">
import MatrixInput from '$lib/components/MatrixInput.svelte';
import NumberInput from '$lib/components/NumberInput.svelte';
import OutputBox from '$lib/components/OutputBox.svelte';
import VectorInput from '$lib/components/VectorInput.svelte';
import Icon from '@iconify/svelte';
import { onMount } from 'svelte';
import {
	sumarVectores,
	restarVectores,
	escalarVector,
	matrizPorVector
	} from '$lib/services/algebra';

	type Op = 'suma' | 'resta' | 'escalar' | 'matriz-vector';

	let op: Op = $state('suma');
	let dimA: number = $state(3);
	let dimB: number = $state(3);
	let vectorA: string[] = $state([]);
	let vectorB: string[] = $state([]);
	let escalar: string = $state('2');

	let mRows: number = $state(3);
	let mCols: number = $state(3);
let matrix: string[][] = $state([]);

let latexOutput: string | null = $state(null);
let errorMessage: string | null = $state(null);
let loading: boolean = $state(false);

const headersM = $derived(Array.from({ length: mCols }, (_, i) => `c${i + 1}`));

const opInfo: Record<Op, { title: string; desc: string; badge: string }> = {
	suma: { title: 'Suma de vectores', desc: 'Ambos vectores deben tener la misma dimensión.', badge: 'A + B' },
	resta: { title: 'Resta de vectores', desc: 'Ambos vectores deben tener la misma dimensión.', badge: 'A - B' },
	escalar: { title: 'Vector por escalar', desc: 'Multiplica cada componente por k.', badge: 'k · A' },
	'matriz-vector': {
		title: 'Matriz por vector',
		desc: 'Columnas de la matriz deben igualar la dimensión del vector.',
		badge: 'M × v'
	}
};

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
			if (dimA !== dimB) throw new Error('Las dimensiones de los dos vectores deben coincidir.');
		}
		if (op === 'matriz-vector') {
			if (mCols !== dimA) throw new Error('Las columnas de la matriz deben coincidir con la dimensión del vector.');
		}

		switch (op) {
			case 'suma':
				latexOutput = await sumarVectores(
					{ dimension: dimA, values: vectorA },
					{ dimension: dimB, values: vectorB }
					);
					break;
				case 'resta':
					latexOutput = await restarVectores(
						{ dimension: dimA, values: vectorA },
						{ dimension: dimB, values: vectorB }
					);
					break;
				case 'escalar':
					latexOutput = await escalarVector({ dimension: dimA, values: vectorA }, escalar);
					break;
				case 'matriz-vector':
					latexOutput = await matrizPorVector(
						{ rows: mRows, columns: mCols, values: matrix },
						{ dimension: dimA, values: vectorA }
					);
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
		<p class="text-sm font-semibold uppercase tracking-wide text-primary">Vectores</p>
		<h1 class="text-3xl font-bold">Operaciones entre vectores y matriz-vector</h1>
		<p class="text-sm text-base-content/70">Introduce los valores (decimales o LaTeX) y obten la salida en LaTeX.</p>
	</header>

	<section class="space-y-4">
		<div class="flex flex-wrap gap-2">
			<span id="suma"></span><span id="resta"></span><span id="escalar"></span><span id="matriz-vector"></span>
			<button class={`btn ${op === 'suma' ? 'btn-primary' : 'btn-soft'}`} onclick={() => (op = 'suma')}>
				<Icon icon="tabler:sum" class="size-4" /> Suma
			</button>
			<button class={`btn ${op === 'resta' ? 'btn-primary' : 'btn-soft'}`} onclick={() => (op = 'resta')}>
				<Icon icon="gg:math-minus" class="size-4" /> Resta
			</button>
			<button
				class={`btn ${op === 'escalar' ? 'btn-primary' : 'btn-soft'}`}
				onclick={() => (op = 'escalar')}
			>
				<Icon icon="mdi:multiplication" class="size-4" /> Escalar
			</button>
			<button
				class={`btn ${op === 'matriz-vector' ? 'btn-primary' : 'btn-soft'}`}
				onclick={() => (op = 'matriz-vector')}
			>
				<Icon icon="mdi:matrix" class="size-4" /> Matriz x vector
			</button>
		</div>

		<div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
			<div class="space-y-4">
				<div class="card-border card space-y-4 p-4">
					<h2 class="text-lg font-semibold">Vector A</h2>
					<NumberInput bind:value={dimA} min={1} max={6} label="Dimension" />
					<VectorInput Header="A" Dimension={dimA} bind:value={vectorA} />
					{#if op === 'suma' || op === 'resta'}
						<div class="space-y-3">
							<h3 class="text-base font-semibold">Vector B</h3>
							<NumberInput bind:value={dimB} min={1} max={6} label="Dimension" />
							<VectorInput Header="B" Dimension={dimB} bind:value={vectorB} />
						</div>
					{/if}

					{#if op === 'escalar'}
						<label class="form-control w-full">
							<div class="label"><span class="label-text">Escalar</span></div>
							<input type="text" class="input input-bordered" bind:value={escalar} />
						</label>
					{/if}
				</div>

				{#if op === 'matriz-vector'}
					<div class="card-border card space-y-4 p-4">
						<h2 class="text-lg font-semibold">Matriz</h2>
						<div class="grid gap-3 sm:grid-cols-2">
							<NumberInput bind:value={mRows} min={1} max={6} label="Filas" />
							<NumberInput bind:value={mCols} min={1} max={6} label="Columnas" />
						</div>
						<MatrixInput Headers={headersM} Rows={mRows} bind:value={matrix} />
						<p class="text-xs text-base-content/60">La dimension del vector A debe coincidir con las columnas.</p>
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
					</div>
				</div>
				<div class="rounded-xl border border-base-300 bg-base-100/80 p-3 text-sm text-base-content/70 space-y-1">
					<p class="font-semibold text-base-content">Resumen</p>
					<ul class="list-disc pl-4 space-y-1">
						<li>Dimensión A: {dimA}</li>
						{#if op === 'suma' || op === 'resta'}
							<li>Dimensión B: {dimB}</li>
						{/if}
						{#if op === 'matriz-vector'}
							<li>Matriz: {mRows}×{mCols}</li>
						{/if}
					</ul>
				</div>
				<OutputBox bind:value={latexOutput} bind:error={errorMessage} className="w-full" />
			</div>
		</div>
	</section>
</main>
