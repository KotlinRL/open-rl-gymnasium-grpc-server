import unittest
import numpy as np
import gymnasium as gym

from src.Env_pb2 import (
    DType,
    NDArray,
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
)
from src.mapper import (
    ndarray_to_proto,
    proto_to_ndarray,
    gym_space_to_proto,
    gym_to_proto_observation,
    proto_to_gym_action,
)


class TestMapper(unittest.TestCase):
    # --- Test NDArray Conversions ---
    def test_ndarray_to_proto_conversion(self):
        array = np.array([[1.5, 2.5], [3.5, 4.5]], dtype=np.float32)
        proto = ndarray_to_proto(array)
        self.assertIsInstance(proto, NDArray)
        self.assertEqual(proto.dtype, DType.float32)
        self.assertEqual(proto.shape, [2, 2])
        self.assertEqual(proto.data, array.tobytes())

    def test_proto_to_ndarray_conversion(self):
        proto = NDArray(
            dtype=DType.float32,
            shape=[2, 2],
            data=np.array([[1.5, 2.5], [3.5, 4.5]], dtype=np.float32).tobytes(),
        )
        array = proto_to_ndarray(proto)
        self.assertIsInstance(array, np.ndarray)
        self.assertEqual(array.dtype, np.float32)
        self.assertTrue(np.array_equal(array, np.array([[1.5, 2.5], [3.5, 4.5]], dtype=np.float32)))

    # --- Test Gym Space to Protobuf Space ---
    def test_gym_box_space_to_proto(self):
        space = gym.spaces.Box(low=-1.0, high=1.0, shape=(2, 2), dtype=np.float32)
        proto = gym_space_to_proto(space)
        self.assertIsInstance(proto, Space)
        self.assertTrue(proto.HasField("box"))
        self.assertEqual(proto.box.low.dtype, DType.float32)
        self.assertEqual(proto.box.high.dtype, DType.float32)

    def test_gym_discrete_space_to_proto(self):
        space = gym.spaces.Discrete(n=5)
        proto = gym_space_to_proto(space)
        self.assertIsInstance(proto, Space)
        self.assertTrue(proto.HasField("discrete"))
        self.assertEqual(proto.discrete.n, 5)

    def test_gym_multidiscrete_space_to_proto(self):
        space = gym.spaces.MultiDiscrete([2, 3, 4])
        proto = gym_space_to_proto(space)
        self.assertIsInstance(proto, Space)
        self.assertTrue(proto.HasField("multidiscrete"))
        self.assertEqual(proto.multidiscrete.nvec, [2, 3, 4])

    def test_gym_multibinary_space_to_proto(self):
        space = gym.spaces.MultiBinary(n=3)
        proto = gym_space_to_proto(space)
        self.assertIsInstance(proto, Space)
        self.assertTrue(proto.HasField("multibinary"))
        self.assertEqual(proto.multibinary.n, 3)

    def test_gym_tuple_space_to_proto(self):
        space = gym.spaces.Tuple([gym.spaces.Discrete(n=5), gym.spaces.Discrete(n=10)])
        proto = gym_space_to_proto(space)
        self.assertIsInstance(proto, Space)
        self.assertTrue(proto.HasField("tuple"))
        self.assertEqual(len(proto.tuple.spaces), 2)
        self.assertEqual(proto.tuple.spaces[0].discrete.n, 5)
        self.assertEqual(proto.tuple.spaces[1].discrete.n, 10)

    def test_gym_dict_space_to_proto(self):
        space = gym.spaces.Dict(
            {}
        )
        proto = gym_space_to_proto(space)
        self.assertIsInstance(proto, Space)
        self.assertTrue(proto.HasField("dict"))
        self.assertEqual(len(proto.dict.spaces), 0)

    # --- Test Gym Observation to Protobuf Observation ---
    def test_gym_array_to_proto_observation_array(self):
        observation = np.array([1.5, 2.5, 3.5], dtype=np.float32)
        proto = gym_to_proto_observation(observation)
        self.assertIsInstance(proto, Observation)
        self.assertTrue(proto.HasField("array"))
        self.assertEqual(proto.array.dtype, DType.float32)
        self.assertEqual(proto.array.shape, [3])

    def test_gym_int32_to_proto_observation_int32(self):
        observation = 3
        proto = gym_to_proto_observation(observation)
        self.assertIsInstance(proto, Observation)
        self.assertTrue(proto.HasField("int32"))
        self.assertEqual(proto.int32, observation)

    def test_gym_float_to_proto_observation_float32(self):
        observation = 3.5
        proto = gym_to_proto_observation(observation)
        self.assertIsInstance(proto, Observation)
        self.assertTrue(proto.HasField("float"))
        self.assertEqual(proto.float, observation)

    def test_gym_string_to_proto_observation_string(self):
        observation = "Hello, world!"
        proto = gym_to_proto_observation(observation)
        self.assertIsInstance(proto, Observation)
        self.assertTrue(proto.HasField("string"))
        self.assertEqual(proto.string, observation)

    def test_gym_tuple_to_proto_observation_tuple(self):
        observation = (1.5, 2.5, 3.5)
        proto = gym_to_proto_observation(observation)
        self.assertIsInstance(proto, Observation)
        self.assertTrue(proto.HasField("tuple"))
        self.assertEqual(len(proto.tuple.items), 3)
        self.assertEqual(proto.tuple.items[0].float, 1.5)
        self.assertEqual(proto.tuple.items[1].float, 2.5)
        self.assertEqual(proto.tuple.items[2].float, 3.5)

    def test_gym_dict_to_proto_observation_map(self):
        observation = {"a": 1.5, "b": 2.5, "c": 3.5}
        proto = gym_to_proto_observation(observation)
        self.assertIsInstance(proto, Observation)
        self.assertTrue(proto.HasField("map"))
        self.assertEqual(len(proto.map.items), 3)
        self.assertEqual(proto.map.items["a"].float, 1.5)
        self.assertEqual(proto.map.items["b"].float, 2.5)
        self.assertEqual(proto.map.items["c"].float, 3.5)

    # --- Test Protobuf Action to Gym Action ---
    def test_proto_array_to_gym_action(self):
        proto = Action(
            array=NDArray(
                dtype=DType.float32,
                shape=[3],
                data=np.array([1.5, 2.5, 3.5], dtype=np.float32).tobytes(),
            )
        )
        action = proto_to_gym_action(proto)
        self.assertIsInstance(action, np.ndarray)
        self.assertTrue(np.array_equal(action, np.array([1.5, 2.5, 3.5], dtype=np.float32)))

    def test_proto_int32_to_gym_action(self):
        proto = Action(int32=3)
        action = proto_to_gym_action(proto)
        self.assertIsInstance(action, int)
        self.assertEqual(action, 3)

    def test_proto_float_to_gym_action(self):
        proto = Action(float=3.5)
        action = proto_to_gym_action(proto)
        self.assertIsInstance(action, float)
        self.assertEqual(action, 3.5)

    def test_proto_string_to_gym_action(self):
        proto = Action(string="Hello, world!")
        action = proto_to_gym_action(proto)
        self.assertIsInstance(action, str)
        self.assertEqual(action, "Hello, world!")

    def test_proto_tuple_to_gym_action(self):
        proto = Action(
            tuple=TupleAction(
                items=[
                    Action(array=NDArray(dtype=DType.float32, shape=[1], data=np.array([1.5], dtype=np.float32).tobytes()))
                ]
            )
        )
        action = proto_to_gym_action(proto)
        self.assertIsInstance(action, tuple)
        self.assertEqual(len(action), 1)
        self.assertIsInstance(action[0], np.ndarray)
        self.assertTrue(np.array_equal(action[0], np.array([1.5], dtype=np.float32)))

    def test_proto_map_to_gym_action(self):
        proto = Action(map=MapAction())
        action = proto_to_gym_action(proto)
        self.assertIsInstance(action, dict)
        self.assertEqual(len(action), 0)

if __name__ == "__main__":
    unittest.main()