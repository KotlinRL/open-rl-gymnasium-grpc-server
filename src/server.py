import grpc
from concurrent import futures
import gymnasium as gym
import numpy as np
from grpc import StatusCode
from Env_pb2_grpc import EnvServicer, add_EnvServicer_to_server
from google.protobuf.struct_pb2 import Struct
from Env_pb2 import (
    MakeResponse,
    SpaceRequest,
    SpaceResponse,
    ResetResponse,
    StepResponse,
    RenderResponse,
    Empty
)
from mapper import (
    ndarray_to_proto,
    gym_space_to_proto,
    gym_to_proto_observation,
    proto_to_gym_action,
    gym_to_proto_info
)

class EnvService(EnvServicer):
    """
    Implementation of the Env gRPC service.
    """

    def __init__(self):
        """
        Initialize the EnvService with a dictionary to store environment instances
        and a separate dictionary to track rendering flags.
        """
        super().__init__()
        self.envs = {}  # A dictionary to store environment instances by their handles
        self.render_flags = {}  # A dictionary to track whether rendering is enabled per environment

    def Make(self, request, context):
        """
        Handles the make request to create a new environment instance.

        Args:
            request: The MakeRequest containing environment id and options.
            context: gRPC context.

        Returns:
            An Env_pb2.MakeResponse containing the environment handle.
        """
        try:
            env_id = request.env_id
            render_mode = "rgb_array" if request.render else None
            options = {key: value for key, value in request.options.items()}

            env_instance = gym.make(env_id, render_mode=render_mode, **options)
            env_handle = str(id(env_instance))

            # Store the environment and render flag
            self.envs[env_handle] = env_instance
            self.render_flags[env_handle] = request.render

            metadata_struct = Struct()
            metadata_struct.update(env_instance.metadata)

            return MakeResponse(env_handle=env_handle, metadata=metadata_struct)
        except gym.error.Error as e:
            context.set_details(f"Failed to create environment: {str(e)}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return MakeResponse()
        except Exception as e:
            self._handle_exception(context, "Unexpected error during environment creation", e)
            return MakeResponse()

    def GetSpace(self, request, context):
        """
        Handles the get_space request to retrieve information about the observation
        or action space.

        Args:
            request: The SpaceRequest containing env_handle and space_type.
            context: gRPC context.

        Returns:
            An Env_pb2.SpaceResponse describing the requested space.
        """
        try:
            env_instance = self._get_env_instance(request.env_handle, context)
            if not env_instance:
                return SpaceResponse()

            space = (env_instance.observation_space if request.space_type == SpaceRequest.OBSERVATION
                     else env_instance.action_space)
            grpc_space = gym_space_to_proto(space)

            if not grpc_space:
                context.set_details(f"Unsupported space type: '{type(space).__name__}'.")
                context.set_code(StatusCode.UNIMPLEMENTED)
                return SpaceResponse()

            return SpaceResponse(space=grpc_space)
        except Exception as e:
            self._handle_exception(context, "Unexpected error during get_space", e)
            return SpaceResponse()

    def Reset(self, request, context):
        """
        Handles the reset request to reset the environment to its initial state.

        Args:
            request: The ResetRequest containing env_handle, optional seed, and options.
            context: gRPC context.

        Returns:
            An Env_pb2.ResetResponse containing the initial observation and optional info.
        """
        try:
            env_instance = self._get_env_instance(request.env_handle, context)
            if not env_instance:
                return ResetResponse()

            observation = env_instance.reset(seed=request.seed if request.HasField("seed") else None)[0]
            grpc_observation = gym_to_proto_observation(observation)

            return ResetResponse(observation=grpc_observation)
        except Exception as e:
            self._handle_exception(context, "Unexpected error during reset", e)
            return ResetResponse()

    def Step(self, request, context):
        """
        Handles the step request to execute a single action in the environment.

        Args:
            request: The StepRequest containing env_handle and action.
            context: gRPC context.

        Returns:
            An Env_pb2.StepResponse containing observation, reward, termination, truncation, and additional info.
        """
        try:
            env_instance = self._get_env_instance(request.env_handle, context)
            if not env_instance:
                return StepResponse()

            action = proto_to_gym_action(request.action)
            observation, reward, terminated, truncated, info = env_instance.step(action)

            grpc_observation = gym_to_proto_observation(observation)
            grpc_info = gym_to_proto_info(info)

            return StepResponse(
                observation=grpc_observation,
                reward=reward,
                terminated=terminated,
                truncated=truncated,
                info=grpc_info,
            )
        except Exception as e:
            self._handle_exception(context, "Unexpected error during step", e)
            return StepResponse()

    def Render(self, request, context):
        """
        Handles the render request to render the current state of the environment.

        Args:
            request: The RenderRequest containing the environment handle.
            context: gRPC context.

        Returns:
            An Env_pb2.RenderResponse containing the rendered frame (RGB, ANSI, or empty).
        """
        try:
            # Retrieve the environment instance
            env_instance = self.envs.get(request.env_handle)
            if not env_instance:
                context.set_details("Environment not found.")
                context.set_code(StatusCode.NOT_FOUND)
                return RenderResponse()

            # Check the render flag
            if not self.render_flags.get(request.env_handle, False):
                return RenderResponse(empt=Empty())

            # Render the frame
            frame = env_instance.render()
            if isinstance(frame, np.ndarray):
                return RenderResponse(rgb_array=ndarray_to_proto(frame))
            elif isinstance(frame, str):
                return RenderResponse(ansi=frame)
            return RenderResponse(empty=Empty())
        except Exception as e:
            self._handle_exception(context, "Unexpected error during render", e)
            return RenderResponse()

    def Close(self, request, context):
        """
        Handles the close request to clean up and remove the specified environment.

        Args:
            request: The CloseRequest containing the environment handle.
            context: gRPC context.

        Returns:
            An Env_pb2.Empty response indicating the operation was successful.
        """
        try:
            env_instance = self._get_env_instance(request.env_handle, context)
            if not env_instance:
                return Empty()

            env_instance.close()
            self.envs.pop(request.env_handle, None)
            self.render_flags.pop(request.env_handle, None)

            return Empty()
        except Exception as e:
            self._handle_exception(context, "Unexpected error during close", e)
            return Empty()

    def _get_env_instance(self, env_handle, context):
        """
        Retrieves the environment instance corresponding to the given handle.

        Args:
            env_handle: The unique identifier of the environment.
            context: The gRPC context to set error details if the handle is invalid.

        Returns:
            The environment instance if found, None otherwise.
        """
        if env_handle not in self.envs:
            context.set_details(f"Environment with handle '{env_handle}' not found.")
            context.set_code(StatusCode.NOT_FOUND)
            return None
        return self.envs[env_handle]

    def _handle_exception(self, context, message, exception=None):
        """
        Handles errors and updates the gRPC context with appropriate details.

        Args:
            context: The gRPC context to set the error details.
            message: A description of the encountered error.
            exception (optional): The exception instance (if available).
        """
        details = f"{message}: {str(exception)}" if exception else message
        context.set_details(details)
        context.set_code(StatusCode.INTERNAL)

def serve():
    """
    Create and start the gRPC server.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_EnvServicer_to_server(EnvService(), server)

    # Bind the server to a specific port
    server.add_insecure_port("[::]:50051")
    server.start()

    print("Server running on port 50051...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down the server...")

if __name__ == "__main__":
    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    import pygame
    pygame.init()
    serve()
