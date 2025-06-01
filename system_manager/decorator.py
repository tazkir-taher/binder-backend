import system_manager.views


def seed_data(view_func):
    def wrapper_func(request, *args, **kwargs):
        system_manager.views.seed()
        return view_func(request, *args, **kwargs)

    return wrapper_func
