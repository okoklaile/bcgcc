#!/bin/bash
# Test BC-GCC setup

echo "========================================"
echo "Testing BC-GCC Setup"
echo "========================================"
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✓ $PYTHON_VERSION"
else
    echo "   ✗ Python 3 not found"
    exit 1
fi

# Check dependencies
echo ""
echo "2. Checking dependencies..."

MISSING_DEPS=()

python3 -c "import torch" 2>/dev/null
if [ $? -eq 0 ]; then
    TORCH_VERSION=$(python3 -c "import torch; print(torch.__version__)")
    echo "   ✓ PyTorch $TORCH_VERSION"
else
    echo "   ✗ PyTorch not found"
    MISSING_DEPS+=("torch")
fi

python3 -c "import numpy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ NumPy installed"
else
    echo "   ✗ NumPy not found"
    MISSING_DEPS+=("numpy")
fi

python3 -c "import matplotlib" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ Matplotlib installed"
else
    echo "   ✗ Matplotlib not found"
    MISSING_DEPS+=("matplotlib")
fi

python3 -c "import tqdm" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ tqdm installed"
else
    echo "   ✗ tqdm not found"
    MISSING_DEPS+=("tqdm")
fi

# Check CUDA
echo ""
echo "3. Checking CUDA..."
python3 -c "import torch; print('   ✓ CUDA available' if torch.cuda.is_available() else '   ⚠ CUDA not available (will use CPU)')" 2>/dev/null

# Check data
echo ""
echo "4. Checking data..."
DATA_DIRS=("data/ghent" "data/norway" "data/NY" "data/opennetlab")
TOTAL_FILES=0

for dir in "${DATA_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        count=$(ls -1 "$dir"/*.pickle 2>/dev/null | wc -l)
        TOTAL_FILES=$((TOTAL_FILES + count))
        echo "   ✓ $dir: $count files"
    else
        echo "   ✗ $dir not found"
    fi
done

echo "   Total: $TOTAL_FILES pickle files"

# Check directories
echo ""
echo "5. Checking directories..."
REQUIRED_DIRS=("src" "tools" "data" "checkpoints" "logs")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✓ $dir/"
    else
        echo "   ✗ $dir/ not found"
        mkdir -p "$dir"
        echo "     Created $dir/"
    fi
done

# Test model import
echo ""
echo "6. Testing model import..."
cd src
python3 -c "from model import GCCBC_LSTM; from config import Config; print('   ✓ Model import successful')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✓ All imports working"
else
    echo "   ✗ Import failed, check Python path"
fi
cd ..

# Summary
echo ""
echo "========================================"
echo "Summary"
echo "========================================"

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo "✓ All dependencies installed"
    echo "✓ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Review configuration: src/config.py"
    echo "  2. Start training: cd src && python train.py"
    echo "  3. Monitor training: tensorboard --logdir ../logs"
else
    echo "⚠ Missing dependencies: ${MISSING_DEPS[*]}"
    echo ""
    echo "To install missing dependencies:"
    echo "  pip install -r requirements.txt"
fi

echo ""
echo "========================================"
