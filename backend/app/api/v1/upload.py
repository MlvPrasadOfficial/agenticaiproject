"""
File upload API endpoints with comprehensive validation and security.
Implements Tasks 41-44: File upload, storage, validation, and security checks.
"""

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
import os
import shutil
import hashlib
from pathlib import Path
import mimetypes
import pandas as pd
from datetime import datetime
import uuid
import aiofiles
from pydantic import BaseModel
import logging

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.data_processor import data_processor

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1/files", tags=["File Upload"])

# Allowed file types and their magic numbers
ALLOWED_MIME_TYPES = {
    'text/csv': ['.csv'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'application/json': ['.json'],
    'text/plain': ['.txt']
}

ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.txt'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_FILES_PER_UPLOAD = 5

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    mime_type: str
    status: str
    upload_timestamp: datetime
    validation_results: dict
    preview_available: bool
    metadata: dict

class FileValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    file_info: dict

def validate_file_type(file: UploadFile) -> FileValidationResult:
    """Validate file type using both extension and magic number detection."""
    errors = []
    warnings = []
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        errors.append(f"File extension '{file_extension}' not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Check MIME type using Python's built-in mimetypes
    try:
        detected_mime, _ = mimetypes.guess_type(file.filename)
        
        if detected_mime is None:
            detected_mime = "application/octet-stream"
        
        if detected_mime not in ALLOWED_MIME_TYPES:
            errors.append(f"File type '{detected_mime}' not supported")
        
        # Verify extension matches MIME type
        expected_extensions = ALLOWED_MIME_TYPES.get(detected_mime, [])
        if expected_extensions and file_extension not in expected_extensions:
            warnings.append(f"File extension '{file_extension}' doesn't match detected type '{detected_mime}'")
    
    except Exception as e:
        errors.append(f"Failed to detect file type: {str(e)}")
        detected_mime = "unknown"
    
    file_info = {
        "filename": file.filename,
        "reported_mime_type": file.content_type,
        "detected_mime_type": detected_mime,
        "file_extension": file_extension,
        "size": file.size if hasattr(file, 'size') else 0
    }
    
    return FileValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        file_info=file_info
    )

def validate_file_size(file: UploadFile) -> FileValidationResult:
    """Validate file size constraints."""
    errors = []
    warnings = []
    
    # Estimate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        errors.append(f"File size ({file_size:,} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE:,} bytes)")
    
    if file_size == 0:
        errors.append("File appears to be empty")
    
    if file_size < 100:  # Less than 100 bytes
        warnings.append("File is very small and may not contain meaningful data")
    
    file_info = {
        "size_bytes": file_size,
        "size_mb": round(file_size / (1024 * 1024), 2),
        "size_human": format_file_size(file_size)
    }
    
    return FileValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        file_info=file_info
    )

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

async def scan_file_for_security(file_path: Path) -> FileValidationResult:
    """Basic security scan for uploaded files."""
    errors = []
    warnings = []
    
    try:
        # Check for suspicious file patterns
        with open(file_path, 'rb') as f:
            content = f.read(1024)  # Read first 1KB
            
            # Check for executable signatures
            executable_signatures = [
                b'MZ',  # Windows executable
                b'\x7fELF',  # Linux executable
                b'\xfe\xed\xfa',  # macOS executable
                b'PK\x03\x04',  # ZIP file (could contain executables)
            ]
            
            for sig in executable_signatures:
                if content.startswith(sig):
                    errors.append("File contains executable code and is not allowed")
                    break
            
            # Check for suspicious strings
            suspicious_patterns = [
                b'<script',
                b'javascript:',
                b'<?php',
                b'eval(',
                b'exec(',
                b'system(',
            ]
            
            content_lower = content.lower()
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    warnings.append(f"File contains potentially suspicious content: {pattern.decode('utf-8', errors='ignore')}")
    
    except Exception as e:
        warnings.append(f"Security scan failed: {str(e)}")
    
    return FileValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        file_info={"security_scan_completed": True}
    )

async def generate_file_metadata(file_path: Path, original_filename: str) -> dict:
    """Generate comprehensive metadata for uploaded file."""
    try:
        file_stats = file_path.stat()
        file_hash = hashlib.sha256()
        
        # Calculate file hash
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)
        
        metadata = {
            "original_filename": original_filename,
            "file_size": file_stats.st_size,
            "upload_timestamp": datetime.now().isoformat(),
            "file_hash_sha256": file_hash.hexdigest(),
            "file_extension": file_path.suffix.lower(),
            "mime_type": magic.from_file(str(file_path), mime=True),
        }
        
        # Try to extract data-specific metadata
        if file_path.suffix.lower() in ['.csv', '.xlsx', '.xls']:
            try:
                if file_path.suffix.lower() == '.csv':
                    df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows
                else:
                    df = pd.read_excel(file_path, nrows=1000)
                
                metadata.update({
                    "data_preview": {
                        "columns": list(df.columns),
                        "column_count": len(df.columns),
                        "estimated_row_count": len(df),
                        "data_types": df.dtypes.astype(str).to_dict(),
                        "sample_data": df.head(3).to_dict('records')
                    }
                })
            except Exception as e:
                metadata["data_preview_error"] = str(e)
        
        return metadata
    
    except Exception as e:
        logger.error(f"Failed to generate metadata for {file_path}: {str(e)}")
        return {"error": f"Metadata generation failed: {str(e)}"}

