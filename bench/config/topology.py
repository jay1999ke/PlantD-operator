from typing import List

class ConfigKeys:
    latency = "latency"
    fail_rate = "failrate"
    stage_count = "stagecount"
    type = "type"
    type_standard = "standard"
    type_custom = "custom"

class Config:
    
    def __init__(self) -> None:
        self.type: str = ConfigKeys.type_standard
        self.latency_ms: int = 1
        self.fail_rate: float = 0.0
        self.stage_count: int = 1

class Node:

    def __init__(self) -> None:
        self.children : List[Node] = []
        self.latency_ms: int = 1
        self._fail_rate: float = 0.0

    @property
    def fail_rate(self) -> float:
        return self._fail_rate
    
    @fail_rate.setter
    def fail_rate(self, value: float) -> None:
        self._fail_rate = value
        assert 0 <= value and value <= 100

    def createStandardChild(self, cfg: Config, stage_index: int) -> None:
        if stage_index < cfg.stage_count:
            node: Node = Node()
            node.fail_rate = cfg.fail_rate
            node.latency_ms = cfg.latency_ms
            self.children.append(node)
            node.createStandardChild(cfg, stage_index + 1)

class Topology:

    def __init__(self) -> None:
        pass

def makeCleanMap(map: dict) -> dict:
    result = {}
    for key in map:
        result[key.lower()] = map[key]
    return result

def parseConfig(config: dict) -> Config:
    cfg: Config = Config()
    cfg.fail_rate = config.get(ConfigKeys.fail_rate)
    cfg.latency_ms = config.get(ConfigKeys.latency)
    cfg.stage_count = config.get(ConfigKeys.stage_count)
    cfg.type = ConfigKeys.type_standard
    return cfg

class StandardTopology(Topology):

    def __init__(self, config: Config) -> None:
        super().__init__()
        config : dict = makeCleanMap(config)

        assert config.get(ConfigKeys.fail_rate) != None
        assert config.get(ConfigKeys.latency) != None
        assert config.get(ConfigKeys.stage_count) != None
        assert config.get(ConfigKeys.type).lower() == ConfigKeys.type_standard.lower()

        self.config: Config = config
        self.root: Node = self.createDAG()

    def createDAG(self) -> Node:
        root: Node = Node()
        root.fail_rate = self.config.fail_rate
        root.latency_ms = self.config.latency_ms
        root.createStandardChild(self.config, 1)
        return root


    
