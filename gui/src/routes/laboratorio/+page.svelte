<script lang="ts">
	import Katex from '$lib/components/Katex.svelte';
	import MathLive from '$lib/components/MathLive.svelte';
	import MatrixInput from '$lib/components/MatrixInput.svelte';
	import VectorInput from '$lib/components/VectorInput.svelte';
	import NumberInput from '$lib/components/NumberInput.svelte';
	import OutputBox from '$lib/components/OutputBox.svelte';
	import Icon from '@iconify/svelte';
	import { EvaluateLatex } from '$lib/services/evaluate_latex';
	import { callPyFunc } from '$lib/eel';

	type VarType = 'matrix' | 'vector' | 'expr';
	type VarMatrix = { kind: 'matrix'; name: string; rows: number; cols: number; values: string[][] };
	type VarVector = { kind: 'vector'; name: string; dim: number; values: string[] };
	type VarExpr = { kind: 'expr'; name: string; value: string };
	type Variable = VarMatrix | VarVector | VarExpr;

	const reserved = new Set(['e', 'E', 't', 'T', 'I']);

	let exprEval: string = $state('');
	let exprLeft: string = $state('');
	let exprRight: string = $state('');
	let resultEval: string = $state('');
	let resultCompare: string = $state('');
	let errEval: string | null = $state(null);
	let errCompare: string | null = $state(null);
	let vars: Variable[] = $state([]);
	let nameError: string | null = $state(null);
	let activeVar = $state(0);

	const presets = [
		{ label: 'Suma conmutativa', left: 'A + B', right: 'B + A' },
		{ label: 'Suma asociativa', left: '(A + B) + C', right: 'A + (B + C)' },
		{ label: 'Elemento neutro', left: 'A + 0', right: 'A' },
		{ label: 'Distributiva escalar sobre suma', left: 'r (A + B)', right: 'r A + r B' },
		{ label: 'Distributiva suma de escalares', left: '(r + s) A', right: 'r A + s A' },
		{ label: 'Compatibilidad de escalares', left: 'r (s A)', right: '(r s) A' },
		{ label: 'Doble transposición', left: '(A^T)^T', right: 'A' },
		{ label: 'Transposición de suma', left: '(A + B)^T', right: 'A^T + B^T' },
		{ label: 'Transposición de resta', left: '(A - B)^T', right: 'A^T - B^T' },
		{ label: 'Transposición escalar', left: '(r A)^T', right: 'r A^T' },
		{ label: 'Transposición de producto', left: '(A B)^T', right: 'B^T A^T' },
		{ label: 'Distributiva escalar traspuesta', left: 'r (A + B)^T', right: 'r A^T + r B^T' },
		{ label: 'Intercambio de filas (det cambia signo)', left: 'det(P A)', right: '- det(A)' },
		{ label: 'Multiplicar fila (det escala)', left: 'det(k A)', right: 'k det(A)' },
		{ label: 'Propiedad multiplicativa det', left: 'det(A B)', right: 'det(A) det(B)' }
	];

	const normalizeName = (raw: string): string => {
		const n = raw.trim();
		if (n.length !== 1) return '';
		if (!/^[A-Za-z]$/.test(n)) return '';
		if (reserved.has(n)) return '';
		return n;
	};

	const addVar = (kind: VarType) => {
		const base: Variable =
			kind === 'matrix'
				? { kind, name: 'A', rows: 2, cols: 2, values: [] }
				: kind === 'vector'
					? { kind, name: 'v', dim: 2, values: [] }
					: { kind, name: 'x', value: '' };
		vars = [...vars, base];
	};

	const updateName = (i: number, raw: string) => {
		const norm = normalizeName(raw);
		if (!norm) {
			nameError = 'Usa una sola letra (no e, T, t, I).';
			return;
		}
		nameError = null;
		vars = vars.map((v, idx) => (idx === i ? { ...v, name: norm } : v));
	};

	const updateMatrixShape = (i: number, rows: number, cols: number) => {
		const v = vars[i];
		if (v.kind !== 'matrix') return;
		const values = Array.from({ length: rows }, (_, r) => {
			const row = v.values?.[r] ? [...v.values[r]] : [];
			while (row.length < cols) row.push('');
			return row.slice(0, cols);
		});
		vars = vars.map((vv, idx) => (idx === i ? { ...v, rows, cols, values } : vv));
	};

	const updateVectorDim = (i: number, dim: number) => {
		const v = vars[i];
		if (v.kind !== 'vector') return;
		const values = Array.from({ length: dim }, (_, r) => v.values?.[r] ?? '');
		vars = vars.map((vv, idx) => (idx === i ? { ...v, dim, values } : vv));
	};

	const normalizeVarsForPayload = (): { name: string; value: string }[] => {
		const seen = new Set<string>();
		const list = vars
			.map((v) => {
				const name = normalizeName(v.name);
				if (!name) return null;
				if (seen.has(name)) {
					throw new Error(`Nombre duplicado: ${name}`);
				}
				seen.add(name);
				if (v.kind === 'expr') {
					return { name, value: JSON.stringify({ type: 'Expression', contents: v.value || '0' }) };
				}
				if (v.kind === 'vector') {
					const comps = Array.from({ length: v.dim }, (_, idx) => v.values?.[idx]?.trim() || '0');
					return { name, value: JSON.stringify({ type: 'Vector', contents: comps }) };
				}
				const rows = Array.from({ length: v.rows }, (_, r) => {
					const row = v.values?.[r] ? [...v.values[r]] : [];
					while (row.length < v.cols) row.push('0');
					return row.slice(0, v.cols).map((c) => (c && c.trim().length ? c : '0'));
				});
				return { name, value: JSON.stringify({ type: 'Matrix', contents: rows }) };
			})
			.filter(Boolean) as { name: string; value: string }[];
		return list;
	};

	const onEval = async () => {
		if (!exprEval.trim()) {
			errEval = 'Ingresa una expresión.';
			return;
		}
		resultEval = '';
		errEval = null;
		try {
			const payload = normalizeVarsForPayload().map((v) => ({ name: v.name, value: v.value }));
			resultEval = await EvaluateLatex(exprEval, payload);
		} catch (e) {
			errEval = e instanceof Error ? e.message : 'Error al evaluar';
		}
	};

	const onCompare = async () => {
		if (!exprLeft.trim() || !exprRight.trim()) {
			errCompare = 'Completa ambas expresiones.';
			return;
		}
		resultCompare = '';
		errCompare = null;
		try {
			const payload = normalizeVarsForPayload();
			const env =
				payload.length > 0
					? JSON.stringify(Object.fromEntries(payload.map((v) => [v.name, JSON.parse(v.value)])))
					: undefined;
			resultCompare = await callPyFunc<string>('comparar_expresiones', exprLeft, exprRight, env);
		} catch (e) {
			errCompare = e instanceof Error ? e.message : 'Error al comparar';
		}
	};
