import sys
import jinja2

class LazyTemplate(jinja2.Template):
    def render(self, *args, **kwargs):
        vars = dict_or_equivalent(*args, **kwargs)
        try:
            cx = self.new_context(vars)
            rendered = self.root_render_func(cx)
            return jinja2.utils.concat(rendered)
        except Exception:
            exc_info = sys.exc_info()
        return self.environment.handle_exception(exc_info, True)

    def new_context(self, vars=None, shared=False, locals=None):
        return new_lazy_context(self.environment, self.name, self.blocks, vars,
                shared, self.globals, locals)

def dict_or_equivalent(*args, **kwargs):
    if len(args)>0 and is_dict_equivalent(args[0]):
        obj = args[0]
        obj.update(**kwargs)
    else:
        obj = dict(*args, **kwargs)
    return obj

def is_dict_equivalent(obj):
    return (hasattr(obj, "__getitem__") 
            and hasattr(obj, "update") 
            and hasattr(obj, "keys"))

def new_lazy_context(environment, template_name, blocks, vars=None,
        shared=None, globals=None, locals=None):
    if vars is None:
        vars = {}
    if shared:
        parent = vars
    else:
        parent = dict_or_equivalent(globals or (), **vars)
    if locals:
        # if the parent is shared a copy should be created because
        # we don't want to modify the dict passed
        if shared:
            parent = dict(parent)
        for key, value in iteritems(locals):
            if value is not missing:
                parent[key] = value
    return environment.context_class(environment, parent, template_name,
                                     blocks)
