<script lang="ts">
	import Icon from '@iconify/svelte';
	import Katex from '$lib/components/Katex.svelte';

	type PositionalTerm = {
		digit: number;
		power: number;
		baseValue: number;
		termValue: number;
	};

	type ErrorConcept = {
		title: string;
		description: string;
		example: string;
		consoleSnippet: string;
	};

	let base10Input = $state('84506');
	let base2Input = $state('1111001');
	let trueValue = $state('2.5');
	let approxValue = $state('2.47');
	let workshopStep = $state('0.1');
	let workshopIterations = $state(12);

	const analyzeConcepts: ErrorConcept[] = [
		{
			title: 'Error inherente',
			description:
				'Existe porque el mundo físico es continuo y nuestras mediciones no. Siempre habrá una diferencia entre la magnitud real y la representada en la máquina.',
			example: 'Medir una resistencia de 10 Ω con un multímetro con resolución de 0.01 Ω.',
			consoleSnippet: "print('Error inherente ≈ |valor_real - valor_ideal|')"
		},
		{
			title: 'Error de redondeo',
			description:
				'Proviene de almacenar un número real con un número fijo de bits. Afecta cada suma/resta repetida y se acumula con rapidez.',
			example: 'Sumar 0.1 diez veces usando precisión float32.',
			consoleSnippet: "print(round(0.1 + 0.2, 17))  # 0.30000000000000004"
		},
		{
			title: 'Error de truncamiento',
			description:
				'Aparece cuando cortamos una serie infinita o un método iterativo. Por ejemplo, usar solo 3 términos en la serie de Taylor del seno.',
			example: 'sin(x) ≈ x - x³/3!',
			consoleSnippet: "print('Truncamiento = |f(x) - aproximación_parcial|')"
		},
		{
			title: 'Overflow / Underflow',
			description:
				'Overflow: el número es demasiado grande para el formato; Underflow: es tan pequeño que se aproxima a cero. Ambos distorsionan resultados posteriores.',
			example: 'np.exp(1000) desborda; np.float32(1e-50) se subrepresenta.',
			consoleSnippet: "print(np.exp(1000))  # inf\nprint(np.float32(1e-50))  # 0.0"
		},
		{
			title: 'Error del modelo matemático',
			description:
				'Se origina cuando idealizamos un fenómeno real. El modelo no contempla todas las variables y la diferencia persiste aunque calculemos con precisión infinita.',
			example: 'Suponer caída libre sin fricción del aire.',
			consoleSnippet: "print('Modelo simplificado ≠ realidad completa')"
		}
	];

	const floatEquality = $derived(0.1 + 0.2 === 0.3);
	const floatSum = 0.1 + 0.2;

	const base10Terms = $derived(decomposeNumber(base10Input, 10));
	const base10Sum = $derived(base10Terms.reduce((acc, term) => acc + term.termValue, 0));
	const base2Terms = $derived(decomposeNumber(base2Input, 2));
	const base2Sum = $derived(base2Terms.reduce((acc, term) => acc + term.termValue, 0));

	const workshopResult = $derived(simulateFloatErrors(Number(workshopStep), workshopIterations));
	const errorTable = $derived(computeErrorTable(trueValue, approxValue));
	const interpretation = $derived(interpretError(errorTable));

	const formatter = new Intl.NumberFormat('es-CO', {
		maximumFractionDigits: 8
	});

	function decomposeNumber(raw: string, base: 10 | 2): PositionalTerm[] {
		const sanitized = raw.replace(base === 10 ? /[^\d]/g : /[^01]/g, '');
		if (!sanitized) return [];
		const digits = sanitized.split('').map((char) => Number.parseInt(char, base));
		const len = digits.length;

		return digits.map((digit, index) => {
			const power = len - index - 1;
			const baseValue = Math.pow(base, power);
			return {
				digit,
				power,
				baseValue,
				termValue: digit * baseValue
			};
		});
	}

	function parseInput(value: string): number | null {
		if (!value?.trim()) return null;
		const parsed = Number(value);
		return Number.isFinite(parsed) ? parsed : null;
	}

	function evaluateFunction(x: number) {
		return Math.sin(x) + x ** 2;
	}

	function computeErrorTable(trueRaw: string, approxRaw: string) {
		const xv = parseInput(trueRaw);
		const xa = parseInput(approxRaw);
		if (xv === null || xa === null) return null;

		const Ea = Math.abs(xv - xa);
		const Er = xv === 0 ? null : Ea / Math.abs(xv);
		const fxTrue = evaluateFunction(xv);
		const fxApprox = evaluateFunction(xa);
		const propagationAbs = Math.abs(fxTrue - fxApprox);
		const propagationRel = fxTrue === 0 ? null : propagationAbs / Math.abs(fxTrue);

		return {
			trueValue: xv,
			approxValue: xa,
			Ea,
			Er,
			fxTrue,
			fxApprox,
			propagationAbs,
			propagationRel
		};
	}

	function interpretError(table: ReturnType<typeof computeErrorTable>) {
		if (!table) return 'Ingresa valores válidos para evaluar la calidad de la aproximación.';

		const rel = table.Er ?? table.propagationRel ?? 0;
		if (rel < 1e-3) {
			return 'La aproximación es excelente. El error relativo es menor a 0.1%, ideal para ingeniería de precisión.';
		}
		if (rel < 1e-2) {
			return 'La aproximación es utilizable. El error relativo ronda el 1%, suficiente para cálculos preliminares.';
		}
		if (rel < 5e-2) {
			return 'Precaución: el error relativo es mayor al 5%. Considera mejorar la medición o el modelo.';
		}
		return 'Error elevado. La aproximación no describe con fidelidad el fenómeno y puede propagar errores grandes en f(x).';
	}

	function simulateFloatErrors(step: number, iterations: number) {
		if (!Number.isFinite(step) || iterations <= 0) {
			return null;
		}

		let float32 = 0;
		let float64 = 0;

		for (let i = 0; i < iterations; i++) {
			float32 = Math.fround(float32 + Math.fround(step));
			float64 += step;
		}

		return {
			float32,
			float64,
			diff: float64 - float32
		};
	}

	const numpySnippet = `import numpy as np
step = np.float32(0.1)
iters = 12
acc32 = np.float32(0.0)
acc64 = np.float64(0.0)
for _ in range(iters):
    acc32 = np.float32(acc32 + step)
    acc64 = np.float64(acc64 + step)
print(acc32, acc64, acc64 - acc32)`;

	const exerciseLatex = String.raw`f(x) = \sin(x) + x^2`;
