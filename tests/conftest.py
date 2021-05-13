import pytest

from omnibot import settings


class SettingsOverrider(object):
    def __call__(self, **kwargs):
        """Override global settings with the keyword arguments."""
        self.orig_values = {k: settings.get(k) for k in kwargs.keys()}
        for k, v in kwargs.items():
            setattr(settings, k, v)

    def reset(self):
        """Reset settings overrides to their original values."""
        if not hasattr(self, "orig_values"):
            raise ValueError("No overriden values to reset")
        for k, v in self.orig_values.items():
            setattr(settings, k, v)


@pytest.fixture
def settings_override():
    """A py.test fixture for temporarily overriding settings during a test.
    When called, this will override global settings using the provided values.
    The new settings will exist during the scope of the test function, and will
    get reset to the original values automatically after the test.

    Usage:

        def test_my_function(settings_override):
            settings(MY_SETTING='my value')
            # do_something()

    Keyword Arguments:

        All keyword arguments will be interpreted as setting names.
    """
    overrider = SettingsOverrider()
    yield overrider
    overrider.reset()
