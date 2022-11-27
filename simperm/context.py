from collections import UserDict


class Context(UserDict):
    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def __hash__(self):
        _res = []
        _size = 0
        for k, v in self.data.items():
            _res.append(k.__hash__() ^ v.__hash__())
            _size += len(k) + len(v)
        return hash(tuple(_res) + (_size,))

    def __repr__(self):
        return (
            f"[{'|'.join(f'{k}={v}' for k, v in self.data.items())}]"
            if self.data
            else "[none]"
        )

    @classmethod
    def from_string(cls, data: str):
        _data = {}
        if data != "[none]":
            for seg in data[1:-2].split("|"):
                segs = seg.split("=")
                _data[segs[0]] = segs[1]
        return cls(**_data)