</script>

<main class="flex-1 overflow-y-auto bg-base-100">
	<section class="border-b border-base-300 bg-base-200/50 px-6 py-10 lg:px-12">
		<div class="mx-auto flex max-w-5xl flex-col gap-6">
			<p class="text-sm font-semibold uppercase tracking-wide text-primary">Métodos numéricos</p>
			<h1 class="text-4xl font-bold leading-tight sm:text-5xl">
				Visualiza las fuentes de error y domina las aproximaciones
			</h1>
			<p class="text-base text-base-content/80">
				Explora notación posicional, errores de representación, ejemplos en punto flotante, un
				taller guiado inspirado en NumPy/SciPy y un ejercicio completo de propagación del error.
			</p>
			<div class="flex flex-col gap-3 sm:flex-row">
				<a class="btn btn-primary" href="#ejercicio-principal">Ir al ejercicio principal</a>
				<a class="btn btn-soft" href="#taller-guiado">Ver taller con NumPy</a>
			</div>
		</div>
	</section>

	<section id="notacion" class="px-6 py-10 lg:px-12">
		<div class="mx-auto flex max-w-5xl flex-col gap-8">
			<header class="flex flex-col gap-2">
				<p class="text-sm font-semibold uppercase text-primary">1. Notación posicional</p>
				<h2 class="text-3xl font-bold">Base 10 y Base 2</h2>
				<p class="text-sm text-base-content/70">
					Ingresa un número y observa cómo la computadora lo descompone según la potencia de la base.
				</p>
			</header>

			<div class="grid gap-6 md:grid-cols-2">
				<article class="card-border card rounded-2xl p-6">
					<h3 class="text-xl font-semibold">Base 10 (decimal)</h3>
					<label class="form-control gap-2">
						<span class="label-text text-sm">Número decimal</span>
						<input
							type="text"
							class="input input-bordered"
							bind:value={base10Input}
							placeholder="Ej. 84506"
						/>
					</label>

					<div class="divider text-xs uppercase">Descomposición</div>

					{#if base10Terms.length > 0}
						<ul class="space-y-2 text-sm">
							{#each base10Terms as term}
								<li class="flex items-center justify-between rounded-xl bg-base-200/60 px-3 py-2">
									<span>{term.digit} × 10^{term.power}</span>
									<span class="font-mono text-base">{formatter.format(term.termValue)}</span>
								</li>
							{/each}
						</ul>
						<p class="mt-4 text-sm">
							Suma final:
							<span class="font-semibold">{formatter.format(base10Sum)}</span>
						</p>
						<div class="mt-3 rounded-xl bg-base-200/70 p-3 text-center text-sm">
							<Katex
								math="84\,506 = 8\times 10^{4} + 4\times 10^{3} + 5\times 10^{2} + 0\times 10^{1} + 6\times 10^{0}"
								displayMode
							/>
						</div>
					{:else}
						<p class="text-sm text-base-content/60">
							Ingresa solo dígitos para generar la descomposición decimal.
						</p>
					{/if}
				</article>

				<article class="card-border card rounded-2xl p-6">
					<h3 class="text-xl font-semibold">Base 2 (binario)</h3>
					<label class="form-control gap-2">
						<span class="label-text text-sm">Número binario</span>
						<input
							type="text"
							class="input input-bordered"
							bind:value={base2Input}
							placeholder="Ej. 1111001"
						/>
					</label>

					<div class="divider text-xs uppercase">Descomposición</div>

					{#if base2Terms.length > 0}
						<ul class="space-y-2 text-sm">
							{#each base2Terms as term}
								<li class="flex items-center justify-between rounded-xl bg-base-200/60 px-3 py-2">
									<span>{term.digit} × 2^{term.power}</span>
									<span class="font-mono text-base">{formatter.format(term.termValue)}</span>
								</li>
							{/each}
						</ul>
						<p class="mt-4 text-sm">
							Equivalencia decimal:
							<span class="font-semibold">{formatter.format(base2Sum)}</span>
						</p>
						<div class="mt-3 rounded-xl bg-base-200/70 p-3 text-center text-sm">
							<Katex
								math="1111001 = 1\cdot 2^6 + 1\cdot 2^5 + 1\cdot 2^4 + 1\cdot 2^3 + 0\cdot 2^2 + 0\cdot 2^1 + 1\cdot 2^0"
								displayMode
							/>
						</div>
					{:else}
						<p class="text-sm text-base-content/60">
							Ingresa solo unos y ceros para ver la suma ponderada en base 2.
						</p>
					{/if}
				</article>
			</div>
		</div>
	</section>

	<section id="errores" class="border-t border-base-300 bg-base-200/40 px-6 py-10 lg:px-12">
		<div class="mx-auto flex max-w-6xl flex-col gap-8">
			<header class="flex flex-col gap-2">
				<p class="text-sm font-semibold uppercase text-primary">2. Conceptos de error</p>
				<h2 class="text-3xl font-bold">Errores en métodos numéricos</h2>
				<p class="text-sm text-base-content/70">
					Cada tarjeta explica el origen del error y cómo detectarlo con un ejemplo simple.
				</p>
			</header>

			<div class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
				{#each analyzeConcepts as concept}
					<article class="card-border card h-full rounded-2xl p-5">
						<h3 class="text-lg font-semibold">{concept.title}</h3>
						<p class="mt-2 text-sm text-base-content/70">{concept.description}</p>
						<p class="mt-2 text-xs text-base-content/60">
							Ejemplo: <span class="font-medium">{concept.example}</span>
						</p>
						<pre class="mockup-code mt-3 text-xs">
<code>{concept.consoleSnippet}</code></pre
						>
					</article>
				{/each}
			</div>
		</div>
	</section>

	<section id="punto-flotante" class="px-6 py-10 lg:px-12">
		<div class="mx-auto flex max-w-5xl flex-col gap-8">
			<header class="flex flex-col gap-2">
				<p class="text-sm font-semibold uppercase text-primary">
					3. Ejemplo con números en punto flotante
				</p>
				<h2 class="text-3xl font-bold">¿Por qué 0.1 + 0.2 ≠ 0.3?</h2>
			</header>

			<div class="grid gap-6 md:grid-cols-2">
				<div class="card-border card rounded-2xl p-6">
					<p class="text-sm text-base-content/70">En Python (y JavaScript):</p>
					<pre class="mockup-code mt-3 text-xs">
<code>print(0.1 + 0.2 == 0.3)  # {floatEquality ? 'True' : 'False'}
print(0.1 + 0.2)            # {floatSum.toPrecision(17)}</code></pre
					>
					<p class="mt-3 text-sm">
						El resultado exacto en binario requiere infinitos bits, pero los tipos flotantes usan 52 bits
						(mantisa) en doble precisión. La suma se almacena como 0.30000000000000004 y la igualdad estricta
						falla.
					</p>
					<div class="mt-4 rounded-xl bg-base-200/70 p-3 text-xs">
						<p>ε máquina (float64): {Number.EPSILON}</p>
						<p>Representación interna 0.1 = 1.100110011... × 2⁻⁴</p>
					</div>
				</div>

				<div class="card-border card rounded-2xl p-6">
					<h3 class="text-lg font-semibold">Consejos prácticos</h3>
					<ul class="list-inside list-disc space-y-2 text-sm">
						<li>Evita comparaciones directas; usa una tolerancia como 1e-9.</li>
						<li>Agrupa sumas de menor a mayor para reducir cancelación catastrófica.</li>
						<li>Prefiere tipos decimal/bigfloat al representar dinero.</li>
						<li>Documenta las tolerancias aceptables en cada cálculo.</li>
					</ul>
				</div>
			</div>
		</div>
	</section>

	<section id="taller-guiado" class="border-t border-base-300 bg-base-200/40 px-6 py-10 lg:px-12">
		<div class="mx-auto flex max-w-6xl flex-col gap-8">
			<header class="flex flex-col gap-2">
				<p class="text-sm font-semibold uppercase text-primary">4. Taller guiado</p>
				<h2 class="text-3xl font-bold">Simula pérdidas de precisión estilo NumPy</h2>
				<p class="text-sm text-base-content/70">
					Ajusta los parámetros y observa cómo cambian las sumas en float32 y float64 (similar a
					<code>numpy.float32</code> vs <code>numpy.float64</code>).
				</p>
			</header>

			<div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
				<div class="card-border card rounded-2xl p-6">
					<div class="grid gap-4 sm:grid-cols-2">
						<label class="form-control">
							<span class="label-text text-sm">Paso (valor a sumar)</span>
							<input
								type="number"
								class="input input-bordered"
								step="0.01"
								bind:value={workshopStep}
							/>
						</label>
						<label class="form-control">
							<span class="label-text text-sm">Iteraciones</span>
							<input
								type="number"
								min={1}
								max={200}
								class="input input-bordered"
								bind:value={workshopIterations}
							/>
						</label>
					</div>

					{#if workshopResult}
						<div class="mt-5 overflow-x-auto rounded-2xl border border-base-300">
							<table class="table table-zebra text-sm">
								<thead>
									<tr>
										<th>Formato</th>
										<th>Resultado</th>
										<th>Error vs float64</th>
									</tr>
								</thead>
								<tbody>
									<tr>
										<td class="font-semibold">float32 (≈ np.float32)</td>
										<td>{formatter.format(workshopResult.float32)}</td>
										<td>{formatter.format(workshopResult.diff)}</td>
									</tr>
									<tr>
										<td class="font-semibold">float64 (≈ np.float64)</td>
										<td>{formatter.format(workshopResult.float64)}</td>
										<td>0</td>
									</tr>
								</tbody>
							</table>
						</div>

						<p class="mt-3 text-sm text-base-content/70">
							La diferencia surge porque float32 guarda 24 bits en la mantisa. Cada suma introduce un
							redondeo, lo que explica la pérdida de precisión acumulada.
						</p>
					{:else}
						<p class="mt-4 text-sm text-error">
							Ingresa un paso válido y al menos una iteración para ejecutar el taller.
						</p>
					{/if}
				</div>

				<div class="card-border card rounded-2xl p-6">
					<h3 class="text-lg font-semibold">Código equivalente en NumPy</h3>
					<pre class="mockup-code mt-4 text-xs">
<code>{numpySnippet}</code></pre
					>
					<p class="mt-4 text-sm">
						NumPy utiliza instrucciones vectoriales para repetir la operación con diferentes anchos de palabra.
						Podemos inspeccionar el error calculando <code>acc64 - acc32</code> y graficándolo para cada
						iteración.
					</p>
				</div>
			</div>
		</div>
	</section>

	<section id="ejercicio-principal" class="px-6 py-12 lg:px-12">
		<div class="mx-auto flex max-w-6xl flex-col gap-8">
			<header class="flex flex-col gap-2">
				<p class="text-sm font-semibold uppercase text-primary">5. Ejercicio principal</p>
				<h2 class="text-3xl font-bold">Errores absoluto, relativo y propagación</h2>
				<p class="text-sm text-base-content/70">
					Introduce el valor verdadero y el aproximado. Calcularemos
					<Katex math={exerciseLatex} /> para evaluar la propagación del error.
				</p>
			</header>

			<div class="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
				<article class="card-border card rounded-2xl p-6">
					<label class="form-control">
						<span class="label-text text-sm">Valor verdadero (xᵥ)</span>
						<input type="number" class="input input-bordered" step="0.001" bind:value={trueValue} />
					</label>
					<label class="form-control mt-4">
						<span class="label-text text-sm">Valor aproximado (xₐ)</span>
						<input type="number" class="input input-bordered" step="0.001" bind:value={approxValue} />
					</label>
					<div class="mt-5 rounded-xl bg-base-200/60 p-4 text-sm">
						<p>f(x) = sin(x) + x²</p>
						<p>Interpretamos x como la magnitud que deseas medir/estimar.</p>
					</div>
				</article>

				<article class="card-border card rounded-2xl p-6">
					<h3 class="text-lg font-semibold">Resultados</h3>
					{#if errorTable}
						<div class="overflow-x-auto rounded-2xl border border-base-300">
							<table class="table text-sm">
								<thead>
									<tr>
										<th>Magnitud</th>
										<th>Valor</th>
									</tr>
								</thead>
								<tbody>
									<tr>
										<td>f(xᵥ)</td>
										<td>{formatter.format(errorTable.fxTrue)}</td>
									</tr>
									<tr>
										<td>f(xₐ)</td>
										<td>{formatter.format(errorTable.fxApprox)}</td>
									</tr>
									<tr>
										<td>Error absoluto (Eₐ)</td>
										<td>{formatter.format(errorTable.Ea)}</td>
									</tr>
									<tr>
										<td>Error relativo (Eᵣ)</td>
										<td>
											{errorTable.Er === null
												? 'N/A'
												: `${formatter.format(errorTable.Er * 100)} %`}
										</td>
									</tr>
									<tr>
										<td>Propagación |f(xᵥ) - f(xₐ)|</td>
										<td>{formatter.format(errorTable.propagationAbs)}</td>
									</tr>
									<tr>
										<td>Propagación relativa</td>
										<td>
											{errorTable.propagationRel === null
												? 'N/A'
												: `${formatter.format(errorTable.propagationRel * 100)} %`}
										</td>
									</tr>
								</tbody>
							</table>
						</div>
					{:else}
						<p class="text-sm text-base-content/70">
							Proporciona números reales para calcular los errores.
						</p>
					{/if}

					<p class="mt-4 rounded-xl bg-base-200/60 p-4 text-sm">{interpretation}</p>
				</article>
			</div>
		</div>
	</section>
	<footer class="border-t border-base-300 px-6 py-6 text-center text-xs text-base-content/60">
		Hecho con FlyonUI · Incluye NumPy/SciPy como referencia conceptual.
	</footer>
</main>
