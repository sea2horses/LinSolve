<script lang="ts">
    import Icon from "@iconify/svelte";
    import { type Variable, VariableType } from "./VariableControl";
	import VariableInput from "./VariableInput.svelte";

    let variables: Variable[] = $state([]);

    let selected_var: number | null = $state(null);

    export function get(): Variable[] {
        return variables
    }

    const selectVar = (i: number) => {
        selected_var = i;
    }

    $inspect(variables)
    $inspect(selected_var)

    const addVar = () => {
        variables.push(
            {
                name: '?',
                type: null,
                value: null
            }
        )
    }
</script>

<div id="variable-control" class="grid grid-cols-[1fr_2fr] border border-base-200 max-w-[700px]">
    <!-- Variables -->
    <div id="variable-cc" class="grid grid-rows-[100px_1fr] border-r border-base-200">
        <div class="w-full h-auto p-5 border-b border-base-200">
            <p class="text-sm">Variables</p>
            <button class="btn btn-soft btn-primary text-sm" onclick={addVar}>
                <Icon icon="ic:baseline-plus"/> Añadir
            </button>
        </div>
        <div class="w-full h-auto p-2">
            {#each variables as variable, i}
                <button class="w-full flex gap-2 hover:bg-neutral/5 p-2 ease-in-out duration-100" onclick={() => {
                    selectVar(i)
                }}>
                    <div class="flex-center">
                        {#if variable.type == VariableType.MATRIX}
                            <div class="p-2 bg-[#132240] rounded-xs">
                                <Icon icon="ic:outline-window" class="text-[#9dbffd]"/>
                            </div>
                        {:else if variable.type == VariableType.VECTOR}
                            <div class="p-2 bg-[#0a343c] rounded-xs">
                                <Icon icon="mdi:vector-line" class="text-[#c0ffff]"/>
                            </div>
                        {:else if variable.type == VariableType.EXPRESSION}
                            <div class="p-2 bg-[#272744] rounded-xs">
                                <Icon icon="mdi:function" class="text-[#c2ccff]"/>
                            </div>
                        {:else}
                            <div class="p-2 bg-[#272727] rounded-xs">
                                <Icon icon="mingcute:question-fill" class="text-white"/>
                            </div>
                        {/if}
                    </div>
                    <div class="text-left">
                        <p class="text-sm">{variable.name}</p>
                        <p class="text-xs opacity-60">
                            {#if variable.type}
                                {variable.type}
                            {:else}
                                No elegido
                            {/if}
                        </p>
                    </div>
                </button>
            {/each}
        </div>
    </div>

    <div id="variableInput" class="p-5">
        {#each variables as variable, i}
            <VariableInput bind:value={variables[i]} className={selected_var === i ? '' : 'hidden'}/>
        {/each}
    </div>
</div>