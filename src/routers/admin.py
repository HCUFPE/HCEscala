from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.auth import auth_handler
from ..resources.database import get_app_db_session
from ..providers.backup_provider import BackupProvider

router = APIRouter(
    prefix="/api",
    tags=["Admin"],
    dependencies=[Depends(auth_handler.decode_token)]
)


class AdminData(BaseModel):
    message: str
    user_groups: List[str]


class GerarBackupRequest(BaseModel):
    nome_base: Optional[str] = None


async def verify_admin_group(current_user: dict = Depends(auth_handler.decode_token)):
    ADMIN_GROUP = "GLO-SEC-HCPE-SETISD"
    groups = current_user.get("groups", []) or []
    username = (current_user.get("username") or current_user.get("sub") or "").lower()
    if ADMIN_GROUP not in groups and username != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
    return current_user


@router.get("/admin-only-data", response_model=AdminData)
async def get_admin_data(current_user: dict = Depends(verify_admin_group)):
    """
    Returns data only accessible by users with admin privileges.
    """
    return AdminData(
        message="This is highly confidential admin data!",
        user_groups=current_user.get("groups", [])
    )


@router.get("/admin/backups")
async def listar_backups_banco(
    current_user: dict = Depends(verify_admin_group)
):
    """
    Lista os backups do banco de dados salvos na máquina. Acesso restrito ao Administrador.
    """
    db_path = BackupProvider.get_db_file_path()
    backup_dir = BackupProvider.get_backup_dir()
    itens = BackupProvider.listar_backups()
    return {
        "banco_origem": db_path.name,
        "caminho_banco_origem": str(db_path),
        "diretorio_backups": str(backup_dir),
        "total": len(itens),
        "items": itens
    }


@router.post("/admin/backups/gerar")
async def gerar_backup_banco(
    payload: Optional[GerarBackupRequest] = None,
    db: AsyncSession = Depends(get_app_db_session),
    current_user: dict = Depends(verify_admin_group)
):
    """
    Gera um backup completo do banco de dados na máquina com nome do arquivo + data, hora, minuto e segundo.
    Acesso restrito ao Administrador do sistema.
    """
    admin_login = current_user.get("username") or current_user.get("sub") or "admin"
    prefixo = payload.nome_base if payload else None
    try:
        info = await BackupProvider.gerar_backup(
            session=db,
            usuario=admin_login,
            prefixo_personalizado=prefixo
        )
        return {
            "sucesso": True,
            "mensagem": f"Backup '{info['filename']}' gerado com sucesso na máquina!",
            "backup": info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao gerar backup do banco de dados: {e}"
        )


@router.get("/admin/backups/download/{filename}")
async def download_backup_banco(
    filename: str,
    current_user: dict = Depends(verify_admin_group)
):
    """
    Realiza o download de um arquivo de backup gerado para a máquina do administrador.
    """
    try:
        file_path = BackupProvider.obter_caminho_backup(filename)
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/octet-stream"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
