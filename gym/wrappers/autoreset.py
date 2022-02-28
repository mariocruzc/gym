from typing import Optional

import numpy as np
import gym


class AutoResetWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self._env_done = False

    def reset(self, **kwargs):
        self._env_done = False
        return self.env.reset(**kwargs)

    def step(self, action):
        if self._env_done:
            obs, info = self.reset(
                return_info=True
            )  # we are assuming the return_info behavior is implemented in environments using this wrapper
            return obs, None, None, info

        obs, reward, done, info = self.env.step(action)
        self._env_done = done

        return obs, reward, done, info
