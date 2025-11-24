<script lang="ts">
	import Katex from "$lib/components/Katex.svelte";
	import MathLive from "$lib/components/MathLive.svelte";
	import VariableInput from "$lib/components/VariableInput.svelte";
    import { EvaluateLatex } from "$lib/services/evaluate_latex";

    let math: string = $state("")
    let result: string = $state("")
    let err: string | null = $state(null)
    // Dynamic variable inputs
    let variables = $state([])
    let nextId = 2

    const addVariable = () => {
        variables.push({ id: nextId++ })
    }

    const removeVariable = (idx: number) => {
        // if (variables.length <= 1) return
        variables.splice(idx, 1)
    }
    
    const onSolve = async () => {
        result = "";
        try {
            result = await EvaluateLatex(math);
            err = null;
        } catch(error) {
            err = error instanceof Error ? error.message : "Hubo un problema";
        }
    }

</script>

<div class="flex-center flex-col w-full h-full gap-6 p-5">
    <div class="w-full flex items-center justify-between mb-3">
        <div class="text-sm">Variables: {variables.length}</div>
        <div class="flex gap-2">
            <button class="btn btn-sm btn-outline" onclick={addVariable}>Añadir Variable</button>
        </div>
    </div>

    <div id="variable-container"
        style="display:grid; grid-template-columns: repeat(3, 1fr); grid-auto-flow: row; gap:1rem; width:100%;">
        {#each variables as v, i (v.id)}
            <div class="relative">
                <VariableInput />
                <button class="btn btn-xs btn-circle btn-outline absolute" style="right:0.5rem; top:0.5rem;"
                    onclick={() => removeVariable(i)}>×</button>
            </div>
        {/each}
    </div>
    <MathLive className="text-2xl" bind:value={math}/>
    <div class="flex-center flex-col p-5">
        Math: {math}
    </div>
    <button class="btn btn-primary" onclick={onSolve}>Calculate</button>
    Output: 
    <Katex math={result}/>
    {#if err}
        <div class="alert alert-error flex items-center gap-4" role="alert">
            <span class="icon-[tabler--alert-triangle] shrink-0 size-6"></span>
            <p><span class="text-lg font-semibold">Error:</span> {err}</p>
        </div>
    {/if}
</div>