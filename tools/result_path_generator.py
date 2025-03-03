import os


class ResultPathGenerator:
    def __init__(self, result_root_dir, study_id):
        self.result_root_dir = result_root_dir
        self.study_id = study_id

    def result_path_for(self, filename, user_id=None):
        """Generate a path for a result file."""
        path = os.path.join(self.result_root_dir, str(self.study_id))
        if user_id:
            path = os.path.join(path, f'user_{user_id}')
        os.path.isdir(path) or os.makedirs(path, exist_ok=True)
        return os.path.join(path, filename)
