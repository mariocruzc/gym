"""Wrapper that autoreset environments when `terminated=True` or `truncated=True`."""
import gym
from gym.utils.step_api_compatibility import step_api_compatibility


class AutoResetWrapper(gym.Wrapper):
    """A class for providing an automatic reset functionality for gym environments when calling :meth:`self.step`.

    When calling step causes :meth:`Env.step` to return `terminated=True` or `truncated=True`, :meth:`Env.reset` is called,
    and the return format of :meth:`self.step` is as follows: ``(new_obs, closing_reward, closing_terminated, closing_truncated, info)``
    with new step API and ``(new_obs, closing_reward, closing_done, info)`` with the old step API.
     - ``new_obs`` is the first observation after calling :meth:`self.env.reset`
     - ``closing_reward`` is the reward after calling :meth:`self.env.step`, prior to calling :meth:`self.env.reset`.
     - ``closing_done`` is always True. In the new API, either ``closing_terminated`` or ``closing_truncated`` is True
     - ``info`` is a dict containing all the keys from the info dict returned by the call to :meth:`self.env.reset`,
       with an additional key "closing_observation" containing the observation returned by the last call to :meth:`self.env.step`
       and "closing_info" containing the info dict returned by the last call to :meth:`self.env.step`.

    Warning: When using this wrapper to collect rollouts, note that when :meth:`Env.step` returns done, a
        new observation from after calling :meth:`Env.reset` is returned by :meth:`Env.step` alongside the
        closing reward and done state from the previous episode.
        If you need the closing state from the previous episode, you need to retrieve it via the
        "closing_observation" key in the info dict.
        Make sure you know what you're doing if you use this wrapper!
    """

    def __init__(self, env: gym.Env, new_step_api: bool = False):
        """A class for providing an automatic reset functionality for gym environments when calling :meth:`self.step`.

        Args:
            env (gym.Env): The environment to apply the wrapper
            new_step_api (bool): Whether the wrapper's step method outputs two booleans (new API) or one boolean (old API)
        """
        super().__init__(env, new_step_api)

    def step(self, action):
        """Steps through the environment with action and resets the environment if a done-signal is encountered.

        Args:
            action: The action to take

        Returns:
            The autoreset environment :meth:`step`
        """
        obs, reward, terminated, truncated, info = step_api_compatibility(
            self.env.step(action), True
        )

        if terminated or truncated:

            new_obs, new_info = self.env.reset(return_info=True)
            assert (
                "closing_observation" not in new_info
            ), 'info dict cannot contain key "closing_observation" '
            assert (
                "closing_info" not in new_info
            ), 'info dict cannot contain key "closing_info" '

            new_info["closing_observation"] = obs
            new_info["closing_info"] = info

            obs = new_obs
            info = new_info

        return step_api_compatibility(
            (obs, reward, terminated, truncated, info), self.new_step_api
        )
