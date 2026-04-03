# app/services/file_service.py
import os
import uuid
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.enum import EntityType, AttachmentType
from app.models.file import File
from app.models.file_attachment import FileAttachment


class FileService:
    UPLOAD_DIR = "uploads"

    @staticmethod
    def save_file(
            db: Session,
            file: UploadFile,
            entity_type: str,
            entity_id,
            attachment_type: str
    ):
        os.makedirs(FileService.UPLOAD_DIR, exist_ok=True)

        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        storage_path = os.path.join(FileService.UPLOAD_DIR, filename)

        with open(storage_path, "wb") as f:
            f.write(file.file.read())

        # создаем запись файла
        db_file = File(
            filename=file.filename,
            storage_path=storage_path,
            mime_type=file.content_type
        )
        db.add(db_file)
        db.flush()  # чтобы получить id

        # создаем связь
        attachment = FileAttachment(
            file_id=db_file.id,
            entity_type=entity_type,
            entity_id=entity_id,
            attachment_type=attachment_type
        )
        db.add(attachment)

        db.commit()

        return db_file

    @staticmethod
    def get_file(
            db: Session,
            entity_type: str,
            entity_id,
            attachment_type: str
    ):
        from app.models.file import File
        from app.models.file_attachment import FileAttachment

        return db.query(File).join(FileAttachment).filter(
            FileAttachment.entity_type == entity_type,
            FileAttachment.entity_id == entity_id,
            FileAttachment.attachment_type == attachment_type
        ).order_by(File.uploaded_at.desc()).first()

    @staticmethod
    def get_files(
            db: Session,
            entity_type: str,
            entity_id,
            attachment_type: str
    ):
        from app.models.file import File
        from app.models.file_attachment import FileAttachment

        return db.query(File).join(FileAttachment).filter(
            FileAttachment.entity_type == entity_type,
            FileAttachment.entity_id == entity_id,
            FileAttachment.attachment_type == attachment_type
        ).order_by(File.uploaded_at.desc()).all()

    @staticmethod
    def delete_files(
            db: Session,
            entity_type: str,
            entity_id,
            attachment_type: str
    ):
        import os
        from app.models.file import File
        from app.models.file_attachment import FileAttachment

        files = db.query(File).join(FileAttachment).filter(
            FileAttachment.entity_type == entity_type,
            FileAttachment.entity_id == entity_id,
            FileAttachment.attachment_type == attachment_type
        ).all()

        for file in files:
            # удаляем файл с диска
            if os.path.exists(file.storage_path):
                os.remove(file.storage_path)

            # удаляем attachment
            db.query(FileAttachment).filter(
                FileAttachment.file_id == file.id
            ).delete()

            # удаляем сам файл
            db.delete(file)

        db.commit()


    @staticmethod
    def get_session_files(db: Session, session_id: uuid.UUID):
        """Возвращает список файлов, прикрепленных к сессии"""
        attachments = db.query(FileAttachment, File).join(
            File, File.id == FileAttachment.file_id
        ).filter(
            FileAttachment.entity_type == EntityType.SESSION,
            FileAttachment.entity_id == session_id,
            FileAttachment.attachment_type == AttachmentType.SESSION_FILE
        ).all()

        return [
            {
                "file_name": file.File.filename,
                "url": f"/uploads/{file.File.storage_path.split('/')[-1]}"
            }
            for file in attachments
        ]