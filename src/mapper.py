import gymnasium as gym
import numpy as np

from Env_pb2 import (
    DType,
    NDArray,
    TextSpace,
    SequenceSpace,
    OneOfSpace,
    GraphSpace,
    BoxSpace,
    Observation,
    DiscreteSpace,
    MultiDiscreteSpace,
    MultiBinarySpace,
    TupleSpace,
    DictSpace,
    Space,
    TupleObservation,
    MapObservation,
    Observation,
    TupleAction,
    MapAction,
    Action,
    Info,
    MakeResponse,
    SpaceRequest,
    SpaceResponse,
    ResetResponse,
    StepResponse,
    Info,
)

# === DTYPE MAPPING HELPERS ===
DTYPE_MAPPING = {
    "float32": DType.float32,
    "float64": DType.float64,
    "int32": DType.int32,
    "int64": DType.int64,
    "bool": DType.bool,
    "uint8": DType.uint8,
}

REVERSE_DTYPE_MAPPING = {v: k for k, v in DTYPE_MAPPING.items()}

def get_proto_dtype(np_dtype):
    """
    Map numpy dtype to Protobuf DType.
    """
    dtype_name = np_dtype.name
    if dtype_name not in DTYPE_MAPPING:
        raise ValueError(f"Unsupported numpy dtype: {dtype_name}")
    return DTYPE_MAPPING[dtype_name]

def get_np_dtype(proto_dtype):
    """
    Map Protobuf DType to numpy dtype.
    """
    if proto_dtype not in REVERSE_DTYPE_MAPPING:
        raise ValueError(f"Unsupported Protobuf DType: {proto_dtype}")
    return np.dtype(REVERSE_DTYPE_MAPPING[proto_dtype])

# === NDARRAY CONVERSION HELPERS ===
def ndarray_to_proto(ndarray):
    """
    Convert numpy array to Protobuf NDArray message.
    """
    return NDArray(
        dtype=get_proto_dtype(ndarray.dtype),
        shape=list(ndarray.shape),
        data=ndarray.tobytes(),
    )

def proto_to_ndarray(proto):
    """
    Convert Protobuf NDArray to numpy array.
    """
    dtype = get_np_dtype(proto.dtype)
    return np.frombuffer(proto.data, dtype=dtype).reshape(proto.shape)

# === SPACE MAPPING ===
def gym_space_to_proto(space):
    """
    Convert Gym space to Protobuf Space message.
    """
    if isinstance(space, gym.spaces.Box):
        return Space(
            box=BoxSpace(
                low=ndarray_to_proto(space.low),
                high=ndarray_to_proto(space.high),
                shape=list(space.shape),
                dtype=get_proto_dtype(space.dtype),
            )
        )
    elif isinstance(space, gym.spaces.Discrete):
        return Space(
            discrete=DiscreteSpace(n=space.n, start=getattr(space, "start", 0))
        )
    elif isinstance(space, gym.spaces.MultiDiscrete):
        return Space(
            multidiscrete=MultiDiscreteSpace(nvec=list(space.nvec))
        )
    elif isinstance(space, gym.spaces.MultiBinary):
        return Space(
            multibinary=MultiBinarySpace(n=space.n)
        )
    elif isinstance(space, gym.spaces.Tuple):
        return Space(
            tuple=TupleSpace(
                spaces=[gym_space_to_proto(s) for s in space.spaces]
            )
        )
    elif isinstance(space, gym.spaces.Dict):
        return Space(
            dict=DictSpace(
                spaces={key: gym_space_to_proto(value) for key, value in space.spaces.items()}
            )
        )
    elif isinstance(space, gym.spaces.Text):
        return Space(
            text=TextSpace(
                min_length=space.min_length,
                max_length=space.max_length
            )
        )
    elif isinstance(space, gym.spaces.Sequence):
        return Space(
            sequence=SequenceSpace(
                space=gym_space_to_proto(space.feature_space),
                stack=space.stack
            )
        )
    elif isinstance(space, gym.spaces.OneOf):
        return Space(
            oneof=OneOfSpace(
                spaces=[gym_space_to_proto(s) for s in space.spaces]
            )
        )
    elif isinstance(space, gym.spaces.Graph):
        return Space(
            graph=GraphSpace(
                node_space=gym_space_to_proto(space.node_space),
                edge_space=gym_space_to_proto(space.edge_space)
            )
        )
    else:
        raise ValueError(f"Unsupported Gym space type: {type(space)}")

# === OBSERVATION MAPPING ===
def gym_to_proto_observation(obs):
    """
    Convert Gym observation to Protobuf Observation message.
    """
    if isinstance(obs, np.ndarray):
        return Observation(array=ndarray_to_proto(obs))
    elif isinstance(obs, int):
        return Observation(int32=obs)
    elif isinstance(obs, float):
        return Observation(float=obs)
    elif isinstance(obs, str):
        return Observation(string=obs)
    elif isinstance(obs, tuple):
        return Observation(
            tuple=TupleObservation(
                items=[gym_to_proto_observation(item) for item in obs]
            )
        )
    elif isinstance(obs, dict):
        return Observation(
            map=MapObservation(
                items={key: gym_to_proto_observation(value) for key, value in obs.items()}
            )
        )
    else:
        raise ValueError(f"Unsupported observation type: {type(obs)}")

# === ACTION MAPPING ===
def proto_to_gym_action(proto):
    """
    Convert Protobuf Action message to Gym action.
    """
    field = proto.WhichOneof("value")
    if field == "array":
        return proto_to_ndarray(proto.array)
    elif field == "int32":
        return proto.int32
    elif field == "float":
        return proto.float
    elif field == "string":
        return proto.string
    elif field == "tuple":
        return tuple(proto_to_gym_action(item) for item in proto.tuple.items)
    elif field == "map":
        return {item.key: proto_to_gym_action(item.value) for item in proto.map.items}
    else:
        raise ValueError(f"Unsupported Protobuf action field: {field}")

def gym_to_proto_info(info):
    return Info(data=[Info.DataEntry(key=str(k), value=str(v)) for k, v in info.items()])
