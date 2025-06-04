# filepath: /home/lonk/codes/SadTalker-WS-API/src/facerender/modules/make_animation.py

from scipy.spatial import ConvexHull
import torch
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm
import math

# Pre-computed constants for optimization
PI = torch.tensor(math.pi, dtype=torch.float32)
DEG_TO_RAD = PI / 180.0

# Pre-computed idx tensor for headpose prediction (cached to avoid recreation)
_idx_tensor_cache = {}


def normalize_kp(
    kp_source,
    kp_driving,
    kp_driving_initial,
    adapt_movement_scale=False,
    use_relative_movement=False,
    use_relative_jacobian=False,
):
    if adapt_movement_scale:
        source_area = ConvexHull(kp_source["value"][0].data.cpu().numpy()).volume
        driving_area = ConvexHull(
            kp_driving_initial["value"][0].data.cpu().numpy()
        ).volume
        adapt_movement_scale = np.sqrt(source_area) / np.sqrt(driving_area)
    else:
        adapt_movement_scale = 1

    kp_new = {k: v for k, v in kp_driving.items()}

    if use_relative_movement:
        kp_value_diff = kp_driving["value"] - kp_driving_initial["value"]
        kp_value_diff *= adapt_movement_scale
        kp_new["value"] = kp_value_diff + kp_source["value"]

        if use_relative_jacobian:
            jacobian_diff = torch.matmul(
                kp_driving["jacobian"], torch.inverse(kp_driving_initial["jacobian"])
            )
            kp_new["jacobian"] = torch.matmul(jacobian_diff, kp_source["jacobian"])

    return kp_new


def headpose_pred_to_degree(pred):
    device = pred.device
    device_key = str(device)

    # Cache idx_tensor per device to avoid recreation
    if device_key not in _idx_tensor_cache:
        idx_tensor = torch.arange(66, dtype=torch.float32, device=device)
        _idx_tensor_cache[device_key] = idx_tensor
    else:
        idx_tensor = _idx_tensor_cache[device_key]

    pred = F.softmax(pred, dim=-1)  # Add explicit dim for clarity
    degree = torch.sum(pred * idx_tensor, dim=1) * 3 - 99
    return degree


def get_rotation_matrix(yaw, pitch, roll):
    # Use pre-computed constant for conversion
    yaw = yaw * DEG_TO_RAD.to(yaw.device)
    pitch = pitch * DEG_TO_RAD.to(pitch.device)
    roll = roll * DEG_TO_RAD.to(roll.device)

    # Compute trigonometric values once
    cos_yaw, sin_yaw = torch.cos(yaw), torch.sin(yaw)
    cos_pitch, sin_pitch = torch.cos(pitch), torch.sin(pitch)
    cos_roll, sin_roll = torch.cos(roll), torch.sin(roll)

    batch_size = yaw.shape[0]
    device = yaw.device

    # Create rotation matrices more efficiently using stack
    zeros = torch.zeros(batch_size, device=device)
    ones = torch.ones(batch_size, device=device)

    # Pitch rotation matrix
    pitch_mat = torch.stack(
        [
            torch.stack([ones, zeros, zeros], dim=1),
            torch.stack([zeros, cos_pitch, -sin_pitch], dim=1),
            torch.stack([zeros, sin_pitch, cos_pitch], dim=1),
        ],
        dim=1,
    )

    # Yaw rotation matrix
    yaw_mat = torch.stack(
        [
            torch.stack([cos_yaw, zeros, sin_yaw], dim=1),
            torch.stack([zeros, ones, zeros], dim=1),
            torch.stack([-sin_yaw, zeros, cos_yaw], dim=1),
        ],
        dim=1,
    )

    # Roll rotation matrix
    roll_mat = torch.stack(
        [
            torch.stack([cos_roll, -sin_roll, zeros], dim=1),
            torch.stack([sin_roll, cos_roll, zeros], dim=1),
            torch.stack([zeros, zeros, ones], dim=1),
        ],
        dim=1,
    )

    # Combine rotations using more efficient matrix multiplication
    rot_mat = torch.bmm(torch.bmm(pitch_mat, yaw_mat), roll_mat)
    return rot_mat


