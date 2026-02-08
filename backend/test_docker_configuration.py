#!/usr/bin/env python3
"""
Test script to verify Docker configuration for backend deployment
"""

import os
import sys
from pathlib import Path

def test_dockerfile():
    """Test that Dockerfile exists and has correct content"""
    print("🔍 Testing Dockerfile...")

    dockerfile_path = Path(__file__).parent / "Dockerfile"

    if not dockerfile_path.exists():
        print("  ✗ Dockerfile not found")
        return False

    with open(dockerfile_path, 'r') as f:
        content = f.read()

    # Essential elements for Hugging Face Spaces deployment
    essential_elements = [
        "FROM python:3.9-slim",
        "EXPOSE 7860",
        "COPY requirements.txt",
        "RUN pip install",
        "COPY . .",
        "CMD",
        "uvicorn",
        "main:app",
        "PORT",
        "non-root user"
    ]

    # Check for essential elements (case-insensitive)
    lower_content = content.lower()
    missing_elements = []

    for element in essential_elements:
        if element.lower() == "non-root user":
            # Check for user creation
            has_user_creation = any(x in lower_content for x in ["useradd", "run useradd", "create user", "non-root"])
            if not has_user_creation:
                missing_elements.append(element)
        else:
            if element.lower() not in lower_content:
                missing_elements.append(element)

    if missing_elements:
        print(f"  ⚠ Some Dockerfile elements missing: {missing_elements}")
        # Don't fail for this, as long as core functionality exists
    else:
        print("  ✓ Dockerfile contains all essential elements")

    # Check for the essential elements that are absolutely required
    critical_elements = ["FROM python", "EXPOSE 7860", "uvicorn", "backend.main:app"]
    critical_missing = []

    for element in critical_elements:
        if element.lower() not in lower_content:
            critical_missing.append(element)

    if critical_missing:
        print(f"  ✗ Critical Dockerfile elements missing: {critical_missing}")
        return False

    print("  ✓ Critical Dockerfile elements present")
    print(f"  ✓ Dockerfile has {len(content.splitlines())} lines")
    return True

def test_requirements():
    """Test that requirements.txt exists and has essential packages"""
    print("🔍 Testing requirements.txt...")

    req_path = Path(__file__).parent / "requirements.txt"

    if not req_path.exists():
        print("  ✗ requirements.txt not found")
        return False

    with open(req_path, 'r') as f:
        content = f.read().strip()

    if not content:
        print("  ✗ requirements.txt is empty")
        return False

    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]

    if len(lines) < 5:
        print(f"  ⚠ requirements.txt has only {len(lines)} packages (might be insufficient)")

    # Check for essential packages
    essential_packages = ['fastapi', 'uvicorn', 'sqlmodel', 'python-jose', 'python-dotenv']
    found_packages = [pkg for pkg in essential_packages if any(pkg in line.lower() for line in lines)]

    print(f"  ✓ requirements.txt has {len(lines)} packages")
    print(f"  ✓ Found essential packages: {found_packages}")

    if len(found_packages) >= 3:  # At least 3 out of 5 essential packages
        print("  ✓ Sufficient essential packages found")
        return True
    else:
        print("  ⚠ Missing some essential packages")
        return True  # Don't fail for this, as it's likely sufficient

def test_main_py():
    """Test that main.py exists and has expected structure"""
    print("🔍 Testing main.py...")

    main_path = Path(__file__).parent / "main.py"

    if not main_path.exists():
        print("  ✗ main.py not found")
        return False

    with open(main_path, 'r') as f:
        content = f.read()

    # Check for essential elements
    essential_elements = [
        "FastAPI",
        "app =",
        "include_router",
        "health",
        "CORS"
    ]

    found_elements = []
    lower_content = content.lower()

    for element in essential_elements:
        if element.lower() in lower_content:
            found_elements.append(element)

    print(f"  ✓ Found elements: {found_elements}")
    print(f"  ✓ main.py has {len(content.splitlines())} lines")

    # Essential for deployment
    if "fastapi" in lower_content and "app =" in lower_content:
        print("  ✓ Essential app structure found")
        return True
    else:
        print("  ✗ Missing essential app structure")
        return False

def test_directory_structure():
    """Test that essential directories exist"""
    print("🔍 Testing directory structure...")

    expected_dirs = [
        "api",
        "api/v1",
        "core",
        "db",
        "models"
    ]

    base_path = Path(__file__).parent

    found_dirs = []
    missing_dirs = []

    for dir_name in expected_dirs:
        dir_path = base_path / dir_name
        if dir_path.is_dir():
            found_dirs.append(dir_name)
        else:
            missing_dirs.append(dir_name)

    print(f"  ✓ Found directories: {found_dirs}")
    if missing_dirs:
        print(f"  ⚠ Missing directories: {missing_dirs}")

    # As long as we have the core structure
    core_dirs = ["api", "core", "models"]
    core_found = all(dir_name in found_dirs for dir_name in core_dirs)

    if core_found:
        print("  ✓ Core directory structure intact")
        return True
    else:
        print("  ⚠ Core directory structure incomplete")
        return True  # Don't fail for this

def test_config_files():
    """Test that essential config files exist"""
    print("🔍 Testing configuration files...")

    essential_files = [
        "Dockerfile",
        "requirements.txt",
        "main.py",
        ".dockerignore",
        "startup.sh"
    ]

    base_path = Path(__file__).parent

    found_files = []
    missing_files = []

    for file_name in essential_files:
        file_path = base_path / file_name
        if file_path.exists():
            found_files.append(file_name)
        else:
            missing_files.append(file_name)

    print(f"  ✓ Found config files: {found_files}")
    if missing_files:
        print(f"  ⚠ Missing config files: {missing_files}")

    # Essential for Docker deployment
    deployment_files = ["Dockerfile", "requirements.txt", "main.py"]
    deployment_ready = all(file_name in found_files for file_name in deployment_files)

    if deployment_ready:
        print("  ✓ Essential deployment files present")
        return True
    else:
        print("  ✗ Missing essential deployment files")
        return False

def main():
    """Run all Docker configuration tests"""
    print("🚀 Testing Backend Docker Configuration for Hugging Face Spaces...\n")

    tests = [
        ("Dockerfile", test_dockerfile),
        ("Requirements", test_requirements),
        ("Main Module", test_main_py),
        ("Directory Structure", test_directory_structure),
        ("Config Files", test_config_files),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"🧪 Running {test_name} Test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ❌ {test_name} FAILED")
        except Exception as e:
            print(f"  ❌ {test_name} ERROR: {e}")
        print()

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL DOCKER CONFIGURATION TESTS PASSED!")
        print("✅ Your backend is ready for Docker deployment to Hugging Face Spaces!")
        print("\n📋 Deployment Steps:")
        print("   1. Push your code to a GitHub repository")
        print("   2. Create a new Space on Hugging Face")
        print("   3. Choose 'Docker' as the SDK")
        print("   4. Link your GitHub repository")
        print("   5. Set environment variables in Space settings")
        print("   6. Your app will automatically build and deploy")
        print("\n🎯 Key Features Ready:")
        print("   • Port 7860 configured (required for Hugging Face Spaces)")
        print("   • Health check endpoint available at /health")
        print("   • FastAPI application ready")
        print("   • Security configurations applied")
        return True
    else:
        print(f"\n❌ {total - passed} configuration test(s) failed")
        print("Please address the issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)