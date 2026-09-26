from types import SimpleNamespace

import numpy as np
from fastapi.testclient import TestClient

import src.backend.app as app_module
from src.backend.app import app


client = TestClient(app)


def test_settings_report_larger_upload_limit():
    response = client.get('/settings')
    assert response.status_code == 200
    assert response.json()['maxFileSize'] == '500 MB'


def test_infer_video_detection_keeps_per_frame_timestamps(monkeypatch, tmp_path):
    source = tmp_path / 'sample.mp4'
    source.write_bytes(b'fake-video')

    class FakeVideoCapture:
        def __init__(self, path):
            self.frames = [
                np.zeros((20, 20, 3), dtype=np.uint8),
                np.zeros((20, 20, 3), dtype=np.uint8),
                np.zeros((20, 20, 3), dtype=np.uint8),
            ]
            self.index = 0

        def isOpened(self):
            return True

        def get(self, prop):
            if prop == 5:
                return 2.0
            return 0.0

        def read(self):
            if self.index >= len(self.frames):
                return False, None
            frame = self.frames[self.index]
            self.index += 1
            return True, frame

        def release(self):
            return None

    class FakeBox:
        cls = [0]
        conf = [0.9]
        xyxy = [[0.0, 0.0, 10.0, 10.0]]

    fake_result = SimpleNamespace(boxes=[FakeBox()], orig_shape=(20, 20))

    class FakeModel:
        names = {0: 'vehicle'}

        def __call__(self, *args, **kwargs):
            return [fake_result]

    monkeypatch.setattr(app_module.cv2, 'VideoCapture', FakeVideoCapture)
    monkeypatch.setattr(app_module, 'model', FakeModel())

    result = app_module.infer_video_detection(source, conf=0.25, iou=0.45, imgsz=640)

    assert len(result['videoFrames']) == 3
    assert [frame['timestamp'] for frame in result['videoFrames']] == [0.0, 0.5, 1.0]
    assert result['videoFrames'][0]['detections'][0]['className'] == 'vehicle'


def test_infer_video_detection_processes_full_video_length(monkeypatch, tmp_path):
    source = tmp_path / 'long_sample.mp4'
    source.write_bytes(b'fake-video')

    class FakeVideoCapture:
        def __init__(self, path):
            self.frames = [np.zeros((20, 20, 3), dtype=np.uint8) for _ in range(150)]
            self.index = 0

        def isOpened(self):
            return True

        def get(self, prop):
            if prop == 5:
                return 30.0
            return 0.0

        def read(self):
            if self.index >= len(self.frames):
                return False, None
            frame = self.frames[self.index]
            self.index += 1
            return True, frame

        def release(self):
            return None

    class FakeBox:
        cls = [0]
        conf = [0.9]
        xyxy = [[0.0, 0.0, 10.0, 10.0]]

    fake_result = SimpleNamespace(boxes=[FakeBox()], orig_shape=(20, 20))

    class FakeModel:
        names = {0: 'vehicle'}

        def __call__(self, *args, **kwargs):
            return [fake_result]

    monkeypatch.setattr(app_module.cv2, 'VideoCapture', FakeVideoCapture)
    monkeypatch.setattr(app_module, 'model', FakeModel())

    result = app_module.infer_video_detection(source, conf=0.25, iou=0.45, imgsz=640)

    assert len(result['videoFrames']) == 150
    assert result['videoFrames'][-1]['timestamp'] == round(149 / 30.0, 3)


def test_ensemble_merge_deduplicates_overlapping_boxes():
    class BoxA:
        cls = [0]
        conf = [0.9]
        xyxy = [[0.0, 0.0, 10.0, 10.0]]

    class BoxB:
        cls = [0]
        conf = [0.8]
        xyxy = [[1.0, 1.0, 11.0, 11.0]]

    first_result = SimpleNamespace(boxes=[BoxA()], orig_shape=(20, 20))
    second_result = SimpleNamespace(boxes=[BoxB()], orig_shape=(20, 20))

    merged = app_module.merge_model_results([first_result, second_result], iou_threshold=0.45)

    assert len(merged) == 1
    assert merged[0]['confidence'] >= 0.8
    assert merged[0]['className'] == 'vehicle'
