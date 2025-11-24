import { callPyFunc } from "$lib/eel"

export async function EvaluateLatex(latex: string): Promise<string> {
    return callPyFunc<string>('evaluar_latex', latex)
}