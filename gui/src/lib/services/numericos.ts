import { callPyFunc } from '$lib/eel';

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
) => {
	return callPyFunc<string>('biseccion', funcion, clean(a), clean(b), clean(tolerancia), maxIter);
};

export const metodoReglaFalsa = async (
	funcion: string,
	a: string,
	b: string,
	tolerancia: string,
	maxIter: number
) => {
	return callPyFunc<string>('regla_falsa', funcion, clean(a), clean(b), clean(tolerancia), maxIter);
};

export const metodoNewtonRaphson = async (
	funcion: string,
	x0: string,
	tolerancia: string,
	maxIter: number
) => {
	return callPyFunc<string>('newton_raphson', funcion, clean(x0), clean(tolerancia), maxIter);
};

export const metodoSecante = async (
	funcion: string,
	x0: string,
	x1: string,
	tolerancia: string,
	maxIter: number
) => {
	return callPyFunc<string>('secante', funcion, clean(x0), clean(x1), clean(tolerancia), maxIter);
};
