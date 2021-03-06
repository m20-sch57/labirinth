from typing import Any, Dict, Union, List

class Button:
    btn_type: str
    turns: List[str]
    image: str

    def __str__(self) -> str: ...

    def get(self, *args, **kwargs) -> Any: ...


class CommonButton(Button):
    def __init__(self, turns: List[str], image: str) -> None: ...

    def get(self, ats: List[str], imagepath: str) -> Dict[str, Union[str, List[str]]]: ...


class DirectionButton(Button):
    def __init__(self, turns: List[str], image: str) -> None: ...

    def get(self, ats: List[str], imagepath: str) -> Dict[str, Union[str, List[str]]]: ...


class ListButton(Button):
    turn_images: List[str]

    def __init__(self, turns: List[str], image: str, turn_images: List[str]) -> None: ...

    def get(self, ats: List[str], imagepath: str) -> Dict[str, Union[str, List[str]]]: ...
