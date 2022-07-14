import sys
from clo import environment, system_settings
from maintenance import maintenancetool


if __name__ == '__main__':
    app_dir = environment.Environment.app_dir()
    m = maintenancetool.Maintenancetool(app_dir)

    sys_settings = system_settings.SystemSettings()

    mt_proxy = maintenancetool.Maintenancetool.ProxySettings(
        str(int(sys_settings.get_proxy_type())),
        sys_settings.get_proxy())
    m.configure_proxy(mt_proxy)

    try:
        update_available, updates_data = m.check_updates()
        if update_available:
            print(updates_data, file=sys.stderr)
            sys.exit(74)
    except Exception as e:
        sys.exit(1)

    sys.exit(0)
