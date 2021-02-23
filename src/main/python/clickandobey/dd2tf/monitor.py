"""
Module used to convert a monitor section of a datadog json file into a terraform monitor.
"""

from typing import Dict, List, Union


class Monitor:
    """
    Class used to convert a datadog json monitor into a terraform monitor.
    """

    def __init__(self, monitor_dict: Dict[str, Union[str, Dict, List]]):
        self.__monitor_dict = monitor_dict

    @property
    def name(self) -> str:
        """
        Name of the Datadog monitor.
        """
        return self.monitor_dict["name"]

    @property
    def type(self) -> str:
        """
        Monitor Type.
        """
        return self.monitor_dict["type"]

    @property
    def query(self) -> str:
        """
        Query used for the monitor.
        """
        return self.monitor_dict["query"]

    @property
    def message(self) -> str:
        """
        Message for the monitor.
        """
        return repr(self.monitor_dict["message"])[1:-1]

    @property
    def escalation_message(self) -> Union[None, str]:
        """
        Escalation message for the monitor.
        """
        return repr(self.options.get("escalation_message", None))[1:-1]

    @property
    def thresholds(self) -> Dict[str, Union[int, float]]:
        """
        The thresholds for the alert.
        """
        return self.options.get("thresholds", {})

    @property
    def tags(self) -> List[str]:
        """
        Tags for the monitor.
        """
        return self.monitor_dict["tags"]

    @property
    def notify_audit(self) -> Union[None, bool]:
        """
        ???
        """
        return self.options.get("notify_audit", None)

    @property
    def locked(self) -> Union[None, bool]:
        """
        Whether the monitor is locked.
        """
        return self.options.get("locked", None)

    @property
    def renotify_interval(self) -> Union[None, int]:
        """
        Number of minutes to wait before resending the alert.
        """
        return self.options.get("renotify_interval", None)

    @property
    def no_data_timeframe(self) -> Union[None, int]:
        """
        Amount of seconds no data can be found before the alert is triggered.
        """
        return self.options.get("no_data_timeframe", None)

    @property
    def include_tags(self) -> bool:
        """
        Whether to include tags.
        """
        return self.options.get("include_tags", False)

    @property
    def new_host_delay(self) -> int:
        """
        Amount of seconds to wait for a new host to come up.
        """
        return self.options.get("new_host_delay", 0)

    @property
    def require_full_window(self) -> bool:
        """
        Require the full time period of data to be populated before raising the alert.
        """
        return self.options.get("require_full_window", False)

    @property
    def notify_no_data(self) -> bool:
        """
        Whether to notify if no data has been received.
        """
        return self.options.get("notify_no_data", False)

    @property
    def monitor_dict(self) -> Dict[str, Union[str, Dict, List]]:
        """
        The dictionary representing the datadog monitor.
        """
        return self.__monitor_dict

    @property
    def options(self) -> Dict[str, Union[str, Dict, List]]:
        """
        Return the dictionary of options from the monitor.
        """
        return self.monitor_dict.get("options", {})

    # pylint: disable=too-many-branches
    def to_terraform(self) -> str:
        """
        Return a string representation of a widget in terraform.
        """
        terraform_string = \
            f'resource "datadog_monitor" "{self.terraform_name()}_monitor" {{\n' + \
            f'  name = "{self.name}"\n' + \
            f'  type = "{self.type}"\n' + \
            f'  message = "{self.message}"\n' + \
            f'  query = "{self.query}"\n'

        if self.escalation_message:
            terraform_string += f'  escalation_message = "{self.escalation_message}"\n'

        terraform_string += "\n"

        if self.thresholds:
            terraform_string += "  thresholds {\n"
            for key in sorted(self.thresholds):
                terraform_string += f"    {key} = {self.thresholds[key]}\n"
            terraform_string += "  }\n\n"

        if self.tags:
            terraform_string += "  tags = [\n"
            for tag in self.tags[:-1]:
                terraform_string += f'    "{tag}",\n'
            terraform_string += f'    "{self.tags[-1]}"\n'
            terraform_string += "  ]\n\n"

        if self.notify_audit is not None:
            terraform_string += f"  notify_audit = {str(self.notify_audit).lower()}\n"

        if self.locked is not None:
            terraform_string += f"  locked = {str(self.locked).lower()}\n"

        if self.renotify_interval is not None:
            terraform_string += f"  renotify_interval = {self.renotify_interval}\n"

        if self.no_data_timeframe is not None:
            terraform_string += f"  no_data_timeframe = {self.no_data_timeframe}\n"

        if self.include_tags is not None:
            terraform_string += f"  include_tags = {str(self.include_tags).lower()}\n"

        if self.new_host_delay is not None:
            terraform_string += f"  new_host_delay = {self.new_host_delay}\n"

        if self.require_full_window is not None:
            terraform_string += f"  require_full_window = {str(self.require_full_window).lower()}\n"

        if self.notify_no_data is not None:
            terraform_string += f"  notify_no_data = {str(self.notify_no_data).lower()}\n"

        terraform_string += "}"
        return terraform_string

    def terraform_name(self):
        """
        Return a string for the terraform resource name based off of the name of the monitor.
        """
        words = []
        for word in self.name.split(" "):
            word = word.lower()
            word = "".join(c for c in word if c.isalpha())
            if word:
                words.append(word)
        return "_".join(words)
