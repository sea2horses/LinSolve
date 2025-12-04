<script lang="ts">
	import Icon from '@iconify/svelte';
	import OutputBox from '$lib/components/OutputBox.svelte';
	import MathLive from '$lib/components/MathLive.svelte';
	import {
		metodoBiseccion,
		metodoNewtonRaphson,
		metodoReglaFalsa,
		metodoSecante,
		type MetodoResultado
	} from '$lib/services/numericos';
	import { graficarFuncion } from '$lib/services/graficador';
	import functionPlot from 'function-plot';

	type MetodoKey = 'biseccion' | 'reglaFalsa' | 'newton' | 'secante';

	const metodos: Record<
		MetodoKey,
		{ title: string; badge: string; description: string; tips: string[] }
	> = {
		biseccion: {
			title: 'Biseccion',
			badge: 'Intervalo',
			description:
				'Divide el intervalo en mitades y conserva el sub-intervalo donde hay cambio de signo.',
			tips: ['f(a) y f(b) deben tener signos opuestos', 'El error se reduce a la mitad en cada paso']
		},
		reglaFalsa: {
			title: 'Regla falsa',
			badge: 'Intervalo',
			description:
				'Usa la recta secante entre (a, f(a)) y (b, f(b)) para aproximar la raiz dentro del intervalo.',
			tips: ['f(a) y f(b) deben tener signos opuestos', 'Suele converger mas rapido que biseccion']
		},
		newton: {
			title: 'Newton-Raphson',
			badge: 'Derivada',
			description:
				'Mejora una sola semilla usando la derivada: x_{n+1} = x_n - f(x_n)/f\'(x_n).',
			tips: ['Necesita f\'(x) distinto de 0', 'Si la semilla esta lejos, puede divergir']
		},
		secante: {
			title: 'Secante',
			badge: '2 semillas',
			description:
				'Aproxima la derivada con dos puntos y avanza como Newton pero sin calcular f\'.',
			tips: ['Evita derivadas complicadas', 'Requiere dos semillas cercanas a la raiz']
		}
	};

	let metodoActivo: MetodoKey = $state('biseccion');
	let latexOutput: string | null = $state(null);
	let raizAprox: number | null = $state(null);
	let fRaiz: number | null = $state(null);
	let errorMessage: string | null = $state(null);
	let loading: boolean = $state(false);
	let grafEl: HTMLDivElement | null = null;

	let form = $state({
		funcion: 'x^3 - x - 2',
		a: '-1',
		b: '2',
		x0: '1',
		x1: '2',
		tolerancia: '0.0001',
		maxIter: 20
	});

	const runMetodo = async () => {
		if (loading) return;
		loading = true;
		errorMessage = null;
		latexOutput = null;
		raizAprox = null;
		fRaiz = null;
		const iteraciones = Math.max(1, Number(form.maxIter) || 0);

		try {
			let res: MetodoResultado | null = null;
			switch (metodoActivo) {
				case 'biseccion':
					res = await metodoBiseccion(
						form.funcion,
						form.a,
						form.b,
						form.tolerancia,
						iteraciones
					);
					break;
				case 'reglaFalsa':
					res = await metodoReglaFalsa(
						form.funcion,
						form.a,
						form.b,
						form.tolerancia,
						iteraciones
					);
					break;
				case 'newton':
					res = await metodoNewtonRaphson(
						form.funcion,
						form.x0,
						form.tolerancia,
						iteraciones
					);
					break;
				case 'secante':
					res = await metodoSecante(
						form.funcion,
						form.x0,
						form.x1,
						form.tolerancia,
						iteraciones
					);
					break;
			}
			if (res) {
				latexOutput = res.latex;
				raizAprox = Number.isFinite(res.raiz ?? NaN) ? res.raiz : null;
				fRaiz = Number.isFinite(res.f_raiz ?? NaN) ? res.f_raiz : null;
				await renderGrafica();
			}
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'No se pudo ejecutar el metodo.';
		} finally {
			loading = false;
		}
	};

	const setDefault = (key: MetodoKey) => {
		metodoActivo = key;
		// Ajustar semillas por defecto segun el metodo
		if (key === 'biseccion' || key === 'reglaFalsa') {
			form.a = '-1';
			form.b = '2';
		}
		if (key === 'newton') {
			form.x0 = '1';
		}
		if (key === 'secante') {
			form.x0 = '0';
			form.x1 = '2';
		}
	};

	const domainGuess = (): [number, number] => {
		const asNum = (v: string, fallback: number) => {
			const n = Number(v);
			return Number.isFinite(n) ? n : fallback;
		};
		const cands: number[] = [];
		if (metodoActivo === 'biseccion' || metodoActivo === 'reglaFalsa') {
			cands.push(asNum(form.a, -5), asNum(form.b, 5));
		} else if (metodoActivo === 'secante') {
			cands.push(asNum(form.x0, -5), asNum(form.x1, 5));
		} else {
			const x0 = asNum(form.x0, 0);
			cands.push(x0 - 2, x0 + 2);
		}
		if (raizAprox !== null) {
			cands.push(raizAprox);
		}
		// Asegura un rango base amplio
		cands.push(-20, 20);

		let xmin = Math.min(...cands);
		let xmax = Math.max(...cands);
		if (xmax <= xmin) {
			xmin -= 1;
			xmax += 1;
		}
		const span = xmax - xmin;
		const pad = Math.max(span * 0.1, 1);
		return [xmin - pad, xmax + pad];
	};

	const renderGrafica = async () => {
		if (!grafEl) return;
		grafEl.innerHTML = '';
		try {
			const [xmin, xmax] = domainGuess();
			const coords = await graficarFuncion(form.funcion, `${xmin}`, `${xmax}`, 220);
			functionPlot({
				target: grafEl,
				width: 760,
				height: 420,
				grid: true,
				xAxis: { label: 'x', domain: [xmin, xmax] },
				yAxis: { label: 'y' },
				data: [
					{
						points: coords.map((p) => [p.x, p.y]),
						fnType: 'points',
						graphType: 'polyline',
						color: '#2563eb'
					},
					...(raizAprox !== null && fRaiz !== null
						? [
								{
									points: [[raizAprox, fRaiz]],
									fnType: 'points',
									graphType: 'scatter',
									color: '#f97316',
									attr: { r: 4 }
								}
							]
						: [])
				]
			});
		} catch (err) {
			console.error('No se pudo graficar la funcion', err);
		}
	};
