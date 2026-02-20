# # # # utils.py
# # # import cv2
# # # import torch
# # # import numpy as np
# # # import torchvision.transforms as transforms

# # # IMG_SIZE = 224

# # # transform = transforms.Compose([
# # #     transforms.ToPILImage(),
# # #     transforms.Resize((IMG_SIZE, IMG_SIZE)),
# # #     transforms.ToTensor(),
# # #     transforms.Normalize(mean=[0.485, 0.456, 0.406],
# # #                          std=[0.229, 0.224, 0.225])
# # # ])

# # # def compute_optical_flow(prev_frame, next_frame):
# # #     prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
# # #     next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
# # #     return cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None,
# # #                                         0.5, 3, 15, 3, 5, 1.2, 0)

# # # def preprocess_video(video_path):
# # #     cap = cv2.VideoCapture(video_path)
# # #     frames, flow_frames = [], []
# # #     success, prev_frame = cap.read()

# # #     while success:
# # #         frames.append(prev_frame)
# # #         success, next_frame = cap.read()
# # #         if success:
# # #             flow = compute_optical_flow(prev_frame, next_frame)
# # #             flow_frames.append(flow)
# # #             prev_frame = next_frame
# # #     cap.release()

# # #     if len(frames) < 3:
# # #         frame = frames[0]
# # #         flow_frame = np.zeros((IMG_SIZE, IMG_SIZE, 2), dtype=np.float32)
# # #     else:
# # #         mid = len(frames) // 2
# # #         frame = frames[mid]
# # #         flow_frame = flow_frames[mid - 1]

# # #     frame = transform(frame).unsqueeze(0)
# # #     flow_tensor = torch.tensor(cv2.resize(flow_frame, (IMG_SIZE, IMG_SIZE))).permute(2, 0, 1).unsqueeze(0)

# # #     return frame, flow_tensor
# # # utils.py
# # import cv2
# # import torch
# # import numpy as np
# # import torchvision.transforms as transforms
# # import face_recognition  # pip install face_recognition

# # IMG_SIZE = 224

# # transform = transforms.Compose([
# #     transforms.ToPILImage(),
# #     transforms.Resize((IMG_SIZE, IMG_SIZE)),
# #     transforms.ToTensor(),
# #     transforms.Normalize(mean=[0.485, 0.456, 0.406],
# #                          std=[0.229, 0.224, 0.225])
# # ])

# # def compute_optical_flow(prev_frame, next_frame):
# #     prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
# #     next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
# #     return cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None,
# #                                         0.5, 3, 15, 3, 5, 1.2, 0)

# # def crop_face(frame):
# #     # Use face_recognition to detect faces and crop the first face
# #     rgb_frame = frame[:, :, ::-1]  # BGR to RGB for face_recognition
# #     face_locations = face_recognition.batch_face_locations([rgb_frame])
# #     if face_locations and len(face_locations[0]) > 0:
# #         top, right, bottom, left = face_locations[0][0]
# #         face = frame[top:bottom, left:right]
# #         return face
# #     else:
# #         # If no face found, return original frame (or optionally a black image)
# #         return frame

# # def preprocess_video(video_path):
# #     cap = cv2.VideoCapture(video_path)
# #     frames, flow_frames = [], []
# #     success, prev_frame = cap.read()

# #     while success:
# #         # Crop face from the frame before adding
# #         face_frame = crop_face(prev_frame)
# #         frames.append(face_frame)
# #         success, next_frame = cap.read()
# #         if success:
# #             flow = compute_optical_flow(prev_frame, next_frame)
# #             flow_frames.append(flow)
# #             prev_frame = next_frame
# #     cap.release()

# #     if len(frames) < 3:
# #         frame = frames[0]
# #         flow_frame = np.zeros((IMG_SIZE, IMG_SIZE, 2), dtype=np.float32)
# #     else:
# #         mid = len(frames) // 2
# #         frame = frames[mid]
# #         flow_frame = flow_frames[mid - 1]

# #     frame = transform(frame).unsqueeze(0)
# #     flow_resized = cv2.resize(flow_frame, (IMG_SIZE, IMG_SIZE))
# #     flow_tensor = torch.tensor(flow_resized).permute(2, 0, 1).unsqueeze(0)

# #     return frame, flow_tensor

# import cv2
# import torch
# import numpy as np
# import torchvision.transforms as transforms

# IMG_SIZE = 224

# transform = transforms.Compose([
#     transforms.ToPILImage(),
#     transforms.Resize((IMG_SIZE, IMG_SIZE)),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406],
#                          std=[0.229, 0.224, 0.225])
# ])

# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# def compute_optical_flow(prev_frame, next_frame):
#     # Convert to grayscale (single channel) as required by calcOpticalFlowFarneback
#     prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
#     next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
#     flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None,
#                                         0.5, 3, 15, 3, 5, 1.2, 0)
#     return flow

# def crop_face(frame):
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray, 1.3, 5)
#     if len(faces) == 0:
#         return None
#     x, y, w, h = faces[0]
#     face = frame[y:y+h, x:x+w]
#     return face

# def preprocess_video(video_path):
#     cap = cv2.VideoCapture(video_path)
#     frames, flow_frames = [], []
#     success, prev_frame = cap.read()

#     while success:
#         face = crop_face(prev_frame)
#         if face is not None:
#             # Resize face to fixed IMG_SIZE
#             face_resized = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
#             frames.append(face_resized)
#         success, next_frame = cap.read()
#         if success:
#             prev_face = crop_face(prev_frame)
#             next_face = crop_face(next_frame)
#             if prev_face is not None and next_face is not None:
#                 # Resize faces before computing optical flow
#                 prev_face_resized = cv2.resize(prev_face, (IMG_SIZE, IMG_SIZE))
#                 next_face_resized = cv2.resize(next_face, (IMG_SIZE, IMG_SIZE))

#                 flow = compute_optical_flow(prev_face_resized, next_face_resized)
#                 flow_frames.append(flow)
#             prev_frame = next_frame
#     cap.release()

#     if len(frames) < 3:
#         frame = frames[0]
#         flow_frame = np.zeros((IMG_SIZE, IMG_SIZE, 2), dtype=np.float32)
#     else:
#         mid = len(frames) // 2
#         frame = frames[mid]
#         flow_frame = flow_frames[mid - 1]

#     # Transform RGB frame to tensor with normalization
#     frame = transform(frame).unsqueeze(0)  # Shape: (1, 3, IMG_SIZE, IMG_SIZE)

#     # Resize optical flow to IMG_SIZE and convert to tensor (2 channels)
#     flow_resized = cv2.resize(flow_frame, (IMG_SIZE, IMG_SIZE))
#     flow_tensor = torch.tensor(flow_resized).permute(2, 0, 1).unsqueeze(0).float()  # Shape: (1, 2, IMG_SIZE, IMG_SIZE)

#     return frame, flow_tensor
# utils.py
import cv2
import torch
import numpy as np
import torchvision.transforms as transforms

IMG_SIZE = 224

# Preprocessing transform (standard for ResNet/ViT)
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Load OpenCV's pre-trained face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def compute_optical_flow(prev_frame, next_frame):
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    next_gray = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prev_gray, next_gray, None,
                                        0.5, 3, 15, 3, 5, 1.2, 0)
    return flow

def crop_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return frame[y:y+h, x:x+w]

def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames, flow_frames = [], []
    success, prev_frame = cap.read()

    while success:
        face = crop_face(prev_frame)
        if face is not None:
            face_resized = cv2.resize(face, (IMG_SIZE, IMG_SIZE))
            frames.append(face_resized)

        success, next_frame = cap.read()
        if not success:
            break

        prev_face = crop_face(prev_frame)
        next_face = crop_face(next_frame)

        if prev_face is not None and next_face is not None:
            prev_face_resized = cv2.resize(prev_face, (IMG_SIZE, IMG_SIZE))
            next_face_resized = cv2.resize(next_face, (IMG_SIZE, IMG_SIZE))
            flow = compute_optical_flow(prev_face_resized, next_face_resized)
            flow_frames.append(flow)

        prev_frame = next_frame

    cap.release()

    # Handle edge cases: too few frames with faces
    if len(frames) == 0:
        frame_tensor = torch.zeros(1, 3, IMG_SIZE, IMG_SIZE)
        flow_tensor = torch.zeros(1, 2, IMG_SIZE, IMG_SIZE)
    elif len(frames) < 3 or len(flow_frames) < 2:
        frame_tensor = transform(frames[0]).unsqueeze(0)
        flow_tensor = torch.zeros(1, 2, IMG_SIZE, IMG_SIZE)
    else:
        mid = len(frames) // 2
        frame_tensor = transform(frames[mid]).unsqueeze(0)

        flow_resized = cv2.resize(flow_frames[mid - 1], (IMG_SIZE, IMG_SIZE))
        flow_tensor = torch.tensor(flow_resized).permute(2, 0, 1).unsqueeze(0).float()

    return frame_tensor, flow_tensor
