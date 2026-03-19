# Galleguimetro Frontend

Este es el frontend del proyecto Galleguimetro, una aplicación web para el análisis de opciones financieras en tiempo real.

## Características

- Dashboard con visualización de portfolios y opciones
- Gestión completa de portfolios y posiciones
- Cálculo y visualización de griegas (delta, gamma, theta, vega, rho)
- Integración con TradingView para gráficos financieros
- Autenticación de usuarios con JWT
- Actualizaciones en tiempo real mediante WebSocket
- Interfaz responsiva con Material-UI

## Tecnologías Utilizadas

- **React 18**: Biblioteca principal para la construcción de la interfaz
- **TypeScript**: Para tipado estático y mejor desarrollo
- **Material-UI**: Componentes de UI de Google
- **Redux Toolkit**: Gestión de estado
- **React Router**: Navegación entre páginas
- **Axios**: Cliente HTTP para comunicación con el backend
- **Recharts**: Biblioteca para gráficos
- **TradingView Widget**: Integración de gráficos financieros

## Estructura del Proyecto

```
frontend/
├── public/                 # Archivos públicos
│   ├── index.html         # HTML principal
│   └── favicon.ico        # Icono de la aplicación
├── src/                   # Código fuente
│   ├── components/        # Componentes reutilizables
│   │   └── TradingViewChart.tsx
│   ├── pages/             # Páginas de la aplicación
│   │   ├── AuthPage.tsx
│   │   ├── Dashboard.tsx
│   │   ├── OptionsPage.tsx
│   │   └── PortfolioPage.tsx
│   ├── services/          # Servicios API
│   │   └── api.ts
│   ├── store/             # Store de Redux
│   │   ├── authSlice.ts
│   │   ├── index.ts
│   │   ├── optionsSlice.ts
│   │   ├── portfolioSlice.ts
│   │   └── store.ts
│   ├── types/             # Definiciones de TypeScript
│   │   ├── auth.ts
│   │   ├── options.ts
│   │   └── portfolio.ts
│   ├── App.tsx            # Componente principal
│   ├── index.tsx          # Punto de entrada
│   ├── index.css          # Estilos globales
│   └── tsconfig.json      # Configuración de TypeScript
├── package.json           # Dependencias y scripts
└── README.md             # Este archivo
```

## Instalación

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd galleguimetro/frontend
```

2. Instala las dependencias:
```bash
npm install
```

3. Inicia la aplicación:
```bash
npm start
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:3000`.

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto para configurar las variables de entorno:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

## Scripts Disponibles

- `npm start`: Inicia el servidor de desarrollo
- `npm build`: Construye la aplicación para producción
- `npm test`: Ejecuta las pruebas
- `npm eject`: Expulsa de Create React App (no recomendado)

## Endpoints de la API

La aplicación se comunica con el backend a través de los siguientes endpoints:

### Autenticación
- `POST /api/auth/login`: Iniciar sesión
- `POST /api/auth/register`: Registrar usuario

### Portfolios
- `GET /api/portfolios`: Obtener todos los portfolios
- `POST /api/portfolios`: Crear nuevo portfolio
- `PUT /api/portfolios/:id`: Actualizar portfolio
- `DELETE /api/portfolios/:id`: Eliminar portfolio
- `POST /api/portfolios/:id/sync`: Sincronizar con Excel

### Opciones
- `GET /api/options`: Obtener todas las opciones
- `POST /api/options`: Crear nueva opción
- `PUT /api/options/:id`: Actualizar opción
- `DELETE /api/options/:id`: Eliminar opción
- `POST /api/options/calculate-greeks`: Calcular griegas

## Contribución

1. Haz un fork del proyecto
2. Crea tu rama de características (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -am 'Añade nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT - ver el archivo LICENSE para más detalles.