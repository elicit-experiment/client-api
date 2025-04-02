import cgi
import requests
import os
import gzip
import msgpack
import json

QUANTIZATION_AMOUNT = 100000.0 # Much match the frontend.

BLENDSHAPE_CATEGORY_NAMES = [
    '_neutral',
    'browDownLeft',
    'browDownRight',
    'browInnerUp',
    'browOuterUpLeft',
    'browOuterUpRight',
    'cheekPuff',
    'cheekSquintLeft',
    'cheekSquintRight',
    'eyeBlinkLeft',
    'eyeBlinkRight',
    'eyeLookDownLeft',
    'eyeLookDownRight',
    'eyeLookInLeft',
    'eyeLookInRight',
    'eyeLookOutLeft',
    'eyeLookOutRight',
    'eyeLookUpLeft',
    'eyeLookUpRight',
    'eyeSquintLeft',
    'eyeSquintRight',
    'eyeWideLeft',
    'eyeWideRight',
    'jawForward',
    'jawLeft',
    'jawOpen',
    'jawRight',
    'mouthClose',
    'mouthDimpleLeft',
    'mouthDimpleRight',
    'mouthFrownLeft',
    'mouthFrownRight',
    'mouthFunnel',
    'mouthLeft',
    'mouthLowerDownLeft',
    'mouthLowerDownRight',
    'mouthPressLeft',
    'mouthPressRight',
    'mouthPucker',
    'mouthRight',
    'mouthRollLower',
    'mouthRollUpper',
    'mouthShrugLower',
    'mouthShrugUpper',
    'mouthSmileLeft',
    'mouthSmileRight',
    'mouthStretchLeft',
    'mouthStretchRight',
    'mouthUpperUpLeft',
    'mouthUpperUpRight',
    'noseSneerLeft',
    'noseSneerRight',
]

BLENDSHAPE_CATEGORY_INDICES = {name: index for index, name in enumerate(BLENDSHAPE_CATEGORY_NAMES)}


def compress_datapoint(config, data_point):
    if config.get("FaceTransformation") and "facialTransformationMatrixes" not in data_point:
        return None

    result_matrix = None
    if config.get("FaceTransformation") and "facialTransformationMatrixes" in data_point:
        result_matrix = [
            [val for sublist in matrix["data"] for val in sublist]
            for matrix in data_point["facialTransformationMatrixes"]
        ]

    result_landmarks = None
    if "faceLandmarks" not in data_point or not data_point["faceLandmarks"]:
        return None
    if config.get("Landmarks") and "faceLandmarks" in data_point:
        result_landmarks = [
            {
                "z": not config.get("StripZCoordinates", False),
                "p": [
                    coord
                    for lm in landmarks
                    for coord in ([lm["x"], lm["y"]] + ([lm["z"]] if not config.get("StripZCoordinates", False) else []))
                ],
            }
            for landmarks in data_point["faceLandmarks"]
        ]

    result_blendshapes = None
    if "faceBlendshapes" not in data_point or not data_point["faceBlendshapes"]:
        return None
    if config.get("Blendshapes") and "faceBlendshapes" in data_point:
        result_blendshapes = [
            {
                "s": [cat["score"] for cat in classifications["categories"]],
                "i": [cat["index"] for cat in classifications["categories"]],
                "c": [
                    BLENDSHAPE_CATEGORY_INDICES.get(cat["categoryName"], None)
                    for cat in classifications["categories"]
                ],
            }
            for classifications in data_point["faceBlendshapes"]
        ]

    result = {}
    if result_landmarks is not None:
        result["l"] = result_landmarks
    if result_blendshapes is not None:
        result["b"] = result_blendshapes
    if result_matrix is not None:
        result["m"] = result_matrix

    return result