</script>

<main class="min-h-screen w-full bg-base-100 px-6 py-8">
	<section class="mx-auto max-w-6xl space-y-2">
		<p class="text-sm font-semibold uppercase tracking-wide text-primary">Raices</p>
		<h1 class="text-4xl font-bold">Métodos de raíces con LaTeX</h1>
		<p class="text-base text-base-content/70">
			Introduce la función y los parámetros. El backend calcula los pasos y devuelve el log listo en LaTeX.
		</p>
		<div class="flex flex-wrap gap-2 pt-2">
			{#each Object.keys(metodos) as key}
				<button type="button" class="btn btn-sm btn-soft" onclick={() => setDefault(key as MetodoKey)}>
					<Icon icon="tabler:wand" class="size-4" />
					{metodos[key as MetodoKey].title}
				</button>
			{/each}
		</div>
	</section>

	<section class="mx-auto mt-6 max-w-6xl space-y-6">
		<div class="flex flex-wrap gap-3">
			{#each Object.entries(metodos) as [key, data]}
				<button
					type="button"
					class={`btn ${metodoActivo === key ? 'btn-primary' : 'btn-soft'} flex items-center gap-2`}
					onclick={() => (metodoActivo = key as MetodoKey)}
				>
					<span class="badge badge-ghost">{data.badge}</span>
					{data.title}
				</button>
			{/each}
		</div>

		<div class="space-y-4">
			<div class="card-border card space-y-4 p-5 shadow-lg">
				<header class="space-y-1">
					<p class="text-sm font-semibold text-primary uppercase">{metodos[metodoActivo].badge}</p>
					<h2 class="text-2xl font-semibold">{metodos[metodoActivo].title}</h2>
					<p class="text-sm text-base-content/70">{metodos[metodoActivo].description}</p>
				</header>

				<div class="grid gap-3">
					<label class="form-control w-full">
						<div class="label">
							<span class="label-text">f(x)</span>
							<span class="label-text-alt text-xs text-base-content/60">Editor MathLive (LaTeX)</span>
						</div>
						<MathLive bind:value={form.funcion} className="input input-bordered min-h-[52px]" />
					</label>

					<div class="grid gap-3 sm:grid-cols-2">
						<label class="form-control w-full">
							<div class="label">
								<span class="label-text">Tolerancia</span>
							</div>
							<input
								type="text"
								class="input input-bordered"
								placeholder="0.0001"
								bind:value={form.tolerancia}
							/>
						</label>
						<label class="form-control w-full">
							<div class="label">
								<span class="label-text">Max iteraciones</span>
							</div>
							<input
								type="number"
								min="1"
								class="input input-bordered"
								bind:value={form.maxIter}
							/>
						</label>
					</div>

					{#if metodoActivo === 'biseccion' || metodoActivo === 'reglaFalsa'}
						<div class="grid gap-3 sm:grid-cols-2">
							<label class="form-control w-full">
								<div class="label"><span class="label-text">a (limite inferior)</span></div>
								<input type="text" class="input input-bordered" bind:value={form.a} />
							</label>
							<label class="form-control w-full">
								<div class="label"><span class="label-text">b (limite superior)</span></div>
								<input type="text" class="input input-bordered" bind:value={form.b} />
							</label>
						</div>
					{:else if metodoActivo === 'newton'}
						<label class="form-control w-full">
							<div class="label"><span class="label-text">x0 (semilla)</span></div>
							<input type="text" class="input input-bordered" bind:value={form.x0} />
						</label>
					{:else}
						<div class="grid gap-3 sm:grid-cols-2">
							<label class="form-control w-full">
								<div class="label"><span class="label-text">x0</span></div>
								<input type="text" class="input input-bordered" bind:value={form.x0} />
							</label>
							<label class="form-control w-full">
								<div class="label"><span class="label-text">x1</span></div>
								<input type="text" class="input input-bordered" bind:value={form.x1} />
							</label>
						</div>
					{/if}
				</div>

				<div class="flex flex-wrap items-center justify-between gap-3 pt-1">
					<div class="flex flex-wrap gap-2 text-xs text-base-content/70">
						{#each metodos[metodoActivo].tips as tip}
							<span class="badge badge-outline">{tip}</span>
						{/each}
					</div>
					<button class="btn btn-primary min-w-40 justify-center" type="button" onclick={runMetodo}>
						{#if loading}
							<Icon icon="line-md:loading-loop" class="size-5" />
						{/if}
						Calcular
					</button>
				</div>
			</div>

			<OutputBox bind:value={latexOutput} bind:error={errorMessage} className="w-full" />
			<div class="card-border card space-y-3 p-4 shadow">
				<header class="flex items-center justify-between">
					<div>
						<p class="text-xs font-semibold uppercase tracking-wide text-secondary">Grafica</p>
						<h3 class="text-xl font-semibold">Funcion y raiz</h3>
					</div>
					{#if raizAprox !== null}
						<span class="badge badge-soft badge-primary">x* = {raizAprox.toFixed(4)}</span>
					{/if}
				</header>
				<div class="rounded-2xl border border-base-300 bg-base-200/60 p-3">
					<div bind:this={grafEl} class="h-[360px] w-full"></div>
				</div>
			</div>
		</div>
	</section>
</main>
