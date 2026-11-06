import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..helpers.audit_helper import registrar_log


class BackupProvider:
    """
    Provider responsável pela geração, listagem e recuperação de backups
    do banco de dados SQLite da aplicação na máquina local.
    """

    @staticmethod
    def get_project_root() -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @staticmethod
    def get_db_file_path() -> Path:
        dsn = settings.SQLITE_DSN or "sqlite+aiosqlite:///./app.db"
        if ":///" in dsn:
            raw_path = dsn.split(":///", 1)[1]
        else:
            raw_path = "./app.db"
        db_path = Path(raw_path)
        if not db_path.is_absolute():
            db_path = (BackupProvider.get_project_root() / db_path).resolve()
        return db_path

    @staticmethod
    def get_backup_dir() -> Path:
        backup_dir = BackupProvider.get_project_root() / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir

    @staticmethod
    async def gerar_backup(
        session: AsyncSession,
        usuario: str,
        prefixo_personalizado: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera uma cópia íntegra (hot backup via API nativa do SQLite) do banco de dados
        na pasta backups/ da máquina, nomeando o arquivo com:
        <nome_do_arquivo>_<YYYY-MM-DD_HH-MM-SS>.db
        """
        db_path = BackupProvider.get_db_file_path()
        if not db_path.exists():
            raise FileNotFoundError(f"Arquivo do banco de dados não encontrado em: {db_path}")

        backup_dir = BackupProvider.get_backup_dir()
        agora = datetime.now()
        timestamp_str = agora.strftime("%Y-%m-%d_%H-%M-%S")

        base_name = (prefixo_personalizado or db_path.stem or "app").strip()
        # Sanitizar nome base mantendo apenas caracteres seguros
        safe_base = "".join(c for c in base_name if c.isalnum() or c in ("_", "-")) or "app"
        filename = f"{safe_base}_{timestamp_str}.db"
        dest_path = backup_dir / filename

        # Executar backup online consistente usando a API nativa do sqlite3
        src_conn = sqlite3.connect(str(db_path))
        dst_conn = sqlite3.connect(str(dest_path))
        try:
            with dst_conn:
                src_conn.backup(dst_conn)
        finally:
            dst_conn.close()
            src_conn.close()

        stat = dest_path.stat()
        tamanho_bytes = stat.st_size
        tamanho_mb = round(tamanho_bytes / (1024 * 1024), 2)

        info = {
            "filename": filename,
            "caminho_completo": str(dest_path),
            "diretorio": str(backup_dir),
            "banco_origem": db_path.name,
            "data_hora": agora.strftime("%d/%m/%Y %H:%M:%S"),
            "timestamp_iso": agora.isoformat(),
            "tamanho_bytes": tamanho_bytes,
            "tamanho_formatado": f"{tamanho_mb:.2f} MB" if tamanho_mb >= 1 else f"{round(tamanho_bytes / 1024, 1)} KB",
            "usuario": usuario
        }

        try:
            await registrar_log(
                session=session,
                usuario=usuario or "admin",
                tela="Administração / Backup",
                tabela="backups",
                operacao="BACKUP",
                registro_id=filename,
                dados_anteriores=None,
                dados_posteriores=info
            )
            await session.commit()
        except Exception:
            await session.rollback()

        return info

    @staticmethod
    def listar_backups() -> List[Dict[str, Any]]:
        """
        Lista todos os arquivos de backup (.db) armazenados na máquina.
        """
        backup_dir = BackupProvider.get_backup_dir()
        arquivos: List[Dict[str, Any]] = []

        for item in backup_dir.glob("*.db"):
            if not item.is_file():
                continue
            stat = item.stat()
            dt = datetime.fromtimestamp(stat.st_mtime)
            tamanho_bytes = stat.st_size
            tamanho_mb = round(tamanho_bytes / (1024 * 1024), 2)
            arquivos.append({
                "filename": item.name,
                "caminho_completo": str(item.resolve()),
                "data_hora": dt.strftime("%d/%m/%Y %H:%M:%S"),
                "timestamp_iso": dt.isoformat(),
                "tamanho_bytes": tamanho_bytes,
                "tamanho_formatado": f"{tamanho_mb:.2f} MB" if tamanho_mb >= 1 else f"{round(tamanho_bytes / 1024, 1)} KB",
            })

        arquivos.sort(key=lambda x: x["timestamp_iso"], reverse=True)
        return arquivos

    @staticmethod
    def obter_caminho_backup(filename: str) -> Path:
        """
        Valida e retorna o caminho seguro de um arquivo de backup existente na máquina.
        """
        safe_name = os.path.basename(filename)
        if not safe_name.endswith(".db") or safe_name != filename:
            raise ValueError("Nome de arquivo de backup inválido.")
        backup_path = (BackupProvider.get_backup_dir() / safe_name).resolve()
        if not backup_path.exists() or not backup_path.is_file():
            raise FileNotFoundError("Arquivo de backup não encontrado.")
        return backup_path

