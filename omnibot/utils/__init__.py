def get_callback_id(component):
    """
    Retrieves the callback ID of the given interactive component.
    In the case the component corresponds to Slack's newer block
    components, return its block ID instead, but treat it as though
    it were the callback ID to minimize code change as the two
    function similarly.
    """
    if component.get("type") == "block_actions":
        actions = component.get("actions", [])
        action = next(iter(actions))
        return action.get("block_id")
    elif component.get("type") == "view_submission":
        view = component.get("view", {})
        return view.get("callback_id")
    else:
        return component.get("callback_id")


def merge_logging_context(*args):
    """
    Merge return a merged dict of the logging context dicts passed in.
    """
    ret = {}
    for arg in args:
        ret.update(arg)
    return ret
