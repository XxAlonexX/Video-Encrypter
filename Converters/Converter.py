import cv2
import numpy as np
import base58
import json
from tqdm import tqdm
from PIL import Image
import io

class VideoConverter:
    def __init__(self):
        self.metadata = {
            "fps": 0,
            "width": 0,
            "height": 0,
            "total_frames": 0
        }

    def video_to_text(self, video_path, output_path=None, progress_callback=None):
        cap = cv2.VideoCapture(video_path)
        self.metadata["fps"] = int(cap.get(cv2.CAP_PROP_FPS))
        self.metadata["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.metadata["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.metadata["total_frames"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_data = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            success, encoded_frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
            if not success:
                continue
            frame_text = base58.b58encode(encoded_frame.tobytes()).decode()
            frames_data.append(frame_text)
            frame_count += 1
            if progress_callback:
                progress = (frame_count / self.metadata["total_frames"]) * 100
                progress_callback(progress)
            else:
                print(f"\rProcessing: {frame_count}/{self.metadata['total_frames']} frames ({frame_count/self.metadata['total_frames']*100:.1f}%)", end="")

        cap.release()
        print("\nEncoding completed!")
        final_data = {
            "metadata": self.metadata,
            "frames": frames_data
        }
        text_data = json.dumps(final_data)
        if output_path:
            with open(output_path, 'w') as f:
                f.write(text_data)
            return f"Video converted and saved to {output_path}"
        return text_data

    def text_to_video(self, text_input, output_path, progress_callback=None):
        if isinstance(text_input, str) and text_input.endswith('.txt'):
            with open(text_input, 'r') as f:
                data = json.loads(f.read())
        else:
            data = json.loads(text_input)
        metadata = data["metadata"]
        frames = data["frames"]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, metadata["fps"], (metadata["width"], metadata["height"]))

        for i, frame_text in enumerate(frames):
            frame_bytes = base58.b58decode(frame_text)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            out.write(frame)
            if progress_callback:
                progress = (i / len(frames)) * 100
                progress_callback(progress)
            else:
                print(f"\rProcessing: {i+1}/{len(frames)} frames ({(i+1)/len(frames)*100:.1f}%)", end="")

        out.release()
        print("\nDecoding completed!")
        return f"Video reconstructed and saved to {output_path}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert video to text and back')
    parser.add_argument('mode', choices=['encode', 'decode'], help='Operation mode')
    parser.add_argument('input_path', help='Input file path')
    parser.add_argument('output_path', help='Output file path')

    args = parser.parse_args()
    converter = VideoConverter()

    if args.mode == 'encode':
        print(converter.video_to_text(args.input_path, args.output_path))
    else:
        print(converter.text_to_video(args.input_path, args.output_path))

if __name__ == "__main__":
    main()
