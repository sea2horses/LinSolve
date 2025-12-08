import { callPyFunc } from '$lib/eel';

export type Punto = { x: number; y: number };

export const graficarFuncion = async (
	expr: string,
	xMin: string,
	xMax: string,
	puntos = 200
): Promise<Punto[]> => {
	const coords = await callPyFunc<[number, number][]>('graficar_funcion', expr, xMin, xMax, puntos);
	return coords.map(([x, y]) => ({ x, y }));
};
