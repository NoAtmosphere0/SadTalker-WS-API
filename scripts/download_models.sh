#!/bin/bash
# filepath: /home/lonk/codes/SadTalker-WS-API/scripts/download_models.sh

# Set error handling
set -e

# Function to safely download file if it doesn't exist
download_if_not_exists() {
    local url="$1"
    local output_path="$2"
    
    if [ ! -f "$output_path" ]; then
        echo "Downloading $(basename "$output_path")..."
        wget -nc "$url" -O "$output_path" || {
            echo "Warning: Failed to download $url"
            return 1
        }
    else
        echo "File $(basename "$output_path") already exists, skipping..."
    fi
    return 0
}

# Create directories safely
echo "Creating necessary directories..."
mkdir -p ./data/checkpoints  
mkdir -p ./gfpgan/weights

# lagency download links (commented out)
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/auido2exp_00300-model.pth -O ./checkpoints/auido2exp_00300-model.pth
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/auido2pose_00140-model.pth -O ./checkpoints/auido2pose_00140-model.pth
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/epoch_20.pth -O ./checkpoints/epoch_20.pth
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/facevid2vid_00189-model.pth.tar -O ./checkpoints/facevid2vid_00189-model.pth.tar
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/shape_predictor_68_face_landmarks.dat -O ./checkpoints/shape_predictor_68_face_landmarks.dat
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/wav2lip.pth -O ./checkpoints/wav2lip.pth
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/mapping_00229-model.pth.tar -O ./checkpoints/mapping_00229-model.pth.tar
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/mapping_00109-model.pth.tar -O ./checkpoints/mapping_00109-model.pth.tar
# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/hub.zip -O ./checkpoints/hub.zip
# unzip -n ./checkpoints/hub.zip -d ./checkpoints/

#### Download the new links with error handling
echo "Downloading SadTalker model files..."
download_if_not_exists "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar" "./data/checkpoints/mapping_00109-model.pth.tar"
download_if_not_exists "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar" "./data/checkpoints/mapping_00229-model.pth.tar"
download_if_not_exists "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors" "./data/checkpoints/SadTalker_V0.0.2_256.safetensors"
download_if_not_exists "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors" "./data/checkpoints/SadTalker_V0.0.2_512.safetensors"

# wget -nc https://github.com/Winfredy/SadTalker/releases/download/v0.0.2/BFM_Fitting.zip -O ./checkpoints/BFM_Fitting.zip
# unzip -n ./checkpoints/BFM_Fitting.zip -d ./checkpoints/

### Download enhancer models
echo "Downloading GFPGAN enhancer models..."
download_if_not_exists "https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth" "./gfpgan/weights/alignment_WFLW_4HG.pth"
download_if_not_exists "https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth" "./gfpgan/weights/detection_Resnet50_Final.pth"
download_if_not_exists "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth" "./gfpgan/weights/GFPGANv1.4.pth"
download_if_not_exists "https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth" "./gfpgan/weights/parsing_parsenet.pth"

echo "Model download script completed successfully!" 

