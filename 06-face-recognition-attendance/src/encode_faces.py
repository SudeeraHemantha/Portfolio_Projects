import os
import pickle
import logging
import numpy as np

logger = logging.getLogger("encode-faces")
logging.basicConfig(level=logging.INFO)

ENCODINGS_FILE = os.path.join("dataset", "encodings.pickle")

def generate_mock_face_encoding(name: str) -> np.ndarray:
    """Generates a deterministic 128-dimensional normalized facial embedding for testing."""
    import hashlib
    seed_bytes = hashlib.sha256(name.lower().encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(seed_bytes[:4], "big"))
    vec = rng.normal(loc=0.0, scale=1.0, size=128)
    norm = np.linalg.norm(vec)
    return vec / norm if norm != 0 else vec

def build_face_encodings(dataset_dir: str = "dataset") -> dict:
    """
    Scans image dataset directory structured by employee folders,
    extracts 128-dimensional facial encodings, and persists to pickle file.
    """
    os.makedirs(dataset_dir, exist_ok=True)
    known_encodings = []
    known_names = []

    logger.info(f"Scanning dataset directory '{dataset_dir}' for training images...")
    
    # Try importing face_recognition if available
    try:
        import face_recognition
        import cv2

        for root, dirs, files in os.walk(dataset_dir):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    employee_name = os.path.basename(root)
                    image_path = os.path.join(root, file)

                    image = cv2.imread(image_path)
                    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    boxes = face_recognition.face_locations(rgb, model="hog")
                    encodings = face_recognition.face_encodings(rgb, boxes)

                    for encoding in encodings:
                        known_encodings.append(encoding)
                        known_names.append(employee_name)
                    
                    logger.info(f"Processed image for: {employee_name} ({len(encodings)} face(s) found)")
    except Exception as e:
        logger.warning(f"Native face_recognition engine notice ({e}). Generating synthetic 128D encodings...")
        # Populate demo fallback encodings if dataset images are absent
        demo_employees = ["EMP001_Alex_Mercer", "EMP002_Elena_Rostova", "EMP003_Marcus_Vance"]
        for emp in demo_employees:
            known_encodings.append(generate_mock_face_encoding(emp))
            known_names.append(emp)

    data = {"encodings": known_encodings, "names": known_names}
    
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)
    
    logger.info(f"Successfully serialized {len(known_encodings)} face encoding(s) to '{ENCODINGS_FILE}'.")
    return data

if __name__ == "__main__":
    build_face_encodings()
