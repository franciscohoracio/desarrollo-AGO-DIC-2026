"""
=============================================================================
🏛️ MICROSERVICIO REST: RESTful APIs, Swagger/OpenAPI, JWT y Versionado
=============================================================================
Materia: Desarrollo de Proyectos de Software · UAdeC — Facultad de Sistemas
Tema 2.3: Interfaces de Comunicación y APIs

Conceptos Clave Demostrados:
1. Verbos HTTP y Códigos de Estado (200, 201, 400, 401, 403, 404).
2. Diseño de URLs con Sustantivos (/v1/students, /v2/students).
3. Documentación Interactiva OpenAPI / Swagger UI (/docs).
4. Seguridad con JWT (JSON Web Tokens): Header, Payload y Firma Digital.
5. Versionado de APIs para evolución sin romper aplicaciones existentes.
=============================================================================
"""

import os
import time
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# =============================================================================
# CONFIGURACIÓN DE FASTAPI Y METADATOS DE OPENAPI (SWAGGER)
# =============================================================================
app = FastAPI(
    title="🎓 Campus API · Servicio RESTful",
    description="""
API RESTful universitaria para la gestión académica.
Demuestra **Buenas Prácticas REST**, **Seguridad con JWT (OAuth 2.0 / Bearer)**, 
**Versionado de URLs (/v1 vs /v2)** y **Documentación Viva con Swagger/OpenAPI**.
    """,
    version="2.0.0",
    contact={
        "name": "Facultad de Sistemas — UAdeC",
        "url": "https://www.uadec.mx",
    }
)

