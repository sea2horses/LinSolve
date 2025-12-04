<script lang="ts">
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import MathLive from '$lib/components/MathLive.svelte';
	import { graficarFuncion, type Punto } from '$lib/services/graficador';

	let expr = '\\sin(x)';
	let xMin = '-6.28';
	let xMax = '6.28';
	let pasos = 180;

	let puntos: Punto[] = [];
	let error: string | null = null;
	let loading = false;

	const width = 680;
	const height = 360;
	const padding = 36;

	const resetEjemplo = () => {
		expr = '\\sin(x)';
		xMin = '-6.28';
		xMax = '6.28';
		pasos = 180;
	};

	const runPlot = async () => {
		if (loading) return;
		error = null;
		loading = true;
		const sampleCount = Math.min(400, Math.max(50, Number(pasos) || 50));
		pasos = sampleCount;
		try {
			puntos = await graficarFuncion(expr, xMin, xMax, sampleCount);
		} catch (err) {
			puntos = [];
			error = err instanceof Error ? err.message : 'No se pudo graficar.';
		} finally {
			loading = false;
		}
	};

	onMount(runPlot);

	const xRange = () => {
		if (!puntos.length) return Number(xMax) - Number(xMin) || 1;
		return Math.max(1e-6, Math.max(...puntos.map((p) => p.x)) - Math.min(...puntos.map((p) => p.x)));
	};

	const xStart = () => (puntos.length ? Math.min(...puntos.map((p) => p.x)) : Number(xMin));
	const xEnd = () => (puntos.length ? Math.max(...puntos.map((p) => p.x)) : Number(xMax));

	const yMinVal = () => (puntos.length ? Math.min(...puntos.map((p) => p.y)) : -1);
	const yMaxVal = () => (puntos.length ? Math.max(...puntos.map((p) => p.y)) : 1);
	const yRange = () => Math.max(1e-6, yMaxVal() - yMinVal());

	const scaleX = (val: number) =>
		padding + ((val - xStart()) / xRange()) * (width - padding * 2);
	const scaleY = (val: number) =>
		height - padding - ((val - yMinVal()) / yRange()) * (height - padding * 2);

	const pathData = () => {
		if (!puntos.length) return '';
		return puntos.map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(p.x)} ${scaleY(p.y)}`).join(' ');
	};

	const xAxisY = () =>
		yMinVal() <= 0 && yMaxVal() >= 0 ? scaleY(0) : null;
	const yAxisX = () =>
		xStart() <= 0 && xEnd() >= 0 ? scaleX(0) : null;
</script>

<svelte:head>
	<title>Graficador de funciones | LinSolve</title>
</svelte:head>

<main class="min-h-screen w-full bg-base-100 px-6 py-8">
	<section class="mx-auto max-w-5xl space-y-3">
		<p class="text-sm font-semibold uppercase tracking-wide text-primary">Visualizador</p>
		<h1 class="text-4xl font-bold">Graficador de funciones</h1>
		<p class="max-w-3xl text-base text-base-content/70">
			Ingresa f(x) en LaTeX, define el rango y genera la curva en tiempo real. Ideal para revisar
			comportamiento de polinomios, trigonometricas o funciones con restricciones de dominio.
		</p>
		<div class="flex flex-wrap gap-2 pt-2">
			<button class="btn btn-soft btn-sm" type="button" on:click={resetEjemplo}>
				<Icon icon="tabler:wand" class="size-4" />
				Usar ejemplo sin(x)
			</button>
			<button class="btn btn-ghost btn-sm" type="button" on:click={() => { expr = '\\ln(x)'; xMin = '0.2'; xMax = '8'; }}>
				<Icon icon="tabler:math" class="size-4" />
				ln(x) con dominio positivo
			</button>
		</div>
	</section>

	<section class="mx-auto mt-6 grid max-w-5xl gap-5 lg:grid-cols-[1.1fr_0.9fr]">
		<div class="card-border card space-y-4 p-5 shadow-lg">
			<header class="space-y-1">
				<p class="text-sm font-semibold uppercase tracking-wide text-primary">Entrada</p>
				<h2 class="text-2xl font-semibold">Configura la funcion</h2>
				<p class="text-sm text-base-content/70">
					La expresion debe depender de x. Puedes usar \\sin, \\cos, \\ln, potencias y fracciones.
				</p>
			</header>

			<label class="form-control w-full">
				<div class="label">
					<span class="label-text">f(x)</span>
					<span class="label-text-alt text-xs text-base-content/60">Editor LaTeX</span>
				</div>
				<MathLive bind:value={expr} className="input input-bordered min-h-[52px]" />
			</label>

			<div class="grid gap-3 sm:grid-cols-2">
				<label class="form-control w-full">
					<div class="label">
						<span class="label-text">x min</span>
					</div>
					<input class="input input-bordered" type="text" bind:value={xMin} />
				</label>
				<label class="form-control w-full">
					<div class="label">
						<span class="label-text">x max</span>
					</div>
					<input class="input input-bordered" type="text" bind:value={xMax} />
				</label>
			</div>

			<label class="form-control w-full">
				<div class="label">
					<span class="label-text">Resolucion ({pasos} puntos)</span>
					<span class="label-text-alt text-xs text-base-content/60">Entre 50 y 400</span>
				</div>
				<input
					type="range"
					min="50"
					max="400"
					step="10"
					value={pasos}
					on:input={(event) =>
						(pasos = Number((event.currentTarget as HTMLInputElement).value))}
					class="range range-primary"
				/>
			</label>

			<div class="flex flex-wrap items-center justify-between gap-3">
				<div class="flex flex-wrap gap-2 text-xs text-base-content/70">
					<span class="badge badge-outline">Salta puntos fuera del dominio</span>
					<span class="badge badge-outline">Escala automatica</span>
					<span class="badge badge-outline">Devuelve datos crudos y SVG</span>
				</div>
				<button class="btn btn-primary min-w-36 justify-center" type="button" on:click={runPlot}>
					{#if loading}
						<Icon icon="line-md:loading-loop" class="size-5" />
					{:else}
						<Icon icon="tabler:chart-line" class="size-5" />
					{/if}
					Graficar
				</button>
			</div>

			{#if error}
				<div class="alert alert-error">
					<Icon icon="tabler:alert-circle" class="size-5" />
					<span class="text-sm">{error}</span>
				</div>
			{/if}
		</div>

		<div class="card-border card space-y-4 p-5 shadow-lg">
			<header class="flex items-center justify-between">
				<div>
					<p class="text-sm font-semibold uppercase tracking-wide text-secondary">Salida</p>
					<h2 class="text-2xl font-semibold">Grafica</h2>
				</div>
				<div class="flex gap-2 text-xs">
					<span class="badge badge-soft badge-primary">x: {xStart().toFixed(2)} .. {xEnd().toFixed(2)}</span>
					<span class="badge badge-soft badge-secondary">y: {yMinVal().toFixed(2)} .. {yMaxVal().toFixed(2)}</span>
				</div>
			</header>

			<div class="rounded-2xl border border-base-300 bg-base-200/60 p-3">
				<svg viewBox={`0 0 ${width} ${height}`} class="h-[320px] w-full">
					<defs>
						<linearGradient id="graphLine" x1="0" x2="1" y1="0" y2="0">
							<stop offset="0%" stop-color="hsl(var(--p))" stop-opacity="0.1" />
							<stop offset="100%" stop-color="hsl(var(--p))" stop-opacity="0.4" />
						</linearGradient>
					</defs>
					<rect
						x="0"
						y="0"
						width={width}
						height={height}
						fill="url(#graphLine)"
						opacity="0.08"
						rx="18"
					/>
					{#if xAxisY() !== null}
						<line
							x1={padding}
							y1={xAxisY() ?? 0}
							x2={width - padding}
							y2={xAxisY() ?? 0}
							stroke="currentColor"
							class="stroke-base-300"
							stroke-width="1"
							stroke-dasharray="4 4"
						/>
					{/if}
					{#if yAxisX() !== null}
						<line
							x1={yAxisX() ?? 0}
							y1={padding}
							x2={yAxisX() ?? 0}
							y2={height - padding}
							stroke="currentColor"
							class="stroke-base-300"
							stroke-width="1"
							stroke-dasharray="4 4"
						/>
					{/if}
					{#if puntos.length}
						<path
							d={pathData()}
							fill="none"
							stroke="hsl(var(--p))"
							stroke-width="2.5"
							stroke-linecap="round"
						/>
					{:else}
						<text
							x="50%"
							y="50%"
							text-anchor="middle"
							fill="currentColor"
							class="fill-base-content/50 text-sm"
						>
							Sin datos. Ingresa una funcion y rango validos.
						</text>
					{/if}
				</svg>
			</div>

			<div class="grid gap-2 sm:grid-cols-2">
				<div class="stat bg-base-200/50">
					<div class="stat-title text-xs">Minimo y maximo (y)</div>
					<div class="stat-value text-xl">{yMinVal().toFixed(3)} / {yMaxVal().toFixed(3)}</div>
					<div class="stat-desc text-xs">Escala auto segun puntos validos</div>
				</div>
				<div class="stat bg-base-200/50">
					<div class="stat-title text-xs">Puntos graficados</div>
					<div class="stat-value text-xl">{puntos.length}</div>
					<div class="stat-desc text-xs">Se omiten valores fuera del dominio</div>
				</div>
			</div>
		</div>
	</section>
</main>
