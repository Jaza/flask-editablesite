import importlib
import re


def get_model_class(model_classpath, model_name):
    """Dynamically imports the model with the specified classpath."""

    model_classpath_format = r'^[a-z0-9_]+(\.[A-Za-z0-9_]+)+$'

    if not re.match(model_classpath_format, model_classpath):
        raise ValueError(
            ('Class path "%s" for model name "%s" '
                'must be a valid Python module / class path (in the '
                'format "%s")') % (
                    model_classpath,
                    model_name,
                    model_classpath_format))

    model_classpath_split = model_classpath.rpartition('.')
    model_modulepath, model_classname = (
        model_classpath_split[0],
        model_classpath_split[2])

    try:
        model_module = importlib.import_module(model_modulepath)
    except ImportError:
        raise ValueError(
            ('Error importing module "%s" for '
                'model name "%s"') % (
                    model_modulepath,
                    model_name))

    model_class = getattr(model_module, model_classname, None)
    if not model_class:
        raise ValueError(
            ('Class "%s" not found in module "%s" for '
                'model name "%s"') % (
                    model_classname,
                    model_modulepath,
                    model_name))

    return model_class
