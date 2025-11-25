<script lang="ts">
	import Katex from "$lib/components/Katex.svelte";
	import MathLive from "$lib/components/MathLive.svelte";
	import VariableControl from "$lib/components/variablecontrol/VariableControl.svelte";
	import VariableInput from "$lib/components/variablecontrol/VariableInput.svelte";
    import { EvaluateLatex } from "$lib/services/evaluate_latex";

    let math: string = $state("")
    let result: string = $state("")
    let err: string | null = $state(null)
    
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
    <div class="w-full">
        <p class="text-sm text-primary">LABORATORIO</p>
        <p class="text-2xl text-neutral">Prueba propiedades, expresiones y evaluaciones</p>
        <p class="text-sm text-secondary">Define variables y evalua</p>
    </div>

    <VariableControl/>

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