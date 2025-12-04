<script lang="ts">
	import Katex from "./Katex.svelte";

    interface Params {
        value: string | null,
        error: string | null,
        className?: string,
    }

    let { value = $bindable<string | null>(null), error = $bindable<string | null>(null), className = "" }: Params = $props();
</script>

<div class="card card-border shadow-none {className}">
    <div class="card-body">
        <h1 class="text-2xl text-neutral">Salida en LaTeX</h1>
        <p class="text-sm text-neutral/50">Visualiza los pasos o copia el código para tu informe.</p>
        {#if value}
            <div class="card bg-base-200 text-white block overflow-auto">
                <Katex math={value} displayMode/>
            </div>

            <div class="accordion divide-neutral/20 divide-y">
                <div class="accordion-item" id="payment-arrow">
                    <button class="accordion-toggle inline-flex items-center gap-x-4 text-primary" aria-controls="payment-arrow-collapse" aria-expanded="true">
                        <span class="icon-[tabler--chevron-right] accordion-item-active:rotate-90 size-5 shrink-0 transition-transform duration-300 rtl:rotate-180" ></span>
                        LaTeX crudo
                    </button>
                    <div id="payment-arrow-collapse" class="accordion-content w-full overflow-hidden transition-[height] duration-300" aria-labelledby="payment-arrow" role="region">
                        <div class="px-5 pb-4">
                            <p class="text-sm text-neutral font-normal">
                                {value}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
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