def uncompress_datapoint(compressed):
    # return if this doesn't look like our compressed format.
    if "faceLandmarks" in compressed:
        return compressed

    facial_transformation_matrices = None
    if "m" in compressed:
        facial_transformation_matrices = [
            {
                "rows": int(len(matrix)**0.5),
                "columns": int(len(matrix)**0.5),
                "data": matrix,
            }
            for matrix in compressed["m"]
        ]

    timeStamp = None
    if "t" in compressed:
        timeStamp = compressed["t"]

    face_landmarks = []
    for compressed_landmark in compressed["l"]:
        has_z = compressed_landmark["z"]
        point_size = 3 if has_z else 2
        landmarks = []
        for i in range(0, len(compressed_landmark["p"]), point_size):
            landmark = {
                "x": compressed_landmark["p"][i]/QUANTIZATION_AMOUNT,
                "y": compressed_landmark["p"][i + 1]/QUANTIZATION_AMOUNT,
                "z": None if not has_z else compressed_landmark["p"][i + 2]/QUANTIZATION_AMOUNT,
                "visibility": 0,
            }
            landmarks.append(landmark)
        face_landmarks.append(landmarks)

    face_blendshapes = []
    for classification in compressed["b"]:
        blendshape = {"categories": [
            {
                "score": (classification["s"][i])/QUANTIZATION_AMOUNT,
                "index": classification["i"][i],
                "categoryName": BLENDSHAPE_CATEGORY_NAMES[classification["c"][i]],
                "displayName": "",
            }
            for i in range(len(classification["c"]))
        ], "headIndex": -1, "headName": ""}
        face_blendshapes.append(blendshape)

    return {
        "timeStamp": timeStamp,
        "faceBlendshapes": face_blendshapes,
        "faceLandmarks": face_landmarks,        
        "facialTransformationMatrixes": facial_transformation_matrices,
    }

def fetch_time_series(url, file_type, base_filename, filename, authorization, verify=True):
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/tab-separated-values' if file_type == 'tsv' else 'application/json',
        'Content-Type': 'application/json',
        'Authorization': authorization,
    }

    with requests.get(url, headers=headers, stream=True, verify=verify) as r:
        # Optional: Check status code, etc.
        if r.status_code == 500:
            print("Server error 500, exiting.")
            exit()

        content_disposition = r.headers.get('Content-Disposition')
        location = r.headers.get('Location')
        
        # If the server gives a content-disposition filename, rename local file accordingly
        if content_disposition:
            value, params = cgi.parse_header(content_disposition)
            filename = base_filename + params['filename']

        # Check if it's gzipped
        is_gzip = ('gzip' in r.headers.get('Content-Encoding', '')) or ('gzip' in r.headers.get('Content-Type', ''))

        # Grab the 'Content-Length' if available
        # content_length_str = r.headers.get('Content-Length')
        # expected_size = None
        # if content_length_str is not None:
        #     try:
        #         expected_size = int(content_length_str)
        #     except ValueError:
        #         pass  # If it fails to parse, we ignore

        # Remove any .gz extension from our local filename, if present
        filename = filename.replace('.gz', '')

        # Write chunks
        with open(filename, 'wb') as fd:
            if is_gzip:
                with gzip.GzipFile(fileobj=r.raw, mode='rb') as gzipped_stream:
                    for chunk in iter(lambda: gzipped_stream.read(128), b''):
                        fd.write(chunk)
            else:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)

    # # Closed the file, do a size check if we have an expected_size
    # if expected_size is not None:
    #     actual_size = os.path.getsize(filename)
    #     if abs(expected_size - actual_size) > 100:  # allow 100 bytes tolerance
    #         print(f"Warning: File size mismatch for {filename}. "
    #               f"Expected ~{expected_size}, got {actual_size}")

    return filename

def convert_msgpack_to_ndjson(final_filename, ndjson_filename):
    """
    Converts a MsgPack file into an NDJSON file.

    Args:
        final_filename (str): Path to the input MsgPack file.
        ndjson_filename (str): Path to the output NDJSON file.
    """
    try:
        # Open and read the MsgPack file
        with open(final_filename, 'rb') as msgpack_file:
            unpacker = msgpack.Unpacker(msgpack_file)
            with open(ndjson_filename, 'w') as ndjson_file:
                for obj in unpacker:
                    if not obj or obj == {}:
                        continue
                    ndjson_file.write(json.dumps(obj) + '\n')

        print(f"Data successfully converted from MsgPack to NDJSON: {ndjson_filename}")

    except Exception as e:
        print(f"Error during conversion: {e}")

