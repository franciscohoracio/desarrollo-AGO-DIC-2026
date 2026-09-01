"""
=============================================================================
🍇 MICROSERVICIO GRAPHQL: Consultas a la Carta y Solución a Over/Under-fetching
=============================================================================
Materia: Desarrollo de Proyectos de Software · UAdeC — Facultad de Sistemas
Tema 2.3: Interfaces de Comunicación y APIs

Conceptos Clave Demostrados:
1. El Menú 'A la Carta': El cliente define la forma exacta de la respuesta.
2. Eliminación del Over-fetching: No descargamos campos pesados innecesarios.
3. Eliminación del Under-fetching: Datos anidados (Alumno + Materias) en 1 sola llamada.
4. Esquema Tipado (Types, Queries, Mutations, Resolvers).
5. Punto de entrada único (/graphql) y Playground Interactivo GraphiQL.
=============================================================================
"""

import os
from typing import List, Optional
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =============================================================================
# BASE DE DATOS EN MEMORIA (SIMULADA CON DATOS PESADOS Y RELACIONES)
# =============================================================================
SUBJECTS_CATALOG = {
    "DPS-2026": {"codigo": "DPS-2026", "nombre": "Desarrollo de Proyectos de Software", "profesor": "Dr. Francisco Ramos", "creditos": 5},
    "AS-2026": {"codigo": "AS-2026", "nombre": "Administración de Servidores", "profesor": "Dr. Francisco Ramos", "creditos": 5},
    "BD-2026": {"codigo": "BD-2026", "nombre": "Bases de Datos Avanzadas", "profesor": "M.C. Elena Soto", "creditos": 4},
    "REDES-2026": {"codigo": "REDES-2026", "nombre": "Redes de Computadoras", "profesor": "Ing. Roberto Garza", "creditos": 4}
}

STUDENTS_DATA = {
    "12345": {
        "matricula": "12345",
        "nombre": "Carlos Gómez",
        "carrera": "Ingeniería en Sistemas Computacionales",
        "email": "carlos.gomez@uadec.mx",
        "semestre": 7,
        "promedio": 94.5,
        "direccion": "Av. Universidad #400, Colonia Valle, Saltillo, Coahuila",
        "curp": "GOMC020315HCLRR01",
        "telefono_emergencia": "+52 (844) 123-4567",
        "historial_medico_alergias": "Penicilina, Polvo",
        "materias": [
            {"codigo": "DPS-2026", "calificacion": 95.0},
            {"codigo": "AS-2026", "calificacion": 92.0}
        ]
    },
    "67890": {
        "matricula": "67890",
        "nombre": "Ana Morales",
        "carrera": "Licenciatura en Tecnologías de Información",
        "email": "ana.morales@uadec.mx",
        "semestre": 5,
        "promedio": 98.2,
        "direccion": "Calle Hidalgo #120, Zona Centro, Ramos Arizpe, Coahuila",
        "curp": "MORA030822MCLRR04",
        "telefono_emergencia": "+52 (844) 987-6543",
        "historial_medico_alergias": "Ninguna",
        "materias": [
            {"codigo": "DPS-2026", "calificacion": 98.0},
            {"codigo": "BD-2026", "calificacion": 100.0}
        ]
    },
    "11223": {
        "matricula": "11223",
        "nombre": "Luis Hernández",
        "carrera": "Ingeniería en Sistemas Computacionales",
        "email": "luis.hernandez@uadec.mx",
        "semestre": 9,
        "promedio": 83.0,
        "direccion": "Blvd. Venustiano Carranza #2500, Saltillo, Coahuila",
        "curp": "HERL010110HCLRR09",
        "telefono_emergencia": "+52 (844) 555-1122",
        "historial_medico_alergias": "Aspirina",
        "materias": [
            {"codigo": "DPS-2026", "calificacion": 85.0}
        ]
    }
}

# =============================================================================
# DEFINICIÓN DE TIPOS GRAPHQL (SCHEMA TYPING CON STRAWBERRY)
# =============================================================================
@strawberry.type(description="Materia universitaria cursada por un alumno")
class Subject:
    codigo: str
    nombre: str
    profesor: str
    creditos: int
    calificacion: Optional[float] = None

