$BasePath = "C:\Ai Agent"

# Folder list
$Folders = @(
    "app",
    "app/api",
    "app/services",
    "app/models",
    "app/utils",
    "app/static",
    "tests",
    "tests/sample_docs"
)

# File list (file path = content)
$Files = @{
    "app\__init__.py" = ""
    "app\main.py" = ""
    "app\config.py" = ""
    "app\dependencies.py" = ""

    "app\api\__init__.py" = ""
    "app\api\upload.py" = ""
    "app\api\report.py" = ""
    "app\api\fix.py" = ""
    "app\api\download.py" = ""
    "app\api\health.py" = ""

    "app\services\__init__.py" = ""
    "app\services\extraction_service.py" = ""
    "app\services\compliance_service.py" = ""
    "app\services\rewrite_service.py" = ""
    "app\services\storage_service.py" = ""

    "app\models\__init__.py" = ""
    "app\models\upload_models.py" = ""
    "app\models\report_models.py" = ""
    "app\models\fix_models.py" = ""

    "app\utils\__init__.py" = ""
    "app\utils\file_validation.py" = ""
    "app\utils\security.py" = ""
    "app\utils\ocr_utils.py" = ""

    "tests\__init__.py" = ""
    "tests\test_api.py" = ""

    ".env.example" = "API_KEY=`nMISTRAL_API_KEY=`nUPLOAD_DIR=static/`nMAX_FILE_SIZE_MB=25`n"
    "requirements.txt" = ""
    "Dockerfile" = ""
    "docker-compose.yml" = ""
    "README.md" = "# AI Compliance Agent Project`n"
}

Write-Host "Creating folder structure..." -ForegroundColor Cyan

# Create folders
foreach ($folder in $Folders) {
    $FullPath = Join-Path $BasePath $folder
    if (-Not (Test-Path $FullPath)) {
        New-Item -ItemType Directory -Force -Path $FullPath | Out-Null
        Write-Host "[OK] Folder created: $FullPath"
    } else {
        Write-Host "[Skip] Folder already exists: $FullPath"
    }
}

Write-Host "`nCreating files..." -ForegroundColor Cyan

# Create files
foreach ($file in $Files.Keys) {
    $FullPath = Join-Path $BasePath $file
    $Content = $Files[$file]

    # Ensure parent folder exists
    $Parent = Split-Path $FullPath -Parent
    if (-Not (Test-Path $Parent)) {
        New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    }

    # Create or overwrite file
    Set-Content -Path $FullPath -Value $Content -Encoding UTF8
    Write-Host "[OK] File created: $FullPath"
}

Write-Host "`n🎉 Project structure created successfully!" -ForegroundColor Green
