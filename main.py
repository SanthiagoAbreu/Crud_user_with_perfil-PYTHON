from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from database import get_connection

app = FastAPI()

# =========================
# MODELOS (Pydantic)
# =========================
class PerfilCreate(BaseModel):
    perfil_nome: str

class PerfilModel(BaseModel):
    id: int
    perfil_nome: str

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: Optional[PerfilCreate] = None

class UsuarioModel(BaseModel):
    id: int
    nome: str
    email: EmailStr
    id_perfil: Optional[int] = None
    perfil: Optional[PerfilModel] = None

class UsuarioCreateResponse(BaseModel):
    mensagem: str
    user: UsuarioModel

class UsuarioListResponse(BaseModel):
    mensagem: str
    users: List[UsuarioModel]

class UsuarioUpdateResponse(BaseModel):
    mensagem: str
    user: UsuarioModel

# =========================
# CREATE
# =========================
@app.post("/api/usuarios", response_model=UsuarioCreateResponse, status_code=201)
def criar_usuario(dados: UsuarioCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (dados.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email já cadastrado")

        id_perfil = None
        
        if dados.perfil:
            cursor.execute(
                "INSERT INTO perfis (perfil_nome) VALUES (?)", 
                (dados.perfil.perfil_nome,)
            )
            id_perfil = cursor.lastrowid

        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, id_perfil) VALUES (?, ?, ?, ?)",
            (dados.nome, dados.email, dados.senha, id_perfil)
        )
        usuario_id = cursor.lastrowid
        conn.commit()

        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.id_perfil, p.perfil_nome 
            FROM usuarios u 
            LEFT JOIN perfis p ON u.id_perfil = p.id 
            WHERE u.id = ?
        """, (usuario_id,))
        
        row = cursor.fetchone()
        
        perfil_data = None
        if row['id_perfil']:
            perfil_data = {"id": row['id_perfil'], "perfil_nome": row['perfil_nome']}

        usuario_criado = {
            "id": row['id'],
            "nome": row['nome'],
            "email": row['email'],
            "id_perfil": row['id_perfil'],
            "perfil": perfil_data
        }

        return {"mensagem": "Usuário cadastrado com sucesso", "user": usuario_criado}

    finally:
        conn.close()

# =========================
# READ - LISTAR
# =========================
@app.get("/api/usuarios", response_model=UsuarioListResponse)
def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.nome, u.email, u.id_perfil, p.perfil_nome 
        FROM usuarios u 
        LEFT JOIN perfis p ON u.id_perfil = p.id
    """)

    rows = cursor.fetchall()
    usuarios = []

    for row in rows:
        perfil_data = None
        if row['id_perfil']:
            perfil_data = {"id": row['id_perfil'], "perfil_nome": row['perfil_nome']}
            
        usuarios.append({
            "id": row['id'],
            "nome": row['nome'],
            "email": row['email'],
            "id_perfil": row['id_perfil'],
            "perfil": perfil_data
        })

    conn.close()
    return {"mensagem": "Usuários encontrados com sucesso", "users": usuarios}

# =========================
# UPDATE
# =========================
@app.put("/api/usuarios/{id}", response_model=UsuarioUpdateResponse)
def atualizar_usuario(id: int, dados: UsuarioCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM usuarios WHERE email = ? AND id != ?", (dados.email, id))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email já está em uso por outro usuário")

        cursor.execute(
            "UPDATE usuarios SET nome = ?, email = ?, senha = ? WHERE id = ?",
            (dados.nome, dados.email, dados.senha, id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        cursor.execute("SELECT id_perfil FROM usuarios WHERE id = ?", (id,))
        row_usuario = cursor.fetchone()
        
        if dados.perfil and row_usuario and row_usuario['id_perfil']:
            cursor.execute(
                "UPDATE perfis SET perfil_nome = ? WHERE id = ?",
                (dados.perfil.perfil_nome, row_usuario['id_perfil'])
            )

        conn.commit()

        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.id_perfil, p.perfil_nome 
            FROM usuarios u 
            LEFT JOIN perfis p ON u.id_perfil = p.id 
            WHERE u.id = ?
        """, (id,))
        
        row = cursor.fetchone()
        
        perfil_data = None
        if row['id_perfil']:
            perfil_data = {"id": row['id_perfil'], "perfil_nome": row['perfil_nome']}

        usuario_atualizado = {
            "id": row['id'],
            "nome": row['nome'],
            "email": row['email'],
            "id_perfil": row['id_perfil'],
            "perfil": perfil_data
        }

        return {"mensagem": "Usuário atualizado com sucesso", "user": usuario_atualizado}

    finally:
        conn.close()

# =========================
# DELETE
# =========================
@app.delete("/api/usuarios/{id}")
def deletar_usuario(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id_perfil FROM usuarios WHERE id = ?", (id,))
        usuario = cursor.fetchone()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        
        if usuario['id_perfil']:
            cursor.execute("DELETE FROM perfis WHERE id = ?", (usuario['id_perfil'],))

        conn.commit()
        return {"mensagem": "Usuário e perfil removidos com sucesso"}

    finally:
        conn.close()