@strawberry.type(description="Entidad Alumno con campos ligeros y pesados")
class Student:
    matricula: str
    nombre: str
    carrera: str
    email: str
    semestre: int
    promedio: float
    # Campos pesados (que en REST siempre se descargaban y aquí solo si los pides):
    direccion: str
    curp: str
    telefono_emergencia: str
    historial_medico_alergias: str

    @strawberry.field(description="Resolver para obtener las materias y profesores asociados")
    def materias(self) -> List[Subject]:
        """
        Resuelve las materias asociadas.
        ¡Solución a Under-fetching: une alumno + catálogo de materias en 1 sola consulta!
        """
        student_raw = STUDENTS_DATA.get(self.matricula, {})
        enrolled = student_raw.get("materias", [])
        
        result = []
        for item in enrolled:
            code = item["codigo"]
            cat = SUBJECTS_CATALOG.get(code, {
                "codigo": code, 
                "nombre": "Materia Desconocida", 
                "profesor": "Por Asignar", 
                "creditos": 0
            })
            result.append(
                Subject(
                    codigo=cat["codigo"],
                    nombre=cat["nombre"],
                    profesor=cat["profesor"],
                    creditos=cat["creditos"],
                    calificacion=item.get("calificacion", 0.0)
                )
            )
        return result

# =============================================================================
# QUERIES (CONSULTAS DE LECTURA)
# =============================================================================
@strawberry.type
class Query:
    @strawberry.field(description="Obtiene la lista completa de estudiantes")
    def students(self) -> List[Student]:
        students_list = []
        for data in STUDENTS_DATA.values():
            students_list.append(Student(
                matricula=data["matricula"],
                nombre=data["nombre"],
                carrera=data["carrera"],
                email=data["email"],
                semestre=data["semestre"],
                promedio=data["promedio"],
                direccion=data["direccion"],
                curp=data["curp"],
                telefono_emergencia=data["telefono_emergencia"],
                historial_medico_alergias=data["historial_medico_alergias"]
            ))
        return students_list

    @strawberry.field(description="Busca a un estudiante por su matrícula")
    def student(self, matricula: str) -> Optional[Student]:
        data = STUDENTS_DATA.get(matricula)
        if not data:
            return None
        return Student(
            matricula=data["matricula"],
            nombre=data["nombre"],
            carrera=data["carrera"],
            email=data["email"],
            semestre=data["semestre"],
            promedio=data["promedio"],
            direccion=data["direccion"],
            curp=data["curp"],
            telefono_emergencia=data["telefono_emergencia"],
            historial_medico_alergias=data["historial_medico_alergias"]
        )

    @strawberry.field(description="Lista de materias disponibles en el catálogo universitario")
    def subjects(self) -> List[Subject]:
        return [
            Subject(
                codigo=s["codigo"],
                nombre=s["nombre"],
                profesor=s["profesor"],
                creditos=s["creditos"],
                calificacion=None
            )
            for s in SUBJECTS_CATALOG.values()
        ]

# =============================================================================
# MUTATIONS (OPERACIONES DE ESCRITURA / MODIFICACIÓN)
# =============================================================================
@strawberry.type
class Mutation:
    @strawberry.mutation(description="Inscribe a un alumno en una materia nueva")
    def enroll_student(self, matricula: str, codigo_materia: str, calificacion: float = 0.0) -> Optional[Student]:
        if matricula not in STUDENTS_DATA:
            raise Exception(f"No existe el alumno con matrícula '{matricula}'")
        if codigo_materia not in SUBJECTS_CATALOG:
            raise Exception(f"La materia con código '{codigo_materia}' no existe en el catálogo.")
        
        student = STUDENTS_DATA[matricula]
        # Evitar duplicados
        for m in student["materias"]:
            if m["codigo"] == codigo_materia:
                m["calificacion"] = calificacion
                break
        else:
            student["materias"].append({"codigo": codigo_materia, "calificacion": calificacion})
        
        return Student(
            matricula=student["matricula"],
            nombre=student["nombre"],
            carrera=student["carrera"],
            email=student["email"],
            semestre=student["semestre"],
            promedio=student["promedio"],
            direccion=student["direccion"],
            curp=student["curp"],
            telefono_emergencia=student["telefono_emergencia"],
            historial_medico_alergias=student["historial_medico_alergias"]
        )

# =============================================================================
# APLICACIÓN FASTAPI Y RUTAS DE GRAPHQL (GRAPHIQL PLAYGROUND)
# =============================================================================
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(
    title="🍇 Campus GraphQL Service",
    description="Microservicio GraphQL para consultas flexibles y eficientes.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")

@app.get("/", tags=["General"])
def root():
    return {
        "service": "GraphQL Campus Service",
        "playground_url": "/graphql",
        "description": "Visita /graphql en tu navegador para abrir el explorador interactivo GraphiQL."
    }

@app.get("/health", tags=["General"])
def health():
    return {"status": "healthy", "service": "graphql_api"}
