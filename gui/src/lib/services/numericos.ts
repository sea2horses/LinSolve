import { callPyFunc } from '$lib/eel';

export type MetodoResultado = {
	latex: string;
	raiz: number | null;
	f_raiz: number | null;
	converge: boolean;
	iteraciones: number;
};

const clean = (value: string | number): string => {
	const asString = `${value ?? ''}`.trim();
	return asString.length ? asString : '0';
};

export const metodoBiseccion = async (
	funcion: string,
	a: string,
	b: string,
	tolerancia: string,
	maxIter: number
): Promise<MetodoResultado> => {
	return callPyFunc<MetodoResultado>('biseccion', funcion, clean(a), clean(b), clean(tolerancia), maxIter);
};

export const metodoReglaFalsa = async (
	funcion: string,
	a: string,
	b: string,
	tolerancia: string,
	maxIter: number
): Promise<MetodoResultado> => {
	return callPyFunc<MetodoResultado>('regla_falsa', funcion, clean(a), clean(b), clean(tolerancia), maxIter);
};

export const metodoNewtonRaphson = async (
	funcion: string,
	x0: string,
	tolerancia: string,
	maxIter: number
): Promise<MetodoResultado> => {
	return callPyFunc<MetodoResultado>('newton_raphson', funcion, clean(x0), clean(tolerancia), maxIter);
};

export const metodoSecante = async (
	funcion: string,
	x0: string,
	x1: string,
	tolerancia: string,
	maxIter: number
): Promise<MetodoResultado> => {
	return callPyFunc<MetodoResultado>('secante', funcion, clean(x0), clean(x1), clean(tolerancia), maxIter);
};
