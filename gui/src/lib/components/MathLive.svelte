<script lang="ts">
	import 'mathlive/fonts.css';
	import 'mathlive';
	import type { MathfieldElement, MathfieldElementAttributes } from 'mathlive';
	import { on } from 'svelte/events';

	type Props = { value?: string; disabled?: boolean, className?: string } & Partial<MathfieldElementAttributes>;

	let { value = $bindable(), disabled = false, className = "", ...rest }: Props = $props();

	const init = (node: MathfieldElement) => {
		$effect(() => {
			if (value) node.value = value;
		});
		$effect(() => {
			return on(node, 'input', () => {
				value = node.value;
			});
		});
		// Prevent the default behavior for '\' and 'Escape' keys
		const handleKeydown = (ev: KeyboardEvent) => {
			if (ev.key === "\\" || ev.key === "Escape") {
				ev.preventDefault();
			}
		};

		// Add the event listener with capture set to true
		node.addEventListener("keydown", handleKeydown, { capture: true });
	}
</script>

<math-field use:init {...rest} class="block w-full text-md {className}" {disabled}></math-field>
<style>
	math-field::part(menu-toggle) {
		display: none;
	}
</style>
