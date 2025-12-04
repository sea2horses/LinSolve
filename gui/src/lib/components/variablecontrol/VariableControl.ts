export enum VariableType {
    MATRIX = "Matriz",
    VECTOR = "Vector",
    EXPRESSION = "Expresión"
}

export type Variable = {
    name: string,
    type: VariableType | null,
    value: string[][] | string[] | string | null
}