from typing import Protocol, TypeVar

In = TypeVar("I")
Out = TypeVar("O")


class Stage(Protocol[In, Out]):
    name: str
    input_type: type[In]
    output_type: type[Out]

    def run(self, input: In) -> Out: ...