if __name__ == "__main__":
    import os
    import sys
    import json
    import ctypes
    from PySide6.QtCore import Qt, QAbstractNativeEventFilter
    from PySide6.QtWidgets import QApplication
    from Include import GetLogger, Callback

    log_prefix = "Application"
    GetLogger().info("Initializing", log_prefix)

    app_class_name = 'MACRO'
    str_app_version: str = "?.?.?"
    str_app_build_date: str = "?.?.?"
    version_info: dict = {
        "version": str_app_version,
        "build_date": str_app_build_date
    }

    try:
        filepath = os.path.abspath('./Resource/version_info.json')
        with open(filepath, "r") as fp:
            info = json.load(fp)
        str_app_version = info.get("version", "???")
        version_info["version"] = str_app_version
        str_app_build_date = info.get("date", "???")
        version_info["build_date"] = str_app_build_date
    except Exception as e:
        GetLogger().critical(f"Failed to read version info: {e}", log_prefix)


    class WinEventFilter(QAbstractNativeEventFilter):
        def __init__(self):
            QAbstractNativeEventFilter.__init__(self)
            self.sig_message = Callback(int)

        def nativeEventFilter(self, eventType, message):
            if eventType == 'windows_generic_MSG':
                msg = ctypes.wintypes.MSG.from_address(int(message))
                self.sig_message.emit(msg.message)
            return False, 0


    # QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar)
    os.environ["QT_FONT_DPI"] = "96"
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi)

    app = QApplication(sys.argv)
    win_event_filter = WinEventFilter()
    app.installNativeEventFilter(win_event_filter)
    app.setStyle("fusion")
    app.styleHints().setColorScheme(Qt.ColorScheme.Light)

    try:
        nsipath = os.path.abspath('./MakeInstaller/MakeInstaller.nsi')
        with open(nsipath, 'r') as fp:
            nsidata = fp.read()
        beg = nsidata.find('APP_VERSION')
        idx1 = nsidata.find('"', beg)
        idx2 = nsidata.find('"', idx1 + 1)
        strleft = nsidata[:idx1 + 1]
        strright = nsidata[idx2:]
        strbetween = nsidata[idx1 + 1:idx2]
        if strbetween != str_app_version:
            # string 분할 후 새 문자열 삽입한 뒤 파일로 쓴다.
            nsinewdata = strleft + str_app_version + strright
            with open(nsipath, 'w') as fp:
                nsidata = fp.write(nsinewdata)
            GetLogger().info("Changed nsis script", log_prefix)
    except FileNotFoundError:
        pass
    except Exception as e:
        GetLogger().critical(f"Failed to modify installer script: {e}", log_prefix)


    # prevent multi-execution
    GetLogger().info('Finding other process which is running now', log_prefix)
    app_mutex = None
    already_running = False
    if os.name == 'nt':
        import win32event
        import win32api

        try:
            app_mutex = win32event.CreateMutex(None, False, app_class_name)
            lasterror = win32api.GetLastError()
            if lasterror == 183:  # ERROR_ALREADY_EXIST
                already_running = True
                win32api.CloseHandle(app_mutex)
            else:
                GetLogger().info(f"Mutex {app_mutex} Created", log_prefix)
        except Exception as e:
            GetLogger().critical(f"Failed to create app mutex: {e}", log_prefix)
            already_running = True

    try:
        if not already_running:
            from Include import AppCore, MainWindow

            core = AppCore()
            mainWnd = MainWindow()
            mainWnd.setCore(core)
            mainWnd.setVersionInfo(version_info)
            mainWnd.show()
            mainWnd.raise_()
            win_event_filter.sig_message.connect(mainWnd.onWindowMessage)
            app.exec()

            if os.name == 'nt':
                import win32api
                try:
                    win32api.CloseHandle(app_mutex)
                    GetLogger().info(f'Mutex Closed', log_prefix)
                except Exception as e:
                    GetLogger().critical(f"Mutex Close Exception: {e}", log_prefix)
            mainWnd.release()
            core.release()
        else:
            if os.name == 'nt':
                import win32gui
                import win32con
                hwnd = win32gui.FindWindow(None, "MACRO")
                GetLogger().info(f'Found other process (hwnd={hwnd}), calling SendMessage', log_prefix)
                if hwnd:
                    win32gui.SendMessage(hwnd, 1025, 0, 0)  # WM_USER + 1
            else:
                from PySide6.QtGui import QIcon, QGuiApplication
                from PySide6.QtWidgets import QMessageBox, QMainWindow

                wnd = QMainWindow()
                wnd.setWindowIcon(QIcon('./Resource/application.ico'))
                wnd.resize(0, 0)
                qtRect = wnd.frameGeometry()
                centerPt = QGuiApplication.primaryScreen().availableGeometry().center()
                qtRect.moveCenter(centerPt)
                wnd.move(qtRect.topLeft())
                wnd.hide()
                ret = QMessageBox.warning(wnd, 'Warning', 'Application is already running!',
                                          QMessageBox.StandardButton.Yes)
                if ret == QMessageBox.StandardButton.Yes:
                    pass
        GetLogger().info("Terminated", log_prefix)
        QApplication.quit()
        sys.exit()
    except Exception as e:
        GetLogger().critical(f"exception when init application: {e}", log_prefix)
