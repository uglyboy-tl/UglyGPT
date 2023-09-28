from pathlib import Path
from typing import List, Dict


IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif',
                    '.bmp', '.tiff', '.ico', '.jfif', '.webp'}
MEDIA_EXTENSIONS = {'.mp4', '.mp3', '.flv',
                    '.avi', '.mov', '.wmv', '.mkv', '.wav'}
IGNORE_EXTENSIONS = {'.bak'}

EXTENSION_MAPPING = {
    ".py": "python",
    ".md": "markdown",
    ".json": "json",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".js": "javascript",
    ".ts": "typescript",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".sh": "shell",
    ".bat": "bat",
    ".tsx": "tsx",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".swift": "swift",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".pl": "perl",
    ".php": "php",
    ".lua": "lua",
    ".r": "r",
    ".scala": "scala",
    ".groovy": "groovy",
    ".ps1": "powershell",
    "txt": "text",
}


def get_directory_structure(path: str | Path, depth=0, max_depth=3) -> str:
    base_dir = Path(path)
    dir_str = ""
    indent = '  ' * depth
    if base_dir.is_dir():
        for item in base_dir.iterdir():
            if item.name.startswith('.') or item.name == "__pycache__":
                continue
            if item.is_dir():
                dir_str += f"{indent}{item.name}/\n"
                if depth < max_depth:
                    dir_str += get_directory_structure(item,
                                                    depth + 1, max_depth)
                else:
                    dir_str += f"{indent}  ...\n"
            else:
                if item.suffix in IGNORE_EXTENSIONS:
                    continue
                dir_str += f"{indent}{item.name}\n"
    return dir_str


def generate_dict(file_list: List[Path], file_dir_dict: Dict[str, str]|Dict[Path, str]) -> Dict[Path, str]:
    # Convert relative paths in file_dir_dict to absolute paths
    absolute_file_dir_dict = {
        str(Path(key).resolve()): value for key, value in file_dir_dict.items()}

    parent_dict = {}
    new_dict = {}
    for file_path in file_list:
        path = Path(file_path)
        while path != Path('/'):
            path_str = str(path.resolve())
            if path_str in absolute_file_dir_dict:
                new_dict[file_path] = absolute_file_dir_dict[path_str]
                break
            elif path_str in parent_dict:
                new_dict[file_path] = absolute_file_dir_dict[parent_dict[path_str]]
                break
            else:
                parent = path.parent
                if str(parent.resolve()) in absolute_file_dir_dict:
                    parent_dict[path_str] = str(parent.resolve())
                path = parent
    return new_dict