# Habilitar CORS para pruebas frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD: JWT (JSON WEB TOKENS)
# =============================================================================
JWT_SECRET = os.getenv("JWT_SECRET", "super-secreto-uadec-desarrollo-2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30

security_scheme = HTTPBearer(auto_error=False)

# =============================================================================
# BASE DE DATOS EN MEMORIA (SIMULADA)
# =============================================================================
# Usuarios para autenticación (en producción usar base de datos con hash bcrypt)
USERS_DB = {
    "docente@uadec.mx": {
        "password": "password123",
        "nombre": "Dr. Francisco Ramos",
        "rol": "docente"
    },
    "alumno@uadec.mx": {
        "password": "password123",
        "nombre": "Carlos Gómez",
        "rol": "alumno"
    },
    "admin@uadec.mx": {
        "password": "admin123",
        "nombre": "Administrador General",
        "rol": "admin"
    }
}

# Estudiantes registrados
STUDENTS_DB = {
    "12345": {
        "matricula": "12345",
        "nombre": "Carlos Gómez",
        "carrera": "Ingeniería en Sistemas Computacionales",
        "email": "carlos.gomez@uadec.mx",
        "semestre": 7,
        "promedio": 94.5,
        "estado": "activo",
        "direccion": "Av. Universidad #400, Saltillo, Coahuila",
        "curp": "GOMC020315HCLRR01",
        "materias": [
            {"codigo": "DPS-2026", "nombre": "Desarrollo de Proyectos de Software", "calificacion": 95},
            {"codigo": "AS-2026", "nombre": "Administración de Servidores", "calificacion": 92}
        ]
    },
    "67890": {
        "matricula": "67890",
        "nombre": "Ana Morales",
        "carrera": "Licenciatura en Tecnologías de Información",
        "email": "ana.morales@uadec.mx",
        "semestre": 5,
        "promedio": 98.2,
        "estado": "activo",
        "direccion": "Calle Hidalgo #120, Ramos Arizpe, Coahuila",
        "curp": "MORA030822MCLRR04",
        "materias": [
            {"codigo": "DPS-2026", "nombre": "Desarrollo de Proyectos de Software", "calificacion": 98},
            {"codigo": "BD-2026", "nombre": "Bases de Datos Avanzadas", "calificacion": 100}
        ]
    },
    "11223": {
        "matricula": "11223",
        "nombre": "Luis Hernández",
        "carrera": "Ingeniería en Sistemas Computacionales",
        "email": "luis.hernandez@uadec.mx",
        "semestre": 9,
        "promedio": 83.0,
        "estado": "inactivo",
        "direccion": "Blvd. Venustiano Carranza #2500, Saltillo",
        "curp": "HERL010110HCLRR09",
        "materias": [
            {"codigo": "IS-2026", "nombre": "Ingeniería de Software", "calificacion": 85}
        ]
    }
}

# =============================================================================
# MODELOS PYDANTIC (ESQUEMAS DE DATOS Y CONTRATOS)
# =============================================================================
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="docente@uadec.mx")
    password: str = Field(..., example="password123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_info: dict

# Modelo v1 (Legacy: Formato básico tradicional sin filtros)
class StudentResponseV1(BaseModel):
    matricula: str
    nombre: str
    carrera: str
    email: str

# Modelo v2 (Moderno: Formato enriquecido con promedio, estado y auditoría)
class SubjectInfo(BaseModel):
    codigo: str
    nombre: str
    calificacion: float

class StudentResponseV2(BaseModel):
    matricula: str
    nombre: str
    carrera: str
    email: str
    semestre: int
    promedio: float
    estado: str
    materias_inscritas: int
    version_api: str = "v2"

class CreateStudentRequest(BaseModel):
    matricula: str = Field(..., min_length=4, max_length=10, example="99887")
    nombre: str = Field(..., min_length=3, example="Sofía Ramírez")
    carrera: str = Field(..., example="Ingeniería en Sistemas Computacionales")
    email: EmailStr = Field(..., example="sofia.ramirez@uadec.mx")
    semestre: int = Field(1, ge=1, le=12, example=1)
    promedio: float = Field(100.0, ge=0.0, le=100.0, example=95.0)

# =============================================================================
# FUNCIONES AUXILIARES DE SEGURIDAD (JWT)
# =============================================================================
def create_jwt_token(email: str, rol: str, nombre: str) -> str:
    """
    Genera un JSON Web Token (JWT) firmado con algoritmo HMAC-SHA256.
    El Payload contiene los 'claims' de identidad (Stateless).
    """
    issued_at = datetime.utcnow()
    expires_at = issued_at + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    
    payload = {
        "sub": email,
        "name": nombre,
        "role": rol,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp())
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)) -> dict:
    """
    Middleware / Dependencia que valida la 'Pulsera VIP' (JWT) en cada petición.
    Es STATELESS: no requiere consultar la base de datos para verificar la validez.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta la cabecera 'Authorization: Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token JWT ha expirado. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT inválido o firma digital alterada.",
            headers={"WWW-Authenticate": "Bearer"}
        )

def require_role(allowed_roles: List[str]):
    """
    Filtro de autorización basado en Roles (RBAC).
    """
    def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role", "")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: tu rol '{user_role}' no tiene permisos para esta acción (Requerido: {allowed_roles})."
            )
        return user
    return role_checker

# =============================================================================
# ENDPOINTS: INFORMACIÓN GENERAL Y SALUD
# =============================================================================
@app.get("/", tags=["General"])
def read_root():
    return {
        "message": "Bienvenido al Servicio RESTful · Práctica 2.3",
        "swagger_docs": "/docs",
        "redoc_docs": "/redoc",
        "endpoints_v1": "/v1/students",
        "endpoints_v2": "/v2/students",
        "login_endpoint": "/auth/login",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["General"])
def health_check():
    return {"status": "healthy", "service": "rest_api", "timestamp": time.time()}

# =============================================================================
# ENDPOINTS: AUTENTICACIÓN Y GENERACIÓN DE JWT (OAUTH2 / BEARER)
# =============================================================================
@app.post(
    "/auth/login", 
    response_model=TokenResponse, 
    tags=["1. Seguridad & JWT"],
    summary="Iniciar Sesión y Obtener Pulsera VIP (JWT)"
)
def login(credentials: LoginRequest):
    """
    🔐 **Inicio de Sesión**: Valida credenciales y emite un JWT firmado.
    
    Usuarios disponibles para prueba:
    * `docente@uadec.mx` (Password: `password123` | Rol: `docente`)
    * `alumno@uadec.mx` (Password: `password123` | Rol: `alumno`)
    * `admin@uadec.mx` (Password: `admin123` | Rol: `admin`)
    """
    user = USERS_DB.get(credentials.email)
    if not user or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos."
        )
    
    token = create_jwt_token(
        email=credentials.email,
        rol=user["rol"],
        nombre=user["nombre"]
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_seconds": JWT_EXPIRATION_MINUTES * 60,
        "user_info": {
            "email": credentials.email,
            "nombre": user["nombre"],
            "rol": user["rol"]
        }
    }

@app.get(
    "/auth/me", 
    tags=["1. Seguridad & JWT"],
    summary="Verificar Datos del Usuario Autenticado (Stateless Payload)"
)
def get_my_profile(current_user: dict = Depends(get_current_user)):
    """
    Muestra los datos contenidos directamente dentro de la firma del JWT.
    ¡El servidor no tuvo que consultar la base de datos para responder!
    """
    return {
        "message": "Token válido y verificado exitosamente",
        "claims_en_token": current_user
    }

# =============================================================================
# ENDPOINTS: API VERSION 1 (LEGACY / COMBO FIJO)
# =============================================================================
@app.get(
    "/v1/students", 
    response_model=List[StudentResponseV1], 
    tags=["2. Versionado de APIs (v1 vs v2)"],
    summary="[v1] Listar estudiantes (Formato Básico Legacy)"
)
def get_students_v1():
    """
    📦 **API v1**: Diseñada originalmente para las primeras versiones de clientes.
    Retorna solo los campos esenciales: matrícula, nombre, carrera y email.
    """
    results = []
    for s in STUDENTS_DB.values():
        results.append({
            "matricula": s["matricula"],
            "nombre": s["nombre"],
            "carrera": s["carrera"],
            "email": s["email"]
        })
    return results

@app.get(
    "/v1/students/{matricula}", 
    response_model=StudentResponseV1, 
    tags=["2. Versionado de APIs (v1 vs v2)"],
    summary="[v1] Obtener estudiante por matrícula"
)
def get_student_by_id_v1(matricula: str):
    student = STUDENTS_DB.get(matricula)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con matrícula '{matricula}' no encontrado."
        )
    return {
        "matricula": student["matricula"],
        "nombre": student["nombre"],
        "carrera": student["carrera"],
        "email": student["email"]
    }

# =============================================================================
# ENDPOINTS: API VERSION 2 (MODERNA / ENRIQUECIDA CON FILTROS Y ROLES)
# =============================================================================
@app.get(
    "/v2/students", 
    response_model=List[StudentResponseV2], 
    tags=["2. Versionado de APIs (v1 vs v2)"],
    summary="[v2] Listar estudiantes (Formato Enriquecido + Filtros)"
)
def get_students_v2(
    estado: Optional[str] = Query(None, description="Filtrar por estado: 'activo' o 'inactivo'"),
    carrera: Optional[str] = Query(None, description="Filtrar por carrera")
):
    """
    🚀 **API v2**: Evolución del contrato de datos.
    Incluye promedio ponderado, número de materias inscritas y soporte para filtrado con query parameters.
    """
    results = []
    for s in STUDENTS_DB.values():
        if estado and s["estado"].lower() != estado.lower():
            continue
        if carrera and carrera.lower() not in s["carrera"].lower():
            continue
            
        results.append({
            "matricula": s["matricula"],
            "nombre": s["nombre"],
            "carrera": s["carrera"],
            "email": s["email"],
            "semestre": s["semestre"],
            "promedio": s["promedio"],
            "estado": s["estado"],
            "materias_inscritas": len(s.get("materias", [])),
            "version_api": "v2"
        })
    return results

@app.get(
    "/v2/students/{matricula}", 
    tags=["2. Versionado de APIs (v1 vs v2)"],
    summary="[v2] Obtener detalle completo de estudiante"
)
def get_student_by_id_v2(matricula: str):
    student = STUDENTS_DB.get(matricula)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con matrícula '{matricula}' no encontrado."
        )
    return {
        "status": "success",
        "data": student,
        "meta": {"api_version": "v2.0", "timestamp": datetime.utcnow().isoformat()}
    }

@app.post(
    "/v2/students", 
    status_code=status.HTTP_201_CREATED, 
    tags=["3. Operaciones Protegidas con JWT"],
    summary="[v2 Protegido] Registrar nuevo estudiante (Requiere rol docente o admin)"
)
def create_student(
    student_data: CreateStudentRequest,
    current_user: dict = Depends(require_role(["docente", "admin"]))
):
    """
    🛡️ **Endpoint Protegido con JWT y Control de Roles**:
    Solo usuarios con rol `docente` o `admin` pueden registrar nuevos alumnos.
    """
    if student_data.matricula in STUDENTS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un alumno registrado con la matrícula '{student_data.matricula}'."
        )
    
    new_student = {
        "matricula": student_data.matricula,
        "nombre": student_data.nombre,
        "carrera": student_data.carrera,
        "email": student_data.email,
        "semestre": student_data.semestre,
        "promedio": student_data.promedio,
        "estado": "activo",
        "direccion": "Dirección pendiente de registro",
        "curp": "CURP-TEMPORAL",
        "materias": [],
        "creado_por": current_user["sub"]
    }
    
    STUDENTS_DB[student_data.matricula] = new_student
    
    return {
        "message": "Estudiante registrado exitosamente en el sistema.",
        "student": new_student,
        "audit": {
            "authorized_by": current_user["name"],
            "role": current_user["role"]
        }
    }

@app.delete(
    "/v2/students/{matricula}", 
    status_code=status.HTTP_200_OK, 
    tags=["3. Operaciones Protegidas con JWT"],
    summary="[v2 Protegido] Eliminar estudiante (Solo rol admin)"
)
def delete_student(
    matricula: str,
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    🛡️ **Eliminación Crítica**: Solo accesible para usuarios con rol `admin`.
    """
    if matricula not in STUDENTS_DB:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con matrícula '{matricula}' no existe."
        )
    
    deleted_student = STUDENTS_DB.pop(matricula)
    return {
        "message": f"Estudiante {deleted_student['nombre']} ({matricula}) eliminado correctamente.",
        "deleted_by": current_user["name"]
    }
