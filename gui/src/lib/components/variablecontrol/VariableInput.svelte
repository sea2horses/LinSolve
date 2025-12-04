<script lang="ts">
	import MathLive from "../MathLive.svelte";
	import MatrixInput from "../MatrixInput.svelte";
	import VectorInput from "../VectorInput.svelte";
    import { VariableType, type Variable } from "./VariableControl";

    interface Params {
        className?: string,
        value: Variable
    }

    let { className = "", value = $bindable<Variable>() }: Params = $props();

    let name = $state("");
    let selected_type: VariableType | null = $state(null)

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

    type ExpressionInfo = {
        value: string
    }

    const expr_info: ExpressionInfo = {
        value: ""
    }

    $effect(() => {
        let rvalue: string[][] | string[] | string | null = null;

        switch(selected_type) {
            case(VariableType.MATRIX): {
                rvalue = matrix_info.value;
                break;
            }

            case(VariableType.VECTOR): {
                rvalue = vector_info.value;
                break;
            }

            case(VariableType.EXPRESSION): {
                rvalue = expr_info.value;
                break;
            }
        }

        value = {
            name: name,
            type: selected_type,
            value: rvalue
        }
    })
</script>

<div id="var-input" class="card p-5 flex border border-base-200 {className}">
    <div class="flex flex-col p-5">
        <div class="input-floating w-96">
            <input type="text" placeholder="X" class="input" id="floatingInput" bind:value={name}/>
            <label class="input-floating-label" for="floatingInput">Variable</label>
        </div>
        <select class="select max-w-sm appearance-none" aria-label="select" bind:value={selected_type}>
            <option value={null} disabled selected>Tipo de Variable</option>
            <option value={VariableType.MATRIX}>Matriz</option>
            <option value={VariableType.VECTOR}>Vector</option>
            <option value={VariableType.EXPRESSION}>Expresión</option>
        </select>
    </div>

    {#if selected_type === VariableType.MATRIX}
        <MatrixInput Rows={matrix_info.rows} Headers={matrix_info.headers} bind:value={matrix_info.value}/>
    {:else if selected_type === VariableType.VECTOR}
        <VectorInput Dimension={vector_info.dimension} Header={vector_info.header} bind:value={vector_info.value}/>
    {:else if selected_type === VariableType.EXPRESSION}
        <MathLive/>
    {/if}
</div>