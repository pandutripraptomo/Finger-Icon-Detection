import cv2
import mediapipe as mp
import numpy as np

# Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Membaca ikon
j1_icon = cv2.imread('icons/j1.png', cv2.IMREAD_UNCHANGED)  # Jempol
j2_icon = cv2.imread('icons/j2.png', cv2.IMREAD_UNCHANGED)  # Telunjuk
j3_icon = cv2.imread('icons/j3.png', cv2.IMREAD_UNCHANGED)  # Kelingking

# Fungsi untuk mengubah ukuran ikon
def resize_icon(icon, scale):
    new_width = int(icon.shape[1] * scale)
    new_height = int(icon.shape[0] * scale)
    return cv2.resize(icon, (new_width, new_height), interpolation=cv2.INTER_AREA)

# Mengubah ukuran ikon agar lebih kecil
j1_icon = resize_icon(j1_icon, 0.2)  # Jempol
j2_icon = resize_icon(j2_icon, 0.2)  # Telunjuk
j3_icon = resize_icon(j3_icon, 0.2)  # Kelingking

# Fungsi untuk menampilkan ikon di frame
def overlay_icon(frame, icon, position):
    h, w, _ = icon.shape
    x, y = position
    if y < 0 or x < 0 or y + h > frame.shape[0] or x + w > frame.shape[1]:
        return frame
    roi = frame[y:y+h, x:x+w]
    icon_rgb = icon[:, :, :3]  # Mengambil RGB dari ikon
    icon_alpha = icon[:, :, 3] / 255.0  # Transparansi ikon

    for c in range(3):
        roi[:, :, c] = roi[:, :, c] * (1 - icon_alpha) + icon_rgb[:, :, c] * icon_alpha
    frame[y:y+h, x:x+w] = roi
    return frame

def main():
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # Membalik gambar
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Mendapatkan posisi landmark jari
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]  # Punggung tangan (wrist)

                # Menyusun koordinat jari
                thumb_y, thumb_x = int(thumb_tip.y * frame.shape[0]), int(thumb_tip.x * frame.shape[1])
                index_y, index_x = int(index_tip.y * frame.shape[0]), int(index_tip.x * frame.shape[1])
                pinky_y, pinky_x = int(pinky_tip.y * frame.shape[0]), int(pinky_tip.x * frame.shape[1])
                wrist_y, wrist_x = int(wrist.y * frame.shape[0]), int(wrist.x * frame.shape[1])

                # Menentukan apakah jari diangkat dengan threshold lebih fleksibel
                thumb_lifted = thumb_y < wrist_y - 50  # Jempol terangkat jika lebih tinggi dari wrist dengan margin 50 piksel
                index_lifted = index_y < wrist_y - 50  # Telunjuk terangkat jika lebih tinggi dari wrist dengan margin 50 piksel
                pinky_lifted = pinky_y < wrist_y - 50  # Kelingking terangkat jika lebih tinggi dari wrist dengan margin 50 piksel

                # Menempatkan ikon jempol (I) jika jempol terangkat
                if thumb_lifted:
                    thumb_icon_pos = (thumb_x - j1_icon.shape[1] // 2, thumb_y - j1_icon.shape[0] - 10)
                    frame = overlay_icon(frame, j1_icon, thumb_icon_pos)

                # Menempatkan ikon telunjuk (II) jika telunjuk terangkat
                if index_lifted:
                    index_icon_pos = (index_x - j2_icon.shape[1] // 2, index_y - j2_icon.shape[0] - 10)
                    frame = overlay_icon(frame, j2_icon, index_icon_pos)

                # Menempatkan ikon kelingking (III) jika kelingking terangkat
                if pinky_lifted:
                    pinky_icon_pos = (pinky_x - j3_icon.shape[1] // 2, pinky_y - j3_icon.shape[0] - 10)
                    frame = overlay_icon(frame, j3_icon, pinky_icon_pos)

        # Menampilkan frame yang telah diproses
        cv2.imshow('Finger Icons', frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Tekan ESC untuk keluar
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
