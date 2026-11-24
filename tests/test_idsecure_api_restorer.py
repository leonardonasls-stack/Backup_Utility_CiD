"""
Testes para IDSecureAPIRestorer (geração de pacote ZIP sem BOM duplo).
"""

import tempfile
import zipfile
from pathlib import Path

from backend.services.idsecure_api_restorer import IDSecureAPIRestorer
from backend.services.sqlite_storage import SQLiteStorage


def test_generate_import_zip_single_bom():
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        db_path = tmp_path / "backup_controlid.sqlite"
        storage = SQLiteStorage(str(db_path))

        # Cria foto fake
        face_file = tmp_path / "1_1001_CARLOS.jpg"
        face_file.write_bytes(b"\xff\xd8\xff\xe0FAKE_JPEG")

        with storage._get_connection() as conn:
            conn.execute(
                "INSERT INTO users (id, registration, name) VALUES (?, ?, ?)",
                (1, "1001", "CARLOS"),
            )
            conn.commit()
        storage.register_user_image(
            user_id=1,
            timestamp=1710000000,
            file_path=str(face_file),
            file_size=14,
            status="DOWNLOADED",
            source_device_serial="TEST001",
        )

        restorer = IDSecureAPIRestorer(storage, str(tmp_path))
        result = restorer.generate_import_zip()
        zip_path = Path(result)

        assert Path(result).exists()
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            assert "usuarios.csv" in names
            assert "fotos/1_1001_CARLOS.jpg" in names

            csv_bytes = zf.read("usuarios.csv")
            # Deve iniciar com exatamente um BOM UTF-8 (\xef\xbb\xbf), nunca duplo
            assert csv_bytes.startswith(b"\xef\xbb\xbf")
            assert not csv_bytes.startswith(b"\xef\xbb\xbf\xef\xbb\xbf")
            assert "CARLOS" in csv_bytes.decode("utf-8-sig")
