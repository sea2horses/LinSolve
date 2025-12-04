<script lang="ts">
	import Icon from '@iconify/svelte';

	const featureCards = [
		{
			title: 'Gauss-Jordan',
			description: 'Resuelve sistemas con bitacora paso a paso y salida en LaTeX.',
			icon: 'tabler:stairs-up',
			href: '/gauss-jordan/'
		},
		{
			title: 'Metodos numericos',
			description: 'Calcula raices con biseccion, regla falsa, Newton y secante.',
			icon: 'mdi:chart-bell-curve',
			href: '/metodos-numericos'
		},
		{
			title: 'Matrices',
			description: 'Suma, resta, multiplica y calcula determinantes en segundos.',
			icon: 'mdi:matrix',
			href: '/matrices'
		},
		{
			title: 'Vectores',
			description: 'Opera vectores, combina y evalua dependencia lineal.',
			icon: 'mdi:vector-line',
			href: '/vectores'
		},
		{
			title: 'Laboratorio',
			description: 'Juega con expresiones simbolicas y ve el resultado renderizado.',
			icon: 'mdi:flask',
			href: '/laboratorio'
		}
	];

	const quickLinks = [
		{ label: 'Matrices basicas', href: '/matrices#operaciones' },
		{ label: 'Producto matriz vector', href: '/vectores#matriz-vector' },
		{ label: 'Combinacion lineal', href: '/vectores#combinacion' },
		{ label: 'Metodos numericos', href: '/metodos-numericos' },
		{ label: 'Configurar tema', href: '/configuracion' }
	];
</script>

<svelte:head>
	<title>LinSolve | Toolkit de algebra lineal</title>
</svelte:head>

