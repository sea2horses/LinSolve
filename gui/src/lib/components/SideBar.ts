export type MenuItem = { name: string; href: string; icon: string };
export type Category = { name: string; items: (MenuItem | Category)[] };

export const SideBarWidth: number = 300;

export const SidebarItems: (MenuItem | Category)[] = [
    { name: 'Inicio', href: '/', icon: 'tabler:home' },
    {
        name: 'Metodos numericos',
        items: [
            { name: 'Raices de ecuaciones', href: '/metodos-numericos', icon: 'mdi:chart-bell-curve' }
        ]
    },
    { name: 'Graficador', href: '/graficador', icon: 'tabler:chart-line' },
    {
        name: 'Matrices',
        items: [
            { name: 'Suma', href: '/matrices#suma', icon: 'tabler:sum' },
            { name: 'Resta', href: '/matrices#resta', icon: 'gg:math-minus' },
            { name: 'Multiplicacion', href: '/matrices#multiplicacion', icon: 'mdi:multiply' },
            {
                name: 'Determinante',
                items: [
                    { name: 'Cofactores', href: '/matrices#det-cof', icon: 'mdi:multiply' },
                    { name: 'Sarrus', href: '/matrices#det-sarrus', icon: 'mdi:multiply' }
                ]
            }
        ]
    },
    {
        name: 'Vectores',
        items: [
            { name: 'Suma', href: '/vectores#suma', icon: 'tabler:sum' },
            { name: 'Resta', href: '/vectores#resta', icon: 'gg:math-minus' },
            { name: 'Escalar', href: '/vectores#escalar', icon: 'mdi:multiplication' },
            { name: 'Matriz x vector', href: '/vectores#matriz-vector', icon: 'mdi:matrix' }
        ]
    },
    {
        name: 'Sistemas Lineales',
        items: [
            { name: 'Gauss-Jordan', href: '/gauss-jordan/', icon: 'tabler:function' },
            { name: 'Cramer', href: '/cramer', icon: 'tabler:function' },
            { name: 'Combinacion Lineal', href: '/combinacion-lineal', icon: 'tabler:function' }
        ]
    },
    { name: 'Laboratorio', href: '/laboratorio', icon: 'tabler:function' },
    { name: 'Configuracion', href: '/configuracion', icon: 'tabler:settings' }
];
