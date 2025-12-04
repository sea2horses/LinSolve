import { callPyFunc } from '$lib/eel';

export type MatrixSpec = {
	rows: number;
	columns: number;
	values: string[][];
};

export type VectorSpec = {
	dimension: number;
	values: string[];
};

const normalizeMatrix = ({ rows, columns, values }: MatrixSpec): string[][] => {
	const matrix = Array.from({ length: rows }, (_, i) => {
		const row = values?.[i] ? [...values[i]] : [];
		while (row.length < columns) row.push('');
		if (row.length > columns) row.length = columns;
		return row.map((cell) => (cell && `${cell}`.trim().length ? `${cell}` : '0'));
	});
	return matrix;
};

const normalizeVector = ({ dimension, values }: VectorSpec): string[] => {
	const vector = Array.from({ length: dimension }, (_, i) => {
		const cell = values?.[i];
		return cell && `${cell}`.trim().length ? `${cell}` : '0';
	});
	return vector;
};

export const sumarMatrices = async (a: MatrixSpec, b: MatrixSpec): Promise<string> => {
	return callPyFunc('sumar_matrices', normalizeMatrix(a), normalizeMatrix(b));
};

export const restarMatrices = async (a: MatrixSpec, b: MatrixSpec): Promise<string> => {
	return callPyFunc('restar_matrices', normalizeMatrix(a), normalizeMatrix(b));
};

export const multiplicarMatrices = async (a: MatrixSpec, b: MatrixSpec): Promise<string> => {
	return callPyFunc('multiplicar_matrices', normalizeMatrix(a), normalizeMatrix(b));
};

export const determinanteCofactores = async (m: MatrixSpec): Promise<string> => {
	return callPyFunc('determinante_cofactores', normalizeMatrix(m));
};

export const determinanteSarrus = async (m: MatrixSpec): Promise<string> => {
	return callPyFunc('determinante_sarrus', normalizeMatrix(m));
};

export const sumarVectores = async (a: VectorSpec, b: VectorSpec): Promise<string> => {
	return callPyFunc('sumar_vectores', normalizeVector(a), normalizeVector(b));
};

export const restarVectores = async (a: VectorSpec, b: VectorSpec): Promise<string> => {
	return callPyFunc('restar_vectores', normalizeVector(a), normalizeVector(b));
};

export const escalarVector = async (vector: VectorSpec, escalar: string): Promise<string> => {
	return callPyFunc('escalar_vector', normalizeVector(vector), escalar && escalar.trim().length ? escalar : '0');
};

export const matrizPorVector = async (matriz: MatrixSpec, vector: VectorSpec): Promise<string> => {
	return callPyFunc('matriz_por_vector', normalizeMatrix(matriz), normalizeVector(vector));
};

export const combinacionLineal = async (
	vectores: VectorSpec[],
	resultado: VectorSpec
): Promise<string> => {
	return callPyFunc(
		'combinacion_lineal_vectores',
		vectores.map((v) => normalizeVector(v)),
		normalizeVector(resultado)
	);
};

export const dependenciaLineal = async (vectores: VectorSpec[]): Promise<string> => {
	return callPyFunc(
		'dependencia_lineal_vectores',
		vectores.map((v) => normalizeVector(v))
	);
};

export const resolverCramer = async (
	coeficientes: MatrixSpec,
	resultados: VectorSpec
): Promise<string> => {
	return callPyFunc(
		'resolver_cramer',
		normalizeMatrix(coeficientes),
		normalizeVector(resultados)
	);
};
