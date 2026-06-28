from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class PipelineNode:
    name: str
    deps: tuple[str, ...] = ()
    enabled: Callable[[dict], bool] = lambda ctx: True


@dataclass
class PipelineDAG:
    nodes: list[PipelineNode] = field(default_factory=list)

    def plan(self, context: dict) -> list[dict]:
        enabled = {node.name: bool(node.enabled(context)) for node in self.nodes}
        steps = []
        completed = set()
        pending = list(self.nodes)
        while pending:
            progressed = False
            for node in pending[:]:
                if not all(dep in completed for dep in node.deps if enabled.get(dep, False)):
                    continue
                steps.append(
                    {
                        "name": node.name,
                        "deps": list(node.deps),
                        "enabled": enabled[node.name],
                        "status": "pending" if enabled[node.name] else "skipped",
                    }
                )
                completed.add(node.name)
                pending.remove(node)
                progressed = True
            if not progressed:
                cycle = ", ".join(node.name for node in pending)
                raise ValueError(f"Pipeline DAG has unresolved dependencies: {cycle}")
        return steps


def transvideo_dag() -> PipelineDAG:
    return PipelineDAG(
        [
            PipelineNode("download"),
            PipelineNode("preflight", ("download",)),
            PipelineNode("extract_audio", ("preflight",), lambda ctx: ctx.get("has_audio", True)),
            PipelineNode("recognize", ("extract_audio",), lambda ctx: ctx.get("needs_recogn", True)),
            PipelineNode("timeline", ("recognize",)),
            PipelineNode("translate", ("timeline",), lambda ctx: ctx.get("needs_translate", True)),
            PipelineNode("bandmatch", ("translate",)),
            PipelineNode("dubbing", ("bandmatch",), lambda ctx: ctx.get("needs_dubbing", False)),
            PipelineNode("audio_normalize", ("dubbing",), lambda ctx: ctx.get("needs_dubbing", False)),
            PipelineNode("align", ("audio_normalize",), lambda ctx: ctx.get("needs_dubbing", False)),
            PipelineNode("subtitle_ass", ("translate",), lambda ctx: ctx.get("needs_subtitle", True)),
            PipelineNode("render", ("align", "subtitle_ass")),
            PipelineNode("cleanup", ("render",)),
        ]
    )
