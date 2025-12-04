import { callPyFunc } from "$lib/eel"

export type VarSpec = { name: string; value: string }; // value must be a JSON descriptor already

export async function EvaluateLatex(latex: string, vars?: VarSpec[]): Promise<string> {
    const payload = vars && vars.length
        ? JSON.stringify(Object.fromEntries(vars.map((v) => [v.name, JSON.parse(v.value)])))
        : undefined;
    return callPyFunc<string>('evaluar_latex', latex, payload);
}