<main class="min-h-screen w-full bg-base-100">
	<section class="relative overflow-hidden border-b border-base-300 bg-gradient-to-br from-primary/10 via-base-200 to-base-100 px-6 py-12 lg:px-12">
		<div class="absolute right-16 top-8 hidden rotate-6 rounded-full border border-primary/30 bg-primary/10 px-4 py-2 text-xs font-semibold text-primary lg:inline-flex">
			<Icon icon="tabler:sparkles" class="mr-1 size-4" /> Python + Eel + SvelteKit
		</div>
		<div class="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[1.1fr_0.9fr]">
			<div class="space-y-5">
				<p class="text-sm font-semibold uppercase tracking-wide text-primary">LinSolve toolkit</p>
				<h1 class="text-5xl font-bold leading-tight">
					Practica algebra lineal con modulos guiados y salida en LaTeX
				</h1>
				<p class="max-w-3xl text-base text-base-content/70">
					Ingresa matrices, vectores o expresiones, obten los pasos y copia el LaTeX listo para tu
					reporte. Todo corre localmente con Python, sin depender de internet.
				</p>
				<div class="flex flex-wrap gap-3">
					<a class="btn btn-primary" href="/gauss-jordan/">Abrir Gauss-Jordan</a>
					<a class="btn btn-soft" href="/matrices">Operar matrices</a>
					<a class="btn btn-ghost" href="/vectores">Modulos de vectores</a>
				</div>
				<div class="flex flex-wrap gap-2 pt-2 text-sm text-base-content/70">
					{#each quickLinks as link}
						<a class="badge badge-outline hover:badge-primary" href={link.href}>{link.label}</a>
					{/each}
				</div>
			</div>
			<div class="card-border card relative overflow-hidden rounded-2xl border border-primary/30 bg-base-100/70 p-6 shadow-lg backdrop-blur">
				<div class="absolute -left-8 -top-10 h-32 w-32 rounded-full bg-primary/10 blur-3xl"></div>
				<div class="absolute -bottom-12 -right-10 h-32 w-32 rounded-full bg-secondary/10 blur-3xl"></div>
				<p class="text-sm font-semibold text-base-content/70">Panel rapido</p>
				<ul class="mt-4 space-y-3">
					<li class="flex items-center gap-3 rounded-xl border border-base-300 bg-base-200/60 p-3">
						<span class="rounded-full bg-primary/10 p-2 text-primary"
							><Icon icon="tabler:sum" class="size-5" /></span
						>
						<div>
							<p class="font-semibold">Operaciones de matrices</p>
							<p class="text-sm text-base-content/70">Suma, resta, producto, determinantes.</p>
						</div>
					</li>
					<li class="flex items-center gap-3 rounded-xl border border-base-300 bg-base-200/60 p-3">
						<span class="rounded-full bg-secondary/10 p-2 text-secondary"
							><Icon icon="mdi:vector-line" class="size-5" /></span
						>
						<div>
							<p class="font-semibold">Vectores y combinacion</p>
							<p class="text-sm text-base-content/70">Dependencia, combinacion lineal y escalares.</p>
						</div>
					</li>
					<li class="flex items-center gap-3 rounded-xl border border-base-300 bg-base-200/60 p-3">
						<span class="rounded-full bg-accent/10 p-2 text-accent"
							><Icon icon="mdi:flask" class="size-5" /></span
						>
						<div>
							<p class="font-semibold">Laboratorio simbolico</p>
							<p class="text-sm text-base-content/70">Evalua expresiones en LaTeX directo en Python.</p>
						</div>
					</li>
				</ul>
			</div>
		</div>
	</section>

	<section class="mx-auto grid max-w-6xl gap-6 px-6 py-10 lg:px-0">
		<div class="flex items-center justify-between">
			<div>
				<h2 class="text-3xl font-semibold">Modulos principales</h2>
				<p class="text-sm text-base-content/70">Accede rapido a cada herramienta.</p>
			</div>
			<a class="btn btn-ghost text-sm" href="/configuracion">
				<Icon icon="tabler:settings" class="size-5" /> Preferencias
			</a>
		</div>

		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			{#each featureCards as card}
				<a
					class="card-border card group relative flex h-full flex-col gap-2 rounded-2xl border border-base-300 bg-base-200/40 p-4 transition hover:-translate-y-1 hover:border-primary hover:shadow-lg"
					href={card.href}
				>
					<div class="flex items-center gap-2">
						<span class="rounded-full bg-primary/10 p-2 text-primary">
							<Icon icon={card.icon} class="size-5" />
						</span>
						<p class="text-lg font-semibold">{card.title}</p>
					</div>
					<p class="text-sm text-base-content/70">{card.description}</p>
					<span class="mt-auto text-xs font-semibold text-primary">Abrir modulo -></span>
				</a>
			{/each}
		</div>
	</section>

	<section class="mx-auto max-w-6xl px-6 pb-14 lg:px-0">
		<div class="grid gap-6 rounded-2xl border border-base-300 bg-base-200/40 p-6 lg:grid-cols-[1.1fr_0.9fr]">
			<div class="space-y-3">
				<p class="text-sm font-semibold uppercase tracking-wide text-primary">Guia rapida</p>
				<h3 class="text-2xl font-semibold">Consejos de entrada</h3>
				<ul class="space-y-2 text-sm text-base-content/80">
					<li>- Escribe fracciones como <code>\\frac12</code> o decimales.</li>
					<li>- Las celdas en blanco se interpretan como 0.</li>
					<li>- Usa constantes <code>\\pi</code> y <code>e</code>, y raices <code>\\sqrt{5}</code>.</li>
					<li>- Todos los modulos entregan LaTeX listo para copiar.</li>
				</ul>
				<div class="flex gap-3 pt-2">
					<a class="btn btn-primary" href="/laboratorio">Probar en laboratorio</a>
					<a class="btn btn-soft" href="/matrices#multiplicacion">Ver multiplicacion</a>
				</div>
			</div>
			<div class="card-border card rounded-xl border border-base-300 bg-base-100 p-5">
				<p class="text-sm font-semibold text-base-content/70">Ejemplo en LaTeX</p>
				<div class="mt-3 rounded-lg bg-base-200/60 p-3 text-sm">
					<code>
						<!-- A = \\begin{bmatrix}1 &amp; 0 &amp; -1\\\\2 &amp; 3 &amp; 0\\\\0 &amp; 1 &amp; 4\\end{bmatrix} -->
						<br />
						<!-- B = \\begin{bmatrix}1 &amp; 2\\\\0 &amp; 1\\\\-2 &amp; 0\\end{bmatrix} -->
					</code>
				</div>
				<p class="mt-2 text-sm text-base-content/70">
					Introduce matrices o vectores con esta sintaxis o usa los editores de tabla para llenar
					valores rapidamente.
				</p>
			</div>
		</div>
	</section>
</main>
