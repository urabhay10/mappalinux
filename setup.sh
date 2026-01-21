#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 &> /dev/null; then
    echo "Error: python3 required"
    exit 1
fi

if [ ! -d "$DIR/.venv" ]; then
    python3 -m venv "$DIR/.venv"
fi

source "$DIR/.venv/bin/activate"
pip install -q -r "$DIR/requirements.txt"
chmod +x "$DIR/mappa_linux.py"

cat << EOF > "$DIR/mappa"
#!/bin/bash
DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
source "\$DIR/.venv/bin/activate"
python "\$DIR/mappa_linux.py" "\$@"
EOF

chmod +x "$DIR/mappa"
echo "Ready. Use: ./mappa <request>"
