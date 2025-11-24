<script lang="ts">
	import MathLive from "./MathLive.svelte";
	import MatrixInput from "./MatrixInput.svelte";
	import VectorInput from "./VectorInput.svelte";

    let { className = "" } = $props();

    let selected_type = $state("")

    type MatrixInfo = {
        rows: number,
        columns: number,
        headers: string[],
        value: string[][]
    }

    const matrix_info: MatrixInfo = $state({
        rows: 3,
        columns: 3,
        headers: [],
        value: [],
    })

	$effect(() => {
		matrix_info.headers.length = matrix_info.columns;
		for (let i = 0; i < matrix_info.columns; i++) {
			matrix_info.headers[i] = `x${i + 1}`;
		}
	});

    type VectorInfo = {
        dimension: number,
        header: string,
        value: string[]
    }

    const vector_info: VectorInfo = $state({
        dimension: 3,
        header: "V",
        value: []
    })
</script>

<div id="var-input" class="card p-5 flex border border-base-200 {className}">
    <div class="flex flex-col p-5">
        <div class="input-floating w-96">
            <input type="text" placeholder="X" class="input" id="floatingInput" />
            <label class="input-floating-label" for="floatingInput">Variable</label>
        </div>
        <select class="select max-w-sm appearance-none" aria-label="select" bind:value={selected_type}>
            <option disabled selected>Tipo de Variable</option>
            <option value="matriz">Matriz</option>
            <option value="vector">Vector</option>
            <option value="expresion">Expresión</option>
        </select>
    </div>

    {#if selected_type === "matriz"}
        <MatrixInput Rows={matrix_info.rows} Headers={matrix_info.headers} bind:value={matrix_info.value}/>
    {:else if selected_type === "vector"}
        <VectorInput Dimension={vector_info.dimension} Header={vector_info.header} bind:value={vector_info.value}/>
    {:else if selected_type === "expresion"}
        <MathLive/>
    {/if}
</div>