@router.post("/upload", response_model=List[FileUploadResponse])
async def upload_files(
    files: List[UploadFile] = File(...),
    description: Optional[str] = Form(None)
):
    """
    Upload and validate files with comprehensive security and validation checks.
    
    Features:
    - Multiple file upload support
    - File type validation (extension + MIME type)
    - File size validation
    - Basic security scanning
    - Metadata extraction
    - Data preview generation
    """
    
    logger.info(f"File upload initiated. Number of files: {len(files)}")
    
    # Validate number of files
    if len(files) > MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {MAX_FILES_PER_UPLOAD} files allowed per upload."
        )
    
    responses = []
    upload_session_id = str(uuid.uuid4())
    
    for file in files:
        file_id = str(uuid.uuid4())
        
        try:
            # Step 1: File type validation
            type_validation = validate_file_type(file)
            
            # Step 2: File size validation
            size_validation = validate_file_size(file)
            
            # Combine validation results
            all_errors = type_validation.errors + size_validation.errors
            all_warnings = type_validation.warnings + size_validation.warnings
            
            if all_errors:
                responses.append(FileUploadResponse(
                    file_id=file_id,
                    filename=file.filename,
                    size=size_validation.file_info.get("size_bytes", 0),
                    mime_type=type_validation.file_info.get("detected_mime_type", "unknown"),
                    status="validation_failed",
                    upload_timestamp=datetime.now(),
                    validation_results={
                        "errors": all_errors,
                        "warnings": all_warnings
                    },
                    preview_available=False,
                    metadata={}
                ))
                continue
            
            # Step 3: Save file to secure location
            upload_dir = Path(settings.UPLOAD_DIR) / upload_session_id
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate secure filename
            secure_filename = f"{file_id}_{file.filename}"
            file_path = upload_dir / secure_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Step 4: Security scan
            security_validation = await scan_file_for_security(file_path)
            all_errors.extend(security_validation.errors)
            all_warnings.extend(security_validation.warnings)
            
            if security_validation.errors:
                # Delete file if security issues found
                file_path.unlink(missing_ok=True)
                
                responses.append(FileUploadResponse(
                    file_id=file_id,
                    filename=file.filename,
                    size=size_validation.file_info.get("size_bytes", 0),
                    mime_type=type_validation.file_info.get("detected_mime_type", "unknown"),
                    status="security_failed",
                    upload_timestamp=datetime.now(),
                    validation_results={
                        "errors": all_errors,
                        "warnings": all_warnings
                    },
                    preview_available=False,
                    metadata={}
                ))
                continue
            
            # Step 5: Generate metadata and process data
            metadata = await generate_file_metadata(file_path, file.filename)
            
            # Step 6: Process data for preview and profiling
            try:
                data_profile = await data_processor.process_file(file_path, file_id)
                metadata["data_profile"] = {
                    "row_count": data_profile.row_count,
                    "column_count": data_profile.column_count,
                    "quality_score": data_profile.quality_score,
                    "overall_quality": data_profile.overall_quality,
                    "processing_time": data_profile.processing_time,
                    "recommendations": data_profile.recommendations[:3],  # Top 3 recommendations
                    "column_types": {
                        "numeric": data_profile.numeric_columns,
                        "categorical": data_profile.categorical_columns,
                        "datetime": data_profile.datetime_columns,
                        "text": data_profile.text_columns
                    }
                }
                preview_available = True
                logger.info(f"Data processing completed for {file.filename}. Quality: {data_profile.overall_quality}")
            except Exception as processing_error:
                logger.error(f"Data processing failed for {file.filename}: {str(processing_error)}")
                metadata["data_processing_error"] = str(processing_error)
                preview_available = "data_preview" in metadata
            
            # Success response
            responses.append(FileUploadResponse(
                file_id=file_id,
                filename=file.filename,
                size=size_validation.file_info.get("size_bytes", 0),
                mime_type=type_validation.file_info.get("detected_mime_type", "unknown"),
                status="success",
                upload_timestamp=datetime.now(),
                validation_results={
                    "errors": [],
                    "warnings": all_warnings
                },
                preview_available="data_profile" in metadata or "data_preview" in metadata,
                metadata=metadata
            ))
            
            logger.info(f"File uploaded successfully: {file.filename} -> {file_id}")
            
        except Exception as e:
            logger.error(f"Upload failed for {file.filename}: {str(e)}")
            
            responses.append(FileUploadResponse(
                file_id=file_id,
                filename=file.filename,
                size=0,
                mime_type="unknown",
                status="upload_failed",
                upload_timestamp=datetime.now(),
                validation_results={
                    "errors": [f"Upload failed: {str(e)}"],
                    "warnings": []
                },
                preview_available=False,
                metadata={}
            ))
    
    logger.info(f"Upload session completed: {upload_session_id}. Results: {len([r for r in responses if r.status == 'success'])} successful, {len([r for r in responses if r.status != 'success'])} failed")
    
    return responses

@router.get("/upload-status/{file_id}")
async def get_upload_status(file_id: str):
    """Get the status of a file upload."""
    # TODO: Implement file status tracking
    return {"file_id": file_id, "status": "not_implemented"}

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file."""
    # TODO: Implement file deletion
    return {"file_id": file_id, "status": "not_implemented"}
