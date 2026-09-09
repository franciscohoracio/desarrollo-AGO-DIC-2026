# 🏭 Práctica 3.1: Integración Continua (CI) y Pipelines Automatizados con GitHub Actions

![CI Pipeline](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=githubactions&logoColor=white)
![Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Quality Gate](https://img.shields.io/badge/quality--gate-85%25%20min-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)

> **Materia:** Desarrollo de Proyectos de Software  
> **Institución:** Universidad Autónoma de Coahuila (UAdeC) — Facultad de Sistemas  
> **Unidad 3:** DevOps, GitOps y Automatización de Despliegues  
> **Tema 3.1:** Integración Continua (CI)  
> **Nivel:** Principiante / Intermedio  

---

## 🎯 Objetivo Didáctico

Comprender, implementar y experimentar de primera mano los fundamentos de la **Integración Continua (CI)** a través de una aplicación real de gestión académica y becas escolares (`school-service`), aprendiendo a:

1. **Eliminar el «Infierno de la Integración»:** Sustituir la peligrosa costumbre de unir código a última hora por integraciones pequeñas, frecuentes y automáticas.
2. **Construir la Banda de Ensamblaje (Pipeline):** Diseñar pipelines declarativos en **GitHub Actions** (`.github/workflows/ci.yml`) con disparadores, runners limpios y pasos ordenados.
3. **Aplicar los 4 Inspectores de Calidad:**
   * **Formateador Automático (`Black`):** Cero discusiones de estilo en el equipo (espacios vs tabs).
   * **Linter y Análisis Estático (`Flake8`):** El corrector ortográfico que detecta variables huérfanas, imports muertos y errores antes de ejecutar el código.
   * **Pruebas Unitarias Automáticas (`Pytest`):** Eliminación total del *«efecto dominó»* (romper lo que ya servía).
   * **Medidor de Cobertura y Quality Gate (`Pytest-Cov`):** Bloqueo automático si el código nuevo no alcanza el **85%** de cobertura mínima.
4. **Blindar Secretos (`GitHub Secrets`):** Inyección segura de credenciales y llaves de API en memoria sin quemar contraseñas en Git.
5. **Proteger la Rama Principal (`main`):** Flujo profesional basado en ramas de características (`feature branches`), **Pull Requests (PR)** y validación doble obligatoria (Robot de CI verde ✅ + Aprobación de un compañero 👤).

---

## 💡 Las Dos Grandes Analogías Didácticas

### 🍽️ 1. La Analogía de los Trastes Sucios
> *«Integrar código es como lavar los platos: si lavas tu plato inmediatamente después de comer, te toma 30 segundos. Si dejas acumular los platos sucios de 4 roomies durante 2 semanas, el domingo por la noche la cocina será un desastre pestilente, con platos rotos y peleas entre todos.»*
> 
> En software pasa lo mismo: trabajar en aislamiento durante semanas provoca el temido **Integration Hell** (80 conflictos de Git a las 11 PM antes de la entrega). CI resuelve esto integrando código varias veces al día.

### 🚗 2. La Analogía de la Fábrica Automotriz
> *«En una planta moderna de automóviles, no esperas a ensamblar 1,000 coches completos para ver si los frenos funcionan. En la banda transportadora existen sensores en cada etapa: si un tornillo tiene un milímetro de desviación, la banda se detiene al instante.»*
> 
> El **Pipeline de CI** es esa banda transportadora: cada commit es inspeccionado por sensores (Linter, Pruebas, Cobertura, Seguridad). Si algo falla, el robot detiene el proceso y bloquea el botón de `Merge`.

---

## 🏗️ Arquitectura del Pipeline de CI

```text
  ┌─────────────────────────────────────────────────────────────────────────────────────────┐
  │ 💻 DESARROLLADOR LOCAL                                                                 │
  │   1. git checkout -b feature/becas                                                      │
  │   2. Modifica código / lógica de negocio                                                │
  │   3. Prueba localmente: ./local_ci.sh (Simulador)                                       │
  │   4. git push origin feature/becas ──► Abre Pull Request (PR) a main                   │
  └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                               │ Disparador: on [push, pull_request]
                                               ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────────┐
  │ 🏭 GITHUB ACTIONS RUNNER (Máquina limpia ubuntu-latest en la nube)                       │
  │                                                                                         │
  │   [Sensor 1] 📥 Checkout del Repo + Setup Python 3.11 con Caché de Dependencias        │
  │                     │ (Descarga en segundos, reproducible)                              │
  │                     ▼                                                                   │
  │   [Sensor 2] 🔍 Formato & Linter (Black --check + Flake8)                               │
  │                     │ Atrapa variables sin usar, estilo sucio y errores tipográficos   │
  │                     ▼                                                                   │
  │   [Sensor 3] 🔒 Verificación de Secretos (GitHub Secrets)                               │
  │                     │ Inyección segura en memoria: censura con *** en logs             │
  │                     ▼                                                                   │
  │   [Sensor 4] 🧪 Pruebas Unitarias Automáticas (Pytest)                                  │
  │                     │ 37 aserciones en < 1 segundo (Evita el Efecto Dominó)            │
  │                     ▼                                                                   │
  │   [Sensor 5] 📊 Quality Gate de Cobertura (Pytest-Cov >= 85%)                           │
  │                     │ Si la cobertura cae a 84%, el pipeline TRUENA en rojo            │
  └────────────────────────────────────────────┬────────────────────────────────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
          ❌ VEREDICTO: PIPELINE EN ROJO                 ✅ VEREDICTO: PIPELINE EN VERDE
      ┌───────────────────────────────────────┐       ┌───────────────────────────────────────┐
      │ • Botón 'Merge' BLOQUEADO en GitHub   │       │ • Palomita verde en el PR (Checks OK) │
      │ • Cero código roto contamina a main   │       │ • Aprobación de 1 compañero (Review)  │
      │ • El dev corrige en su rama y reintenta│      │ • Merge a 'main' con total confianza  │
      └───────────────────────────────────────┘       │ • Badge de estado: [build: passing]   │
                                                      └───────────────────────────────────────┘
```

> 🗺️ **Diagrama Visual:** Puedes abrir e interactuar con el diagrama completo en Obsidian usando el archivo [`diagrama_practica.excalidraw.md`](diagrama_practica.excalidraw.md).

---

## 📂 Estructura de Archivos del Proyecto

```text
3.1_Practica_Integracion_Continua_CI/
├── .github/
│   └── workflows/
│       └── ci.yml                     # Pipeline oficial de GitHub Actions (Sensórica y Jobs)
├── app/                               # CÓDIGO FUENTE DE LA APLICACIÓN
│   ├── __init__.py
│   ├── main.py                        # API REST con FastAPI (Endpoints y Swagger UI)
│   └── school_service.py              # Reglas de negocio: promedios, becas y secretos
├── tests/                             # SUITE DE PRUEBAS AUTOMÁTICAS
│   ├── __init__.py
│   ├── test_school_service.py         # Pruebas unitarias de lógica pura y casos límite
│   └── test_api.py                    # Pruebas de integración HTTP con TestClient
├── .flake8                            # Configuración del linter (Largo de línea 88, exclusiones)
├── pyproject.toml                     # Configuración central de Black, Pytest y Coverage
├── requirements.txt                   # Dependencias fijadas (FastAPI, Pytest, Flake8, Black)
├── Dockerfile                         # Contenedor para levantar la app o correr CI
├── docker-compose.yml                 # Orquestación de la API (puerto 8000) y runner de CI
├── local_ci.sh                        # 🚀 Simulador local del runner de CI (Terminal interactiva)
├── simulador_escenarios.sh            # 🧪 Laboratorio de escenarios de prueba para alumnos
├── diagrama_practica.excalidraw       # Diagrama de arquitectura en formato Excalidraw JSON
├── diagrama_practica.excalidraw.md    # Wrapper del diagrama compatible con plugin de Obsidian
└── README.md                          # Esta guía didáctica maestra
```

---

## 🚀 Requisitos Previos

* **Git** instalado y configurado (`git --version`).
* **Python 3.10+** (recomendado 3.11) o **Docker Desktop**.
* Cuenta gratuita en **GitHub** para subir tu repositorio.

---

## 🛠️ Guía Paso a Paso de Ejecución

### Paso 1: Preparar el Entorno Local

Abre tu terminal en la carpeta de la práctica:

```bash
cd /Users/framos/DevOps/desarrollo-AGO-DIC-2026/3.1_Practica_Integracion_Continua_CI
```

Crea tu entorno virtual e instala las dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Paso 2: Ejecutar el Simulador Local de CI (`./local_ci.sh`)

Antes de subir cambios a GitHub, los desarrolladores profesionales prueban su pipeline localmente. Ejecuta:

```bash
./local_ci.sh
```

Verás cómo la terminal ejecuta de forma secuencial cada uno de los sensores:
1. Verificación de dependencias.
2. Formateador `Black` (revisa sangrías y comillas).
3. Linter `Flake8` (detecta variables huérfanas y errores estáticos).
4. Verificación de secretos simulados.
5. Pruebas automáticas con `Pytest` y cálculo de cobertura con `Quality Gate` (mínimo 85%).

Si todo está sano, recibirás el veredicto:  
`✅ VEREDICTO: PASSED (TODO EN VERDE)`.

---

### Paso 3: Experimentar con el Laboratorio de Escenarios (`./simulador_escenarios.sh`)

Para entender por qué el pipeline es indispensable, ejecuta el simulador interactivo:

```bash
./simulador_escenarios.sh
```

El script te ofrecerá un menú interactivo con 6 opciones:

* **[1] Camino Feliz:** Corre el pipeline en estado 100% verde y saludable.
* **[2] Bug en Pruebas (El Efecto Dominó):** Inyecta un error de regresión en el cálculo de becas y observa cómo `pytest` detiene la banda en milisegundos.
* **[3] Infracción de Linter (El Corrector Automático):** Agrega variables no usadas y código descuidado para ver cómo `flake8` y `black` rechazan el commit antes de correr pruebas.
* **[4] Caída de Cobertura (El Quality Gate):** Inyecta 30 líneas de código nuevo sin pruebas y observa cómo el Quality Gate reprueba el build aunque los tests existentes pasen.
* **[5] Manejo de Secretos:** Muestra qué ocurre cuando falta una clave privada requerida por la aplicación.
* **[6] Restaurar Proyecto:** Limpia cualquier alteración y devuelve el código al estado verde.

---

### Paso 4: Levantar la API y Explorar Swagger UI (Opcional)

Si deseas probar la aplicación web funcionando en vivo:

```bash
# Opción A: Con Python local
uvicorn app.main:app --reload --port 8000

# Opción B: Con Docker Compose
docker compose up -d school_api
```

Abre tu navegador en: **[http://localhost:8000/docs](http://localhost:8000/docs)**  
Podrás interactuar con los endpoints de cálculo de promedios, becas, descuentos de inscripción y la auditoría con secreto.

---

## 🌐 Práctica en la Nube: Configurar GitHub Actions en tu Repositorio

Para vivir la experiencia real de trabajo en equipo en la industria, sigue estos pasos:

### 1. Inicializar o subir el proyecto a GitHub
Crea un repositorio en tu cuenta de GitHub (ej. `practica-ci-uadec`) y sube el contenido:

```bash
git init
git add .
git commit -m "feat: inicializar proyecto escolar con pipeline de CI"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

En cuanto hagas `push`, ve a la pestaña **Actions** en tu repositorio de GitHub: ¡verás a tu robot de CI despertando y ejecutando el workflow automáticamente!

---

### 2. Configurar el Secreto en GitHub (`GitHub Secrets`)

> 🔒 **Regla Inviolable:** ¡Nunca subas contraseñas a Git!

1. En tu repositorio de GitHub, ve a **Settings** ➔ **Secrets and variables** ➔ **Actions**.
2. Haz clic en el botón verde **"New repository secret"**.
3. Configura:
   * **Name:** `ACADEMIC_AUDIT_KEY`
   * **Secret:** `UAdeC-CI-SECRET-KEY-2026`
4. Haz clic en **"Add secret"**.  
   *Nota que nadie (ni tú) podrá volver a ver la clave en texto plano; GitHub la almacena cifrada con algoritmo asimétrico.*

---

### 3. Proteger la Rama `main` (Branch Protection Rules)

Para asegurar que **nadie pueda subir código roto directo a producción**:

1. En GitHub, ve a **Settings** ➔ **Branches**.
2. En **Branch protection rules**, haz clic en **"Add branch protection rule"** (o "Add rule").
3. En **Branch name pattern**, escribe: `main`.
4. Activa las siguientes casillas:
   * ✅ **Require a pull request before merging:** Nadie hace push directo a main; todos deben abrir un PR.
   * ✅ **Require status checks to pass before merging:** Busca y selecciona el check del pipeline: `🏭 Control de Calidad y Pruebas Automáticas`.
   * ✅ **Do not allow bypassing the above settings:** Aplica las reglas incluso para administradores.
5. Haz clic en **Save changes**.

---

### 4. El Flujo Profesional de Trabajo: Crear una Feature Branch y un Pull Request

Simulemos el día a día de un ingeniero de software:

```bash
# 1. Crear una rama de función para una nueva característica
git checkout -b feature/regla-becas-deportivas

# 2. Hacer un cambio (por ejemplo, agregar una prueba o ajustar documentación)
# 3. Guardar el commit
git commit -am "feat: documentar nueva regla de apoyo académico"

# 4. Subir la rama a GitHub
git push origin feature/regla-becas-deportivas
```

5. Ve a GitHub y haz clic en **"Compare & pull request"**.
6. Observa cómo en la parte inferior del PR aparece:  
   *`Some checks haven't completed yet...`*  
   El robot de CI está corriendo.
7. Al terminar, si el código está limpio, el check se pintará de **verde ✅**.
8. Si algún linter o test falla, se pintará de **rojo ❌** y el botón **"Merge pull request" quedará completamente deshabilitado**.

---

### 5. Colocar la Medalla de Calidad (Badge de CI) en tu README

1. En tu repositorio de GitHub, ve a la pestaña **Actions**.
2. Selecciona el workflow **"Pipeline de Integración Continua (CI)"** en la barra lateral izquierda.
3. Haz clic en el menú de tres puntos (`...`) en la esquina superior derecha y selecciona **"Create status badge"**.
4. Copia el código Markdown generado y pégalo al inicio de tu `README.md`:

```markdown
![CI Pipeline](https://github.com/TU_USUARIO/TU_REPOSITORIO/actions/workflows/ci.yml/badge.svg)
```

¡Ahora tu repositorio lucirá un badge en verde brillante que certifica su calidad técnica ante cualquier reclutador o profesor!

---

## 🧠 Retos Didácticos para el Estudiante

### Reto 1: Desarrollo Guiado por Pruebas (TDD) para Becas Deportivas 🏅
Aplica el ciclo *Red-Green-Refactor*:
1. Escribe primero una prueba en `tests/test_school_service.py` para una nueva función `determinar_beca_deportiva(disciplina, es_seleccionado_estatal)`. La prueba debe verificar que si es seleccionado estatal, recibe 60% de beca.
2. Ejecuta `./local_ci.sh` y observa cómo el pipeline truena en **ROJO ❌** porque la función aún no existe (*Red*).
3. Implementa la función en `app/school_service.py` con el código mínimo para pasar la prueba (*Green*).
4. Vuelve a ejecutar `./local_ci.sh` y comprueba que regrese a **VERDE ✅**.

### Reto 2: Elevar el Quality Gate al 95% 📈
1. Abre `pyproject.toml` y el workflow `.github/workflows/ci.yml`.
2. Modifica el umbral de cobertura para exigir un mínimo de **95%** (`--cov-fail-under=95`).
3. Agrega código nuevo en `app/school_service.py` y verifica que el pipeline te obligue a escribir pruebas para cubrir todas las ramas condicionales (`if/else`).

### Reto 3: Auditoría y Detección de Secretos Expuestos 🕵️
1. Intenta simular el error de un compañero descuidado: escribe una cadena con aspecto de contraseña (`API_KEY = "sk-live-1234567890abcdef"`) dentro de `app/school_service.py`.
2. Investiga e integra la herramienta gratuita `trufflehog` o `gitleaks` en el paso de seguridad de `.github/workflows/ci.yml` para que el pipeline detecte credenciales quemadas y detenga el build antes de que se suban a la nube.

---

## 🛡️ Guía de Supervivencia: Los 5 Errores Típicos en CI

| Error de Novato | ¿Por qué es muy peligroso? | ¿Cómo se soluciona en la industria? |
|---|---|---|
| **1. Ignorar builds en rojo** | Si dejas la rama `main` en rojo, nadie sabe si su nuevo cambio rompió algo o si ya estaba roto. | Arreglar un build roto es la **prioridad #1** de todo el equipo de desarrollo. |
| **2. Subir commits gigantes (>2000 líneas)** | Imposible hacer Code Review y dificulta encontrar el origen de una falla. | Commits pequeños, atómicos y frecuentes (10 a 50 líneas por commit). |
| **3. Quemar contraseñas en Git** | Bots maliciosos escanean GitHub 24/7 y vacían tarjetas o roban bases de datos en segundos. | Usar siempre **GitHub Secrets** y variables de entorno (`.env` en `.gitignore`). |
| **4. Pipelines eternos (>20 minutos)** | Desespera al equipo, retrasa entregas y fomenta saltarse las revisiones. | Usar caché de dependencias (`cache: 'pip'`) y mantener pruebas unitarias en memoria. |
| **5. Pruebas que dependen de internet** | Si la API externa se cae o el WiFi está lento, el pipeline falla falsamente (*Flaky Tests*). | Usar Mocks (`unittest.mock`) o datos simulados locales para que las pruebas sean 100% aisladas. |

---

## 💡 Conceptos Clave para Recordar

* **CI es tu copiloto automático:** En cada `git push`, una máquina limpia en la nube descarga, compila y prueba tu software sin intervención humana.
* **El runner no miente:** Si el código falla en CI pero jalaba en tu laptop, significa que en tu máquina funcionaba "de casualidad" por archivos o paquetes locales no documentados.
* **La regla de los 5 minutos:** Un pipeline ideal de CI debe ofrecer retroalimentación en menos de 5 a 7 minutos.
* **Doble validación en Pull Requests:** Ningún código entra a la rama protegida sin dos sellos: la palomita verde del robot de CI y el visto bueno de un colega humano.

---

## 📋 Rúbrica de Evaluación para el Docente

| Criterio | Ponderación | Excelente (100%) | Aceptable (70%) | Insuficiente (0-50%) |
|---|:---:|---|---|---|
| **Ejecución del Pipeline Local** | 25% | Ejecuta `./local_ci.sh` sin errores; comprende el propósito de cada sensor (Black, Flake8, Pytest). | Ejecuta el script pero requiere ayuda para interpretar los fallos del linter. | No logra ejecutar el simulador local o ignora los pasos de formateo. |
| **Comprensión de Escenarios Didácticos** | 25% | Experimenta con `./simulador_escenarios.sh`, provocando y explicando fallos de linter, tests y Quality Gate. | Ejecuta algunos escenarios pero confunde el rol del linter con las pruebas unitarias. | No demuestra comprensión del efecto dominó ni del Quality Gate. |
| **GitHub Actions & Ramas Protegidas** | 30% | Workflow configurado en GitHub, rama `main` protegida, apertura de Pull Request con checks automáticos en verde. | Pipeline configurado en GitHub pero sin protección de rama `main` o con merge forzado. | Repositorio sin Actions configurado o con commits directos sobre `main` en rojo. |
| **Manejo Seguro de Secretos & Badges** | 20% | Secreto `ACADEMIC_AUDIT_KEY` inyectado en GitHub Secrets sin credenciales expuestas en código; Badge en README. | Badge colocado pero el manejo de secretos está incompleto o con valores hardcodeados. | Contraseñas quemadas en texto plano dentro del repositorio de Git. |

---

*Desarrollo de Proyectos de Software · Universidad Autónoma de Coahuila (UAdeC) — Facultad de Sistemas*
