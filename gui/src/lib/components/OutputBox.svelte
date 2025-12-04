<script lang="ts">
	import Katex from "./Katex.svelte";

    interface Params {
        value: string | null,
        error: string | null,
        className?: string,
    }

    let { value = $bindable<string | null>(null), error = $bindable<string | null>(null), className = "" }: Params = $props();
</script>

<div class={`card card-border shadow-none ${className}`}>
    <div class="card-body">
        <h1 class="text-2xl text-base-content">Salida en LaTeX</h1>
        <p class="text-sm text-base-content/60">Visualiza los pasos o copia el codigo para tu informe.</p>
        {#if value}
            <div class="card bg-base-200 text-base-content block overflow-auto">
                <Katex math={value} displayMode/>
            </div>

            <details class="mt-3">
                <summary class="cursor-pointer text-primary flex items-center gap-2">
                    <span class="icon-[tabler--chevron-right] size-4"></span>
                    LaTeX crudo
                </summary>
                <div class="px-2 py-2">
                    <p class="text-sm text-base-content font-normal break-words whitespace-pre-wrap">
                        {value}
                    </p>
                </div>
            </details>
        {:else if error}
            <div class="alert alert-error flex items-center gap-4" role="alert">
                <span class="icon-[tabler--alert-triangle] shrink-0 size-6"></span>
                <p>
                    <span class="text-lg font-semibold">Error:</span>
                    {error}
                </p>
            </div>
        {/if}
    </div>
</div>
