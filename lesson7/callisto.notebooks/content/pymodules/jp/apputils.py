import asyncio
import functools

def run_in_main_thread(func):
    loop = asyncio.get_event_loop()

    def inner(*args, **kwargs):
        loop.call_soon_threadsafe(functools.partial(func,
                                                    *args,
                                                    **kwargs))
    return inner
