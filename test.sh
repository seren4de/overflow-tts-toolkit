#!/usr/bin/env bash

# Enable strict mode
set -euo pipefail
IFS=$'\n\t'

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME=$(basename "$0")
readonly LOG_FILE="${SCRIPT_DIR}/tts_test_$(date +%Y%m%d_%H%M%S).log"

# Default configuration (can be overridden via environment variables)
: "${TEST_PHRASES:="The quick brown fox jumps over the lazy dog."}"
: "${VOCODER_NAME:="vocoder_models/en/ljspeech/hifigan_v2"}"
: "${OUTPUT_DIR:="/tmp/overflow-tts-toolkit/audio/output/testlr"}"
: "${MODEL_BASE_DIR:="/tmp/overflow-tts-toolkit/out"}"
: "${MAX_PARALLEL_JOBS:=4}"
: "${FAIL_FAST:=false}"

# File extensions and paths
readonly PTH_EXT=".pth"
readonly CHECKPOINT_PREFIX="/checkpoint_"
readonly WAV_EXT=".wav"
readonly CONFIG_SUFFIX="/config.json"

# Arrays of checkpoints and learning rates to test
readonly CHECKPOINTS=("55500" "56000" "56500")
readonly LEARNING_RATES=("1e-3")

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Logging functions
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$*"; }
log_warn() { log "WARN" "$*" >&2; }
log_error() { log "ERROR" "$*" >&2; }
log_success() { log "SUCCESS" "$*"; }

# Error handling
trap 'handle_error $? $LINENO $BASH_LINENO "$BASH_COMMAND" $(printf "::%s" ${FUNCNAME[@]:-})' ERR

handle_error() {
    local exit_code=$1
    local line_no=$2
    local bash_lineno=$3
    local last_command=$4
    local func_trace=$5
    
    log_error "Error in ${SCRIPT_NAME}: Command '$last_command' exited with status $exit_code"
    log_error "Line number: $line_no"
    log_error "Function trace: $func_trace"
    
    if [[ "$FAIL_FAST" == "true" ]]; then
        exit "$exit_code"
    fi
}

# Check required commands
check_requirements() {
    local required_commands=("tts" "parallel")
    local missing_commands=()
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_commands+=("$cmd")
        fi
    done
    
    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        log_error "Missing required commands: ${missing_commands[*]}"
        log_error "Please install missing commands and try again"
        exit 1
    fi
}

# Create necessary directories
setup_directories() {
    mkdir -p "$OUTPUT_DIR" "$(dirname "$LOG_FILE")"
    log_info "Created output directory: $OUTPUT_DIR"
}

# Validate model files
validate_model_path() {
    local lr="$1"
    local checkpoint="$2"
    local model_path="${MODEL_BASE_DIR}${lr}${CHECKPOINT_PREFIX}${checkpoint}${PTH_EXT}"
    local config_path="${MODEL_BASE_DIR}${lr}${CONFIG_SUFFIX}"
    
    if [[ ! -f "$model_path" ]]; then
        log_warn "Model not found: $model_path"
        return 1
    fi
    
    if [[ ! -f "$config_path" ]]; then
        log_warn "Config not found: $config_path"
        return 1
    fi
    
    return 0
}

# Process single TTS generation
process_tts() {
    local lr="$1"
    local checkpoint="$2"
    local output_file="${OUTPUT_DIR}/${lr}_${checkpoint}${WAV_EXT}"
    
    if [[ -f "$output_file" ]]; then
        log_info "Output already exists: $output_file"
        return 0
    fi
    
    if ! validate_model_path "$lr" "$checkpoint"; then
        return 1
    fi
    
    log_info "Processing TTS for LR=$lr, Checkpoint=$checkpoint"
    
    local model_path="${MODEL_BASE_DIR}${lr}${CHECKPOINT_PREFIX}${checkpoint}${PTH_EXT}"
    local config_path="${MODEL_BASE_DIR}${lr}${CONFIG_SUFFIX}"
    
    if tts --text "$TEST_PHRASES" \
           --model_path "$model_path" \
           --config_path "$config_path" \
           --out_path "$output_file" \
           --vocoder_name "$VOCODER_NAME" 2>> "$LOG_FILE"; then
        log_success "Successfully generated TTS for LR=$lr, Checkpoint=$checkpoint"
        return 0
    else
        log_error "Failed to generate TTS for LR=$lr, Checkpoint=$checkpoint"
        return 1
    fi
}

# Export function for GNU Parallel
export -f process_tts
export -f log_info log_warn log_error log_success
export -f validate_model_path

# Main execution
main() {
    log_info "Starting TTS checkpoint testing"
    log_info "Test phrases: $TEST_PHRASES"
    
    check_requirements
    setup_directories
    
    # Create job list for parallel processing
    local job_list=()
    for lr in "${LEARNING_RATES[@]}"; do
        for cp in "${CHECKPOINTS[@]}"; do
            job_list+=("$lr $cp")
        done
    done
    
    # Process jobs in parallel
    printf "%s\n" "${job_list[@]}" | \
        parallel --jobs "$MAX_PARALLEL_JOBS" \
                 --colsep ' ' \
                 process_tts {1} {2}
    
    log_info "TTS checkpoint testing completed"
    log_info "Results available in: $OUTPUT_DIR"
    log_info "Log file: $LOG_FILE"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi