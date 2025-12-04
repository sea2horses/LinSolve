<script lang="ts">
	import { onMount } from 'svelte';
	import Icon from '@iconify/svelte';
	import functionPlot from 'function-plot';

	let expr = 'sin(x)';
	let xMin = '-6';
	let xMax = '6';
	let samples = 200;

	let error: string | null = null;
	let loading = false;
	let graphEl: HTMLDivElement;

	const clampSamples = (val: number) => Math.min(400, Math.max(50, Math.round(val)));

	const runPlot = () => {
		if (!graphEl) return;
		loading = true;
		error = null;
		graphEl.innerHTML = '';
		const n = clampSamples(Number(samples) || 200);
		samples = n;
		try {
			functionPlot({
				target: graphEl,
				width: 720,
				height: 420,
				grid: true,
				disableZoom: false,
				xAxis: { label: 'x', domain: [Number(xMin), Number(xMax)] },
				yAxis: { label: 'y' },
				data: [
					{
						fn: expr,
						sampler: 'builtIn',
						nSamples: n,
						graphType: 'polyline',
						color: '#2563eb'
					}
				]
			});
		} catch (e) {
			error = e instanceof Error ? e.message : 'No se pudo graficar.';
		}
		loading = false;
	};

	onMount(runPlot);

	const setEjemplo = (fn: string, min: string, max: string) => {
		expr = fn;
		xMin = min;
		xMax = max;
		runPlot();
	};
</script>

<svelte:head>
	<title>Graficador de funciones | LinSolve</title>
</svelte:head>

<main class="min-h-screen w-full bg-base-100 px-6 py-8">
	<section class="mx-auto max-w-5xl space-y-3">
		<p class="text-sm font-semibold uppercase tracking-wide text-primary">Visualizador</p>
		<h1 class="text-4xl font-bold">Graficador de funciones</h1>
		<p class="max-w-3xl text-base text-base-content/70">
			Escribe f(x), define el rango y usa function-plot (npm) para dibujarla en el cliente.
		</p>
		<div class="flex flex-wrap gap-2 pt-2">
			<button class="btn btn-soft btn-sm" type="button" on:click={() => setEjemplo('sin(x)', '-6', '6')}>
				<Icon icon="tabler:wand" class="size-4" />
				Usar ejemplo sin(x)
			</button>
			<button class="btn btn-ghost btn-sm" type="button" on:click={() => setEjemplo('ln(x)', '0.2', '8')}>
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
					Sintaxis tipo mathjs: sin(x), cos(x), exp(x), ln(x), (x^2-4)/x, etc.
				</p>
			</header>

			<label class="form-control w-full">
				<div class="label">
					<span class="label-text">f(x)</span>
					<span class="label-text-alt text-xs text-base-content/60">Se envia directo a function-plot</span>
				</div>
				<input class="input input-bordered" type="text" bind:value={expr} />
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
					<span class="label-text">Resolucion ({samples} puntos)</span>
					<span class="label-text-alt text-xs text-base-content/60">Entre 50 y 400</span>
				</div>
				<input
					type="range"
					min="50"
					max="400"
					step="10"
					bind:value={samples}
					class="range range-primary"
					on:change={runPlot}
				/>
			</label>

			<div class="flex flex-wrap items-center justify-between gap-3">
				<div class="flex flex-wrap gap-2 text-xs text-base-content/70">
					<span class="badge badge-outline">Cliente puro</span>
					<span class="badge badge-outline">Zoom y pan habilitados</span>
					<span class="badge badge-outline">Muestra errores de parseo</span>
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
					<span class="badge badge-soft badge-primary">Usa rueda para zoom</span>
					<span class="badge badge-soft badge-secondary">Arrastra para mover</span>
				</div>
			</header>

			<div class="rounded-2xl border border-base-300 bg-base-200/60 p-3">
				<div bind:this={graphEl} class="h-[360px] w-full"></div>
			</div>
		</div>
	</section>
</main>