def keypoint_transformation(kp_canonical, he, wo_exp=False):
    kp = kp_canonical["value"]  # (bs, k, 3)
    yaw, pitch, roll = he["yaw"], he["pitch"], he["roll"]

    # Convert predictions to degrees
    yaw = headpose_pred_to_degree(yaw)
    pitch = headpose_pred_to_degree(pitch)
    roll = headpose_pred_to_degree(roll)

    # Override with input values if provided
    if "yaw_in" in he:
        yaw = he["yaw_in"]
    if "pitch_in" in he:
        pitch = he["pitch_in"]
    if "roll_in" in he:
        roll = he["roll_in"]

    rot_mat = get_rotation_matrix(yaw, pitch, roll)  # (bs, 3, 3)

    t, exp = he["t"], he["exp"]
    if wo_exp:
        exp = torch.zeros_like(exp)  # More explicit than exp*0

    # keypoint rotation - using bmm for better performance
    kp_rotated = torch.bmm(rot_mat, kp.transpose(1, 2)).transpose(1, 2)

    # keypoint translation - optimize by creating t directly in the right shape
    t_modified = t.clone()
    t_modified[:, 0] = 0  # Zero out x translation
    t_modified[:, 2] = 0  # Zero out z translation
    t_expanded = t_modified.unsqueeze(1).expand(-1, kp.shape[1], -1)
    kp_t = kp_rotated + t_expanded

    # add expression deviation
    exp = exp.view(exp.shape[0], -1, 3)
    kp_transformed = kp_t + exp

    return {"value": kp_transformed}


def make_animation(
    source_image,
    source_semantics,
    target_semantics,
    generator,
    kp_detector,
    he_estimator,
    mapping,
    yaw_c_seq=None,
    pitch_c_seq=None,
    roll_c_seq=None,
    use_exp=True,
    use_half=False,
):
    with torch.no_grad():
        # Pre-allocate list with known size for better memory management
        num_frames = target_semantics.shape[1]
        predictions = []

        # Compute source keypoints once
        kp_canonical = kp_detector(source_image)
        he_source = mapping(source_semantics)
        kp_source = keypoint_transformation(kp_canonical, he_source)

        # Pre-extract sequences for faster indexing
        has_yaw_seq = yaw_c_seq is not None
        has_pitch_seq = pitch_c_seq is not None
        has_roll_seq = roll_c_seq is not None

        for frame_idx in tqdm(range(num_frames), "Face Renderer:"):
            target_semantics_frame = target_semantics[:, frame_idx]
            he_driving = mapping(target_semantics_frame)

            # Batch assignment for better performance
            if has_yaw_seq:
                he_driving["yaw_in"] = yaw_c_seq[:, frame_idx]
            if has_pitch_seq:
                he_driving["pitch_in"] = pitch_c_seq[:, frame_idx]
            if has_roll_seq:
                he_driving["roll_in"] = roll_c_seq[:, frame_idx]

            kp_driving = keypoint_transformation(kp_canonical, he_driving)

            # Direct assignment since kp_norm = kp_driving is just aliasing
            out = generator(source_image, kp_source=kp_source, kp_driving=kp_driving)
            predictions.append(out["prediction"])

        # Stack all predictions at once (more memory efficient)
        predictions_ts = torch.stack(predictions, dim=1)
    return predictions_ts


class AnimateModel(torch.nn.Module):
    """
    Merge all generator related updates into single model for better multi-gpu usage
    """

    def __init__(self, generator, kp_extractor, mapping):
        super(AnimateModel, self).__init__()
        self.kp_extractor = kp_extractor
        self.generator = generator
        self.mapping = mapping

        # Set models to eval mode
        self.kp_extractor.eval()
        self.generator.eval()
        self.mapping.eval()

    def forward(self, x):
        # Extract inputs once for cleaner code
        source_image = x["source_image"]
        source_semantics = x["source_semantics"]
        target_semantics = x["target_semantics"]
        yaw_c_seq = x.get("yaw_c_seq")  # Use .get() for optional parameters
        pitch_c_seq = x.get("pitch_c_seq")
        roll_c_seq = x.get("roll_c_seq")

        predictions_video = make_animation(
            source_image,
            source_semantics,
            target_semantics,
            self.generator,
            self.kp_extractor,
            self.mapping,
            use_exp=True,
            yaw_c_seq=yaw_c_seq,
            pitch_c_seq=pitch_c_seq,
            roll_c_seq=roll_c_seq,
        )

        return predictions_video
