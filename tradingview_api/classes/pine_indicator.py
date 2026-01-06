class PineIndicator:
    def __init__(self, options):
        self._options = options
        self._type = "Script@tv-scripting-101!"

    @property
    def pineId(self):
        return self._options.get("pineId")

    @property
    def pineVersion(self):
        return self._options.get("pineVersion")

    @property
    def description(self):
        return self._options.get("description")

    @property
    def shortDescription(self):
        return self._options.get("shortDescription")

    @property
    def inputs(self):
        return self._options.get("inputs")

    @property
    def plots(self):
        return self._options.get("plots")

    @property
    def type(self):
        return self._type

    def setType(self, indicator_type="Script@tv-scripting-101!"):
        self._type = indicator_type

    @property
    def script(self):
        return self._options.get("script")

    def setOption(self, key, value):
        prop_id = ""
        inputs = self._options.get("inputs") or {}

        if f"in_{key}" in inputs:
            prop_id = f"in_{key}"
        elif key in inputs:
            prop_id = key
        else:
            for input_id, item in inputs.items():
                if item.get("inline") == key or item.get("internalID") == key:
                    prop_id = input_id
                    break

        if not prop_id or prop_id not in inputs:
            raise ValueError(f"Input '{key}' not found ({prop_id}).")

        input_item = inputs[prop_id]
        input_type = input_item.get("type")

        types = {
            "bool": bool,
            "integer": int,
            "float": (int, float),
            "text": str,
        }

        required = types.get(input_type)
        if required is not None:
            if not isinstance(value, required) or (input_type == "integer" and isinstance(value, bool)):
                expected = required.__name__ if hasattr(required, "__name__") else "Number"
                raise TypeError(
                    f"Input '{input_item.get('name')}' ({prop_id}) must be a {expected} !"
                )

        options = input_item.get("options")
        if options and value not in options:
            raise ValueError(
                f"Input '{input_item.get('name')}' ({prop_id}) must be one of these values: {options}"
            )

        input_item["value"] = value
