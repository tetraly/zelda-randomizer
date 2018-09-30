from randomizer.flags import FLAGS


class Settings:
  def __init__(self, mode='full', debug_mode=False, custom_flags=None):
    """
        :type mode: str
        :type debug_mode: bool
        :type custom_flags: dict[bool]
        """
    self._mode = mode
    self._debug_mode = debug_mode
    self._custom_flags = {}
    if custom_flags is not None:
      self._custom_flags.update(custom_flags)
    for flag in FLAGS:
      # If we're in full randomize mode, override all the flags to on.
      if mode == 'full':
        self._custom_flags[flag[0]] = True
      else:
        self._custom_flags.setdefault(flag[0], False)
      self._custom_flags.setdefault(flag[0], True)

  def custom_flags_to_json(self):
    """Return JSON serialization of custom flags.
        :rtype: list[bool]
        """
    return [self._custom_flags[flag[0]] for flag in FLAGS]

  @property
  def mode(self):
    """:rtype: str"""
    return self._mode

  @property
  def debug_mode(self):
    """:rtype: bool"""
    return self._debug_mode

  def get_flag(self, flag):
    """Get a specific custom flag.
        :param flag:
        :return:
        """
    return self._custom_flags.get(flag, True)

  def __getattr__(self, item):
    """Fall-back to get the custom flags as if they were class attributes.
        :type item: str
        :rtype: bool
        """
    if self._mode == 'full':
      return True
    if item in self._custom_flags:
      return self._custom_flags[item]
    raise AttributeError(item)
