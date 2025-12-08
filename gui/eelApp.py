from pathlib import Path
import sys
import io
import argparse
import logging


def get_static_path():
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    # return base / ("dist" if hasattr(sys, "_MEIPASS") else "build")
    return base / "build"


def main():
    import eel
    from py.models import EelExposer

    web_dir = get_static_path()
    eel.init(str(web_dir))

    EelExposer().expose_fns()

    def on_close(route, websockets):
        if websockets:  # aún hay sockets abiertos
            return
        closer = getattr(eel, "close", None)
        if callable(closer):
            closer()  # versiones nuevas
        sys.exit(0)

    eel.start(
        "index.html",
        size=(800, 600),
        port=8888,
        close_callback=on_close,
        block=True,
        mode='edge'
    )


if __name__ == "__main__":
    main()