</script>

<main class="min-h-screen w-full px-6 py-8 space-y-6">
	<header class="space-y-1">
		<p class="text-sm font-semibold uppercase tracking-wide text-primary">Laboratorio</p>
		<h1 class="text-3xl font-bold">Evalúa, comprueba propiedades y juega con LaTeX</h1>
		<p class="text-sm text-base-content/70">Define variables (matrices, vectores, expresiones), carga presets y compara.</p>
	</header>

	<section class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
		<div class="card card-border bg-base-200/50 p-4 space-y-4">
			<div class="flex items-center justify-between gap-3 flex-wrap">
				<div>
					<p class="text-lg font-semibold">Variables</p>
					<p class="text-xs text-base-content/60">Una sola letra (no e, T, t, I). Valores en LaTeX.</p>
				</div>
				<div class="flex gap-2">
					<button class="btn btn-sm btn-soft" type="button" onclick={() => addVar('matrix')}>
						<Icon icon="mdi:table-large" class="size-4" /> Matriz
					</button>
					<button class="btn btn-sm btn-soft" type="button" onclick={() => addVar('vector')}>
						<Icon icon="mdi:vector-line" class="size-4" /> Vector
					</button>
					<button class="btn btn-sm btn-soft" type="button" onclick={() => addVar('expr')}>
						<Icon icon="mdi:function-variant" class="size-4" /> Expresión
					</button>
				</div>
			</div>
			{#if nameError}
				<p class="text-xs text-error">{nameError}</p>
			{/if}
			{#if vars.length === 0}
				<p class="text-sm text-base-content/60">No hay variables. Agrega una para empezar.</p>
			{:else}
				<div role="tablist" class="tabs tabs-lifted">
					{#each vars as v, i}
						<button
							role="tab"
							class={`tab ${activeVar === i ? 'tab-active' : ''}`}
							onclick={() => (activeVar = i)}
						>
							{v.name || v.kind}
						</button>
					{/each}
				</div>
				{#each vars as v, i}
					<div class={`rounded-xl border border-base-300 bg-base-100/80 p-3 space-y-3 ${activeVar === i ? '' : 'hidden'}`}>
						<div class="flex items-center gap-2">
							<input
								class="input input-sm input-bordered w-20"
								placeholder="A"
								value={v.name}
								oninput={(e) => updateName(i, (e.target as HTMLInputElement).value)}
							/>
							<span class="badge badge-outline">{v.kind}</span>
							<button class="btn btn-ghost btn-sm text-error" type="button" onclick={() => vars = vars.filter((_, idx) => idx !== i)}>
								<Icon icon="tabler:x" class="size-4" />
							</button>
						</div>

						{#if v.kind === 'expr'}
							<MathLive bind:value={(vars[i] as VarExpr).value} className="w-full" />
						{:else if v.kind === 'vector'}
							<div class="space-y-2">
								<NumberInput bind:value={(vars[i] as VarVector).dim} min={1} max={6} label="Dimensión" on:change={() => updateVectorDim(i, (vars[i] as VarVector).dim)} />
								<VectorInput
									Header={(vars[i] as VarVector).name}
									Dimension={(vars[i] as VarVector).dim}
									bind:value={(vars[i] as VarVector).values}
								/>
							</div>
						{:else}
							<div class="space-y-2">
								<div class="grid gap-2 sm:grid-cols-2">
									<NumberInput bind:value={(vars[i] as VarMatrix).rows} min={1} max={6} label="Filas" on:change={() => updateMatrixShape(i, (vars[i] as VarMatrix).rows, (vars[i] as VarMatrix).cols)} />
									<NumberInput bind:value={(vars[i] as VarMatrix).cols} min={1} max={6} label="Columnas" on:change={() => updateMatrixShape(i, (vars[i] as VarMatrix).rows, (vars[i] as VarMatrix).cols)} />
								</div>
								<MatrixInput
									Headers={Array.from({ length: (vars[i] as VarMatrix).cols }, (_, c) => `${(vars[i] as VarMatrix).name}${c + 1}`)}
									Rows={(vars[i] as VarMatrix).rows}
									bind:value={(vars[i] as VarMatrix).values}
								/>
							</div>
						{/if}
					</div>
				{/each}
			{/if}
		</div>

		<div class="card card-border bg-base-200/50 p-4 space-y-3 max-h-80 overflow-auto">
			<p class="text-lg font-semibold">Presets de propiedades</p>
			<div class="grid gap-2">
				{#each presets as p}
					<button class="btn btn-soft justify-between" type="button" onclick={() => { exprLeft = p.left; exprRight = p.right; }}>
						<span>{p.label}</span>
						<Icon icon="tabler:arrow-autofit-width" class="size-4" />
					</button>
				{/each}
			</div>
		</div>
	</section>

	<section class="grid gap-6 lg:grid-cols-2">
		<div class="card card-border bg-base-100 p-4 space-y-3">
			<p class="text-lg font-semibold">Evaluar expresión</p>
			<MathLive bind:value={exprEval} className="w-full" />
			<button class="btn btn-primary" type="button" onclick={onEval}>Evaluar</button>
			<OutputBox bind:value={resultEval} bind:error={errEval} />
		</div>

		<div class="card card-border bg-base-100 p-4 space-y-3">
			<p class="text-lg font-semibold">Comprobar igualdad</p>
			<div class="space-y-2">
				<MathLive bind:value={exprLeft} className="w-full" />
				<MathLive bind:value={exprRight} className="w-full" />
			</div>
			<button class="btn btn-primary" type="button" onclick={onCompare}>Comparar</button>
			<OutputBox bind:value={resultCompare} bind:error={errCompare} />
		</div>
	</section>
</main>
