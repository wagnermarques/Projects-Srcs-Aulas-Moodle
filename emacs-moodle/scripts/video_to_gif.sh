#!/usr/bin/env bash
# ==============================================================================
# Script: video_to_gif.sh
# Description: Converts a video file (MP4, MKV, WebM) into an optimized
#              animated GIF and extracts a high-quality poster thumbnail (PNG).
# Usage: ./video_to_gif.sh <input_video> [output_gif] [fps=10] [width=800] [duration_sec]
# ==============================================================================

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <video_origem> [gif_destino] [fps (default 10)] [largura (default 800)] [duracao_segundos]"
    exit 1
fi

INPUT_VIDEO="$1"
OUTPUT_GIF="${2:-"${INPUT_VIDEO%.*}.gif"}"
OUTPUT_THUMB="${INPUT_VIDEO%.*}-thumb.png"
FPS="${3:-10}"
WIDTH="${4:-800}"
DURATION_ARG=""

if [ "$#" -ge 5 ]; then
    DURATION_ARG="-t $5"
fi

if ! command -v ffmpeg &> /dev/null; then
    echo "Erro: ffmpeg não está instalado no sistema."
    exit 1
fi

echo "🎬 Processando: $INPUT_VIDEO"

# 1. Extrair thumbnail em 00:00:02 (ou início)
echo "📸 Gerando thumbnail em PNG: $OUTPUT_THUMB"
ffmpeg -y -ss 00:00:02 -i "$INPUT_VIDEO" -vframes 1 -q:v 2 "$OUTPUT_THUMB" -loglevel error

# 2. Gerar GIF animado de alta qualidade com palettegen otimizada
echo "🎞️ Gerando GIF animado: $OUTPUT_GIF (FPS: $FPS, Largura: ${WIDTH}px)"
ffmpeg -y -i "$INPUT_VIDEO" ${DURATION_ARG} \
    -vf "fps=${FPS},scale=${WIDTH}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:reserve_transparent=0[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" \
    "$OUTPUT_GIF" -loglevel error

echo "✅ Concluído com sucesso!"
echo "   • GIF:   $OUTPUT_GIF"
echo "   • Thumb: $OUTPUT_THUMB"
